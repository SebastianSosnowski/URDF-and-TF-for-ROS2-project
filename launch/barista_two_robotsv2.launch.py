import os

from ament_index_python.packages import get_package_share_directory

from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node


def generate_launch_description():

    # Package

    package_description = get_package_share_directory(
        'barista_robot_description'
    )

    # Gazebo

    gazebo_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(
                package_description,
                'launch',
                'gazebo.launch.py'
            )
        )
    )

    # Robot Rick
    
    robot_rick = 'rick'
    rick_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(
                package_description,
                'launch',
                'robot.launch.py'
            )
        ),
        launch_arguments={
            'robot_name': robot_rick,
            'x': '0.0',
            'y': '-0.5',
            'z': '0.2',
            'yaw': '3.14',
            'include_laser': 'false',
        }.items()
    )

    # Robot Morty

    robot_morty = 'morty'
    morty_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(
                package_description,
                'launch',
                'robot.launch.py'
            )
        ),
        launch_arguments={
            'robot_name': robot_morty,
            'x': '0.0',
            'y': '0.5',
            'z': '0.2',
            'yaw': '3.14',
            'include_laser': 'false',
        }.items()
    )

    # ROS-Gazebo Bridge

    gz_bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        name='gz_bridge',
        arguments=[
            '/clock@rosgraph_msgs/msg/Clock[gz.msgs.Clock',
            '/tf@tf2_msgs/msg/TFMessage[gz.msgs.Pose_V',

            f'/{robot_rick}/cmd_vel@geometry_msgs/msg/Twist@gz.msgs.Twist',
            f'/{robot_rick}/odom@nav_msgs/msg/Odometry[gz.msgs.Odometry',
            f'/{robot_rick}/joint_states@sensor_msgs/msg/JointState[gz.msgs.Model',
            f'/{robot_rick}/scan@sensor_msgs/msg/LaserScan[gz.msgs.LaserScan',

            f'/{robot_morty}/cmd_vel@geometry_msgs/msg/Twist@gz.msgs.Twist',
            f'/{robot_morty}/odom@nav_msgs/msg/Odometry[gz.msgs.Odometry',
            f'/{robot_morty}/joint_states@sensor_msgs/msg/JointState[gz.msgs.Model',
            f'/{robot_morty}/scan@sensor_msgs/msg/LaserScan[gz.msgs.LaserScan',
        ],
        output='screen',
    )

    # RViz

    rviz_config = os.path.join(
        package_description,
        'rviz',
        'two_barista_bots.rviz'
    )

    rviz_node = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz_node',
        parameters=[
            {
                'use_sim_time': True
            }
        ],
        arguments=[
            '-d',
            rviz_config
        ],
        output='screen'
    )

    # Launch description

    return LaunchDescription([
        gazebo_launch,
        rick_launch,
        morty_launch,
        gz_bridge,
        rviz_node,
    ])