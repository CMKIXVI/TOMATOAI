# TomatoAI Robot Platform

## Target platform
A mobile base with an articulated arm, crop-aware end effector, RGB-D sensing, navigation sensors, optional wrist camera, and environmental sensors.

## Integration boundaries
- ROS 2: hardware interfaces, transforms, sensor streams, diagnostics and task actions.
- Nav2: mobile-base navigation.
- MoveIt 2: arm kinematics, planning scene and collision-aware motion planning.
- VLA adapter: maps observation/task structures to and from the selected policy.
- TomatoAI state service: plant identity, crop observations, temporal state and analytics.
- Safety supervisor: limits and interlocks independent of generative models.

## Sequence at each plant
1. Navigate to a row waypoint.
2. Stop the base and confirm localization/workspace clearance.
3. Capture images and sensor observations.
4. Update the plant record and uncertainty.
5. Decide whether to observe, report, request approval, or propose a task.
6. Validate reachability, collision clearance, data freshness and action limits.
7. Execute a constrained action.
8. Verify, log, and retract the arm before base motion.

## Physical safety requirements
- Hardware emergency stop must disable hazardous motion without cloud or model availability.
- Configure joint, velocity, workspace and payload constraints for the actual robot.
- Interlock mobile motion and extended-arm manipulation by default.
- Test at low speed with a mock canopy and mock fruit before real crops.
- Never allow natural-language content to set unbounded actuator commands.
- Loss of localization, sensor freshness, communication or confidence must result in a defined safe hold/stop.

## Platform selection checklist
Aisle width/floor; footprint/turning radius/stopping distance; arm reach/DoF/payload/repeatability; canopy clearance; camera range and lighting; gripper compliance and cleaning; ROS 2 driver availability and license; compute/power/thermal limits; emergency stop, recovery and maintenance.
