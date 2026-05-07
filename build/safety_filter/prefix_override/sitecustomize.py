import sys
if sys.prefix == '/usr':
    sys.real_prefix = sys.prefix
    sys.prefix = sys.exec_prefix = '/mnt/c/Sidarth/robotics/projects_robotics/dsp/ros2_ws/install/safety_filter'
