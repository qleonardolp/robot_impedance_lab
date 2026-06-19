# robot_impedance_lab

Virtual laboratory for robot impedance control assessment in ROS 2 and Gazebo Harmonic.

This repo host controllers and generators [configuration](./config/), Gazebo [worlds](./worlds/), and [launchers](./launch/). The [simulation.launch.py](./launch/simulation.launch.py) is a general purpose launcher with the following arguments:

| **Argument** | **Description** |
| ---------- | ----------- |
| robot | Robot platform to be controlled. See available models in [ros2_descriptions](https://github.com/qleonardolp/ros2_descriptions) |
| controller | Controller name. The controller configuration must have the robot joints and the proper options for the respective controller |
| world | Gazebo world file |
| bench_setup | Models `spot_leg` and `hyl` have test bench options. Choose `fixed` to simulate the leg suspended and free to move. Choose `vertical` to set the leg on a vertical slider, allowing jumping or troting. Choose `walker` to simulate the leg in a carousel-like setup, with 2-DoF, a central pivot and the z-axis. |
| gz_gui | Start Gazebo GUI (`true`), or Rviz2 (`false`) |

Available controllers (see [ros2_impedance_controller](https://github.com/qleonardolp/ros2_impedance_controller)):

| **Controller Type** | **Description** |
| ---------- | ----------- |
| CartesianController | Classical impedance control law with inertia shaping |
| BasicCartesianController | PD impedance + gravity compensation |
| MPCIController | Model Predictive Cartesian Impedance Control |

For convenience there are specific launchers too:

- [spot_simulation](./launch/spot_simulation.launch.py): Launch Spot quadruped with four impedance controllers activated;
- [spot_walker_simulation](./launch/spot_walker_simulation.launch.py): Launch spot_leg walking. The foot reference is generated with CPG;
- [bravo7_simulation](./launch/bravo7_simulation.launch.py): Launch Bravo 7 underwater manipulator in an underwater environment with impedance controller for 6-DoF and a jaw controller.

Except for `spot_simulation` launch, the controller must be activated after the simulation launch:

```bash
ros2 control set_controller_state <controller_name> active
```

## Examples

```bash
ros2 launch robot_impedance_lab simulation.launch.py robot:=spot_leg controller:=spot_fl_control bench_setup:=fixed gz_gui:=false
```

```bash
ros2 control set_controller_state spot_fl_control active
```
