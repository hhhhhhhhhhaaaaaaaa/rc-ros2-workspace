from setuptools import find_packages, setup

package_name = 'vision_detect'

setup(
    name=package_name,
    version='0.0.0',
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']), 
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='jjh',
    maintainer_email='jjh@todo.todo',
    description='TODO: Package description',
    license='TODO: License declaration',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [
            'yolo_publisher = vision_detect.yolo_identify_publisher:main',
            'subscriber_node = vision_detect.subscribernode:main',
            'move_robot_action_server = vision_detect.Actionserve:main',
            'move_robot_action_client = vision_detect.Actioncilent:main',
            'serial_bridge = vision_detect.serial_bridge:main',
        ],
    },
)