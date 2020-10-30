# generated from catkin/cmake/template/pkg.context.pc.in
CATKIN_PACKAGE_PREFIX = ""
PROJECT_PKG_CONFIG_INCLUDE_DIRS = "${prefix}/include;/usr/include/eigen3".split(';') if "${prefix}/include;/usr/include/eigen3" != "" else []
PROJECT_CATKIN_DEPENDS = "control_msgs;geometry_msgs;moveit_msgs;moveit_ros_planning_interface;rosparam_shortcuts;sensor_msgs;std_msgs;trajectory_msgs".replace(';', ' ')
PKG_CONFIG_LIBRARIES_WITH_PREFIX = "-lmoveit_servo_cpp_api".split(';') if "-lmoveit_servo_cpp_api" != "" else []
PROJECT_NAME = "moveit_servo"
PROJECT_SPACE_DIR = "/usr/local"
PROJECT_VERSION = "1.0.5"
