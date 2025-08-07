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
Despite of adding the joint state publisher in isaac sims action graph, dont forget to add an Isaac Read Simulation Time Node, wich ads a timestamp for the publsiher and rviz would be fine.

### Join gripper and robot body in USD
1. Create Articulation root parent prim
2. Add flattened body and gripper usd. NO articulation root for both.
3. Join the last rigid body of the robots body and the first rigid body of the gripper using fixed joint
4. Manually set fixed joint pose to match relative gripper position to the robot so they look joined.
5. Export as flattened and remove instancebale if necessary.
    
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

##  Object detection 
6D pose is needed even on the starting purpose of the proeyct. Se usara el framwork de DOPE para obtener posicion y orientacion de objetos en tiempo real. Ademas, es posible aceelerar el proceso de inferencia con CUDA. 
1. Se obtiene un data set adaptando el workflow de nvidia para obtener anotaciones de rgb para modelo DOPE. https://github.com/NVIDIA-AI-IOT/synthetic_data_generation_training_workflow
Se han hecho ediciones para utilziar modelo usd de archivo local, cambiar el writer de replicatror (isaac sim extension) (KittiWriter originalmente) a DOPEwriter que da como output imagen rgb y json con pose 6d del modelo en camara. El cambio se resumen en:
```python

    output_directory = args.data_dir
    class_name_to_index_map = {"palletjack": 1}
    bucket = ""
    endpoint = ""
    writer_config = {"output_folder":output_directory,"use_s3": False, "bucket_name": bucket,"endpoint_url": endpoint}
    config_data = {
    "CLASS_NAME_TO_INDEX": {
        "palletjack": 1
    },

    "WIDTH": 1280,
    "HEIGHT": 720,
    "CAMERA_ROTATION": [-180, 0, 0], 
    "CAMERA_INTRINSICS" : {
        "fx": 1297.672904,
        "fy": 1298.631344,
        "cx": 620.914026,
        "cy": 238.280325
        }
    }
    
    writer_helper = DOPEWriter
    writer_helper.register_pose_annotator(config_data=config_data)
    writer = writer_helper.setup_writer(config_data=config_data, writer_config=writer_config)
    writer.attach(render_product)
    run_orchestrator()
    simulation_app.update()
```

La ventaja de usar DOPE es que tiene soporte oficial para ros2 y aceleracion por GPU en tiempo real. Puede hacerse con TensorFlow puro pero se pierde modularidad para:
1. Hacer el modelo compacto, real time y directamente compatible con ros2.2
2. Propenso a cambios que deben hacerse de forma completamente manual.

Se recomienda trabajar con Isaac ROS desde docker para facilitar el proceso. Comience desde setupear el ambiente 

https://nvidia-isaac-ros.github.io/concepts/docker_devenv/index.html#development-environment

3. Clone el repo de isaac ros common, vaya a la carpeta scripts y ejecute
```bash

./run_dev.sh 
```
Comenzaara la instalacion del contenedor con todas las dependencias necesarias. Incluye ros2 humble y el entorno completo de isaac ros. Al terminar, vuelva a abrir el contenedor para comenzar a generar codigo

Create the alias on bashrc
```bash
alias isaac_ros="/home/isaac_ros-dev/isaac_ros_common/scripts/run_dev.sh"

```
https://nvidia-isaac-ros.github.io/repositories_and_packages/isaac_ros_pose_estimation/isaac_ros_dope/index.html

https://nvidia-isaac-ros.github.io/concepts/pose_estimation/dope/tutorial_custom_model.html

Details for dataset
https://github.com/NVlabs/Deep_Object_Pose/tree/master/data_generation

Training 

https://github.com/NVlabs/Deep_Object_Pose/tree/master/train

Custom model 

https://nvidia-isaac-ros.github.io/concepts/pose_estimation/dope/tutorial_custom_model.html
