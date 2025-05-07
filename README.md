# kinovaGen3 Robot Setup

Quick ROS2 setup for Kinova gen 3

## Conexión inicial 
 
- Make sure youre using ros2 humble or foxy which tiene mejor soporte de hardware para estas versiones de ros. 
- Encienda el robot y asegurerse que lo puede operar con el joystick de xbox (solo para verificar que el robot funciona). 
- Establezca una ip manual en la PC, en este caso se usa IPV4 manual con 192.168.1.11 con mascara 255.255.255.1. 
- Conecte el cable ethernet a la computadora y asegurerse que puede hacer ping a la ip del robot 192.168.1.11. Si hay paquetes, la conexion esta establecida. 

## ROS2 setup 

1.  Asegurese de usar la version correcta de ros2, crear un workspace con capacidad de source y construir paquetes. 
2. En el wks, dentro del src clone el repositorio de kenova robotics: git clone https://github.com/Kinovarobotics/kinova_ros2.git
3. fuera de src, agregue las dependencias
```bash
rosdep install --from-paths src --ignore-src -r -y
```
construya el paquete con colcon build y source 
5. Dependiedno de la version que se haya instalado de los paquetes es el nombre que tienen los launch files y demas, para esta version, se esta utilizando el launch 
ros2 launch kortex_bringup gen3.launch.py robot_ip:=192.168.1.10 (importante indicar la IP ya mencionada). 
6. Al correr este launch file el robot estara ahora controlado por ROS2, por lo que no sera posible moverlo manualmente o con el joystick. 
7. Para asegurarse que esta funcionando el launch, vea la lista de topicos, debe haber una lista grande, incluyendo twist_controller/commands, donde se publicara manualmente para depurar. 
8. Publicando en tal topico, el efector final se movera de acuerdo a los parametros que usted indique, recuerde mantener velocidades bajas para evitar cualquier tipo de movimiento inesperado. En caso de ser necesario, presione el boton rojo de emergencia (que apaga completamente el robot) o en su caso, mantenga presionado hasta que se apague el boton de encendido del robot.
9. Para probar, publique en el topico desde la terminal:
```bash
ros2 topic pub /twist_controller/commands geometry_msgs/Twist "{linear: {x: 0.0, y: 0.0, z: 0.0}, angular: {x: 0.0, y: 0.0, z: 0.02}}"
```
