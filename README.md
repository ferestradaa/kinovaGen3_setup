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
