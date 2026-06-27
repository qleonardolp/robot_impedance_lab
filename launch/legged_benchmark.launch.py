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

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, EmitEvent, IncludeLaunchDescription
from launch.conditions import IfCondition, UnlessCondition
import launch.events

from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import (
  Command,
  FindExecutable,
  LaunchConfiguration,
  PathJoinSubstitution
)
from launch_ros.actions import LifecycleNode, Node
from launch_ros.events.lifecycle import ChangeState
from launch_ros.substitutions import FindPackageShare
from lifecycle_msgs.msg import Transition


def generate_launch_description():

    # Declare arguments
    declared_arguments = []
    declared_arguments.append(
        DeclareLaunchArgument(
            'gz_gui',
            default_value='false',
            description='Start Gazebo GUI. The default behavior'
            + ' starts gazebo in server mode using Rviz2 as graphical interface.',
        )
    )

    # Leg controllers
    spot_controllers = [
        'spot_leg_control',
    ]

    # Configurations
    gz_gui = LaunchConfiguration('gz_gui')
    package_share = FindPackageShare('robot_impedance_lab')
    gazebo_world = PathJoinSubstitution([package_share, 'worlds', 'legged_benchmark.sdf'])
    bridges = PathJoinSubstitution([package_share, 'config', 'bridges_ft_sensor.yaml'])
    controllers_config = PathJoinSubstitution([package_share, 'config', 'controllers.yaml'])
    generator_config = PathJoinSubstitution([package_share, 'config', 'generators.yaml'])
    rviz_config = PathJoinSubstitution([package_share, 'config', 'legged_benchmark.rviz'])

    # Gazebo launch
    gazebosim = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            [FindPackageShare('ros_gz_sim'), '/launch/gz_sim.launch.py']
        ),
        launch_arguments={
            'gz_args': ['-r -v1 ', gazebo_world],
            'on_exit_shutdown': 'true',
        }.items(),
        condition=IfCondition(gz_gui),
    )
    gazebosim_headless = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            [FindPackageShare('ros_gz_sim'), '/launch/gz_sim.launch.py']
        ),
        launch_arguments={
            'gz_args': ['-r -v0 -s --headless-rendering ', gazebo_world],
            'on_exit_shutdown': 'true',
        }.items(),
        condition=UnlessCondition(gz_gui),
    )

    # ROS-Gazebo bridges
    gazebo_bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        parameters=[{'config_file': bridges}],
        output='screen',
    )

    # Get URDF via xacro
    robot_urdf = Command(
        [
            PathJoinSubstitution([FindExecutable(name='xacro')]),
            ' ',
            PathJoinSubstitution(
                [
                    FindPackageShare('ros2_descriptions'),
                    'description',
                    'spot_leg.urdf.xacro',
                ]
            ),
            ' setup:=fixed',
        ]
    )

    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        output='screen',
        parameters=[{'robot_description': robot_urdf}],
    )

    # Robot spawner in Gazebo.
    # This node indirectly uses the robot_urdf parsed here,
    # through the topic /robot_description
    gazebo_spawner = Node(
        package='ros_gz_sim',
        executable='create',
        arguments=['-topic', '/robot_description'],
    )

    broadcaster_spawner = Node(
        package='controller_manager',
        executable='spawner',
        arguments=['joint_state_broadcaster'],
    )

    controllers_spawner = Node(
        package='controller_manager',
        executable='spawner',
        arguments=[
            *spot_controllers,
            '--activate-as-group',
            '--param-file',
            controllers_config,
        ],
    )

    reference_generator = LifecycleNode(
        package='robot_impedance_analyzer',
        executable='kinematic_reference',
        name='benchmark_reference',
        namespace='',
        autostart=True,
        parameters=[generator_config],
        )

    identification = LifecycleNode(
        package='robot_impedance_analyzer',
        executable='identification',
        name='identification',
        namespace='',
        parameters=[generator_config],
        )

    config_identification = EmitEvent(
        event=ChangeState(
            lifecycle_node_matcher=launch.events.matches_action(identification),
            transition_id=Transition.TRANSITION_CONFIGURE,
        )
    )

    rviz = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        arguments=['-d', rviz_config],
        condition=UnlessCondition(gz_gui),
    )

    nodes = [
        gazebosim,
        gazebosim_headless,
        gazebo_bridge,
        robot_state_publisher,
        gazebo_spawner,
        broadcaster_spawner,
        controllers_spawner,
        reference_generator,
        identification,
        config_identification,
        rviz,
    ]

    return LaunchDescription(declared_arguments + nodes)
