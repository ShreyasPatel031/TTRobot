## Moveit Servo

#### Quick Start Guide for UR5 example

Clone the `universal_robot` repo into your catkin workspace:

    git clone https://github.com/ros-industrial/universal_robot.git

Run `rosdep install` from the `src` folder to install dependencies.

    rosdep install --from-paths . --ignore-src -y

Build and subsequently source the catkin workspace. Startup the robot and MoveIt:

```sh
roslaunch tt_robot tt_robot.launch 

roslaunch tt_robot_moveit_config tt_robot_planning_execution.launch 

roslaunch tt_robot_moveit_config moveit_rviz.launch
```

In RViz, "plan and execute" a motion to a non-singular position (not all zero joint angles) that is not close to a joint limit.

Switch to a compatible type of `ros-control` controller. It should be a `JointGroupVelocityController` or a `JointGroupPositionController`, not a trajectory controller like MoveIt usually requires.

```sh
rosservice call /controller_manager/switch_controller "start_controllers:
- 'joint_group_position_controller'
stop_controllers:
- 'arm_controller'
strictness: 2"
```

```sh
rosservice call /controller_manager/switch_controller "start_controllers:
- 'arm_controller'
stop_controllers:
- 'joint_group_position_controller'
strictness: 2"
```

Launch the servo node. This example uses commands from a SpaceNavigator joystick-like device:

```sh
roslaunch moveit_servo spacenav_cpp.launch
    
cd catkin_ws/src/tt_robot_training/
rosrun tt_robot_training listener_test.py 3600 # change trainging back to q learning
```


If you dont have a SpaceNavigator, send commands like this:

```sh
rostopic pub -r 100 /servo_server/delta_twist_cmds geometry_msgs/TwistStamped "header: auto
twist:
  linear:
    x: 0
    y: 0  
    z: 1
  angular:
    x: 0
    y: 0.0
    z: 0.0"
```

If you see a warning about "close to singularity", try changing the direction of motion.

#### Running Tests

Run tests from the moveit\_servo folder:

    catkin run_tests --no-deps --this