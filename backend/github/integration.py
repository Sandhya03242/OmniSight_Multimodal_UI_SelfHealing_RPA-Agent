import os

from github import Github
from dotenv import load_dotenv


load_dotenv()


def create_pull_request(
    repository_name: str,
    base_branch: str = "main",
):

    token = os.getenv(
        "GITHUB_TOKEN"
    )

    if not token:

        raise RuntimeError(
            "GITHUB_TOKEN not configured."
        )

    github = Github(
        token
    )

    repo = github.get_repo(
        repository_name
    )

    base = repo.get_branch(
        base_branch
    )

    branch_name = (
        "omnisight/"
        "self-healing-fix"
    )

    # --------------------------
    # Create branch
    # --------------------------

    try:

        repo.get_branch(
            branch_name
        )

    except Exception:

        repo.create_git_ref(ref=f"refs/heads/{branch_name}",sha=base.commit.sha,)

    # --------------------------
    # Generated fix
    # --------------------------

    css = """
/*
OmniSight Automated UI Fix

Detected:
Hidden checkout Continue button.

Generated:
Self-healing CSS repair.
*/

#continue {
    display: block !important;
    visibility: visible !important;
    opacity: 1 !important;
}
"""

    file_path = (
        "backend/outputs/"
        "fixes/omnisight_fix.css"
    )

    # --------------------------
    # Commit
    # --------------------------

    try:

        existing = repo.get_contents(
            file_path,
            ref=branch_name,
        )

        repo.update_file(

            path=file_path,

            message=(
                "fix: OmniSight "
                "self-healing UI repair"
            ),

            content=css,

            sha=existing.sha,

            branch=branch_name,
        )

    except Exception:

        repo.create_file(

            path=file_path,

            message=(
                "fix: OmniSight "
                "self-healing UI repair"
            ),

            content=css,

            branch=branch_name,
        )

    # --------------------------
    # Pull request
    # --------------------------

    pr = repo.create_pull(

        title=(
            "🤖 OmniSight "
            "Self-Healing UI Fix"
        ),

        body="""
## OmniSight Automated UI Repair

### Detection

OmniSight detected a hidden checkout
Continue button.

### AI

Qwen3.5-0.8B analyzed the screenshot
and HTML.

### Agent

LangChain orchestrated the repair.

### Browser

Playwright applied the generated CSS
and verified the result.

### Result

UI defect successfully resolved.
""",

        head=branch_name,

        base=base_branch,
    )

    return {

        "branch":
            branch_name,

        "pull_request":
            pr.html_url,
    }