# TomatoAI Dataset Register

This is a review checklist, not a claim that each candidate dataset has been downloaded or approved for every use.

## Onboarding manifest
Record: name, publisher, canonical URL, version/access date; license and permitted use; attribution; task and annotation type; cultivars/environment/season where known; modality and sensor calibration; known biases; split assignment; checksum and preprocessing version; privacy review and owner approval.

## Candidate dataset families
| Capability | Candidate lead | Integration notes |
|---|---|---|
| Longitudinal plant state, environment and yield | Horti-M3-Tomato | Verify edition, license, schema and modalities |
| Greenhouse climate/control time series | Wageningen Autonomous Greenhouse Challenge tomato datasets | Align timestamps and control/measurement semantics |
| Detection/ripeness/segmentation | Public tomato maturity datasets on Zenodo or academic repositories | Normalize labels and preserve source labels |
| RGB-D localization | BUTom21 | Verify depth/calibration format and annotations |
| Robot demonstrations | Tomato pruning/harvesting demonstrations, including DINO+CDP where available | Check robot/camera geometry and license |
| Field maturity/disease | Open-field tomato datasets | Keep field/greenhouse domain labels |
| Project data | TomatoAI-owned, consented farm/robot logs | Include calibration and failure cases |

These are research leads; availability and terms must be confirmed before use.

## Split policy
Do not split adjacent frames from one video into both training and test. Split by plant, session, greenhouse/field, or time as appropriate. Maintain a locked test set and report results by environment and lighting where possible.

## Synthetic and teacher-generated labels
Treat teacher outputs as weak labels. Record teacher model/revision, prompts, confidence and date. Human-review uncertain or safety-critical labels. Do not put synthetic images into a real-world test set.
