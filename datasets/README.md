# TomatoAI Datasets

TomatoAI uses a **dataset registry + manifests** rather than committing large raw datasets to Git. Raw images, videos, HDF5 files and sensor archives stay at their original host or an approved object store. This repository stores metadata, download references, checksums when available, licensing notes, preprocessing definitions and split policy.

## Priority datasets

| ID | Dataset | Primary role | Modality | Status |
|---|---|---|---|---|
| `horti-m3-tomato` | Horti-M3-Tomato | growth, environment, phenotype, yield | RGB + sensors + manual traits | candidate/open |
| `aghc4-dwarf-tomato` | 4th Autonomous Greenhouse Challenge: Dwarf Tomato Timeseries and Images | greenhouse monitoring, RGB-D, yield and climate | RGB-D + time series | candidate/open |
| `aghc2-tomato` | Autonomous Greenhouse Challenge, Second Edition | greenhouse control, irrigation, climate, harvest | time series + agronomic records | candidate/open |
| `butom21` | BUTom21 | tomato detection and segmentation | RGB + noisy depth | candidate/open |
| `tomatowur` | TomatoWUR | 3D plant segmentation, skeletonisation and phenotyping | 3D annotated plant data | candidate/open |
| `dino-cdp-tomato` | DINO+CDP Tomato Harvesting Dataset | robot imitation/manipulation | multi-view RGB + robot joints | candidate/open, CC BY 4.0 |
| `aerialyield-t2m` | AerialYield-T2M | ripeness, masks, fruit counts | RGB, drone + close range | candidate/open |

## Acquisition rule

Do not blindly mirror external data. For each dataset:

1. Read the original dataset page and license.
2. Record the exact version and access date in the manifest.
3. Download outside Git history.
4. Verify the checksum when one is published.
5. Preserve the original citation and attribution.
6. Convert to the TomatoAI canonical schema without overwriting the source data.
7. Generate a provenance record for every derived dataset.

## Dataset layers

```text
external source
      |
      v
raw/                  # never committed
      |
      v
staging/              # checksum + source validation
      |
      v
canonical/            # TomatoAI-normalized samples
      |
      +---- perception
      +---- temporal_state
      +---- agronomic_prediction
      +---- robot_demonstrations
      |
      v
benchmarks/           # fixed evaluation splits
```

## Important

Some candidate datasets are extremely large. For example, the 4th Autonomous Greenhouse Challenge release contains a very large canopy-camera archive. Keep these outside Git and download only the portions needed for an experiment.

Dataset inclusion in this registry does **not** mean that every dataset is approved for commercial use, redistribution, model training, or derivative datasets. The original license always controls.
