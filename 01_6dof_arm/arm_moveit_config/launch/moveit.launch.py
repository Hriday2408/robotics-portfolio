import os
import yaml
from launch import LaunchDescription
from launch.substitutions import Command
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue
from ament_index_python.packages import get_package_share_directory

def load_file(path):
    with open(path, 'r') as f:
        return f.read()

def load_yaml(path):
    with open(path, 'r') as f:
        return yaml.safe_load(f)

def generate_launch_description():

    arm_desc_pkg   = get_package_share_directory('arm_description')
    arm_moveit_pkg = get_package_share_directory('arm_moveit_config')

    urdf_file      = os.path.join(arm_desc_pkg,   'urdf',   'arm.urdf.xacro')
    srdf_file      = os.path.join(arm_moveit_pkg, 'config', 'arm.srdf')
    kinematics_file     = os.path.join(arm_moveit_pkg, 'config', 'kinematics.yaml')
    joint_limits_file   = os.path.join(arm_moveit_pkg, 'config', 'joint_limits.yaml')
    ompl_file           = os.path.join(arm_moveit_pkg, 'config', 'ompl_planning.yaml')
    controllers_file    = os.path.join(arm_moveit_pkg, 'config', 'moveit_controllers.yaml')

    robot_description_content = ParameterValue(
        Command(['xacro ', urdf_file]),
        value_type=str
    )
    robot_description_semantic_content = load_file(srdf_file)
    kinematics_config  = load_yaml(kinematics_file)
    joint_limits_config = load_yaml(joint_limits_file)
    ompl_config        = load_yaml(ompl_file)
    controllers_config = load_yaml(controllers_file)

    robot_description_param = {
        'robot_description': robot_description_content
    }
    robot_description_semantic_param = {
        'robot_description_semantic': robot_description_semantic_content
    }

    # robot_state_publisher
    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        output='screen',
        parameters=[
            robot_description_param,
            {'use_sim_time': False}
        ]
    )

    # joint_state_publisher_gui
    joint_state_publisher = Node(
        package='joint_state_publisher_gui',
        executable='joint_state_publisher_gui',
        output='screen'
    )

    # move_group
    move_group = Node(
        package='moveit_ros_move_group',
        executable='move_group',
        output='screen',
        parameters=[
            robot_description_param,
            robot_description_semantic_param,
            {'robot_description_kinematics': kinematics_config},
            {'robot_description_planning': joint_limits_config},
            {'planning_pipelines': ['ompl']},
            {'ompl': ompl_config},
            {'moveit_controller_manager':
                'moveit_simple_controller_manager/MoveItSimpleControllerManager'},
            {'moveit_manage_controllers': True},
            {'use_sim_time': False},
            controllers_config,
        ]
    )

    # RViz — with SRDF passed directly so MotionPlanning plugin works
    rviz = Node(
        package='rviz2',
        executable='rviz2',
        output='screen',
        parameters=[
            robot_description_param,
            robot_description_semantic_param,
            {'robot_description_kinematics': kinematics_config},
        ]
    )

    return LaunchDescription([
        robot_state_publisher,
        joint_state_publisher,
        move_group,
        rviz,
    ])
