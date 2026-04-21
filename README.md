# robot_impedance_lab

Virtual laboratory for [robot impedance control](https://github.com/qleonardolp/ros2_impedance_controller) assessment on Gazebo Harmonic simulations.

## Instructions

### Simulation with UR5 manipulator

Using the default setting:

```bash
ros2 launch robot_impedance_lab simulation.launch.py
```

Activate the manipulator controller:

```bash
ros2 control set_controller_state ur5_controller active
```

### Simulation with Spot leg

The `spot_leg` model is a single quadruped leg on a vertical slider. It can be either
free to move vertically, or in a fixed height, allowing a free movement on the foot frame without contact with the ground.

```bash
ros2 launch robot_impedance_lab simulation.launch.py robot:=spot_leg controller:=spot_leg_controller is_fixed:=false
```

```bash
ros2 launch robot_impedance_lab simulation.launch.py robot:=spot_leg controller:=spot_leg_controller is_fixed:=true
```

```bash
ros2 control set_controller_state spot_leg_controller active
```

Similarly, you can use these vertical setup with the hydraulic leg model HyL:

```bash
ros2 launch robot_impedance_lab simulation.launch.py robot:=hyl controller:=hyl_controller is_fixed:=false
```

### Simulation with Spot

This setting launch four impedance controllers, one for each leg:

```bash
ros2 launch robot_impedance_lab spot_simulation.launch.py
```

In this case the controllers are already active.
