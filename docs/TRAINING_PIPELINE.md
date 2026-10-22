# TomatoAI Training Pipeline

## 1. Acquisition
External datasets remain outside Git. Record source, license, checksum, capture conditions, and provenance.

## 2. Canonicalization
Convert each source into `CanonicalSample` records. Preserve RGB, depth, timestamps, sensors, labels, plant/episode identity, and source metadata.

## 3. Leakage-safe splitting
Split by plant, episode, greenhouse compartment, capture session, or equivalent group—not individual frames. Temporal datasets also require future holdouts.

## 4. Perception
Train tomato detection/segmentation/ripeness baselines first. AerialYield-T2M provides six ripeness stages and masks; BUTom21 provides RGB-D pixel annotations. These are complementary rather than interchangeable. 

## 5. Temporal plant state
Fuse repeated observations with environmental measurements to estimate growth stage, fruit count, ripeness distribution, and stress indicators. Horti-M3-Tomato is particularly useful because it spans three seasons and combines images, environmental sensors, soil conditions, management, phenotype, and yield records.

## 6. Robotics demonstrations
Convert teleoperation episodes into action-aligned sequences. The DINO+CDP dataset contains synchronized multi-view RGB and robot joint trajectories at 20 Hz and is therefore a direct source for manipulation-policy adaptation.

## 7. VLA adaptation
Keep the selected open VLA frozen initially. Add TomatoAI adapters/action heads only after perception and plant-state contracts are stable.

## 8. Validation gates
Simulation -> offline replay -> controlled robot tests -> greenhouse tests. Every action passes deterministic safety limits and confidence gates before execution.

## 9. Release criteria
A model is not considered deployable merely because perception metrics are high. It must pass unseen-plant evaluation, temporal holdout evaluation, action safety checks, and real-robot verification.
