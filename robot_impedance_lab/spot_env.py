# Copyright 2026 qleonardolp
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import gymnasium as gym
from gymnasium import spaces

from kinematic_pose_msgs.msg import KinematicPose

import numpy as np
import rclpy
from rclpy.qos import qos_profile_sensor_data
from sensor_msgs.msg import Imu


class SpotROS2Env(gym.Env):
    """
    ROS2-based gymnasium environment.

    ROS2-based environment for reinforcement learning
    with the Spot robot with Cartesian impedance controllers.

    - State: trunk IMU data [angular_velocity, linear_acceleration] (6D)
    - Action: desired feet velocity w.r.t the trunk (4 x 3D)
    - Goal: Learn to walk
    """

    def __init__(self):
        super().__init__()
        # Action and observation spaces
        self.action_space = spaces.Box(low=-1.0, high=1.0, shape=(12,), dtype=np.float32)
        self.observation_space = spaces.Box(
            low=-100.0, high=100.0, shape=(6,), dtype=np.float32)

        if not rclpy.ok():
            rclpy.init()
        self.node = rclpy.create_node('spot_learning')

        self.fr_control = self.node.create_publisher(
            KinematicPose, '/spot_fr_control/reference', qos_profile_sensor_data)
        self.fl_control = self.node.create_publisher(
            KinematicPose, '/spot_fl_control/reference', qos_profile_sensor_data)
        self.hr_control = self.node.create_publisher(
            KinematicPose, '/spot_hr_control/reference', qos_profile_sensor_data)
        self.hl_control = self.node.create_publisher(
            KinematicPose, '/spot_hl_control/reference', qos_profile_sensor_data)

        self.imu_subscriber = self.node.create_subscription(
            Imu, '/spot_trunk/imu', self._state_callback, qos_profile_sensor_data)

        # Legs command message
        self.fr_cmd = KinematicPose()
        self.fl_cmd = KinematicPose()
        self.hr_cmd = KinematicPose()
        self.hl_cmd = KinematicPose()

        self._imu_state = np.zeros((6,), dtype=np.float32)
        self._new_imu_data = False
        self._spot_reward = 0.0

    def _state_callback(self, msg: Imu):
        self._imu_state[0] = np.float32(msg.angular_velocity.x)
        self._imu_state[1] = np.float32(msg.angular_velocity.y)
        self._imu_state[2] = np.float32(msg.angular_velocity.z)
        self._imu_state[3] = np.float32(msg.linear_acceleration.x)
        self._imu_state[4] = np.float32(msg.linear_acceleration.y)
        self._imu_state[5] = np.float32(msg.linear_acceleration.z)

        self._new_imu_data = True

    def _publish_action(self, action):
        self.fr_cmd.pose_twist.linear.x = float(action[0])
        self.fr_cmd.pose_twist.linear.y = float(action[1])
        self.fr_cmd.pose_twist.linear.z = float(action[2])

        self.fl_cmd.pose_twist.linear.x = float(action[3])
        self.fl_cmd.pose_twist.linear.y = float(action[4])
        self.fl_cmd.pose_twist.linear.z = float(action[5])

        self.hr_cmd.pose_twist.linear.x = float(action[6])
        self.hr_cmd.pose_twist.linear.y = float(action[7])
        self.hr_cmd.pose_twist.linear.z = float(action[8])

        self.hl_cmd.pose_twist.linear.x = float(action[9])
        self.hl_cmd.pose_twist.linear.y = float(action[10])
        self.hl_cmd.pose_twist.linear.z = float(action[11])

        self.fr_control.publish(self.fr_cmd)
        self.fl_control.publish(self.fl_cmd)
        self.hr_control.publish(self.hr_cmd)
        self.hl_control.publish(self.hl_cmd)

    def _check_termination(self):
        return abs(self._imu_state[3]) > 3.0

    def step(self, action):
        self._new_imu_data = False

        self._publish_action(action)

        while not self._new_imu_data:
            rclpy.spin_once(self.node, timeout_sec=0.008)

        self._spot_reward += self._imu_state[3:].dot([0.0, 0.0, -9.80665])
        terminated = bool(self._check_termination())

        return self._imu_state, self._spot_reward, terminated, False, {}

    def reset(self, seed=None, options=None):
        self._spot_reward = 0.0
        self.close()
        return self._imu_state, {}

    def close(self):
        stop_cmd = KinematicPose()
        self.fr_control.publish(stop_cmd)
        self.fl_control.publish(stop_cmd)
        self.hr_control.publish(stop_cmd)
        self.hl_control.publish(stop_cmd)
