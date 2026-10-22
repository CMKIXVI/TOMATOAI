# TomatoAI Safety

## Non-negotiable rules
- Hardware emergency stop and actuator disable are independent of VLA, LLM, cloud, and the ordinary ROS graph.
- All motion passes through robot-driver limits and collision-aware planning.
- Base/arm movement is interlocked by default: stop the base before manipulation and retract the arm before driving.
- Localization loss, stale sensors, model timeout, invalid output, collision warning, or low confidence triggers a defined safe hold/stop.
- New manipulation tasks require simulation, bench tests, mock fruit, supervised real-world trials and a recovery plan.
- Keep operator approval for manipulation until task/platform-specific safety evidence supports otherwise.
- No autonomous pesticide or chemical application in initial scope.

## Minimum test scenarios
- Emergency stop during navigation and arm motion
- Network loss while using a cloud model
- Camera occlusion and stale depth
- Localization loss or wheel slip
- Invalid, NaN, out-of-range or late policy outputs
- Unexpected person/object in workspace
- Blocked gripper, dropped mock fruit and failed grasp
- Low battery, motor fault, overheating and sensor disconnect
- Base command while arm is outside the safe pose

Record the test setup, versions, expected safe response, actual response and evidence.
