"""Build a canonical JSONL manifest from already-created sample records."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from tomatoai.data.canonical import CanonicalSample, ImageRecord, SensorRecord
from tomatoai.data.ingest import write_jsonl


def load_records(path: Path) -> list[CanonicalSample]:
    samples: list[CanonicalSample] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        item = json.loads(line)
        samples.append(
            CanonicalSample(
                sample_id=item["sample_id"],
                split=item["split"],
                images=[ImageRecord(**image) for image in item.get("images", [])],
                sensors=[SensorRecord(**sensor) for sensor in item.get("sensors", [])],
                labels=item.get("labels", {}),
                metadata=item.get("metadata", {}),
            )
        )
    return samples


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    count = write_jsonl(load_records(args.input), args.output)
    print(f"wrote {count} canonical samples to {args.output}")


if __name__ == "__main__":
    main()
