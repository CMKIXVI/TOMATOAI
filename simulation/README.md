# TomatoAI Simulation

The simulation layer will reproduce the target robot before physical integration.

## Required simulated elements

- mobile base and greenhouse aisle geometry
- articulated arm and joint limits
- RGB/RGB-D camera model
- navigation sensor model
- tomato plants with variable geometry and fruit states
- collision objects and human/worker safety zones
- task state and robot telemetry

## First simulated tasks

1. Navigate to a plant.
2. Stop the base and inspect with the camera.
3. Update TomatoAI plant state.
4. Move the arm to a safe inspection pose.
5. Approach a mock fruit.
6. Execute a constrained grasp/harvest trajectory.
7. Verify success and retract.
8. Demonstrate emergency-stop and recovery behavior.

Simulation metrics must be reported separately from real greenhouse results.
