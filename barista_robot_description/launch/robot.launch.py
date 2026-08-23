import os

from ament_index_python.packages import get_package_share_directory

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, TimerAction
from launch.substitutions import Command, LaunchConfiguration
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue


def generate_launch_description():

    # Package / Xacro

    package_description = get_package_share_directory(
        'barista_robot_description'
    )

    xacro_file = os.path.join(
        package_description,
        'xacro',
        'barista_robot_model.urdf.xacro'
    )

    # Launch arguments

    robot_name = LaunchConfiguration('robot_name')
    body_color = LaunchConfiguration('body_color')
    x = LaunchConfiguration('x')
    y = LaunchConfiguration('y')
    z = LaunchConfiguration('z')
    yaw = LaunchConfiguration('yaw')
    include_laser = LaunchConfiguration('include_laser')

    declare_robot_name = DeclareLaunchArgument(
        'robot_name',
        default_value='barista_bot'
    )

    declare_body_color = DeclareLaunchArgument(
        'body_color',
        default_value='0.0 0.0 1.0 1.0'
    )

    declare_x = DeclareLaunchArgument(
        'x',
        default_value='0.0'
    )

    declare_y = DeclareLaunchArgument(
        'y',
        default_value='0.0'
    )

    declare_z = DeclareLaunchArgument(
        'z',
        default_value='0.2'
    )

    declare_yaw = DeclareLaunchArgument(
        'yaw',
        default_value='0.0'
    )

    declare_include_laser = DeclareLaunchArgument(
        'include_laser',
        default_value='true'
    )

    # Robot description

    robot_description = ParameterValue(
        Command([
            'xacro ',
            xacro_file,
            ' include_laser:=', include_laser,
            ' robot_name:=', robot_name,
            ' body_color:=\'', body_color, '\'',
        ]),
        value_type=str
    )

    # Robot State Publisher

    rsp = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='robot_state_publisher_node',
        namespace=robot_name,
        parameters=[
            {
                'frame_prefix': [robot_name, '/'],
                'robot_description': robot_description
            }
        ],
        output='screen'
    )

    world_to_robot = Node(
        package='tf2_ros',
        executable='static_transform_publisher',
        name='world_to_robot',
        namespace=robot_name,
        arguments=[
            '--x', x,
            '--y', y,
            '--z', z,
            '--yaw', yaw,
            '--frame-id', 'world',
            '--child-frame-id', [robot_name, '/odom'],
        ],
        output='screen'
    )

    # Spawn robot in Gazebo

    spawn_robot = Node(
        package='ros_gz_sim',
        executable='create',
        name='spawn_robot',
        arguments=[
            '-name', robot_name,
            '-allow_renaming', 'true',
            '-topic', [robot_name, '/robot_description'],
            '-x', x,
            '-y', y,
            '-z', z,
            '-Y', yaw,
        ],
        output='screen',
    )

    delayed_spawn = TimerAction(
        period=3.0,
        actions=[
            spawn_robot
        ]
    )

    # Launch description

    return LaunchDescription([
        declare_robot_name,
        declare_body_color,
        declare_x,
        declare_y,
        declare_z,
        declare_yaw,
        declare_include_laser,

        rsp,
        world_to_robot,
        delayed_spawn,
    ])