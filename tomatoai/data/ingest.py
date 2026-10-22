"""Dataset ingestion utilities.

Keeps acquisition separate from model training. Large raw datasets stay external;
this layer produces small, deterministic canonical manifests.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Iterable

from .canonical import CanonicalSample


def sha256_file(path: str | Path, chunk_size: int = 1024 * 1024) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        while chunk := handle.read(chunk_size):
            digest.update(chunk)
    return digest.hexdigest()


def validate_samples(samples: Iterable[CanonicalSample]) -> int:
    count = 0
    for sample in samples:
        sample.validate()
        count += 1
    return count


def write_jsonl(samples: Iterable[CanonicalSample], output: str | Path) -> int:
    count = 0
    destination = Path(output)
    destination.parent.mkdir(parents=True, exist_ok=True)
    with destination.open("w", encoding="utf-8") as handle:
        for sample in samples:
            sample.validate()
            payload = {
                "sample_id": sample.sample_id,
                "split": sample.split,
                "images": [vars(item) for item in sample.images],
                "sensors": [vars(item) for item in sample.sensors],
                "labels": sample.labels,
                "metadata": sample.metadata,
            }
            handle.write(json.dumps(payload, ensure_ascii=False) + "\n")
            count += 1
    return count
