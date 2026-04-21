from glob import glob

from setuptools import find_packages, setup

package_name = 'robot_impedance_lab'
share_path = 'share/' + package_name

setup(
    name=package_name,
    version='1.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        (share_path, ['package.xml']),
        (share_path + '/worlds', glob('worlds/*.sdf')),
        (share_path + '/config', glob('config/*.yaml')),
        (share_path + '/launch', glob('launch/*launch.[pxy][yma]*')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='qleonardolp',
    maintainer_email='44267124+qleonardolp@users.noreply.github.com',
    description='Virtual laboratory for robot impedance control on Gazebo Harmonic.',
    license='Apache License 2.0',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [
        ],
    },
)
