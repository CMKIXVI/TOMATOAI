"""Validate the lightweight TomatoAI dataset registry without downloading data."""
from pathlib import Path
import re


REQUIRED_KEYS = {"id", "name", "source_url", "role", "modalities"}


def validate(path: Path) -> list[str]:
    text = path.read_text(encoding="utf-8")
    errors = []
    if "schema_version:" not in text:
        errors.append("missing schema_version")
    ids = re.findall(r"^  - id: ([^\n]+)$", text, flags=re.MULTILINE)
    if not ids:
        errors.append("no dataset entries found")
    for dataset_id in ids:
        block_match = re.search(
            rf"^  - id: {re.escape(dataset_id)}$(.*?)(?=^  - id: |\Z)",
            text,
            flags=re.MULTILINE | re.DOTALL,
        )
        block = block_match.group(1) if block_match else ""
        for key in REQUIRED_KEYS - {"id"}:
            if re.search(rf"^    {re.escape(key)}:", block, flags=re.MULTILINE) is None:
                errors.append(f"{dataset_id}: missing {key}")
        if not re.search(r"^    source_url: https?://", block, flags=re.MULTILINE):
            errors.append(f"{dataset_id}: invalid source_url")
    return errors


if __name__ == "__main__":
    manifest = Path(__file__).parents[1] / "datasets" / "manifests" / "datasets.yaml"
    errors = validate(manifest)
    if errors:
        raise SystemExit("\n".join(errors))
    print(f"OK: {manifest}")
