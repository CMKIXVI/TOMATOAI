# TomatoAI Model Adapters

## Purpose
The adapter makes TomatoAI independent from one open-weight vision-language-action model. Verify exact model revision, license, hardware, action schema and fine-tuning support before adopting a base.

## Conceptual contract
- `load(config)`
- `prepare_observation(rgb, depth, robot_state, tomato_state, task)`
- `propose_action(observation)`
- `decode_action(output)`
- `reset()`
- `metadata()`

Expose model ID/revision, observation shape, action representation, coordinate frame, normalization, control frequency, latency/device, license and data provenance.

## Action boundary
Model output is an untrusted proposal. Validate output schema, finite values, freshness, reachability, workspace, speed/force, collision clearance, timeout and authorization before sending anything to a controller. Invalid output must stop/hold and report, never silently become motion.

## Adaptation sequence
1. Reproduce the model's documented baseline.
2. Create a tomato task benchmark.
3. Collect aligned demonstrations under consistent action/coordinate conventions.
4. Start with a frozen backbone plus adapter/action-expert fine-tuning if supported.
5. Compare with deterministic and unadapted baselines.
6. Evaluate unseen plants/lighting and simulation-to-real separately.
7. Promote only if task and safety regression tests pass.
