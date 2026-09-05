import os
from datetime import datetime
from pathlib import Path

from github import Github


GITHUB_TOKEN = os.getenv(
    "GITHUB_TOKEN"
)

GITHUB_REPOSITORY = os.getenv(
    "GITHUB_REPOSITORY"
)


def create_pull_request(
    file_path,
    css_fix,
    issue_description="OmniSight UI self-healing fix",
):
    if not GITHUB_TOKEN:
        raise ValueError(
            "GITHUB_TOKEN environment variable is not set"
        )

    if not GITHUB_REPOSITORY:
        raise ValueError(
            "GITHUB_REPOSITORY environment variable is not set"
        )

    github = Github(
        GITHUB_TOKEN
    )

    repo = github.get_repo(
        GITHUB_REPOSITORY
    )

    default_branch = (
        repo.default_branch
    )

    branch_name = (
        "omnisight/"
        + datetime.now().strftime(
            "%Y%m%d%H%M%S"
        )
    )

    source_branch = repo.get_branch(
        default_branch
    )

    repo.create_git_ref(
        ref=f"refs/heads/{branch_name}",
        sha=source_branch.commit.sha,
    )

    root = Path(
        __file__
    ).resolve().parents[2]

    local_path = Path(
        file_path
    )

    if not local_path.exists():
        raise FileNotFoundError(
            f"File not found: {file_path}"
        )

    try:
        repo_path = str(
            local_path.relative_to(
                root
            )
        )

    except ValueError:
        repo_path = str(
            local_path
        )

    repo_path = repo_path.replace(
        "\\",
        "/",
    )

    content = local_path.read_text(
        encoding="utf-8"
    )

    remote_file = repo.get_contents(
        repo_path,
        ref=branch_name,
    )

    repo.update_file(
        path=remote_file.path,
        message="fix: self-heal UI issue",
        content=content,
        sha=remote_file.sha,
        branch=branch_name,
    )

    pull_request = repo.create_pull(
        title="fix: OmniSight self-healed UI issue",
        body=f"""## OmniSight Self-Healing

OmniSight automatically detected and healed a UI issue.

### Issue

{issue_description}

### Generated CSS

```css
{css_fix}""")