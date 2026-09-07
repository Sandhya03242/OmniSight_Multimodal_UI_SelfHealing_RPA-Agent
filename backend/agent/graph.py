from __future__ import annotations

import asyncio
import hashlib
import time
from pathlib import Path
from typing import Any, TypedDict

from langgraph.graph import END, StateGraph

from backend.browser.navigator import run_healing_test
from backend.github.integration import publish_healing_fix
from backend.vision.analyzer import (
    analyze_ui,
    generate_healing_fix,
    verify_healing,
)


# ============================================================
# CONFIGURATION
# ============================================================

BASE_URL = "http://localhost:5173"

APP_FILE = Path("demo-store/src/App.jsx")

MAX_ATTEMPTS = 2

# Give Vite enough time to detect the App.jsx modification.
VITE_REBUILD_WAIT_SECONDS = 2.0


# ============================================================
# LANGGRAPH STATE
# ============================================================

class HealingState(TypedDict, total=False):
    url: str

    attempt: int
    max_attempts: int

    screenshots: list[dict[str, Any]]
    html_files: list[str]

    before_screenshot: str | None
    after_screenshot: str | None

    before_html: str | None
    after_html: str | None

    before_hash: str | None
    after_hash: str | None

    analysis: dict[str, Any]
    issues: list[dict[str, Any]]
    fixes: list[dict[str, Any]]

    applied: bool
    retest_failed: bool
    fixed: bool

    verification: dict[str, Any]

    github_result: dict[str, Any]

    status: str
    error: str


# ============================================================
# HELPERS
# ============================================================

def get_screenshot_path(
    screenshot_data: Any,
) -> str:

    if isinstance(
        screenshot_data,
        dict,
    ):

        path = screenshot_data.get(
            "screenshot"
        )

        if not path:

            raise ValueError(
                "Screenshot dictionary does not contain "
                "'screenshot' path."
            )

        return str(path)

    if isinstance(
        screenshot_data,
        (str, Path),
    ):

        return str(
            screenshot_data
        )

    raise TypeError(
        "Screenshot must be a path string or dictionary, "
        f"got {type(screenshot_data).__name__}."
    )


def get_html_path(
    screenshot_data: Any,
    html_files: list[str],
) -> str:

    if isinstance(
        screenshot_data,
        dict,
    ):

        html_path = screenshot_data.get(
            "html"
        )

        if html_path:

            return str(
                html_path
            )

    if html_files:

        return str(
            html_files[0]
        )

    raise ValueError(
        "No HTML file available."
    )


def get_first_screenshot(
    screenshots: Any,
) -> str | None:

    if not screenshots:

        return None

    try:

        return get_screenshot_path(
            screenshots[0]
        )

    except Exception:

        return None


def get_first_html(
    screenshots: Any,
    html_files: list[str],
) -> str | None:

    if not screenshots:

        return None

    try:

        return get_html_path(
            screenshots[0],
            html_files,
        )

    except Exception:

        return None


def file_hash(
    path: str | Path,
) -> str:

    file_path = Path(
        path
    )

    if not file_path.exists():

        return ""

    digest = hashlib.sha256()

    with file_path.open(
        "rb"
    ) as file:

        for chunk in iter(
            lambda: file.read(1024 * 1024),
            b"",
        ):

            digest.update(
                chunk
            )

    return digest.hexdigest()


def wait_for_vite_rebuild() -> None:

    print(
        f"[VITE] Waiting "
        f"{VITE_REBUILD_WAIT_SECONDS}s "
        f"for React/Vite rebuild..."
    )

    time.sleep(
        VITE_REBUILD_WAIT_SECONDS
    )


def choose_retest_screenshot(
    screenshots: list[Any],
    before_screenshot: str | None,
) -> str:

    if not screenshots:

        raise RuntimeError(
            "No screenshots were returned by Playwright."
        )

    # --------------------------------------------------------
    # Prefer a screenshot that is NOT the original BEFORE path.
    # --------------------------------------------------------

    before_normalized = (
        str(
            Path(
                before_screenshot
            ).resolve()
        )
        if before_screenshot
        else None
    )

    candidates: list[str] = []

    for screenshot_data in screenshots:

        try:

            path = get_screenshot_path(
                screenshot_data
            )

            candidates.append(
                path
            )

        except Exception:

            continue

    if not candidates:

        raise RuntimeError(
            "Playwright returned screenshots, but no "
            "valid screenshot paths were found."
        )

    for candidate in candidates:

        candidate_normalized = str(
            Path(
                candidate
            ).resolve()
        )

        if (
            before_normalized is None
            or candidate_normalized
            != before_normalized
        ):

            return candidate

    # If every path is identical, return the first one.
    # Hash validation below will catch this.
    return candidates[0]


# ============================================================
# CAPTURE NODE
# ============================================================

async def capture_node(
    state: HealingState,
) -> HealingState:

    print("\n" + "=" * 70)
    print("[GRAPH] CAPTURE BEFORE")
    print("=" * 70)

    url = state[
        "url"
    ]

    try:

        result = await run_healing_test(
            url
        )

        if not isinstance(
            result,
            dict,
        ):

            raise RuntimeError(
                "Playwright returned an invalid result."
            )

        screenshots = result.get(
            "screenshots",
            [],
        )

        html_files = result.get(
            "html_files",
            [],
        )

        if not screenshots:

            raise RuntimeError(
                "Playwright did not produce any screenshots."
            )

        if not html_files:

            raise RuntimeError(
                "Playwright did not produce any HTML files."
            )

        before_screenshot = (
            get_first_screenshot(
                screenshots
            )
        )

        before_html = (
            get_first_html(
                screenshots,
                html_files,
            )
        )

        if not before_screenshot:

            raise RuntimeError(
                "Could not determine BEFORE screenshot."
            )

        before_hash = file_hash(
            before_screenshot
        )

        print(
            f"[PLAYWRIGHT] Screenshots: "
            f"{len(screenshots)}"
        )

        print(
            f"[PLAYWRIGHT] HTML files: "
            f"{len(html_files)}"
        )

        print(
            f"[BEFORE] "
            f"{before_screenshot}"
        )

        print(
            f"[BEFORE HTML] "
            f"{before_html}"
        )

        print(
            f"[BEFORE HASH] "
            f"{before_hash[:16]}..."
        )

        return {
            **state,

            "screenshots":
                screenshots,

            "html_files": [
                str(
                    path
                )
                for path in html_files
            ],

            "before_screenshot":
                before_screenshot,

            "before_html":
                before_html,

            "before_hash":
                before_hash,

            # New attempt starts without AFTER.
            "after_screenshot":
                None,

            "after_html":
                None,

            "after_hash":
                None,

            "status":
                "captured",

            "error":
                "",

            "retest_failed":
                False,
        }

    except Exception as exc:

        print(
            f"[CAPTURE ERROR] {exc}"
        )

        return {
            **state,

            "status":
                "error",

            "error":
                str(exc),
        }


# ============================================================
# ANALYZE NODE
# ============================================================

async def analyze_node(
    state: HealingState,
) -> HealingState:

    print("\n" + "=" * 70)
    print("[GRAPH] VLM ANALYSIS")
    print("=" * 70)

    screenshots = state.get(
        "screenshots",
        [],
    )

    html_files = state.get(
        "html_files",
        [],
    )

    if not screenshots:

        return {
            **state,

            "status":
                "error",

            "error":
                "No screenshots available for analysis.",
        }

    try:

        screenshot_data = screenshots[0]

        screenshot = get_screenshot_path(
            screenshot_data
        )

        html = get_html_path(
            screenshot_data,
            html_files,
        )

        print(
            f"[GRAPH] Screenshot: "
            f"{screenshot}"
        )

        print(
            f"[GRAPH] HTML: "
            f"{html}"
        )

        analysis = await asyncio.to_thread(
            analyze_ui,
            screenshot,
            html,
        )

        if not isinstance(
            analysis,
            dict,
        ):

            raise RuntimeError(
                "VLM analyzer returned an invalid result."
            )

        issues = analysis.get(
            "issues",
            [],
        )

        if not isinstance(
            issues,
            list,
        ):

            issues = []

        dashboard_issues: list[
            dict[str, Any]
        ] = []

        for index, issue in enumerate(
            issues,
            start=1,
        ):

            if isinstance(
                issue,
                dict,
            ):

                normalized_issue = dict(
                    issue
                )

            else:

                normalized_issue = {
                    "description":
                        str(issue)
                }

            normalized_issue.setdefault(
                "id",
                str(index),
            )

            normalized_issue.setdefault(
                "status",
                "pending",
            )

            normalized_issue.setdefault(
                "screenshot",
                screenshot,
            )

            normalized_issue.setdefault(
                "before_screenshot",
                state.get(
                    "before_screenshot"
                ),
            )

            dashboard_issues.append(
                normalized_issue
            )

        optimization = analysis.get(
            "optimization",
            {},
        )

        if not isinstance(
            optimization,
            dict,
        ):

            optimization = {}

        print(
            "[WEEK 4] Image optimization:",
            optimization.get(
                "image",
                {},
            ),
        )

        print(
            "[WEEK 4] HTML reduction:",
            optimization.get(
                "html",
                {},
            ),
        )

        print(
            f"[VLM] Detected issues: "
            f"{len(dashboard_issues)}"
        )

        if dashboard_issues:

            print(
                "[VLM] UI issue detected."
            )

            analysis["status"] = (
                "issue_found"
            )

            analysis["issues"] = (
                dashboard_issues
            )

            return {
                **state,

                "analysis":
                    analysis,

                "issues":
                    dashboard_issues,

                "status":
                    "issue_found",

                "fixed":
                    False,

                "error":
                    "",
            }

        print(
            "[VLM] No UI issue detected."
        )

        analysis["status"] = (
            "no_issue"
        )

        analysis["issues"] = []

        return {
            **state,

            "analysis":
                analysis,

            "issues":
                [],

            "fixed":
                True,

            "status":
                "no_issue",

            "error":
                "",
        }

    except Exception as exc:

        print(
            f"[ANALYSIS ERROR] {exc}"
        )

        return {
            **state,

            "status":
                "error",

            "error":
                str(exc),
        }


# ============================================================
# EXTRACT FIX NODE
# ============================================================

async def extract_fix_node(
    state: HealingState,
) -> HealingState:

    print("\n" + "=" * 70)
    print("[GRAPH] EXTRACT HEALING FIX")
    print("=" * 70)

    analysis = state.get(
        "analysis",
        {},
    )

    issues = state.get(
        "issues",
        [],
    )

    if not issues:

        issues = analysis.get(
            "issues",
            [],
        )

    screenshots = state.get(
        "screenshots",
        [],
    )

    if not issues:

        return {
            **state,

            "fixes":
                [],

            "status":
                "no_fix_required",
        }

    if not screenshots:

        return {
            **state,

            "status":
                "error",

            "error":
                "No screenshot available for fix generation.",
        }

    try:

        screenshot = get_screenshot_path(
            screenshots[0]
        )

    except Exception as exc:

        return {
            **state,

            "status":
                "error",

            "error":
                str(exc),
        }

    if not APP_FILE.exists():

        return {
            **state,

            "status":
                "error",

            "error":
                f"Source file not found: {APP_FILE}",
        }

    source_code = APP_FILE.read_text(
        encoding="utf-8",
    )

    if not source_code.strip():

        return {
            **state,

            "status":
                "error",

            "error":
                "Source file is empty.",
        }

    print(
        f"[SOURCE] Reading: "
        f"{APP_FILE}"
    )

    print(
        f"[SOURCE] Characters: "
        f"{len(source_code)}"
    )

    fixes: list[
        dict[str, Any]
    ] = []

    for index, issue in enumerate(
        issues,
        start=1,
    ):

        print(
            f"\n[VLM] Generating fix "
            f"{index}/{len(issues)}"
        )

        try:

            result = await asyncio.to_thread(
                generate_healing_fix,
                screenshot,
                issue,
                source_code,
            )

            if not isinstance(
                result,
                dict,
            ):

                continue

            generated_fixes = result.get(
                "fixes",
                [],
            )

            if not isinstance(
                generated_fixes,
                list,
            ):

                generated_fixes = []

            if not generated_fixes:

                old = result.get(
                    "old"
                )

                new = result.get(
                    "new"
                )

                if old and new:

                    generated_fixes = [
                        {
                            "old":
                                old,

                            "new":
                                new,

                            "reason":
                                result.get(
                                    "reason",
                                    "",
                                ),
                        }
                    ]

            for fix in generated_fixes:

                if not isinstance(
                    fix,
                    dict,
                ):

                    continue

                old = fix.get(
                    "old"
                )

                new = fix.get(
                    "new"
                )

                if not old or not new:

                    continue

                if old == new:

                    print(
                        "[VLM] Fix rejected: "
                        "old/new identical."
                    )

                    continue

                if old not in source_code:

                    print(
                        "[VLM] Fix rejected: "
                        "old code not found."
                    )

                    continue

                test_source = (
                    source_code.replace(
                        old,
                        new,
                        1,
                    )
                )

                if test_source == source_code:

                    continue

                fixes.append(
                    {
                        "issue":
                            issue,

                        "old":
                            old,

                        "new":
                            new,

                        "reason":
                            fix.get(
                                "reason",
                                "",
                            ),
                    }
                )

        except Exception as exc:

            print(
                f"[FIX ERROR] {exc}"
            )

    print(
        f"[VLM] Valid fixes: "
        f"{len(fixes)}"
    )

    if not fixes:

        return {
            **state,

            "fixes":
                [],

            "status":
                "fix_generation_failed",

            "error":
                "VLM did not produce a valid source patch.",
        }

    return {
        **state,

        "fixes":
            fixes,

        "status":
            "fixes_ready",

        "error":
            "",
    }


# ============================================================
# APPLY FIX NODE
# ============================================================

async def apply_fix_node(
    state: HealingState,
) -> HealingState:

    print("\n" + "=" * 70)
    print("[GRAPH] APPLY SOURCE FIX")
    print("=" * 70)

    fixes = state.get(
        "fixes",
        [],
    )

    if not fixes:

        return {
            **state,

            "applied":
                False,

            "status":
                "no_fix",
        }

    if not APP_FILE.exists():

        return {
            **state,

            "applied":
                False,

            "status":
                "error",

            "error":
                f"Source file not found: {APP_FILE}",
        }

    source_code = APP_FILE.read_text(
        encoding="utf-8",
    )

    original_source = source_code

    applied_count = 0

    for index, fix in enumerate(
        fixes,
        start=1,
    ):

        old = fix.get(
            "old"
        )

        new = fix.get(
            "new"
        )

        if not old or not new:

            continue

        if old == new:

            continue

        if old not in source_code:

            print(
                f"[PATCH {index}] "
                "Old code not found."
            )

            continue

        source_code = (
            source_code.replace(
                old,
                new,
                1,
            )
        )

        applied_count += 1

        print(
            f"[PATCH {index}] "
            "Applied successfully."
        )

    if source_code == original_source:

        print(
            "[PATCH] No changes applied."
        )

        return {
            **state,

            "applied":
                False,

            "status":
                "patch_not_applied",
        }

    APP_FILE.write_text(
        source_code,
        encoding="utf-8",
    )

    # --------------------------------------------------------
    # IMPORTANT:
    # Wait for Vite to detect and rebuild App.jsx.
    # --------------------------------------------------------

    wait_for_vite_rebuild()

    # --------------------------------------------------------
    # Confirm source was really changed.
    # --------------------------------------------------------

    current_source = APP_FILE.read_text(
        encoding="utf-8",
    )

    if current_source == original_source:

        return {
            **state,

            "applied":
                False,

            "status":
                "patch_not_applied",

            "error":
                "App.jsx did not change after patch.",
        }

    print(
        f"[PATCH] Applied "
        f"{applied_count} fix(es)."
    )

    print(
        f"[PATCH] App.jsx size: "
        f"{len(current_source)} characters"
    )

    return {
        **state,

        "applied":
            True,

        "status":
            "fix_applied",

        "error":
            "",
    }


# ============================================================
# RETEST NODE
# ============================================================

async def retest_node(
    state: HealingState,
) -> HealingState:

    print("\n" + "=" * 70)
    print("[GRAPH] RETEST AFTER HEALING")
    print("=" * 70)

    before_screenshot = state.get(
        "before_screenshot"
    )

    before_hash = state.get(
        "before_hash"
    )

    try:

        # ----------------------------------------------------
        # Wait once more before opening a fresh browser.
        # ----------------------------------------------------

        wait_for_vite_rebuild()

        # ----------------------------------------------------
        # IMPORTANT:
        # run_healing_test() creates a fresh browser
        # session in navigator.py.
        # ----------------------------------------------------

        result = await run_healing_test(
            state["url"]
        )

        if not isinstance(
            result,
            dict,
        ):

            raise RuntimeError(
                "Playwright retest returned an invalid result."
            )

        screenshots = result.get(
            "screenshots",
            [],
        )

        html_files = result.get(
            "html_files",
            [],
        )

        if not screenshots:

            raise RuntimeError(
                "Retest did not produce screenshots."
            )

        if not html_files:

            raise RuntimeError(
                "Retest did not produce HTML files."
            )

        # ----------------------------------------------------
        # Choose a screenshot that is different from BEFORE.
        # ----------------------------------------------------

        after_screenshot = (
            choose_retest_screenshot(
                screenshots,
                before_screenshot,
            )
        )

        after_html = (
            get_first_html(
                screenshots,
                html_files,
            )
        )

        if not after_screenshot:

            raise RuntimeError(
                "Could not determine AFTER screenshot."
            )

        after_hash = file_hash(
            after_screenshot
        )

        # ----------------------------------------------------
        # Detect exact same file/path.
        # ----------------------------------------------------

        same_path = False

        if (
            before_screenshot
            and after_screenshot
        ):

            same_path = (
                Path(
                    before_screenshot
                ).resolve()
                == Path(
                    after_screenshot
                ).resolve()
            )

        # ----------------------------------------------------
        # Detect identical binary screenshot.
        # ----------------------------------------------------

        same_hash = (
            bool(before_hash)
            and bool(after_hash)
            and before_hash == after_hash
        )

        print(
            f"[RETEST] Screenshots: "
            f"{len(screenshots)}"
        )

        print(
            f"[RETEST] HTML files: "
            f"{len(html_files)}"
        )

        print(
            f"[BEFORE] "
            f"{before_screenshot}"
        )

        print(
            f"[AFTER]  "
            f"{after_screenshot}"
        )

        print(
            f"[BEFORE HASH] "
            f"{before_hash[:16] if before_hash else 'N/A'}..."
        )

        print(
            f"[AFTER HASH]  "
            f"{after_hash[:16] if after_hash else 'N/A'}..."
        )

        print(
            f"[SAME PATH] "
            f"{same_path}"
        )

        print(
            f"[SAME HASH] "
            f"{same_hash}"
        )

        # ----------------------------------------------------
        # If same path, this is definitely invalid.
        # ----------------------------------------------------

        if same_path:

            raise RuntimeError(
                "AFTER screenshot points to the same file "
                "as BEFORE screenshot."
            )

        # ----------------------------------------------------
        # Same hash is suspicious.
        #
        # We do NOT immediately fail because the UI may
        # legitimately remain visually identical even when
        # the source changed.
        #
        # Verification will decide whether the issue remains.
        # ----------------------------------------------------

        if same_hash:

            print(
                "[WARNING] BEFORE and AFTER screenshot "
                "binary hashes are identical."
            )

            print(
                "[WARNING] The browser may not have "
                "rendered the updated React source."
            )

        return {
            **state,

            # Current retest result is used by verification.
            "screenshots":
                screenshots,

            "html_files": [
                str(
                    path
                )
                for path in html_files
            ],

            # Preserve original BEFORE.
            "before_screenshot":
                before_screenshot,

            "before_html":
                state.get(
                    "before_html"
                ),

            "before_hash":
                before_hash,

            # New AFTER.
            "after_screenshot":
                after_screenshot,

            "after_html":
                after_html,

            "after_hash":
                after_hash,

            "retest_failed":
                False,

            "status":
                "retested",

            "error":
                "",
        }

    except Exception as exc:

        print(
            f"[RETEST ERROR] {exc}"
        )

        return {
            **state,

            "retest_failed":
                True,

            "status":
                "retest_failed",

            "error":
                str(exc),
        }


# ============================================================
# VERIFY NODE
# ============================================================

async def verify_node(
    state: HealingState,
) -> HealingState:

    print("\n" + "=" * 70)
    print("[GRAPH] VERIFY AFTER SCREENSHOT")
    print("=" * 70)

    if state.get(
        "retest_failed",
        False,
    ):

        return {
            **state,

            "fixed":
                False,

            "status":
                "verification_failed",

            "error":
                state.get(
                    "error",
                    "Retest failed.",
                ),
        }

    issues = state.get(
        "issues",
        [],
    )

    if not issues:

        return {
            **state,

            "fixed":
                True,

            "status":
                "no_issue",

            "verification": {
                "status":
                    "no_issue",

                "fixed":
                    True,
            },
        }

    # --------------------------------------------------------
    # CRITICAL:
    # Verify the AFTER screenshot.
    # --------------------------------------------------------

    after_screenshot = state.get(
        "after_screenshot"
    )

    after_html = state.get(
        "after_html"
    )

    if not after_screenshot:

        return {
            **state,

            "fixed":
                False,

            "status":
                "verification_failed",

            "error":
                "AFTER screenshot is missing.",
        }

    if not after_html:

        # Try to recover HTML from retest result.
        screenshots = state.get(
            "screenshots",
            [],
        )

        html_files = state.get(
            "html_files",
            [],
        )

        try:

            after_html = get_html_path(
                screenshots[0],
                html_files,
            )

        except Exception as exc:

            return {
                **state,

                "fixed":
                    False,

                "status":
                    "verification_failed",

                "error":
                    f"AFTER HTML is missing: {exc}",
            }

    print(
        f"[VERIFY] BEFORE: "
        f"{state.get('before_screenshot')}"
    )

    print(
        f"[VERIFY] AFTER:  "
        f"{after_screenshot}"
    )

    print(
        f"[VERIFY] AFTER HTML: "
        f"{after_html}"
    )

    try:

        issue = issues[0]

        verification = await asyncio.to_thread(
            verify_healing,
            after_screenshot,
            after_html,
            issue,
        )

        if not isinstance(
            verification,
            dict,
        ):

            verification = {
                "status":
                    "unknown",

                "fixed":
                    bool(
                        verification
                    ),
            }

        fixed = bool(
            verification.get(
                "fixed",
                False,
            )
        )

        status = str(
            verification.get(
                "status",
                "",
            )
        ).lower()

        if status in {
            "fixed",
            "passed",
            "verified",
        }:

            fixed = True

        # ----------------------------------------------------
        # Ensure source still exists.
        # ----------------------------------------------------

        if not APP_FILE.exists():

            fixed = False

            verification[
                "source_check"
            ] = (
                "Source file missing."
            )

        else:

            source = APP_FILE.read_text(
                encoding="utf-8",
            )

            if not source.strip():

                fixed = False

                verification[
                    "source_check"
                ] = (
                    "Source file is empty."
                )

            else:

                verification[
                    "source_check"
                ] = (
                    "Source file exists and "
                    "is not empty."
                )

        verification[
            "before_screenshot"
        ] = state.get(
            "before_screenshot"
        )

        verification[
            "after_screenshot"
        ] = after_screenshot

        verification[
            "before_hash"
        ] = state.get(
            "before_hash"
        )

        verification[
            "after_hash"
        ] = state.get(
            "after_hash"
        )

        print(
            f"[VERIFY] Fixed: "
            f"{fixed}"
        )

        print(
            f"[VERIFY] Result: "
            f"{verification}"
        )

        return {
            **state,

            "after_html":
                after_html,

            "verification":
                verification,

            "fixed":
                fixed,

            "status": (
                "verified"
                if fixed
                else "verification_failed"
            ),

            "error":
                "",
        }

    except Exception as exc:

        print(
            f"[VERIFY ERROR] {exc}"
        )

        return {
            **state,

            "fixed":
                False,

            "status":
                "verification_failed",

            "error":
                str(exc),
        }


# ============================================================
# PUBLISH NODE
# ============================================================

async def publish_node(
    state: HealingState,
) -> HealingState:

    print("\n" + "=" * 70)
    print("[GRAPH] GITHUB PUBLISH")
    print("=" * 70)

    if not state.get(
        "fixed",
        False,
    ):

        print(
            "[GITHUB] Skipped because "
            "fix was not verified."
        )

        return {
            **state,

            "status":
                "not_published",
        }

    if not state.get(
        "issues",
        [],
    ):

        return {
            **state,

            "status":
                "no_issue",
        }

    try:

        result = await asyncio.to_thread(
            publish_healing_fix,
        )

        print(
            f"[GITHUB] Result: "
            f"{result}"
        )

        if isinstance(
            result,
            dict,
        ):

            github_result = result

        else:

            github_result = {
                "status":
                    "published",

                "result":
                    str(result),
            }

        return {
            **state,

            "github_result":
                github_result,

            "status":
                "published",

            "error":
                "",
        }

    except Exception as exc:

        print(
            f"[GITHUB ERROR] {exc}"
        )

        return {
            **state,

            "github_result": {
                "status":
                    "error",

                "error":
                    str(exc),
            },

            "status":
                "github_failed",

            "error":
                str(exc),
        }


# ============================================================
# ROUTING
# ============================================================

def route_after_capture(
    state: HealingState,
) -> str:

    if state.get(
        "status"
    ) == "error":

        return "end"

    return "analyze"


def route_after_analyze(
    state: HealingState,
) -> str:

    if state.get(
        "status"
    ) == "error":

        return "end"

    if not state.get(
        "issues",
        [],
    ):

        return "end"

    return "extract_fix"


def route_after_apply(
    state: HealingState,
) -> str:

    if state.get(
        "applied",
        False,
    ):

        return "retest"

    return "retry"


def route_after_retest(
    state: HealingState,
) -> str:

    if state.get(
        "retest_failed",
        False,
    ):

        return "retry"

    return "verify"


def route_after_verify(
    state: HealingState,
) -> str:

    if (
        state.get(
            "fixed",
            False,
        )
        and state.get(
            "issues",
            [],
        )
    ):

        return "publish"

    attempt = state.get(
        "attempt",
        1,
    )

    max_attempts = state.get(
        "max_attempts",
        MAX_ATTEMPTS,
    )

    if attempt < max_attempts:

        return "retry"

    return "end"


# ============================================================
# RETRY NODE
# ============================================================

def retry_node(
    state: HealingState,
) -> HealingState:

    next_attempt = (
        state.get(
            "attempt",
            1,
        )
        + 1
    )

    max_attempts = state.get(
        "max_attempts",
        MAX_ATTEMPTS,
    )

    print("\n" + "=" * 70)

    print(
        f"[GRAPH] SELF-HEALING RETRY "
        f"{next_attempt}/{max_attempts}"
    )

    print("=" * 70)

    return {
        **state,

        "attempt":
            next_attempt,

        "status":
            "retrying",

        "screenshots":
            [],

        "html_files":
            [],

        "before_screenshot":
            None,

        "after_screenshot":
            None,

        "before_html":
            None,

        "after_html":
            None,

        "before_hash":
            None,

        "after_hash":
            None,

        "analysis":
            {},

        "issues":
            [],

        "fixes":
            [],

        "applied":
            False,

        "retest_failed":
            False,

        "fixed":
            False,

        "verification":
            {},

        "error":
            "",
    }


# ============================================================
# BUILD LANGGRAPH
# ============================================================

def build_healing_graph():

    graph = StateGraph(
        HealingState
    )

    # --------------------------------------------------------
    # NODES
    # --------------------------------------------------------

    graph.add_node(
        "capture",
        capture_node,
    )

    graph.add_node(
        "analyze",
        analyze_node,
    )

    graph.add_node(
        "extract_fix",
        extract_fix_node,
    )

    graph.add_node(
        "apply_fix",
        apply_fix_node,
    )

    graph.add_node(
        "retest",
        retest_node,
    )

    graph.add_node(
        "verify",
        verify_node,
    )

    graph.add_node(
        "publish",
        publish_node,
    )

    graph.add_node(
        "retry",
        retry_node,
    )

    # --------------------------------------------------------
    # START
    # --------------------------------------------------------

    graph.set_entry_point(
        "capture"
    )

    # --------------------------------------------------------
    # CAPTURE
    # --------------------------------------------------------

    graph.add_conditional_edges(
        "capture",
        route_after_capture,
        {
            "analyze":
                "analyze",

            "end":
                END,
        },
    )

    # --------------------------------------------------------
    # ANALYZE
    # --------------------------------------------------------

    graph.add_conditional_edges(
        "analyze",
        route_after_analyze,
        {
            "extract_fix":
                "extract_fix",

            "end":
                END,
        },
    )

    # --------------------------------------------------------
    # EXTRACT
    # --------------------------------------------------------

    graph.add_edge(
        "extract_fix",
        "apply_fix",
    )

    # --------------------------------------------------------
    # APPLY
    # --------------------------------------------------------

    graph.add_conditional_edges(
        "apply_fix",
        route_after_apply,
        {
            "retest":
                "retest",

            "retry":
                "retry",
        },
    )

    # --------------------------------------------------------
    # RETEST
    # --------------------------------------------------------

    graph.add_conditional_edges(
        "retest",
        route_after_retest,
        {
            "verify":
                "verify",

            "retry":
                "retry",
        },
    )

    # --------------------------------------------------------
    # VERIFY
    # --------------------------------------------------------

    graph.add_conditional_edges(
        "verify",
        route_after_verify,
        {
            "publish":
                "publish",

            "retry":
                "retry",

            "end":
                END,
        },
    )

    # --------------------------------------------------------
    # RETRY
    # --------------------------------------------------------

    graph.add_edge(
        "retry",
        "capture",
    )

    # --------------------------------------------------------
    # PUBLISH
    # --------------------------------------------------------

    graph.add_edge(
        "publish",
        END,
    )

    return graph.compile()


# ============================================================
# GLOBAL GRAPH
# ============================================================

healing_graph = build_healing_graph()


# ============================================================
# RUN HEALING AGENT
# ============================================================

async def run_healing_agent(
    url: str = BASE_URL,
    max_attempts: int = MAX_ATTEMPTS,
) -> HealingState:

    print("\n")
    print("=" * 70)
    print("OMNISIGHT SELF-HEALING AGENT")
    print("=" * 70)

    print(
        f"[URL]          {url}"
    )

    print(
        f"[MAX ATTEMPTS] {max_attempts}"
    )

    print(
        "[IMAGE OPT]    Enabled"
    )

    print(
        "[HTML REDUCE]  Enabled"
    )

    print(
        "[VLM]          Qwen/Qwen3.5-0.8B"
    )

    print(
        "[BROWSER]      Playwright"
    )

    print(
        "[GRAPH]        LangGraph"
    )

    print("=" * 70)

    initial_state: HealingState = {

        "url":
            url,

        "attempt":
            1,

        "max_attempts":
            max_attempts,

        "screenshots":
            [],

        "html_files":
            [],

        "before_screenshot":
            None,

        "after_screenshot":
            None,

        "before_html":
            None,

        "after_html":
            None,

        "before_hash":
            None,

        "after_hash":
            None,

        "analysis":
            {},

        "issues":
            [],

        "fixes":
            [],

        "applied":
            False,

        "retest_failed":
            False,

        "fixed":
            False,

        "verification":
            {},

        "github_result":
            {},

        "status":
            "starting",

        "error":
            "",
    }

    try:

        final_state = await healing_graph.ainvoke(
            initial_state,
            config={
                "recursion_limit":
                    50,
            },
        )

        final_state = dict(
            final_state
        )

        print("\n")
        print("=" * 70)
        print("OMNISIGHT HEALING SUMMARY")
        print("=" * 70)

        print(
            f"[STATUS]       "
            f"{final_state.get('status')}"
        )

        print(
            f"[ATTEMPT]      "
            f"{final_state.get('attempt')}"
        )

        print(
            f"[ISSUES]       "
            f"{len(final_state.get('issues', []))}"
        )

        print(
            f"[FIXES]        "
            f"{len(final_state.get('fixes', []))}"
        )

        print(
            f"[FIXED]        "
            f"{final_state.get('fixed')}"
        )

        print(
            f"[APPLIED]      "
            f"{final_state.get('applied')}"
        )

        print(
            f"[BEFORE]       "
            f"{final_state.get('before_screenshot')}"
        )

        print(
            f"[AFTER]        "
            f"{final_state.get('after_screenshot')}"
        )

        print(
            f"[BEFORE HASH]  "
            f"{str(final_state.get('before_hash', ''))[:16]}..."
        )

        print(
            f"[AFTER HASH]   "
            f"{str(final_state.get('after_hash', ''))[:16]}..."
        )

        print(
            f"[GITHUB]       "
            f"{final_state.get('github_result')}"
        )

        if final_state.get(
            "error"
        ):

            print(
                f"[ERROR]        "
                f"{final_state.get('error')}"
            )

        print("=" * 70)

        return final_state

    except Exception as exc:

        print(
            f"[AGENT ERROR] {exc}"
        )

        return {
            **initial_state,

            "status":
                "error",

            "error":
                str(exc),
        }


# ============================================================
# DIRECT TEST
# ============================================================

if __name__ == "__main__":

    asyncio.run(
        run_healing_agent(
            BASE_URL,
            MAX_ATTEMPTS,
        )
    )