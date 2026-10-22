# TomatoAI Training

Training is intentionally staged. Do not begin by fine-tuning a giant VLA on every task.

## Stage 1 — perception

Train/evaluate plant, leaf, flower, stem and fruit perception; maturity; and visible anomaly flags. Start with frozen pretrained vision encoders where useful.

## Stage 2 — plant state

Fuse repeated observations and environmental data. Train temporal models only after a reliable observation schema and leakage-safe splits exist.

## Stage 3 — task data

Create structured tasks such as:

- inspect plant
- count visible fruit
- inspect ripeness
- inspect suspected stress
- measure growth
- navigate to plant
- position camera
- approach fruit
- grasp/harvest candidate
- prune candidate

Each demonstration must include observation timestamps, robot state, camera calibration/version, task ID, action representation, and outcome.

## Stage 4 — VLA adaptation

Keep the base VLA frozen initially. Train an adapter/action expert if the chosen framework supports it. Compare against the unadapted base and a deterministic/teleoperated baseline.

## Stage 5 — real-world validation

Simulation is not a substitute for greenhouse evaluation. Hold out plants/scenes and measure success, crop damage, interventions, recovery, latency, and safe-stop behavior.

## Experiment record

Every training run should record:

- dataset manifest version
- split manifest version
- model ID and exact revision
- code commit
- configuration
- hardware/GPU
- seed
- metrics
- evaluation commit
- known limitations
