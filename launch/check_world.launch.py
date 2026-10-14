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
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
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
            'world',
            default_value='waterworld',
            description='Gazebo world. Check worlds directory.',
        )
    )

    # Arguments variables
    gz_gui = LaunchConfiguration('gz_gui')

    this_package_share = FindPackageShare('robot_impedance_lab')
    gazebo_world = PathJoinSubstitution(
        [this_package_share, 'worlds', [LaunchConfiguration('world'), '.sdf']]
    )
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
        rviz,
    ]

    return LaunchDescription(declared_arguments + nodes)
