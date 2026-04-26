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
        self.action_space = spaces.Box(low=-5.0, high=5.0, shape=(4, 3), dtype=np.float32)
        self.observation_space = spaces.Box(
            low=-1000.0, high=1000.0, shape=(2, 3), dtype=np.float32)

        if not rclpy.ok():
            rclpy.init()
        self.node = rclpy.create_node('spot_learning')

        self.fr_pub = self.node.create_publisher(
            KinematicPose, '/spot_fr_control/reference', qos_profile_sensor_data)
        self.fl_pub = self.node.create_publisher(
            KinematicPose, '/spot_fl_control/reference', qos_profile_sensor_data)
        self.hr_pub = self.node.create_publisher(
            KinematicPose, '/spot_hr_control/reference', qos_profile_sensor_data)
        self.hl_pub = self.node.create_publisher(
            KinematicPose, '/spot_hl_control/reference', qos_profile_sensor_data)

        self.imu_sub = self.node.create_subscription(
            Imu, '/spot_trunk/imu', self._state_callback, qos_profile_sensor_data)
        
        self.terminate_msg = KinematicPose()
        self.terminate_msg.pose_twist.linear.x = 0.0
        self.terminate_msg.pose_twist.linear.y = 0.0
        self.terminate_msg.pose_twist.linear.z = 0.0

        self._imu_state = np.zeros((2, 3), dtype=np.float32)
        self._new_imu_data = False

    def _state_callback(self, msg: Imu):
        self._imu_state[0] = np.array(
            [
                msg.angular_velocity.x,
                msg.angular_velocity.y,
                msg.angular_velocity.z
            ]
        )
        self._imu_state[1] = np.array(
            [
                msg.linear_acceleration.x,
                msg.linear_acceleration.y,
                msg.linear_acceleration.z
            ]
        )
        self._new_imu_data = True

    def step(self, action):
        ...
        return observation, reward, terminated, truncated, info

    def reset(self, seed=None, options=None):
        ...
        return observation, info

    def close(self):
        stop_cmd = KinematicPose()
        self.fr_pub.publish(stop_cmd)
        self.fl_pub.publish(stop_cmd)
        self.hr_pub.publish(stop_cmd)
        self.hl_pub.publish(stop_cmd)
