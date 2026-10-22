# TomatoAI Data Pipeline

```text
External datasets / robot logs / farm sensors
                  |
                  v
          Source manifests
                  |
                  v
       checksum + license check
                  |
                  v
             RAW STORAGE
                  |
                  v
       normalization / QA
                  |
                  v
       TomatoAI canonical schema
          /       |        \
         v        v         v
    perception  temporal   robot demos
         |        |         |
         +--------+---------+
                  |
                  v
             benchmarks
                  |
                  v
          training / eval
```

## Canonical data principles

Every sample should retain:

- source dataset ID and source sample ID
- capture timestamp when available
- plant/scene/demonstration ID
- camera/sensor ID and calibration version
- coordinate frame when spatial data is present
- original label and normalized TomatoAI label
- model-generated labels separately from human labels
- uncertainty and missing-data flags
- preprocessing version
- split/benchmark membership

## Multimodal alignment

RGB, depth, robot state and environmental data must be aligned by timestamp and calibration. Never silently interpolate a missing sensor value when that changes the meaning of a label. Store the fact that a value was missing.

## Robot demonstrations

For VLA training, each episode should contain:

```text
observation_t
robot_state_t
task_t
action_t
observation_t+1
outcome
```

and metadata for robot model, camera calibration, action/control frequency, workspace and safety state.

## Data quality gates

Reject or quarantine samples with corrupted files, invalid timestamps, missing mandatory calibration, impossible joint states, impossible depth values, duplicate IDs, or contradictory labels. Do not silently repair data used for benchmark evaluation.
