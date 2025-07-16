# Kinova Gen3 Robot Setup

Quick ROS 2 setup guide for the Kinova Gen3 robot.

##  Initial Connection

- Make sure you're using **ROS 2 Humble** or **Foxy**, since those versions have better hardware support.  
- Turn on the robot and confirm you can control it using the Xbox joystick (just to check it's working).  
- Manually assign an IP address to your PC. In this setup, we're using **IPv4** with:  
  - IP: `192.168.1.11`  
  - Subnet mask: `255.255.255.0`  
- Connect the Ethernet cable and make sure you can ping the robot at `192.168.1.10`. If packets are received, the connection is working.

##  ROS 2 Setup

1. Make sure you're using the correct ROS 2 version and that you’ve created a workspace (`colcon` and `source` ready).

2. Inside the `src` folder of your workspace, clone the Kinova ROS 2 repository:

```bash
   git clone https://github.com/Kinovarobotics/ros2_kortex.git
```


  Outside the src folder, install the dependencies:

    rosdep install --from-paths src --ignore-src -r -y

Then build the package with colcon build and source it.

    Depending on the version of the packages installed, the launch file names may vary. For this version, use the launch file:

    ros2 launch kortex_bringup gen3.launch.py robot_ip:=192.168.1.10

(It’s important to specify the mentioned IP address.)

  Once this launch file is running, the robot will be controlled by ROS2, and manual or joystick control will no longer be possible.

  To ensure the launch is working, list the topics. There should be a long list, including twist_controller/commands, where commands will be manually published for debugging.

   By publishing to that topic, the end-effector will move according to the parameters you specify. Make sure to use low speeds to avoid any unexpected movements. If needed, press the red emergency button (which completely shuts down the robot), or hold the power button until it turns off.

  To test, publish to the topic from the terminal:

    ros2 topic pub /twist_controller/commands geometry_msgs/Twist "{linear: {x: 0.0, y: 0.0, z: 0.0}, angular: {x: 0.0, y: 0.0, z: 0.02}}"

  If an error occurs, such as the robot not moving, it’s likely that the motors are locked for safety. Check if the twist_controller is active using:

    ros2 control list_controllers

  Activate it with:
  ```bash
  ros2 control switch_controllers --start twist_controller --stop joint_trajectory_controller --strict --controller-manager /controller_manager
```
##  ROS2 rgb and depth camera setup 


##  Considerations
### Isaac sim - Rviz Bridge
For this robot, the package includes a default pubisher for joint position. But we will use joint_states topic to publish joint position from isaac sim. In roder to avoid 2 publishers at the same time (which its not actually possible) well need to delete the launcher publisher manually meanwhile another 
option is actuallty considered. For doing this, find kortex_control.launch.py and look for joint_state_broadcaster_spawner. Inactive the node in order to stop publishing on the topic. So those lines shoudl look like this:
```python
    joint_state_broadcaster_spawner = Node(
        package="controller_manager",
        executable="spawner",
        arguments=[
            "joint_state_broadcaster",
            "--controller-manager",
            "/controller_manager",
            "--inactive",
        ],
    )
```

### Move it 
Kinovas repo has probably not been updated for last pkg versions. Some commands might not work instantly after instalation. For this, some manual changes to launch files have been implemented:
1. For running Moveit2, official documentation refers to
```bash
 ros2 launch kinova_gen3_7dof_robotiq_2f_85_moveit_config robot.launch.py   robot_ip:=192.168.1.10   use_fake_hardware:=true   fake_sensor_commands:=true
```
Youll need to modificate xacros until downgraded parameters stop interferring with the lunch. 
Follow the route on your workspace:

```bash
  /fes_ros2_ws/src/ros2_kortex/kortex_description/grippers/robotiq_2f_85/urdf/robotiq_2f_85_macro.xacro

```
And delete every xacro:robotiq_gripper that may cause issues. Launch again and verify. For the moment, the xacro file should look like this:


```xml
<?xml version="1.0"?>
<robot name="robotiq_2f_85_model" xmlns:xacro="http://ros.org/wiki/xacro">
  <xacro:macro name="load_gripper" params="
    parent
    prefix
    use_fake_hardware:=false
    fake_sensor_commands:=false
    sim_gazebo:=false
    sim_isaac:=false
    isaac_joint_commands:=/isaac_joint_commands
    isaac_joint_states:=/isaac_joint_states
    use_internal_bus_gripper_comm:=false
    com_port:=/dev/ttyUSB0
    moveit_active:=false">
    <xacro:include filename="$(find robotiq_description)/urdf/robotiq_2f_85_macro.urdf.xacro" />

    <!-- Hardware talks directly to the gripper so we don't need ros2_control unless we are simulating -->
    <xacro:property name="include_ros2_control" value="false"/>
    <xacro:if value="${sim_gazebo or sim_isaac or use_fake_hardware or not use_internal_bus_gripper_comm}">
      <xacro:property name="include_ros2_control" value="true"/>
    </xacro:if>

    <xacro:robotiq_gripper
        name="RobotiqGripperHardwareInterface"
        prefix="${prefix}"
        parent="${parent}"
        include_ros2_control="${include_ros2_control}"
        com_port="${com_port}"
        use_fake_hardware="${use_fake_hardware}"
        fake_sensor_commands="${fake_sensor_commands}"
  
   >
        <origin xyz="0 0 0" rpy="0 0 0" />
    </xacro:robotiq_gripper>
  </xacro:macro>
</robot>

```
