# GitHub Actions Cloud Runner

This is the fully automated free/offloaded path for heavier work.

Unlike the Colab fallback, this workflow does not require manual upload/download. Once this workspace is connected to a GitHub repository, Codex can prepare a job, push or create the needed files, watch GitHub Actions, read logs, fix failures, and download artifacts through GitHub.

## Why GitHub Actions

- Public repositories can use standard GitHub-hosted runners for free.
- Private repositories get a limited free monthly quota and artifact storage.
- Jobs run on GitHub infrastructure, not on the MacBook Neo.
- Artifacts can be downloaded programmatically.

## Requirements

- A GitHub repository with Actions enabled.
- Codex/GitHub access with permission to write workflow/job files.
- For command-line automation outside the Codex GitHub connector, a GitHub token in `GITHUB_TOKEN`.

## Job Shape

Each job folder should live under:

```text
remote-compute/github-actions/jobs/<job-name>/
```

Each job should contain:

- `task.py`: script run remotely.
- `requirements.txt`: optional Python dependencies installed on the GitHub runner.
- `README.md`: purpose, inputs, outputs, and cleanup notes.

Write outputs to `CODEX_CLOUD_RESULTS`:

```python
from pathlib import Path
import os

results_dir = Path(os.environ["CODEX_CLOUD_RESULTS"])
results_dir.mkdir(parents=True, exist_ok=True)
```

## How Codex Will Use It

1. Decide a task is too heavy for the laptop.
2. Create or update a job folder under `jobs/`.
3. Push the job to GitHub or update it through the GitHub connector.
4. Let `.github/workflows/codex-cloud-runner.yml` run it in GitHub Actions.
5. Inspect logs if it fails.
6. Patch the job and rerun as needed.
7. Download the `codex-cloud-results` artifact.
8. Delete or ignore temporary local artifacts.

## Limits

This is good for builds, tests, data transforms, batch scripts, and moderate Python workloads. It is not a free GPU system, and it should not be used for secrets-heavy work unless the repository and workflow permissions are configured carefully.
