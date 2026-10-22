"""Run a dependency-light perception evaluation from JSON arrays."""
import argparse
import json
from pathlib import Path

from tomatoai.evaluation import classification_accuracy, confusion_counts


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path, help="JSON file with predicted and expected labels")
    args = parser.parse_args()
    payload = json.loads(args.input.read_text(encoding="utf-8"))
    predicted = payload["predicted"]
    expected = payload["expected"]
    result = {
        "accuracy": classification_accuracy(predicted, expected),
        "confusion": confusion_counts(predicted, expected),
    }
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
