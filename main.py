from __future__ import annotations

from typing import Any

from fastapi import FastAPI, HTTPException

from backend.actions.engine import extract_fixes
from backend.browser.navigator import run_browser_flow
from backend.models.schemas import (
    NavigationRequest,
    VisionRequest,
    WebhookRequest,
)
from backend.vision.analyzer import analyze_ui


# ============================================================
# FASTAPI APPLICATION
# ============================================================

app = FastAPI(
    title="OmniSight",
    description=(
        "OmniSight - Browser Automation, "
        "VLM UI Analysis and Action Engine"
    ),
    version="2.0.0",
)


# ============================================================
# ROOT
# ============================================================

@app.get("/")
async def root() -> dict[str, str]:

    return {
        "project": "OmniSight",
        "week": "Week 2",
        "status": "running",
    }


# ============================================================
# HEALTH CHECK
# ============================================================

@app.get("/health")
async def health() -> dict[str, str]:

    return {
        "status": "healthy",
    }


# ============================================================
# BROWSER AUTOMATION
# ============================================================

@app.post("/navigation/run")
async def navigation_run(
    request: NavigationRequest,
) -> dict[str, Any]:

    result = await run_browser_flow(
        request.url
    )

    if result["status"] == "failed":

        raise HTTPException(
            status_code=500,
            detail=result,
        )

    return {
        "status": "success",
        "message": "Browser automation completed",
        "result": result,
    }


# ============================================================
# CI/CD WEBHOOK
# ============================================================

@app.post("/webhook")
async def webhook(
    request: WebhookRequest,
) -> dict[str, Any]:

    if request.event != "build.completed":

        return {
            "status": "ignored",
            "message": (
                f"Event '{request.event}' "
                "does not trigger testing"
            ),
        }

    result = await run_browser_flow(
        request.url
    )

    if result["status"] == "failed":

        raise HTTPException(
            status_code=500,
            detail=result,
        )

    return {
        "status": "success",
        "message": (
            "Build event received and "
            "browser testing completed"
        ),
        "result": result,
    }


# ============================================================
# VISION ANALYSIS
# ============================================================

@app.post("/vision/analyze")
async def vision_analyze(
    request: VisionRequest,
) -> dict[str, Any]:

    try:

        result = analyze_ui(
            screenshot_path=request.screenshot_path,
            html_path=request.html_path,
        )

        return result

    except FileNotFoundError as exc:

        raise HTTPException(
            status_code=404,
            detail=str(exc),
        ) from exc

    except Exception as exc:

        raise HTTPException(
            status_code=500,
            detail={
                "status": "failed",
                "error": str(exc),
            },
        ) from exc


# ============================================================
# ACTION ENGINE
# ============================================================

@app.post("/actions/extract-fixes")
async def actions_extract_fixes(
    request: VisionRequest,
) -> dict[str, Any]:

    try:

        # --------------------------------------------
        # Run VLM analysis
        # --------------------------------------------

        vlm_result = analyze_ui(
            screenshot_path=request.screenshot_path,
            html_path=request.html_path,
        )

        # --------------------------------------------
        # Extract CSS / React fixes
        # --------------------------------------------

        action_result = extract_fixes(
            vlm_result
        )

        return {
            "status": "success",
            "vision": vlm_result,
            "actions": action_result,
        }

    except FileNotFoundError as exc:

        raise HTTPException(
            status_code=404,
            detail=str(exc),
        ) from exc

    except Exception as exc:

        raise HTTPException(
            status_code=500,
            detail={
                "status": "failed",
                "error": str(exc),
            },
        ) from exc


# ============================================================
# RUN SERVER
# ============================================================

if __name__ == "__main__":

    import uvicorn

    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
    )