# Phase 1 — ROS2 Foundations

## What was built
- Clean `robot_arm_ws` colcon workspace from scratch
- `arm_description` package with correct CMakeLists and package.xml
- `arm.urdf.xacro` — base link with visual, collision, and inertial properties
- `display.launch.py` — launches robot_state_publisher, joint_state_publisher_gui, RViz2
- RViz config saved with RobotModel display and base_link fixed frame

## Key concepts understood
- `xacro:property` — define values once, reuse with `${}`
- Inertia tensor for cylinder — `Ixx = Iyy = m(3r²+h²)/12`, `Izz = mr²/2`
- `visual` vs `collision` vs `inertial` — three separate representations of one link
- `ParameterValue(..., value_type=str)` — required in Humble when passing xacro Command output
- `--symlink-install` — edits to Python/XML files take effect without rebuilding

## Issues hit and fixed
- `joint_state_publisher` listed as CMake dependency — it's runtime only, remove from find_package()
- `robot_description` yaml parse error — fixed with ParameterValue wrapper
- Corrupted heredoc paste — use gedit for long files going forward

## Next: Phase 2
- Design 6DOF arm in Onshape (joint naming conventions)
- Export URDF via onshape-to-robot
- Add all 6 joints and links to arm.urdf.xacro
