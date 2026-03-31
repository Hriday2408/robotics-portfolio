from setuptools import setup

package_name = 'arm_controller'

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
    maintainer='hriday',
    maintainer_email='hridayrana2408@gmail.com',
    description='MoveIt2 motion controller for arm_6dof',
    license='MIT',
    entry_points={
        'console_scripts': [
            'arm_motion = arm_controller.arm_motion:main',
        ],
    },
)
