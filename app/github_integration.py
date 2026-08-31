import os

from github import Github


def create_pull_request(
    repo_name: str,
    source_file: str,
    fixed_content: str,
    issue_type: str,
    issue_description: str,
):
    """
    Create GitHub branch, commit the generated
    fix, and open a Pull Request.
    """

    token = os.getenv(
        "GITHUB_TOKEN"
    )

    if not token:

        raise RuntimeError(
            "GITHUB_TOKEN environment variable "
            "is not configured."
        )

    github = Github(token)

    repo = github.get_repo(
        repo_name
    )

    default_branch = repo.default_branch

    base_branch = repo.get_branch(
        default_branch
    )

    # ---------------------------------
    # Create branch
    # ---------------------------------

    branch_name = (
        f"omnisight/fix-{issue_type}"
    )

    try:

        repo.create_git_ref(
            ref=f"refs/heads/{branch_name}",
            sha=base_branch.commit.sha
        )

        print(
            f"[GITHUB] Created branch: "
            f"{branch_name}"
        )

    except Exception as exc:

        if "Reference already exists" not in str(
            exc
        ):
            raise

        print(
            "[GITHUB] Branch already exists."
        )

    # ---------------------------------
    # Get source file
    # ---------------------------------

    file = repo.get_contents(
        source_file,
        ref=branch_name
    )

    # ---------------------------------
    # Commit fix
    # ---------------------------------

    commit_message = (
        f"fix: resolve {issue_type}"
    )

    repo.update_file(
        path=source_file,
        message=commit_message,
        content=fixed_content,
        sha=file.sha,
        branch=branch_name
    )

    print(
        "[GITHUB] Fix committed successfully."
    )

    # ---------------------------------
    # Create Pull Request
    # ---------------------------------

    pr = repo.create_pull(
        title=commit_message,

        body=f"""
## OmniSight Self-Healing Fix

### Issue Type

{issue_type}

### Description

{issue_description}

### Automated Pipeline

Detect
→ Generate Fix
→ Apply Fix
→ Playwright Re-test
→ VLM Verification
→ Pull Request

### Source File

`{source_file}`

This Pull Request was generated
automatically by OmniSight.
""",

        head=branch_name,
        base=default_branch
    )

    print(
        f"[GITHUB] Pull Request created: "
        f"{pr.html_url}"
    )

    return {
        "status": "created",
        "branch": branch_name,
        "pull_request": pr.html_url
    }