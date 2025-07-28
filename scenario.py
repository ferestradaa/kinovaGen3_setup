from omni.isaac.core.utils.extensions import get_extension_path_from_name
from omni.isaac.core.utils.stage import add_reference_to_stage
from omni.isaac.core.articulations import Articulation
from omni.isaac.core.utils.nucleus import get_assets_root_path
from omni.isaac.core.objects.cuboid import FixedCuboid
from omni.isaac.core.objects import VisualCylinder
from omni.isaac.core.objects import VisualSphere
from omni.isaac.core.prims import XFormPrim
from omni.isaac.core.utils.numpy.rotations import euler_angles_to_quats
from omni.isaac.motion_generation import RmpFlow, ArticulationMotionPolicy
from omni.isaac.motion_generation.interface_config_loader import (
    get_supported_robot_policy_pairs,
    load_supported_motion_policy_config,)
from omni.isaac.core.prims import RigidPrim  
import json 
import numpy as np
import os
import carb 
from pxr import Usd
import omni.usd
import omni.graph.core as og

from .scripts.human import Human
from .scripts.ros_bridge import  Ros_Bridge

class Hri_ue5e():
    if not hasattr(carb, "log_warning"):
        carb.log_warning = carb.log_warn

    def __init__(self):
        self._rmpflow = None
        self._articulation_rmpflow = None
        self._articulation = None
        self._target = None
        self._dbg_mode = False
    

    def load_example_assets(self):
        self.stage = omni.usd.get_context().get_stage()
        stage_path = '/World'
        robot_prim_path = "/World/kinova/complete_kinova_flat2" #literal 
        path_to_robot_usd = "/home/aist/Desktop/FES/HRI/extensions/hri_integration/RmpFlow_Example_python/robot_scene2.usd" #path for 
        add_reference_to_stage(path_to_robot_usd, stage_path)
        self._articulation = Articulation(robot_prim_path)    

        self._target = VisualCylinder("/World/target/target",scale=[0.04, 0.04 , 0.04],color=np.array([0.1,0.0,0.0]))
        #self.esfera = VisualSphere("/World/target/target3",scale=[0.04, 0.04 , 0.06],color=np.array([1.0,0.0,0.0]))
        #self._obstacle = RigidPrim("/World/obstacles/table/AnyConv_com__table/instance_def_1_a8d2744e_c4ac_4c01_9007_d297f2c4fa8a", name="ObstacleTable")
        self._obstacle2 = RigidPrim("/World/obstacles/table2/thor_table", name="ObstacleTable2")
        self._obstacle3 = RigidPrim("/World/obstacles/desks/desk1/desk1_proxy", name="desk1")
        self._obstacle4 = RigidPrim("/World/obstacles/desks/desk2/desk2_proxy", name="desk2")        #self._obstacle5 = RigidPrim("/World/obstacles/desks/computer", name="comp")
        self.landmark_data_prim = self.stage.GetPrimAtPath('/World/human/human_landmarks')

        self.attr = self.landmark_data_prim.GetAttribute('data')
        if self.attr.IsValid():
            self.human_landmarks = Human()
            self.human_landmarks.set_landmarks()

        return self._articulation, self._target, self._obstacle2, self._obstacle3, self._obstacle4
    
    def setup(self):
        #with open("/home/aist/Desktop/FES/ur5e/RmpFlow_Example_python/config3.json", "r") as f: root for ur5e data
        with open("/home/aist/Desktop/FES/kinova_files/config3.json", "r") as f: #data for kinova gen3
            rmp_config = json.load(f)

        self._rmpflow = RmpFlow(**rmp_config)   

        #self._rmpflow.add_obstacle(self._obstacle)
        self._rmpflow.add_obstacle(self._obstacle2)
        self._rmpflow.add_obstacle(self._obstacle3)
        self._rmpflow.add_obstacle(self._obstacle4)
        #self._rmpflow.add_obstacle(self._obstacle5)
          
        if self._dbg_mode:
            self._rmpflow.set_ignore_state_updates(True)
            self._rmpflow.visualize_collision_spheres()

            # Set the robot gains to be deliberately poor
            bad_proportional_gains = self._articulation.get_articulation_controller().get_gains()[0]/50
            self._articulation.get_articulation_controller().set_gains(kps = bad_proportional_gains)

        #Use the ArticulationMotionPolicy wrapper object to connect rmpflow to the Franka robot articulation.
        self._articulation_rmpflow = ArticulationMotionPolicy(self._articulation,self._rmpflow)

        self._target.set_world_pose(np.array([1.81, 0.7, 0.75]),euler_angles_to_quats([0.0,0.0,np.pi]))
        #self.esfera.set_world_pose(np.array([2, 1.5, 2.0]),euler_angles_to_quats([-1.57,np.pi,0]))

    def update(self, step: float):
        # Step is the time elapsed on this frame
        self.read_data = self.attr.Get()  
        self.human_landmarks.build_landmarks(self.read_data)

        target_position, target_orientation = self._target.get_world_pose()

        self._rmpflow.set_end_effector_target(
            target_position, target_orientation
        )

        # Track any movements of the cube obstacle
        self._rmpflow.update_world()

        #Track any movements of the robot base
        robot_base_translation,robot_base_orientation = self._articulation.get_world_pose()
        self._rmpflow.set_robot_base_pose(robot_base_translation,robot_base_orientation)

        action = self._articulation_rmpflow.get_next_articulation_action(step)
        self._articulation.apply_action(action)

    def reset(self):
        # Rmpflow is stateless unless it is explicitly told not to be
        if self._dbg_mode:
            # RMPflow was set to roll out robot state internally, assuming that all returned
            # joint targets were hit exactly.
            self._rmpflow.reset()
            self._rmpflow.visualize_collision_spheres()

        self._target.set_world_pose(np.array([1, 1.5, 1.0]),euler_angles_to_quats([-1.57,np.pi,0]))
        self.human_landmarks.reset_landmarks()

