from __future__ import annotations

from typing import Any

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from backend.agent.graph import run_healing_agent


# ============================================================
# FASTAPI APPLICATION
# ============================================================

app = FastAPI(
    title="OmniSight",
    description="Multimodal UI Self-Healing & RPA Agent",
    version="3.0.0",
)


# ============================================================
# REQUEST MODELS
# ============================================================

class HealingRequest(BaseModel):
    url: str = Field(
        default="http://localhost:5173",
        description="URL of the application to test",
    )

    max_attempts: int = Field(
        default=2,
        ge=1,
        le=5,
        description="Maximum number of healing attempts",
    )


class WebhookRequest(BaseModel):
    event: str = "build"
    status: str = "success"
    repository: str | None = None
    branch: str = "main"
    commit: str | None = None
    url: str = "http://localhost:5173"


# ============================================================
# ROOT
# ============================================================

@app.get("/")
async def root() -> dict[str, Any]:
    return {
        "name": "OmniSight",
        "description": "Multimodal UI Self-Healing & RPA Agent",
        "version": "3.0.0",
        "status": "running",
        "endpoints": {
            "health": "GET /health",
            "navigation": "POST /navigation/run",
            "vision": "POST /vision/analyze",
            "actions": "POST /actions/extract-fixes",
            "webhook": "POST /webhook",
            "healing": "POST /healing/run",
        },
    }


# ============================================================
# HEALTH CHECK
# ============================================================

@app.get("/health")
async def health() -> dict[str, Any]:
    return {
        "status": "healthy",
        "service": "OmniSight",
        "version": "3.0.0",
    }


# ============================================================
# WEEK 1 - BROWSER NAVIGATION
# ============================================================

@app.post("/navigation/run")
async def navigation_run(
    url: str = "http://localhost:5173",
) -> dict[str, Any]:

    try:
        from backend.browser.navigator import run_browser_flow

        result = await run_browser_flow(url)

        return {
            "status": "success",
            "message": "Browser navigation completed.",
            "result": result,
        }

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail={
                "status": "failed",
                "error": str(exc),
            },
        )


# ============================================================
# WEEK 2 - VISION ANALYSIS
# ============================================================

@app.post("/vision/analyze")
async def vision_analyze(
    screenshot: str,
    html: str | None = None,
) -> dict[str, Any]:

    try:
        from backend.vision.vision_analyzer import analyze_ui

        result = await analyze_ui(
            screenshot=screenshot,
            html=html or "",
        )

        return {
            "status": "success",
            "result": result,
        }

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail={
                "status": "failed",
                "error": str(exc),
            },
        )


# ============================================================
# WEEK 2 - ACTION ENGINE
# ============================================================

@app.post("/actions/extract-fixes")
async def extract_fixes(
    analysis: dict[str, Any],
) -> dict[str, Any]:

    try:
        from backend.actions.action_engine import extract_fixes

        result = extract_fixes(analysis)

        return {
            "status": "success",
            "result": result,
        }

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail={
                "status": "failed",
                "error": str(exc),
            },
        )


# ============================================================
# WEEK 2 - CI/CD WEBHOOK
# ============================================================

@app.post("/webhook")
async def webhook(
    payload: WebhookRequest,
) -> dict[str, Any]:

    print("\n" + "=" * 60)
    print("[WEBHOOK] CI/CD EVENT RECEIVED")
    print("=" * 60)

    print(f"Event      : {payload.event}")
    print(f"Status     : {payload.status}")
    print(f"Repository : {payload.repository}")
    print(f"Branch     : {payload.branch}")
    print(f"Commit     : {payload.commit}")

    return {
        "status": "received",
        "event": payload.event,
        "repository": payload.repository,
        "branch": payload.branch,
        "commit": payload.commit,
        "message": "Webhook received successfully.",
    }


# ============================================================
# WEEK 3 - SELF HEALING
# ============================================================

@app.post("/healing/run")
async def healing_run(
    request: HealingRequest,
) -> dict[str, Any]:

    print("\n" + "=" * 70)
    print("OMNISIGHT WEEK 3 HEALING API")
    print("=" * 70)

    print(f"URL          : {request.url}")
    print(f"Max attempts : {request.max_attempts}")

    try:
        result = await run_healing_agent(
            url=request.url,
            max_attempts=request.max_attempts,
        )

        return {
            "status": result.get("status"),
            "fixed": result.get("fixed", False),
            "attempts": result.get("attempt", 1),
            "url": result.get("url"),
            "screenshots": result.get("screenshots", []),
            "html_files": result.get("html_files", []),
            "analysis": result.get("analysis", {}),
            "fixes": result.get("fixes", []),
            "verification": result.get(
                "verification",
                {},
            ),
            "github": result.get(
                "github_result",
                {},
            ),
            "error": result.get(
                "error",
                "",
            ),
        }

    except Exception as exc:
        print(
            f"[HEALING API] Error: {exc}"
        )

        raise HTTPException(
            status_code=500,
            detail={
                "status": "failed",
                "error": str(exc),
            },
        )


# ============================================================
# WEEK 3 - SIMPLE STATUS ENDPOINT
# ============================================================

@app.get("/healing/status")
async def healing_status() -> dict[str, Any]:
    return {
        "status": "ready",
        "module": "Week 3 Self-Healing Agent",
        "pipeline": [
            "Playwright capture",
            "UI analysis",
            "Fix extraction",
            "Source modification",
            "Fresh Playwright retest",
            "UI verification",
            "GitHub publish",
        ],
    }


# ============================================================
# APPLICATION STARTUP
# ============================================================

@app.on_event("startup")
async def startup_event() -> None:
    print("\n")
    print("=" * 70)
    print("OMNISIGHT API")
    print("=" * 70)
    print("Version : 3.0.0")
    print("Status  : Running")
    print("URL     : http://127.0.0.1:8000")
    print("Docs    : http://127.0.0.1:8000/docs")
    print("=" * 70)