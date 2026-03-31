#!/usr/bin/env python3
"""
arm_motion.py — MoveIt2 motion client for arm_6dof
Uses MoveGroup action server to plan and execute joint trajectories.
"""
import rclpy
from rclpy.node import Node
from rclpy.action import ActionClient
from rclpy.duration import Duration
from action_msgs.msg import GoalStatus
from moveit_msgs.action import MoveGroup
from moveit_msgs.msg import (
    MotionPlanRequest,
    WorkspaceParameters,
    Constraints,
    JointConstraint,
    RobotState,
    MoveItErrorCodes
)
from sensor_msgs.msg import JointState
from std_msgs.msg import Header
import math
import time


JOINT_NAMES = [
    'joint_1', 'joint_2', 'joint_3',
    'joint_4', 'joint_5', 'joint_6'
]


class ArmMotionClient(Node):

    def __init__(self):
        super().__init__('arm_motion_client')

        # Subscribe to joint states so we always know current position
        self._current_joint_positions = [0.0] * 6
        self._joint_states_received = False

        self._joint_state_sub = self.create_subscription(
            JointState,
            '/joint_states',
            self._joint_state_callback,
            10
        )

        self._action_client = ActionClient(
            self,
            MoveGroup,
            '/move_action'
        )

        self.get_logger().info('Waiting for move_group action server...')
        self._action_client.wait_for_server()
        self.get_logger().info('Connected!')

        # Wait for first joint state
        self.get_logger().info('Waiting for joint states...')
        timeout = 10.0
        start = self.get_clock().now()
        while not self._joint_states_received:
            rclpy.spin_once(self, timeout_sec=0.1)
            elapsed = (self.get_clock().now() - start).nanoseconds / 1e9
            if elapsed > timeout:
                self.get_logger().warn('No joint states received, using zeros')
                break
        self.get_logger().info(
            f'Current joints: {[round(p, 3) for p in self._current_joint_positions]}'
        )

    def _joint_state_callback(self, msg):
        if len(msg.position) == 6:
            self._current_joint_positions = list(msg.position)
            self._joint_states_received = True

    def _build_goal(self, target_positions: list) -> MoveGroup.Goal:
        """Build a MoveGroup goal from a list of 6 joint positions."""
        goal_msg = MoveGroup.Goal()
        request = MotionPlanRequest()

        request.group_name = 'arm'
        request.num_planning_attempts = 10
        request.allowed_planning_time = 10.0
        request.max_velocity_scaling_factor = 0.3
        request.max_acceleration_scaling_factor = 0.3

        # Workspace
        ws = WorkspaceParameters()
        ws.header.frame_id = 'world'
        ws.min_corner.x = -2.0
        ws.min_corner.y = -2.0
        ws.min_corner.z = -2.0
        ws.max_corner.x = 2.0
        ws.max_corner.y = 2.0
        ws.max_corner.z = 2.0
        request.workspace_parameters = ws

        # Start state from current joint positions
        start_state = RobotState()
        js = JointState()
        js.header = Header()
        js.header.frame_id = 'world'
        js.header.stamp = self.get_clock().now().to_msg()
        js.name = JOINT_NAMES
        js.position = self._current_joint_positions
        js.velocity = [0.0] * 6
        js.effort = [0.0] * 6
        start_state.joint_state = js
        start_state.is_diff = False
        request.start_state = start_state

        # Goal constraints
        constraints = Constraints()
        for i, name in enumerate(JOINT_NAMES):
            jc = JointConstraint()
            jc.joint_name = name
            jc.position = target_positions[i]
            jc.tolerance_above = 0.05
            jc.tolerance_below = 0.05
            jc.weight = 1.0
            constraints.joint_constraints.append(jc)
        request.goal_constraints.append(constraints)

        goal_msg.request = request
        goal_msg.planning_options.plan_only = True
        goal_msg.planning_options.replan = True
        goal_msg.planning_options.replan_attempts = 3

        return goal_msg

    def move_to(self, target_positions: list, label: str = '') -> bool:
        """Send motion goal and wait for result."""
        self.get_logger().info(f'=== {label} ===')
        self.get_logger().info(
            f'Target: {[round(p, 3) for p in target_positions]}'
        )

        goal_msg = self._build_goal(target_positions)
        future = self._action_client.send_goal_async(goal_msg)
        rclpy.spin_until_future_complete(self, future)

        goal_handle = future.result()
        if not goal_handle.accepted:
            self.get_logger().error('Goal REJECTED by move_group')
            return False

        self.get_logger().info('Goal accepted, planning...')
        result_future = goal_handle.get_result_async()
        rclpy.spin_until_future_complete(self, result_future)

        result = result_future.result().result
        code = result.error_code.val

        if code == MoveItErrorCodes.SUCCESS:
            self.get_logger().info('SUCCESS')
            # Update current positions to target
            self._current_joint_positions = list(target_positions)
            return True
        else:
            self.get_logger().error(f'FAILED — error code: {code}')
            return False


def main(args=None):
    rclpy.init(args=args)
    node = ArmMotionClient()

    # HOME
    node.move_to(
        [0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
        'Moving to HOME'
    )
    time.sleep(0.5)

    # READY
    node.move_to(
        [0.0, -0.785, 0.785, 0.0, 0.785, 0.0],
        'Moving to READY'
    )
    time.sleep(0.5)

    # SWEEP waist
    node.move_to(
        [math.pi/2, -0.785, 0.785, 0.0, 0.785, 0.0],
        'Sweeping waist 90deg'
    )
    time.sleep(0.5)

    # HOME
    node.move_to(
        [0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
        'Back to HOME'
    )

    node.get_logger().info('Demo sequence complete')
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
