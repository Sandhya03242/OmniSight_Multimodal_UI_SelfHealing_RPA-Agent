from __future__ import annotations

import asyncio
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


# ============================================================
# LANGGRAPH STATE
# ============================================================

class HealingState(TypedDict, total=False):
    url: str

    attempt: int
    max_attempts: int

    # Playwright returns screenshot dictionaries:
    #
    # {
    #     "name": "...",
    #     "screenshot": "...png",
    #     "html": "...html",
    #     "viewport": {...}
    # }
    #
    screenshots: list[dict[str, Any]]
    html_files: list[str]

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
    """
    Convert a Playwright screenshot entry into a string path.
    """

    if isinstance(screenshot_data, dict):
        path = screenshot_data.get("screenshot")

        if not path:
            raise ValueError(
                "Screenshot dictionary does not contain "
                "'screenshot' path."
            )

        return str(path)

    if isinstance(screenshot_data, (str, Path)):
        return str(screenshot_data)

    raise TypeError(
        "Screenshot must be a path string or dictionary, "
        f"got {type(screenshot_data).__name__}."
    )


def get_html_path(
    screenshot_data: Any,
    html_files: list[str],
) -> str:
    """
    Get the HTML path associated with a screenshot.

    Prefer the HTML path stored inside the screenshot
    dictionary. Fall back to html_files.
    """

    if isinstance(screenshot_data, dict):

        html_path = screenshot_data.get("html")

        if html_path:
            return str(html_path)

    if html_files:
        return str(html_files[0])

    raise ValueError(
        "No HTML file available."
    )


# ============================================================
# CAPTURE NODE
# ============================================================

async def capture_node(
    state: HealingState,
) -> HealingState:

    print("\n" + "=" * 70)
    print("[GRAPH] CAPTURE")
    print("=" * 70)

    url = state["url"]

    try:

        result = await run_healing_test(url)

        if not isinstance(result, dict):
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

        print(
            f"[PLAYWRIGHT] Screenshots: "
            f"{len(screenshots)}"
        )

        print(
            f"[PLAYWRIGHT] HTML files: "
            f"{len(html_files)}"
        )

        return {
            **state,
            "screenshots": screenshots,
            "html_files": [
                str(path)
                for path in html_files
            ],
            "status": "captured",
            "error": "",
            "retest_failed": False,
        }

    except Exception as exc:

        print(
            f"[CAPTURE ERROR] {exc}"
        )

        return {
            **state,
            "status": "error",
            "error": str(exc),
        }


# ============================================================
# ANALYZE NODE
# ============================================================

async def analyze_node(
    state: HealingState,
) -> HealingState:

    print("\n" + "=" * 70)
    print("[GRAPH] WEEK 4 VLM ANALYSIS")
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
            "status": "error",
            "error": (
                "No screenshots available for analysis."
            ),
        }

    try:

        # ----------------------------------------------------
        # IMPORTANT FIX
        # ----------------------------------------------------
        # Playwright returns a dictionary.
        # Extract the actual screenshot path.
        # ----------------------------------------------------

        screenshot_data = screenshots[0]

        screenshot = get_screenshot_path(
            screenshot_data
        )

        html = get_html_path(
            screenshot_data,
            html_files,
        )

        print(
            f"[GRAPH] Screenshot: {screenshot}"
        )

        print(
            f"[GRAPH] HTML: {html}"
        )

        # ----------------------------------------------------
        # VLM ANALYSIS
        # ----------------------------------------------------

        analysis = await asyncio.to_thread(
            analyze_ui,
            screenshot,
            html,
        )

        if not isinstance(analysis, dict):

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

        # ----------------------------------------------------
        # NORMALIZE ISSUES
        # ----------------------------------------------------

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
                    "description": str(issue)
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

            dashboard_issues.append(
                normalized_issue
            )

        # ----------------------------------------------------
        # OPTIMIZATION INFORMATION
        # ----------------------------------------------------

        optimization = analysis.get(
            "optimization",
            {},
        )

        if not isinstance(
            optimization,
            dict,
        ):

            optimization = {}

        image_stats = optimization.get(
            "image",
            {},
        )

        html_stats = optimization.get(
            "html",
            {},
        )

        print(
            "[WEEK 4] Image optimization:",
            image_stats,
        )

        print(
            "[WEEK 4] HTML reduction:",
            html_stats,
        )

        print(
            f"[VLM] Detected issues: "
            f"{len(dashboard_issues)}"
        )

        # ----------------------------------------------------
        # ISSUE FOUND
        # ----------------------------------------------------

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
                "analysis": analysis,
                "issues": dashboard_issues,
                "status": "issue_found",
                "fixed": False,
                "error": "",
            }

        # ----------------------------------------------------
        # NO ISSUE
        # ----------------------------------------------------

        print(
            "[VLM] No UI issue detected."
        )

        analysis["status"] = (
            "no_issue"
        )

        analysis["issues"] = []

        return {
            **state,
            "analysis": analysis,
            "issues": [],
            "fixed": True,
            "status": "no_issue",
            "error": "",
        }

    except Exception as exc:

        print(
            f"[ANALYSIS ERROR] {exc}"
        )

        return {
            **state,
            "status": "error",
            "error": str(exc),
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

    html_files = state.get(
        "html_files",
        [],
    )

    if not issues:

        return {
            **state,
            "fixes": [],
            "status": "no_fix_required",
        }

    if not screenshots:

        return {
            **state,
            "status": "error",
            "error": (
                "No screenshot available "
                "for fix generation."
            ),
        }

    try:

        screenshot = get_screenshot_path(
            screenshots[0]
        )

        html_path = get_html_path(
            screenshots[0],
            html_files,
        )

    except Exception as exc:

        return {
            **state,
            "status": "error",
            "error": str(exc),
        }

    # --------------------------------------------------------
    # READ SOURCE
    # --------------------------------------------------------

    if not APP_FILE.exists():

        return {
            **state,
            "status": "error",
            "error": (
                f"Source file not found: "
                f"{APP_FILE}"
            ),
        }

    source_code = APP_FILE.read_text(
        encoding="utf-8",
    )

    if not source_code.strip():

        return {
            **state,
            "status": "error",
            "error": (
                "Source file is empty."
            ),
        }

    print(
        f"[SOURCE] Reading: {APP_FILE}"
    )

    print(
        f"[SOURCE] Characters: "
        f"{len(source_code)}"
    )

    fixes: list[
        dict[str, Any]
    ] = []

    # --------------------------------------------------------
    # GENERATE FIX FOR EACH ISSUE
    # --------------------------------------------------------

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
                issue,
                screenshot,
                html_path,
                source_code,
            )

            if not isinstance(
                result,
                dict,
            ):

                print(
                    "[VLM] Invalid fix-generation result."
                )

                continue

            print(
                f"[VLM] Fix generation result: "
                f"{result}"
            )

            generated_fixes = result.get(
                "fixes",
                [],
            )

            if not isinstance(
                generated_fixes,
                list,
            ):

                generated_fixes = []

            # ------------------------------------------------
            # SUPPORT SINGLE FIX FORMAT
            # ------------------------------------------------

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
                            "old": old,
                            "new": new,
                        }
                    ]

            # ------------------------------------------------
            # VALIDATE FIXES
            # ------------------------------------------------

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
                        "old and new are identical."
                    )

                    continue

                if old not in source_code:

                    print(
                        "[VLM] Fix rejected: "
                        "old code not found "
                        "in source."
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

                    print(
                        "[VLM] Fix rejected: "
                        "replacement produced "
                        "no change."
                    )

                    continue

                fixes.append(
                    {
                        "issue": issue,
                        "old": old,
                        "new": new,
                    }
                )

        except Exception as exc:

            print(
                f"[FIX ERROR] {exc}"
            )

    print(
        f"\n[VLM] Valid fixes: "
        f"{len(fixes)}"
    )

    if not fixes:

        return {
            **state,
            "fixes": [],
            "status": "fix_generation_failed",
            "error": (
                "VLM did not produce "
                "a valid source patch."
            ),
        }

    return {
        **state,
        "fixes": fixes,
        "status": "fixes_ready",
        "error": "",
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
            "applied": False,
            "status": "no_fix",
        }

    if not APP_FILE.exists():

        return {
            **state,
            "applied": False,
            "status": "error",
            "error": (
                f"Source file not found: "
                f"{APP_FILE}"
            ),
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

        if old not in source_code:

            print(
                f"[PATCH {index}] "
                "Old code not found."
            )

            continue

        if old == new:

            print(
                f"[PATCH {index}] "
                "Skipped identical patch."
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
            "applied": False,
            "status": "patch_not_applied",
        }

    APP_FILE.write_text(
        source_code,
        encoding="utf-8",
    )

    print(
        f"[PATCH] Applied "
        f"{applied_count} fix(es)."
    )

    return {
        **state,
        "applied": True,
        "status": "fix_applied",
        "error": "",
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

    try:

        # run_healing_test is async.
        result = await run_healing_test(
            state["url"]
        )

        if not isinstance(
            result,
            dict,
        ):

            raise RuntimeError(
                "Playwright retest returned "
                "an invalid result."
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

        print(
            f"[RETEST] Screenshots: "
            f"{len(screenshots)}"
        )

        print(
            f"[RETEST] HTML files: "
            f"{len(html_files)}"
        )

        return {
            **state,
            "screenshots": screenshots,
            "html_files": [
                str(path)
                for path in html_files
            ],
            "retest_failed": False,
            "status": "retested",
            "error": "",
        }

    except Exception as exc:

        print(
            f"[RETEST ERROR] {exc}"
        )

        return {
            **state,
            "retest_failed": True,
            "status": "retest_failed",
            "error": str(exc),
        }


# ============================================================
# VERIFY NODE
# ============================================================

async def verify_node(
    state: HealingState,
) -> HealingState:

    print("\n" + "=" * 70)
    print("[GRAPH] VERIFY HEALING")
    print("=" * 70)

    # --------------------------------------------------------
    # NEVER VERIFY AFTER A FAILED RETEST
    # --------------------------------------------------------

    if state.get(
        "retest_failed",
        False,
    ):

        return {
            **state,
            "fixed": False,
            "status": "verification_failed",
            "error": state.get(
                "error",
                "Retest failed.",
            ),
        }

    screenshots = state.get(
        "screenshots",
        [],
    )

    html_files = state.get(
        "html_files",
        [],
    )

    issues = state.get(
        "issues",
        [],
    )

    if not issues:

        analysis = state.get(
            "analysis",
            {},
        )

        issues = analysis.get(
            "issues",
            [],
        )

    if not screenshots:

        return {
            **state,
            "fixed": False,
            "status": "verification_failed",
            "error": (
                "No screenshot available "
                "for verification."
            ),
        }

    try:

        screenshot = get_screenshot_path(
            screenshots[0]
        )

        html = get_html_path(
            screenshots[0],
            html_files,
        )

    except Exception as exc:

        return {
            **state,
            "fixed": False,
            "status": "verification_failed",
            "error": str(exc),
        }

    # --------------------------------------------------------
    # NO ISSUE
    # --------------------------------------------------------

    if not issues:

        return {
            **state,
            "fixed": True,
            "status": "no_issue",
            "verification": {
                "status": "no_issue",
                "fixed": True,
            },
        }

    try:

        issue = issues[0]

        print(
            f"[VERIFY] Screenshot: "
            f"{screenshot}"
        )

        print(
            f"[VERIFY] HTML: "
            f"{html}"
        )

        verification = await asyncio.to_thread(
            verify_healing,
            screenshot,
            html,
            issue,
        )

        if not isinstance(
            verification,
            dict,
        ):

            verification = {
                "status": "unknown",
                "fixed": bool(
                    verification
                ),
            }

        status = str(
            verification.get(
                "status",
                "",
            )
        ).lower()

        fixed = bool(
            verification.get(
                "fixed",
                False,
            )
        )

        if status in {
            "fixed",
            "passed",
            "success",
            "verified",
        }:

            fixed = True

        # ----------------------------------------------------
        # SOURCE VALIDATION
        # ----------------------------------------------------

        if not APP_FILE.exists():

            fixed = False

            verification[
                "source_check"
            ] = "Source file missing."

        else:

            source = APP_FILE.read_text(
                encoding="utf-8",
            )

            if not source.strip():

                fixed = False

                verification[
                    "source_check"
                ] = "Source file is empty."

            else:

                verification[
                    "source_check"
                ] = (
                    "Source file exists "
                    "and is not empty."
                )

        print(
            f"[VERIFY] Fixed: {fixed}"
        )

        print(
            f"[VERIFY] Result: "
            f"{verification}"
        )

        return {
            **state,
            "verification": verification,
            "fixed": fixed,
            "status": (
                "verified"
                if fixed
                else "verification_failed"
            ),
            "error": "",
        }

    except Exception as exc:

        print(
            f"[VERIFY ERROR] {exc}"
        )

        return {
            **state,
            "fixed": False,
            "status": "verification_failed",
            "error": str(exc),
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
            "status": "not_published",
        }

    # Do not create a PR for a clean application.
    if not state.get(
        "issues",
        [],
    ):

        print(
            "[GITHUB] Skipped because "
            "no issue was detected."
        )

        return {
            **state,
            "status": "no_issue",
        }

    try:

        result = await asyncio.to_thread(
            publish_healing_fix,
        )

        print(
            f"[GITHUB] Result: {result}"
        )

        if isinstance(
            result,
            dict,
        ):

            github_result = result

        else:

            github_result = {
                "status": "published",
                "result": str(result),
            }

        return {
            **state,
            "github_result": github_result,
            "status": "published",
            "error": "",
        }

    except Exception as exc:

        print(
            f"[GITHUB ERROR] {exc}"
        )

        return {
            **state,
            "github_result": {
                "status": "error",
                "error": str(exc),
            },
            "status": "github_failed",
            "error": str(exc),
        }


# ============================================================
# ROUTING FUNCTIONS
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

    issues = state.get(
        "issues",
        [],
    )

    if not issues:

        return "verify"

    return "extract_fix"


def route_after_apply(
    state: HealingState,
) -> str:

    if state.get(
        "applied",
        False,
    ):

        return "retest"

    return "verify"


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

    # --------------------------------------------------------
    # NO ISSUE → END
    # --------------------------------------------------------

    if state.get(
        "status"
    ) == "no_issue":

        return "end"

    # --------------------------------------------------------
    # VERIFIED → GITHUB
    # --------------------------------------------------------

    if state.get(
        "fixed",
        False,
    ) and state.get(
        "issues",
        [],
    ):

        return "publish"

    # --------------------------------------------------------
    # RETRY
    # --------------------------------------------------------

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

        "attempt": next_attempt,

        "status": "retrying",

        "screenshots": [],

        "html_files": [],

        "analysis": {},

        "issues": [],

        "fixes": [],

        "applied": False,

        "retest_failed": False,

        "fixed": False,

        "verification": {},

        "error": "",
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
    # CAPTURE → ANALYZE
    # --------------------------------------------------------

    graph.add_conditional_edges(
        "capture",
        route_after_capture,
        {
            "analyze": "analyze",
            "end": END,
        },
    )

    # --------------------------------------------------------
    # ANALYZE → FIX / VERIFY
    # --------------------------------------------------------

    graph.add_conditional_edges(
        "analyze",
        route_after_analyze,
        {
            "extract_fix": "extract_fix",
            "verify": "verify",
            "end": END,
        },
    )

    # --------------------------------------------------------
    # EXTRACT → APPLY
    # --------------------------------------------------------

    graph.add_edge(
        "extract_fix",
        "apply_fix",
    )

    # --------------------------------------------------------
    # APPLY → RETEST / VERIFY
    # --------------------------------------------------------

    graph.add_conditional_edges(
        "apply_fix",
        route_after_apply,
        {
            "retest": "retest",
            "verify": "verify",
        },
    )

    # --------------------------------------------------------
    # RETEST → VERIFY / RETRY
    # --------------------------------------------------------

    graph.add_conditional_edges(
        "retest",
        route_after_retest,
        {
            "verify": "verify",
            "retry": "retry",
        },
    )

    # --------------------------------------------------------
    # VERIFY → PUBLISH / RETRY / END
    # --------------------------------------------------------

    graph.add_conditional_edges(
        "verify",
        route_after_verify,
        {
            "publish": "publish",
            "retry": "retry",
            "end": END,
        },
    )

    # --------------------------------------------------------
    # RETRY → FRESH CAPTURE
    # --------------------------------------------------------

    graph.add_edge(
        "retry",
        "capture",
    )

    # --------------------------------------------------------
    # PUBLISH → END
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
    print("OMNISIGHT WEEK 4 SELF-HEALING AGENT")
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
        "url": url,

        "attempt": 1,

        "max_attempts": max_attempts,

        "screenshots": [],

        "html_files": [],

        "analysis": {},

        "issues": [],

        "fixes": [],

        "applied": False,

        "retest_failed": False,

        "fixed": False,

        "verification": {},

        "github_result": {},

        "status": "starting",

        "error": "",
    }

    try:

        final_state = await healing_graph.ainvoke(
            initial_state,
            config={
                "recursion_limit": 50,
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
            "status": "error",
            "error": str(exc),
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