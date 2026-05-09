from pathlib import Path
import json
import os


def main() -> None:
    results_dir = Path(os.environ["CODEX_CLOUD_RESULTS"])
    results_dir.mkdir(parents=True, exist_ok=True)

    summary = {
        "status": "ok",
        "message": "Replace this template with the cloud task.",
    }
    (results_dir / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
