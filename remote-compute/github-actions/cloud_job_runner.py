#!/usr/bin/env python3
"""Run a prepared Codex cloud job inside GitHub Actions."""

from __future__ import annotations

import json
import os
from pathlib import Path
import shutil
import subprocess
import sys


REPO_ROOT = Path(__file__).resolve().parents[2]
JOBS_ROOT = REPO_ROOT / "remote-compute" / "github-actions" / "jobs"
DEFAULT_JOB = JOBS_ROOT / "smoke-test"


def run(command: list[str], cwd: Path | None = None) -> None:
    print("$ " + " ".join(command), flush=True)
    subprocess.run(command, cwd=str(cwd) if cwd else None, check=True)


def changed_job_path() -> Path:
    diff = subprocess.run(
        ["git", "diff-tree", "--no-commit-id", "--name-only", "-r", "HEAD"],
        check=True,
        text=True,
        capture_output=True,
    ).stdout.splitlines()
    job_files = [line for line in diff if line.startswith("remote-compute/github-actions/jobs/")]
    if not job_files:
        if DEFAULT_JOB.exists():
            print("No changed job path found. Running smoke-test job.", flush=True)
            return DEFAULT_JOB
        raise SystemExit("No changed GitHub Actions job path found. Use workflow_dispatch with job_path.")

    parts = Path(job_files[0]).parts
    if len(parts) < 4:
        raise SystemExit(f"Changed path is not inside a job folder: {job_files[0]}")
    return REPO_ROOT / Path(*parts[:4])


def requested_job_path() -> Path:
    raw = os.environ.get("CODEX_JOB_PATH", "").strip()
    if raw:
        return (REPO_ROOT / raw).resolve()
    return changed_job_path().resolve()


def ensure_safe_job_path(job_dir: Path) -> None:
    jobs_root = JOBS_ROOT.resolve()
    if jobs_root != job_dir and jobs_root not in job_dir.parents:
        raise SystemExit(f"Refusing to run job outside {jobs_root}: {job_dir}")
    if not job_dir.is_dir():
        raise SystemExit(f"Job folder not found: {job_dir}")
    if not (job_dir / "task.py").is_file():
        raise SystemExit(f"Job folder must contain task.py: {job_dir}")


def install_requirements(job_dir: Path) -> None:
    requirements = job_dir / "requirements.txt"
    if requirements.exists() and requirements.read_text(encoding="utf-8").strip():
        run([sys.executable, "-m", "pip", "install", "-q", "-r", str(requirements)])
    else:
        print("No job dependencies requested.", flush=True)


def main() -> None:
    results_dir = Path(os.environ["CODEX_CLOUD_RESULTS"]).resolve()
    if results_dir.exists():
        shutil.rmtree(results_dir)
    results_dir.mkdir(parents=True, exist_ok=True)

    job_dir = requested_job_path()
    ensure_safe_job_path(job_dir)

    metadata = {
        "job_dir": str(job_dir.relative_to(REPO_ROOT)),
        "python": sys.version,
        "runner": os.environ.get("RUNNER_NAME"),
        "workflow": os.environ.get("GITHUB_WORKFLOW"),
        "sha": os.environ.get("GITHUB_SHA"),
    }
    (results_dir / "codex-cloud-metadata.json").write_text(json.dumps(metadata, indent=2), encoding="utf-8")

    install_requirements(job_dir)

    env = os.environ.copy()
    env["CODEX_CLOUD_RESULTS"] = str(results_dir)
    print(f"Running job: {metadata['job_dir']}", flush=True)
    subprocess.run([sys.executable, str(job_dir / "task.py")], cwd=str(job_dir), env=env, check=True)


if __name__ == "__main__":
    main()
