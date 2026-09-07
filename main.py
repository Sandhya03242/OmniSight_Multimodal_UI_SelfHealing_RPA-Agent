from __future__ import annotations

import asyncio
from pathlib import Path
from typing import Any

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from backend.browser.navigator import run_healing_test
from backend.vision.analyzer import (
    analyze_ui,
    generate_healing_fix,
)
from backend.agent.graph import run_healing_agent


# ============================================================
# CONFIGURATION
# ============================================================

APP_VERSION = "4.0.0"

MOCK_STORE_URL = "http://localhost:5173"
DASHBOARD_URL = "http://localhost:5174"
API_URL = "http://localhost:8000"

APP_FILE = Path("demo-store/src/App.jsx")

SCREENSHOTS_DIR = Path("screenshots")
OUTPUTS_DIR = Path("outputs")

SCREENSHOTS_DIR.mkdir(
    parents=True,
    exist_ok=True,
)

OUTPUTS_DIR.mkdir(
    parents=True,
    exist_ok=True,
)


# ============================================================
# FASTAPI APPLICATION
# ============================================================

app = FastAPI(
    title="OmniSight API",
    description="Multimodal UI Self-Healing & RPA Agent",
    version=APP_VERSION,
)


# ============================================================
# STATIC FILES
# ============================================================

# This allows the React dashboard to display:
#
# http://localhost:8000/screenshots/example.png
#
app.mount(
    "/screenshots",
    StaticFiles(
        directory=str(SCREENSHOTS_DIR)
    ),
    name="screenshots",
)


# ============================================================
# CORS
# ============================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        MOCK_STORE_URL,
        DASHBOARD_URL,
        "http://localhost:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# IN-MEMORY STATE
# ============================================================

LATEST_HEALING_RESULT: dict[str, Any] = {
    "status": "not_started",
    "attempt": 0,

    "issues": [],
    "fixes": [],

    "screenshots": [],
    "html_files": [],

    "before_screenshot": None,
    "after_screenshot": None,

    "analysis": {},
    "verification": {},
    "github_result": {},

    "applied": False,
    "fixed": False,

    "error": None,
}


# ============================================================
# REQUEST MODELS
# ============================================================


class HealingRequest(BaseModel):
    url: str = MOCK_STORE_URL
    max_attempts: int = 2


class WebhookRequest(BaseModel):
    event: str = "build"
    url: str = MOCK_STORE_URL
    branch: str = "main"


class VisionRequest(BaseModel):
    screenshot_path: str
    html_path: str


class FixRequest(BaseModel):
    screenshot_path: str
    html_path: str


class DashboardActionRequest(BaseModel):
    issue_id: str
    pr_number: int | None = None
    comment: str | None = None


# ============================================================
# HELPERS
# ============================================================


def normalize_screenshot_path(
    path: Any,
) -> str | None:

    if not path:
        return None

    return str(path)


def normalize_paths(
    items: Any,
) -> list[str]:

    if not items:
        return []

    result: list[str] = []

    for item in items:

        if isinstance(item, dict):

            screenshot = (
                item.get("screenshot")
                or item.get("path")
                or item.get("file")
            )

            if screenshot:
                result.append(
                    str(screenshot)
                )

        else:

            result.append(
                str(item)
            )

    return result


def normalize_issues(
    issues: Any,
    screenshot_path: str,
) -> list[dict[str, Any]]:

    if not issues:
        return []

    normalized: list[
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

            item = dict(issue)

        else:

            item = {
                "description": str(issue)
            }

        item.setdefault(
            "id",
            str(index),
        )

        item.setdefault(
            "screenshot",
            screenshot_path,
        )

        normalized.append(
            item
        )

    return normalized


def get_first_screenshot(
    screenshots: Any,
) -> str | None:

    if not screenshots:
        return None

    first = screenshots[0]

    if isinstance(
        first,
        dict,
    ):

        return (
            first.get("screenshot")
            or first.get("path")
            or first.get("file")
        )

    return str(first)


def get_last_screenshot(
    screenshots: Any,
) -> str | None:

    if not screenshots:
        return None

    last = screenshots[-1]

    if isinstance(
        last,
        dict,
    ):

        return (
            last.get("screenshot")
            or last.get("path")
            or last.get("file")
        )

    return str(last)


# ============================================================
# ROOT
# ============================================================


@app.get("/")
async def root():

    return {
        "project": "OmniSight",
        "description": (
            "Multimodal UI Self-Healing & RPA Agent"
        ),
        "version": APP_VERSION,
        "status": "running",
        "services": {
            "mock_store": MOCK_STORE_URL,
            "dashboard": DASHBOARD_URL,
            "api": API_URL,
            "docs": f"{API_URL}/docs",
            "screenshots": (
                f"{API_URL}/screenshots"
            ),
        },
    }


# ============================================================
# HEALTH
# ============================================================


@app.get("/health")
async def health():

    return {
        "status": "healthy",
        "service": "OmniSight FastAPI",
        "version": APP_VERSION,
    }


# ============================================================
# WEEK 1
# PLAYWRIGHT NAVIGATION
# ============================================================


@app.post("/navigation/run")
async def navigation_run(
    request: HealingRequest,
):

    try:

        print("\n" + "=" * 70)
        print(
            "[FASTAPI] Starting browser navigation..."
        )
        print("=" * 70)

        result = await run_healing_test(
            request.url
        )

        return {
            "status": "success",
            "url": request.url,
            "result": result,
        }

    except Exception as exc:

        print(
            f"[NAVIGATION ERROR] {exc}"
        )

        return {
            "status": "error",
            "url": request.url,
            "error": str(exc),
        }


# ============================================================
# WEEK 2
# VISION ANALYSIS
# ============================================================


@app.post("/vision/analyze")
async def vision_analyze(
    request: VisionRequest,
):

    try:

        print("\n" + "=" * 70)
        print(
            "[FASTAPI] Starting VLM analysis..."
        )
        print("=" * 70)

        result = await asyncio.to_thread(
            analyze_ui,
            request.screenshot_path,
            request.html_path,
        )

        return {
            "status": "success",
            "result": result,
        }

    except Exception as exc:

        print(
            f"[VISION ERROR] {exc}"
        )

        return {
            "status": "error",
            "error": str(exc),
        }


# ============================================================
# WEEK 2
# AUTOMATIC FIX EXTRACTION
# ============================================================


@app.post("/actions/extract-fixes")
async def extract_fixes(
    request: FixRequest,
):

    try:

        print("\n" + "=" * 70)
        print(
            "[FASTAPI] AUTOMATIC FIX GENERATION"
        )
        print("=" * 70)

        # ----------------------------------------------------
        # STEP 1
        # VERIFY SOURCE
        # ----------------------------------------------------

        if not APP_FILE.exists():

            raise FileNotFoundError(
                f"Source file not found: {APP_FILE}"
            )

        print(
            f"[SOURCE] Reading: {APP_FILE}"
        )

        source_code = APP_FILE.read_text(
            encoding="utf-8"
        )

        if not source_code.strip():

            raise ValueError(
                f"Source file is empty: {APP_FILE}"
            )

        print(
            f"[SOURCE] Characters: {len(source_code)}"
        )

        # ----------------------------------------------------
        # STEP 2
        # VLM ANALYSIS
        # ----------------------------------------------------

        print(
            "[VLM] Analyzing screenshot + HTML..."
        )

        analysis = await asyncio.to_thread(
            analyze_ui,
            request.screenshot_path,
            request.html_path,
        )

        if not isinstance(
            analysis,
            dict,
        ):

            raise ValueError(
                "VLM analysis returned invalid response."
            )

        issues = normalize_issues(
            analysis.get(
                "issues",
                [],
            ),
            request.screenshot_path,
        )

        print(
            f"[VLM] Issues detected: {len(issues)}"
        )

        # ----------------------------------------------------
        # STEP 3
        # NO ISSUE
        # ----------------------------------------------------

        if not issues:

            return {
                "status": "success",
                "result": {
                    "status": "no_issue",
                    "message": (
                        "VLM did not detect any UI issue."
                    ),
                    "issues": [],
                    "fixes": [],
                    "source_file": str(
                        APP_FILE
                    ),
                    "analysis": analysis,
                },
            }

        # ----------------------------------------------------
        # STEP 4
        # GENERATE FIXES
        # ----------------------------------------------------

        all_fixes: list[
            dict[str, Any]
        ] = []

        for index, issue in enumerate(
            issues,
            start=1,
        ):

            print(
                f"[FIX] Generating fix "
                f"{index}/{len(issues)}..."
            )

            # IMPORTANT:
            #
            # Current generate_healing_fix()
            # accepts:
            #
            #   screenshot
            #   issue
            #   source_code
            #
            # NOT four arguments.
            #

            fix_result = await asyncio.to_thread(
                generate_healing_fix,
                request.screenshot_path,
                issue,
                source_code,
            )

            if not isinstance(
                fix_result,
                dict,
            ):

                print(
                    "[FIX] Invalid fix response."
                )

                continue

            # ------------------------------------------------
            # MULTIPLE FIXES
            # ------------------------------------------------

            generated_fixes = (
                fix_result.get(
                    "fixes",
                    [],
                )
            )

            if isinstance(
                generated_fixes,
                list,
            ):

                for fix in generated_fixes:

                    if not isinstance(
                        fix,
                        dict,
                    ):
                        continue

                    old = str(
                        fix.get(
                            "old",
                            "",
                        )
                    )

                    new = str(
                        fix.get(
                            "new",
                            "",
                        )
                    )

                    if (
                        old
                        and new
                        and old != new
                        and old in source_code
                    ):

                        all_fixes.append(
                            {
                                "issue": issue,
                                "old": old,
                                "new": new,
                            }
                        )

            # ------------------------------------------------
            # SINGLE FIX
            # ------------------------------------------------

            else:

                old = str(
                    fix_result.get(
                        "old",
                        "",
                    )
                )

                new = str(
                    fix_result.get(
                        "new",
                        "",
                    )
                )

                if (
                    old
                    and new
                    and old != new
                    and old in source_code
                ):

                    all_fixes.append(
                        {
                            "issue": issue,
                            "old": old,
                            "new": new,
                        }
                    )

        # ----------------------------------------------------
        # STEP 5
        # RETURN
        # ----------------------------------------------------

        print(
            f"[FIX] Valid fixes generated: "
            f"{len(all_fixes)}"
        )

        return {
            "status": "success",
            "result": {
                "status": (
                    "fix_generated"
                    if all_fixes
                    else "fix_generation_failed"
                ),
                "source_file": str(
                    APP_FILE
                ),
                "issues": issues,
                "fixes": all_fixes,
                "analysis": analysis,
            },
        }

    except Exception as exc:

        print(
            f"[FIX ERROR] {exc}"
        )

        return {
            "status": "error",
            "error": str(exc),
        }


# ============================================================
# CI/CD WEBHOOK
# ============================================================


@app.post("/webhook")
async def webhook(
    request: WebhookRequest,
):

    print("\n" + "=" * 70)
    print(
        "[WEBHOOK] CI/CD EVENT RECEIVED"
    )
    print("=" * 70)

    print(
        f"[EVENT]  {request.event}"
    )

    print(
        f"[URL]    {request.url}"
    )

    print(
        f"[BRANCH] {request.branch}"
    )

    return {
        "status": "received",
        "event": request.event,
        "url": request.url,
        "branch": request.branch,
        "message": (
            "OmniSight webhook received successfully."
        ),
    }


# ============================================================
# COMPLETE SELF-HEALING PIPELINE
# ============================================================


@app.post("/healing/run")
async def healing_run(
    request: HealingRequest,
):

    global LATEST_HEALING_RESULT

    print("\n" + "=" * 70)
    print(
        "OMNISIGHT HEALING RUN"
    )
    print("=" * 70)

    try:

        # ----------------------------------------------------
        # RESET STATE
        # ----------------------------------------------------

        LATEST_HEALING_RESULT = {
            "status": "running",
            "attempt": 0,

            "issues": [],
            "fixes": [],

            "screenshots": [],
            "html_files": [],

            "before_screenshot": None,
            "after_screenshot": None,

            "analysis": {},
            "verification": {},
            "github_result": {},

            "applied": False,
            "fixed": False,

            "error": None,
        }

        # ----------------------------------------------------
        # RUN LANGGRAPH AGENT
        # ----------------------------------------------------

        result = await run_healing_agent(
            url=request.url,
            max_attempts=request.max_attempts,
        )

        if not isinstance(
            result,
            dict,
        ):

            raise ValueError(
                "Healing agent returned invalid result."
            )

        # ----------------------------------------------------
        # NORMALIZE RESULT
        # ----------------------------------------------------

        screenshots = result.get(
            "screenshots",
            [],
        )

        screenshots = (
            screenshots
            if isinstance(
                screenshots,
                list,
            )
            else []
        )

        html_files = result.get(
            "html_files",
            [],
        )

        html_files = (
            html_files
            if isinstance(
                html_files,
                list,
            )
            else []
        )

        issues = result.get(
            "issues",
            [],
        )

        fixes = result.get(
            "fixes",
            [],
        )

        # ----------------------------------------------------
        # BEFORE SCREENSHOT
        # ----------------------------------------------------

        before_screenshot = result.get(
            "before_screenshot"
        )

        if not before_screenshot:
            before_screenshot = (
                get_first_screenshot(
                    screenshots
                )
            )

        # ----------------------------------------------------
        # AFTER SCREENSHOT
        # ----------------------------------------------------

        after_screenshot = result.get(
            "after_screenshot"
        )

        if not after_screenshot:

            if len(screenshots) >= 2:

                after_screenshot = (
                    get_last_screenshot(
                        screenshots
                    )
                )

            elif result.get(
                "fixed",
                False,
            ):

                after_screenshot = (
                    get_last_screenshot(
                        screenshots
                    )
                )

        # ----------------------------------------------------
        # STORE FINAL STATE
        # ----------------------------------------------------

        LATEST_HEALING_RESULT = {
            **result,

            "status": result.get(
                "status",
                "completed",
            ),

            "issues": issues,
            "fixes": fixes,

            "screenshots": screenshots,
            "html_files": html_files,

            "before_screenshot":
                before_screenshot,

            "after_screenshot":
                after_screenshot,

            "analysis": result.get(
                "analysis",
                {},
            ),

            "verification": result.get(
                "verification",
                {},
            ),

            "github_result": result.get(
                "github_result",
                {},
            ),

            "applied": result.get(
                "applied",
                False,
            ),

            "fixed": result.get(
                "fixed",
                False,
            ),

            "error": result.get(
                "error"
            ),
        }

        print(
            "\n[HEALING] Pipeline completed."
        )

        print(
            f"[HEALING] Issues: "
            f"{len(issues)}"
        )

        print(
            f"[HEALING] Fixes: "
            f"{len(fixes)}"
        )

        print(
            f"[HEALING] Fixed: "
            f"{result.get('fixed', False)}"
        )

        print(
            f"[HEALING] Before: "
            f"{before_screenshot}"
        )

        print(
            f"[HEALING] After: "
            f"{after_screenshot}"
        )

        return {
            "status": "success",
            "result": LATEST_HEALING_RESULT,
        }

    except Exception as exc:

        print(
            f"[HEALING ERROR] {exc}"
        )

        LATEST_HEALING_RESULT = {
            **LATEST_HEALING_RESULT,
            "status": "error",
            "error": str(exc),
        }

        return {
            "status": "error",
            "error": str(exc),
            "result": LATEST_HEALING_RESULT,
        }


# ============================================================
# HEALING STATUS
# ============================================================


@app.get("/healing/status")
async def healing_status():

    return {
        "status": LATEST_HEALING_RESULT.get(
            "status",
            "not_started",
        ),

        "attempt": LATEST_HEALING_RESULT.get(
            "attempt",
            0,
        ),

        "fixed": LATEST_HEALING_RESULT.get(
            "fixed",
            False,
        ),

        "applied": LATEST_HEALING_RESULT.get(
            "applied",
            False,
        ),

        "before_screenshot":
            LATEST_HEALING_RESULT.get(
                "before_screenshot"
            ),

        "after_screenshot":
            LATEST_HEALING_RESULT.get(
                "after_screenshot"
            ),

        "error": LATEST_HEALING_RESULT.get(
            "error",
            "",
        ),
    }


# ============================================================
# OPTIMIZATION STATUS
# ============================================================


@app.get("/optimization/status")
async def optimization_status():

    analysis = LATEST_HEALING_RESULT.get(
        "analysis",
        {},
    )

    if not isinstance(
        analysis,
        dict,
    ):
        analysis = {}

    optimization = analysis.get(
        "optimization",
        {},
    )

    if not isinstance(
        optimization,
        dict,
    ):
        optimization = {}

    return {
        "image_optimization": optimization.get(
            "image",
            {},
        ),

        "html_reduction": optimization.get(
            "html",
            {},
        ),

        "enabled": True,
    }


# ============================================================
# DASHBOARD ISSUES
# ============================================================


@app.get("/dashboard/issues")
async def dashboard_issues():

    analysis = LATEST_HEALING_RESULT.get(
        "analysis",
        {},
    )

    if not isinstance(
        analysis,
        dict,
    ):
        analysis = {}

    issues = LATEST_HEALING_RESULT.get(
        "issues",
        [],
    )

    if not issues:

        issues = analysis.get(
            "issues",
            [],
        )

    if not isinstance(
        issues,
        list,
    ):
        issues = []

    fixes = LATEST_HEALING_RESULT.get(
        "fixes",
        [],
    )

    if not isinstance(
        fixes,
        list,
    ):
        fixes = []

    github_result = LATEST_HEALING_RESULT.get(
        "github_result",
        {},
    )

    before_screenshot = (
        LATEST_HEALING_RESULT.get(
            "before_screenshot"
        )
    )

    after_screenshot = (
        LATEST_HEALING_RESULT.get(
            "after_screenshot"
        )
    )

    dashboard_items = []

    for index, issue in enumerate(
        issues,
        start=1,
    ):

        if not isinstance(
            issue,
            dict,
        ):

            issue = {
                "description": str(issue)
            }

        item = dict(issue)

        item.setdefault(
            "id",
            str(index),
        )

        item.setdefault(
            "status",
            "pending",
        )

        # ----------------------------------------------------
        # SCREENSHOTS
        # ----------------------------------------------------

        item["before_screenshot"] = (
            before_screenshot
            or item.get(
                "before_screenshot"
            )
            or item.get(
                "screenshot"
            )
        )

        item["after_screenshot"] = (
            after_screenshot
            or item.get(
                "after_screenshot"
            )
        )

        # Keep original screenshot
        # for backward compatibility.

        if not item.get(
            "screenshot"
        ):

            item["screenshot"] = (
                item["before_screenshot"]
            )

        # ----------------------------------------------------
        # MATCH FIX
        # ----------------------------------------------------

        matching_fix = None

        for fix in fixes:

            if not isinstance(
                fix,
                dict,
            ):
                continue

            fix_issue = fix.get(
                "issue",
                {},
            )

            if (
                fix_issue == issue
                or fix_issue.get(
                    "description"
                )
                == issue.get(
                    "description"
                )
            ):

                matching_fix = fix
                break

        if matching_fix:

            item["fix"] = {
                "old": matching_fix.get(
                    "old",
                    "",
                ),

                "new": matching_fix.get(
                    "new",
                    "",
                ),
            }

        # ----------------------------------------------------
        # GITHUB
        # ----------------------------------------------------

        if isinstance(
            github_result,
            dict,
        ):

            item["pr_number"] = (
                github_result.get(
                    "pr_number"
                )
            )

            item["pr_url"] = (
                github_result.get(
                    "pr_url"
                )
            )

        dashboard_items.append(
            item
        )

    return {
        "status": "success",

        "count": len(
            dashboard_items
        ),

        "issues": dashboard_items,

        "healing_status":
            LATEST_HEALING_RESULT.get(
                "status"
            ),

        "before_screenshot":
            before_screenshot,

        "after_screenshot":
            after_screenshot,

        "fixes": fixes,
    }


# ============================================================
# DASHBOARD STATUS
# ============================================================


@app.get("/dashboard/status")
async def dashboard_status():

    analysis = LATEST_HEALING_RESULT.get(
        "analysis",
        {},
    )

    if not isinstance(
        analysis,
        dict,
    ):
        analysis = {}

    issues = LATEST_HEALING_RESULT.get(
        "issues",
        [],
    )

    if not issues:

        issues = analysis.get(
            "issues",
            [],
        )

    if not isinstance(
        issues,
        list,
    ):
        issues = []

    fixes = LATEST_HEALING_RESULT.get(
        "fixes",
        [],
    )

    if not isinstance(
        fixes,
        list,
    ):
        fixes = []

    github_result = LATEST_HEALING_RESULT.get(
        "github_result",
        {},
    )

    if not isinstance(
        github_result,
        dict,
    ):
        github_result = {}

    return {
        "project": "OmniSight",

        "version": APP_VERSION,

        "healing_status":
            LATEST_HEALING_RESULT.get(
                "status",
                "not_started",
            ),

        "attempt":
            LATEST_HEALING_RESULT.get(
                "attempt",
                0,
            ),

        "issues_detected":
            len(issues),

        "fixes_generated":
            len(fixes),

        "issues":
            issues,

        "fixes":
            fixes,

        "fixed":
            LATEST_HEALING_RESULT.get(
                "fixed",
                False,
            ),

        "applied":
            LATEST_HEALING_RESULT.get(
                "applied",
                False,
            ),

        # ----------------------------------------------------
        # IMPORTANT FOR DASHBOARD
        # ----------------------------------------------------

        "before_screenshot":
            LATEST_HEALING_RESULT.get(
                "before_screenshot"
            ),

        "after_screenshot":
            LATEST_HEALING_RESULT.get(
                "after_screenshot"
            ),

        "screenshots":
            LATEST_HEALING_RESULT.get(
                "screenshots",
                [],
            ),

        "html_files":
            LATEST_HEALING_RESULT.get(
                "html_files",
                [],
            ),

        "analysis":
            analysis,

        "verification":
            LATEST_HEALING_RESULT.get(
                "verification",
                {},
            ),

        "github":
            github_result,

        "error":
            LATEST_HEALING_RESULT.get(
                "error"
            ),
    }


# ============================================================
# QA APPROVE
# ============================================================


@app.post("/github/pr/approve")
async def approve_pr(
    request: DashboardActionRequest,
):

    global LATEST_HEALING_RESULT

    issues = LATEST_HEALING_RESULT.get(
        "issues",
        [],
    )

    issue_id = request.issue_id

    for issue in issues:

        if not isinstance(
            issue,
            dict,
        ):
            continue

        if str(
            issue.get(
                "id",
                "",
            )
        ) == str(issue_id):

            issue["status"] = "approved"

            issue[
                "qa_decision"
            ] = "approved"

            if request.comment:

                issue[
                    "qa_comment"
                ] = request.comment

    return {
        "status": "approved",

        "issue_id": issue_id,

        "pr_number":
            request.pr_number,

        "message": (
            "QA approval recorded successfully."
        ),
    }


# ============================================================
# QA REJECT
# ============================================================


@app.post("/github/pr/reject")
async def reject_pr(
    request: DashboardActionRequest,
):

    global LATEST_HEALING_RESULT

    issues = LATEST_HEALING_RESULT.get(
        "issues",
        [],
    )

    issue_id = request.issue_id

    for issue in issues:

        if not isinstance(
            issue,
            dict,
        ):
            continue

        if str(
            issue.get(
                "id",
                "",
            )
        ) == str(issue_id):

            issue["status"] = "rejected"

            issue[
                "qa_decision"
            ] = "rejected"

            if request.comment:

                issue[
                    "qa_comment"
                ] = request.comment

    return {
        "status": "rejected",

        "issue_id": issue_id,

        "pr_number":
            request.pr_number,

        "message": (
            "QA rejection recorded successfully."
        ),
    }


# ============================================================
# STARTUP
# ============================================================


@app.on_event("startup")
async def startup_event():

    print("\n")

    print("=" * 70)

    print(
        "OMNISIGHT FASTAPI SERVER"
    )

    print("=" * 70)

    print(
        f"[PROJECT]   OmniSight"
    )

    print(
        f"[VERSION]   {APP_VERSION}"
    )

    print(
        f"[STORE]     {MOCK_STORE_URL}"
    )

    print(
        f"[DASHBOARD] {DASHBOARD_URL}"
    )

    print(
        f"[API]       {API_URL}"
    )

    print(
        f"[DOCS]      {API_URL}/docs"
    )

    print(
        f"[SCREENSHOT] {API_URL}/screenshots"
    )

    print(
        f"[SOURCE]    {APP_FILE}"
    )

    print("=" * 70)


# ============================================================
# DIRECT RUN
# ============================================================


if __name__ == "__main__":

    import uvicorn

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )