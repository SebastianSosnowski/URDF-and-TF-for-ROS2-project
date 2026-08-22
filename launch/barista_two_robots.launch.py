import os

from ament_index_python.packages import get_package_share_directory, get_package_prefix
from launch import LaunchDescription
from launch.substitutions import Command, PathJoinSubstitution, LaunchConfiguration
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue
from launch.actions import IncludeLaunchDescription, DeclareLaunchArgument, TimerAction
from launch.launch_description_sources import PythonLaunchDescriptionSource

import xacro

# this is the function launch system will look for
def generate_launch_description():

    ####### DATA INPUT ##########
    # urdf_file = 'barista_robot_model.urdf'
    xacro_file = "barista_robot_model.urdf.xacro"
    package_description = get_package_share_directory('barista_robot_description')
    gz_sim_pkg = get_package_share_directory('ros_gz_sim')
    ####### DATA INPUT END ##########

    # Robot State Publisher
    robot_name_1 = "rick"
    robot_name_2 = "morty"

    # parse args
    declare_include_laser = DeclareLaunchArgument(
        'include_laser',
        default_value='true'
    )

    xacro_path = os.path.join(
        package_description,
        'xacro',
        xacro_file
    )

    # Load Robot State Publisher Rick
    robot1_description = ParameterValue(
        Command([
            'xacro ',
            xacro_path,
            ' include_laser:=', LaunchConfiguration('include_laser'),
            ' robot_name:=', robot_name_1
        ]),
        value_type=str
    )
    rsp_rick = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='robot_state_publisher_node',
        namespace=robot_name_1,
        parameters=[{'frame_prefix': robot_name_1 + '/', 
                    'robot_description': robot1_description}],
        output="screen"
    )
    # Load Robot State Publisher Morty
    robot2_description = ParameterValue(
        Command([
            'xacro ',
            xacro_path,
            ' include_laser:=', LaunchConfiguration('include_laser'),
            ' robot_name:=', robot_name_2
        ]),
        value_type=str
    )
    rsp_morty = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='robot_state_publisher_node',
        namespace=robot_name_2,
        parameters=[{'frame_prefix': robot_name_2 + '/', 
                    'robot_description': robot2_description}],
        output="screen"
    )
    # Spawn Robot Rick
    spawn_robot_rick = Node(
        package="ros_gz_sim",
        executable="create",
        name="robot_rick_spawn",
        arguments=[
            "-name", robot_name_1,
            "-allow_renaming", "true",
            "-topic", robot_name_1 + "/robot_description",
            "-x", "0.0",
            "-y", "-0.5",
            "-z", "0.2",
            "-Y", "3.14",
        ],
        output="screen",
    )
    delayed_spawn_rick = TimerAction(
        period=3.0,
        actions=[
            spawn_robot_rick
        ]
    )

    # Spawn Robot  Morty
    spawn_robot_morty = Node(
        package="ros_gz_sim",
        executable="create",
        name="robot_morty_spawn",
        arguments=[
            "-name", robot_name_2,
            "-allow_renaming", "true",
            "-topic", robot_name_2 + "/robot_description",
            "-x", "0.0",
            "-y", "0.5",
            "-z", "0.2",
            "-Y", "3.14",
        ],
        output="screen",
    )
    delayed_spawn_morty = TimerAction(
        period=3.0,
        actions=[
            spawn_robot_morty
        ]
    )

    # RVIZ Configuration
    rviz_config_dir = os.path.join(package_description, 'rviz', 'barista_bot.rviz')

    rviz_node = Node(
            package='rviz2',
            executable='rviz2',
            output='screen',
            name='rviz_node',
            parameters=[{'use_sim_time': True}],
            arguments=['-d', rviz_config_dir])

    # Gazebo Configuration
    pkg_barista_description = get_package_share_directory(
        'barista_robot_description'
    )

    install_dir_path = (
        get_package_prefix('barista_robot_description') + '/share'
    )
    meshes_path = os.path.join(
        pkg_barista_description,
        'meshes'
    )
    gazebo_resource_paths = [
        install_dir_path,
        meshes_path
    ]

    if "GZ_SIM_RESOURCE_PATH" in os.environ:
        for resource_path in gazebo_resource_paths:
            if resource_path not in os.environ["GZ_SIM_RESOURCE_PATH"]:
                os.environ["GZ_SIM_RESOURCE_PATH"] += (':' + resource_path)
    else:
        os.environ["GZ_SIM_RESOURCE_PATH"] = (':'.join(gazebo_resource_paths))

    gz_sim = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(gz_sim_pkg, 'launch', 'gz_sim.launch.py')),
            launch_arguments={'gz_args': [
            '-r ',  # <-- start unpaused
            PathJoinSubstitution([pkg_barista_description, 'worlds', 'barista_robot_empty.world'])
        ]}.items(),
    )

    # ROS-Gazebo Bridge #
    gz_bridge = Node(
        package="ros_gz_bridge",
        executable="parameter_bridge",
        name="gz_bridge",
        arguments=[
            "/clock" + "@rosgraph_msgs/msg/Clock" + "[gz.msgs.Clock",
            "/tf" + "@tf2_msgs/msg/TFMessage" + "[gz.msgs.Pose_V",
            "/rick/cmd_vel" + "@geometry_msgs/msg/Twist" + "@gz.msgs.Twist",
            "/rick/odom" + "@nav_msgs/msg/Odometry" + "[gz.msgs.Odometry",
            "/rick/joint_states" + "@sensor_msgs/msg/JointState" + "[gz.msgs.Model",
            "/rick/scan" + "@sensor_msgs/msg/LaserScan" + "[gz.msgs.LaserScan",
            "/morty/cmd_vel" + "@geometry_msgs/msg/Twist" + "@gz.msgs.Twist",
            "/morty/odom" + "@nav_msgs/msg/Odometry" + "[gz.msgs.Odometry",
            "/morty/joint_states" + "@sensor_msgs/msg/JointState" + "[gz.msgs.Model",
            "/morty/scan" + "@sensor_msgs/msg/LaserScan" + "[gz.msgs.LaserScan",
        ],
        remappings=[
            # there are no remappings for this robot description
        ],
        output="screen",
    )

    # create and return launch description object
    return LaunchDescription(
        [   
            declare_include_laser,

            rsp_rick,
            rsp_morty,
            
            gz_sim,     
            rviz_node,
            delayed_spawn_rick,
            delayed_spawn_morty,
            gz_bridge
        ]
    )