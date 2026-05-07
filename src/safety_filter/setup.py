from setuptools import find_packages, setup

package_name = 'safety_filter'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='sidarth',
    maintainer_email='sidarth@todo.todo',
    description='TODO: Package description',
    license='TODO: License declaration',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [ 'safety_filter_node = safety_filter.safety_filter_node:main','ultrasonic_sensor_node = safety_filter.ultrasonic_sensor_node:main','sensor_controller_node = safety_filter.sensor_controller_node:main','keyboard_attack_node = safety_filter.keyboard_attack_node:main','sensor_attack_node = safety_filter.sensor_attack_node:main','dsp_sensor_filter_node = safety_filter.dsp_sensor_filter_node:main','sensor_router_node = safety_filter.sensor_router_node:main','dsp_filter_node = safety_filter.dsp_filter_node:main',
        ],
    },
)

