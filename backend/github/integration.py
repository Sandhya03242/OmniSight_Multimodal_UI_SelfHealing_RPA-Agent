from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from github import Auth, Github
from github.GithubException import GithubException


# ============================================================
# ENVIRONMENT
# ============================================================

load_dotenv()

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GITHUB_REPOSITORY = os.getenv("GITHUB_REPOSITORY")
GITHUB_BASE_BRANCH = os.getenv("GITHUB_BASE_BRANCH", "main")
GITHUB_HEALING_BRANCH = os.getenv("GITHUB_HEALING_BRANCH", "main")


# ============================================================
# FILE CONFIGURATION
# ============================================================

SOURCE_FILE = Path("demo-store/src/App.jsx")
GITHUB_FILE_PATH = "demo-store/src/App.jsx"


# ============================================================
# VALIDATION
# ============================================================

def validate_config() -> None:
    if not GITHUB_TOKEN:
        raise RuntimeError("GITHUB_TOKEN is not configured in .env")

    if not GITHUB_REPOSITORY:
        raise RuntimeError(
            "GITHUB_REPOSITORY is not configured in .env"
        )


# ============================================================
# GITHUB CLIENT
# ============================================================

def get_github_client() -> Github:
    validate_config()

    auth = Auth.Token(GITHUB_TOKEN)

    return Github(auth=auth)


# ============================================================
# GET REPOSITORY
# ============================================================

def get_repository():
    github = get_github_client()

    print()
    print("=" * 70)
    print("[GITHUB] Connecting to GitHub")
    print("=" * 70)

    repository = github.get_repo(GITHUB_REPOSITORY)

    print(
        f"[GITHUB] Repository: "
        f"{repository.full_name}"
    )

    print("[GITHUB] Connected successfully:", repository.full_name)

    return repository


# ============================================================
# CHECK BRANCH
# ============================================================

def get_healing_branch(repository):
    branch_name = GITHUB_HEALING_BRANCH

    print()
    print(f"[GITHUB] Checking healing branch: {branch_name}")

    try:
        branch = repository.get_branch(branch_name)

        print(f"[GITHUB] Branch found: {branch_name}")

        return branch

    except GithubException as exc:
        if exc.status == 404:
            raise RuntimeError(
                f"Branch '{branch_name}' does not exist."
            ) from exc

        raise


# ============================================================
# READ LOCAL SOURCE
# ============================================================

def read_local_source() -> str:
    if not SOURCE_FILE.exists():
        raise FileNotFoundError(
            f"Local source file not found: {SOURCE_FILE}"
        )

    return SOURCE_FILE.read_text(
        encoding="utf-8"
    )


# ============================================================
# GET REMOTE FILE
# ============================================================

def get_remote_file(repository):
    try:
        return repository.get_contents(
            GITHUB_FILE_PATH,
            ref=GITHUB_HEALING_BRANCH,
        )

    except GithubException as exc:
        if exc.status == 404:
            return None

        raise


# ============================================================
# COMMIT HEALED SOURCE
# ============================================================

def commit_healing_fix() -> dict[str, Any]:
    repository = get_repository()

    get_healing_branch(repository)

    print()
    print("=" * 70)
    print("[GITHUB] Preparing healed App.jsx")
    print("=" * 70)

    print(f"[GITHUB] Local file: {SOURCE_FILE}")

    local_content = read_local_source()

    remote_file = get_remote_file(repository)

    commit_message = (
        "fix: apply OmniSight self-healing UI fix"
    )

    # --------------------------------------------------------
    # FILE DOES NOT EXIST
    # --------------------------------------------------------

    if remote_file is None:
        print(
            "[GITHUB] App.jsx not found on "
            f"{GITHUB_HEALING_BRANCH} branch."
        )

        print("[GITHUB] Creating App.jsx...")

        result = repository.create_file(
            path=GITHUB_FILE_PATH,
            message=commit_message,
            content=local_content,
            branch=GITHUB_HEALING_BRANCH,
        )

        commit_sha = result["commit"].sha

        print("[GITHUB] App.jsx created successfully.")
        print(f"[GITHUB] Commit SHA: {commit_sha}")

        return {
            "status": "created",
            "sha": commit_sha,
            "message": commit_message,
            "path": GITHUB_FILE_PATH,
        }

    # --------------------------------------------------------
    # FILE EXISTS
    # --------------------------------------------------------

    print("[GITHUB] App.jsx already exists on GitHub.")

    try:
        remote_content = remote_file.decoded_content.decode(
            "utf-8"
        )
    except AttributeError:
        remote_content = remote_file.decoded_content.decode(
            "utf-8"
        )

    # --------------------------------------------------------
    # NO CHANGE
    # --------------------------------------------------------

    if remote_content == local_content:
        print(
            "[GITHUB] Remote App.jsx already matches "
            "the healed local file."
        )

        print("[GITHUB] No new commit required.")

        return {
            "status": "unchanged",
            "sha": remote_file.sha,
            "message": "No changes required.",
            "path": GITHUB_FILE_PATH,
        }

    # --------------------------------------------------------
    # UPDATE FILE
    # --------------------------------------------------------

    print("[GITHUB] Changes detected.")
    print("[GITHUB] Updating App.jsx...")

    result = repository.update_file(
        path=GITHUB_FILE_PATH,
        message=commit_message,
        content=local_content,
        sha=remote_file.sha,
        branch=GITHUB_HEALING_BRANCH,
    )

    commit_sha = result["commit"].sha

    print("[GITHUB] App.jsx updated successfully.")
    print(f"[GITHUB] Commit SHA: {commit_sha}")

    return {
        "status": "updated",
        "sha": commit_sha,
        "message": commit_message,
        "path": GITHUB_FILE_PATH,
    }


# ============================================================
# FIND EXISTING PR
# ============================================================

def find_existing_pr(repository):
    print()
    print("[GITHUB] Checking existing Pull Requests...")

    if GITHUB_HEALING_BRANCH == GITHUB_BASE_BRANCH:
        print(
            "[GITHUB] Healing branch and base branch "
            "are the same."
        )

        print("[GITHUB] PR search skipped.")

        return None

    pulls = repository.get_pulls(
        state="open",
        base=GITHUB_BASE_BRANCH,
        head=(
            f"{repository.owner.login}:"
            f"{GITHUB_HEALING_BRANCH}"
        ),
    )

    for pull in pulls:
        print(
            f"[GITHUB] Existing PR found: #{pull.number}"
        )

        return pull

    print("[GITHUB] No existing healing PR found.")

    return None


# ============================================================
# CREATE PULL REQUEST
# ============================================================

def create_healing_pr(repository):
    # --------------------------------------------------------
    # DIRECT MAIN MODE
    # --------------------------------------------------------

    if GITHUB_HEALING_BRANCH == GITHUB_BASE_BRANCH:
        print()
        print(
            "[GITHUB] Healing branch == base branch."
        )

        print(
            "[GITHUB] Direct commit mode enabled."
        )

        print(
            "[GITHUB] Pull Request creation skipped."
        )

        return {
            "status": "skipped",
            "reason": (
                "Healing branch and base branch "
                "are both main."
            ),
        }

    # --------------------------------------------------------
    # PR MODE
    # --------------------------------------------------------

    existing_pr = find_existing_pr(repository)

    if existing_pr:
        return {
            "status": "existing",
            "number": existing_pr.number,
            "url": existing_pr.html_url,
            "title": existing_pr.title,
        }

    print()
    print("[GITHUB] Creating Pull Request...")

    try:
        pull_request = repository.create_pull(
            title="OmniSight: Self-Healing UI Fix",
            body=(
                "This Pull Request was automatically "
                "created by OmniSight.\n\n"
                "The UI defect was detected, healed, "
                "and verified by the self-healing pipeline."
            ),
            head=GITHUB_HEALING_BRANCH,
            base=GITHUB_BASE_BRANCH,
        )

        print(
            f"[GITHUB] Pull Request created: "
            f"#{pull_request.number}"
        )

        print(
            f"[GITHUB] URL: "
            f"{pull_request.html_url}"
        )

        return {
            "status": "created",
            "number": pull_request.number,
            "url": pull_request.html_url,
            "title": pull_request.title,
        }

    except GithubException as exc:
        raise RuntimeError(
            f"Failed to create Pull Request: {exc.data}"
        ) from exc


# ============================================================
# COMPLETE GITHUB PUBLISH WORKFLOW
# ============================================================

def publish_healing_fix() -> dict[str, Any]:
    print()
    print("=" * 70)
    print("OMNISIGHT GITHUB INTEGRATION")
    print("=" * 70)

    print(
        f"[GITHUB] Repository: "
        f"{GITHUB_REPOSITORY}"
    )

    print(
        f"[GITHUB] Healing branch: "
        f"{GITHUB_HEALING_BRANCH}"
    )

    print(
        f"[GITHUB] Base branch: "
        f"{GITHUB_BASE_BRANCH}"
    )

    repository = get_repository()

    # --------------------------------------------------------
    # COMMIT FIX
    # --------------------------------------------------------

    commit_result = commit_healing_fix()

    # --------------------------------------------------------
    # DIRECT MAIN MODE
    # --------------------------------------------------------

    if GITHUB_HEALING_BRANCH == GITHUB_BASE_BRANCH:
        print()
        print("=" * 70)
        print("[GITHUB] DIRECT MAIN MODE")
        print("=" * 70)

        print(
            "[GITHUB] Healing branch and base branch "
            "are both main."
        )

        print(
            "[GITHUB] Pull Request creation skipped."
        )

        print(
            "[GITHUB] Healing fix committed directly "
            "to main."
        )

        return {
            "status": "success",
            "repository": GITHUB_REPOSITORY,
            "branch": GITHUB_HEALING_BRANCH,
            "commit": commit_result,
            "pull_request": {
                "status": "skipped",
                "reason": (
                    "Direct commit mode: "
                    "healing branch and base branch "
                    "are both main."
                ),
            },
        }

    # --------------------------------------------------------
    # PR MODE
    # --------------------------------------------------------

    pr_result = create_healing_pr(repository)

    return {
        "status": "success",
        "repository": GITHUB_REPOSITORY,
        "branch": GITHUB_HEALING_BRANCH,
        "commit": commit_result,
        "pull_request": pr_result,
    }


# ============================================================
# BACKWARD COMPATIBILITY
# ============================================================

def create_healing_pr_workflow() -> dict[str, Any]:
    return publish_healing_fix()


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    try:
        result = publish_healing_fix()

        print()
        print("=" * 70)
        print("OMNISIGHT GITHUB INTEGRATION SUCCESS")
        print("=" * 70)

        print(
            f"Status     : {result['status']}"
        )

        print(
            f"Repository : {result['repository']}"
        )

        print(
            f"Branch     : {result['branch']}"
        )

        commit = result.get("commit", {})

        print(
            f"Commit     : {commit.get('sha')}"
        )

        pull_request = result.get(
            "pull_request",
            {},
        )

        print(
            f"PR Status  : "
            f"{pull_request.get('status')}"
        )

        if pull_request.get("url"):
            print(
                f"PR URL     : "
                f"{pull_request['url']}"
            )

        print("=" * 70)

    except Exception as exc:

        print()
        print("=" * 70)
        print("OMNISIGHT GITHUB INTEGRATION FAILED")
        print("=" * 70)

        print(f"Error: {exc}")

        print("=" * 70)

        raise