import os

from ament_index_python.packages import get_package_share_directory, get_package_prefix

from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import PathJoinSubstitution


def generate_launch_description():

    # Packages

    pkg_barista_description = get_package_share_directory('barista_robot_description')
    gz_sim_pkg = get_package_share_directory('ros_gz_sim')

    # Gazebo resource paths

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
                os.environ["GZ_SIM_RESOURCE_PATH"] += (
                    ':' + resource_path
                )
    else:
        os.environ["GZ_SIM_RESOURCE_PATH"] = (
            ':'.join(gazebo_resource_paths)
        )

    # Gazebo

    gz_sim = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(
                gz_sim_pkg,
                'launch',
                'gz_sim.launch.py'
            )
        ),
        launch_arguments={
            'gz_args': [
                '-r ',
                PathJoinSubstitution([
                    pkg_barista_description,
                    'worlds',
                    'barista_robot_empty.world'
                ])
            ]
        }.items(),
    )

    # Launch description
    
    return LaunchDescription([
        gz_sim
    ])