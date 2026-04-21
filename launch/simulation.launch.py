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
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.conditions import IfCondition, UnlessCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import Command, FindExecutable, LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():

    # Declare arguments
    declared_arguments = []
    declared_arguments.append(
        DeclareLaunchArgument(
            'gz_gui',
            default_value='true',
            description='Start Gazebo GUI. The default behavior'
            + ' starts gazebo in server mode using Rviz2 as graphical interface.',
        )
    )
    declared_arguments.append(
        DeclareLaunchArgument(
            'robot',
            default_value='ur5',
            description='Robot model. Options: ur5, spot, spot_leg, hyl',
        )
    )
    declared_arguments.append(
        DeclareLaunchArgument(
            'controller',
            default_value='ur5_controller',
            description='Controller name in controllers.yaml',
        )
    )
    declared_arguments.append(
        DeclareLaunchArgument(
            'world',
            default_value='benchmark',
            description='Gazebo world. Check worlds directory.',
        )
    )
    declared_arguments.append(
        DeclareLaunchArgument(
            'is_fixed',
            default_value='true',
            description='Set the URDF in fixed (test stand) configuration.',
        )
    )

    # Arguments variables
    gz_gui = LaunchConfiguration('gz_gui')
    robot_model = LaunchConfiguration('robot')
    controller_name = LaunchConfiguration('controller')

    this_package_share = FindPackageShare('robot_impedance_lab')
    gazebo_world = PathJoinSubstitution(
        [this_package_share, 'worlds', [LaunchConfiguration('world'), '.sdf']]
    )
    bridges = PathJoinSubstitution([this_package_share, 'config', 'bridges_ft_sensor.yaml'])
    controllers_config = PathJoinSubstitution([this_package_share, 'config', 'controllers.yaml'])
    rviz_config = PathJoinSubstitution([this_package_share, 'config', 'rviz2.rviz'])

    # gazebo
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
            'gz_args': ['-s -r -v0 ', gazebo_world],
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
                    [robot_model, '.urdf.xacro'],
                ]
            ),
            ' fixed:=',
            LaunchConfiguration('is_fixed'),
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
        output='log',
        arguments=[
            '-topic',
            '/robot_description',
        ],
    )

    broadcaster_spawner = Node(
        package='controller_manager',
        executable='spawner',
        arguments=['joint_state_broadcaster'],
    )

    controller_spawner = Node(
        package='controller_manager',
        executable='spawner',
        arguments=[
            controller_name,
            '--inactive',
            '--param-file',
            controllers_config,
        ],
    )
    rviz = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        output='log',
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
        controller_spawner,
        rviz,
    ]

    return LaunchDescription(declared_arguments + nodes)
