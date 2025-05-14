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


3. fuera de src, agregue las dependencias
```bash
rosdep install --from-paths src --ignore-src -r -y
```
construya el paquete con colcon build y source 

4. Dependiedno de la version que se haya instalado de los paquetes es el nombre que tienen los launch files y demas, para esta version, se esta utilizando el launch 
ros2 launch kortex_bringup gen3.launch.py robot_ip:=192.168.1.10 (importante indicar la IP ya mencionada). 

5. Al correr este launch file el robot estara ahora controlado por ROS2, por lo que no sera posible moverlo manualmente o con el joystick.
   
6. Para asegurarse que esta funcionando el launch, vea la lista de topicos, debe haber una lista grande, incluyendo twist_controller/commands, donde se publicara manualmente para depurar.
    
7. Publicando en tal topico, el efector final se movera de acuerdo a los parametros que usted indique, recuerde mantener velocidades bajas para evitar cualquier tipo de movimiento inesperado. En caso de ser necesario, presione el boton rojo de emergencia (que apaga completamente el robot) o en su caso, mantenga presionado hasta que se apague el boton de encendido del robot.
   
8. Para probar, publique en el topico desde la terminal:
```bash
ros2 topic pub /twist_controller/commands geometry_msgs/Twist "{linear: {x: 0.0, y: 0.0, z: 0.0}, angular: {x: 0.0, y: 0.0, z: 0.02}}"
```
9. En caso de presentar algun error, como que el robot no se mueva, es probable que los motores esten bloqueados por seguridad. Verifique que twist_controller este activo usando:
```bash
ros2 control list_controllers
```
Hagalo activo con:
```bash
ros2 control switch_controllers --start twist_controller --stop joint_trajectory_controller --strict --controller-manager /controller_manager 
```
Verifique nuevamente

##  ROS2 rgb and depth camera setup 


##  Considerations
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
