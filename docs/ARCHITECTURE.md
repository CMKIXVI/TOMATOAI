# TomatoAI Architecture

## Design objective
TomatoAI adds tomato-specific plant intelligence to a replaceable open-weight VLA. Agronomic state representation should not be entangled with a specific action model.

## Main data path
1. Sensor drivers publish timestamped observations.
2. Perception emits detections, masks, maturity labels and calibrated spatial estimates.
3. Plant registry associates observations to a plant only when confidence is sufficient.
4. State fusion combines visual observations and environment readings with provenance and missing-data indicators.
5. Analytics emits predictions with model version and uncertainty.
6. Planner emits typed task proposals.
7. Safety supervisor rejects unsafe or unsupported proposals.
8. VLA adapter maps approved tasks to the chosen model's input/output contract.
9. ROS 2 / MoveIt 2 / Nav2 execute bounded actions.
10. Verification logs outcomes for evaluation.

## Interface expectations
A task proposal should include task ID, plant ID, goal, timestamp, expiry, source observations, model revisions, confidence, allowed workspace, speed/force limits, approval requirement, cancellation and recovery conditions.

The VLA output is a proposal, not authorization. Validate schema, freshness, finite values, reachability, workspace, speed/force, collision clearance, timeout, and task authorization before any robot command.

## First milestones
1. Offline perception over sample images.
2. Plant-state JSON generation.
3. Temporal tracking and monitoring.
4. Robot simulation.
5. Teleoperated demonstration collection.
6. One constrained manipulation skill on mock fruit.
7. Supervised greenhouse trials.

Do not start with unattended chemical application, unrestricted motion, or simultaneous training of all subsystems.
