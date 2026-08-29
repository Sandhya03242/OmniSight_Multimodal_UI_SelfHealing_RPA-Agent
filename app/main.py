from pathlib import Path

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from .action_engine import (
    generate_fix_file,
    process_analysis,
)

from .playwright_bot import (
    capture_page,
    capture_responsive_pages,
    run_checkout_flow,
)

from .vision_analyzer import analyze_ui
from .self_healing import self_healing_loop


app = FastAPI(
    title="OmniSight",
    description="Multimodal UI Self-Healing and RPA Agent",
    version="1.0.0",
)


# -----------------------------
# Request Models
# -----------------------------

class AnalyzeRequest(BaseModel):
    screenshot: str
    html: str


class URLRequest(BaseModel):
    url: str


class SelfHealingRequest(BaseModel):
    url: str
    css_code: str
    html_path: str


# -----------------------------
# Health Check
# -----------------------------

@app.get("/")
async def root():
    return {
        "project": "OmniSight",
        "status": "running",
        "description": "Multimodal UI Self-Healing and RPA Agent",
    }


@app.get("/health")
async def health():
    return {
        "status": "healthy"
    }


# -----------------------------
# Week 1
# -----------------------------

@app.post("/capture")
async def capture(request: URLRequest):
    try:
        return await capture_page(
            url=request.url
        )

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=str(exc)
        )


@app.post("/responsive-test")
async def responsive_test(request: URLRequest):
    try:
        result = await capture_responsive_pages(
            url=request.url
        )

        return {
            "count": len(result),
            "results": result,
        }

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=str(exc)
        )


@app.post("/checkout-flow")
async def checkout_flow(request: URLRequest):
    try:
        return await run_checkout_flow(
            url=request.url
        )

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=str(exc)
        )


# -----------------------------
# Week 2
# -----------------------------

@app.post("/analyze")
async def analyze(request: AnalyzeRequest):

    screenshot = Path(request.screenshot)
    html = Path(request.html)

    if not screenshot.exists():
        raise HTTPException(
            status_code=404,
            detail="Screenshot not found"
        )

    if not html.exists():
        raise HTTPException(
            status_code=404,
            detail="HTML file not found"
        )

    try:
        result = await analyze_ui(
            screenshot_path=str(screenshot),
            html_path=str(html),
        )

        analysis = process_analysis(result)

        generated_files = generate_fix_file(result)

        return {
            "analysis": analysis,
            "generated_fix_files": generated_files,
        }

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=str(exc)
        )


# -----------------------------
# Week 3 - Self Healing
# -----------------------------

@app.post("/self-heal")
async def self_heal(request: SelfHealingRequest):

    html_path = Path(request.html_path)

    if not html_path.exists():
        raise HTTPException(
            status_code=404,
            detail="HTML file not found"
        )

    try:
        result = await self_healing_loop(
            url=request.url,
            css_code=request.css_code,
            html_path=str(html_path),
        )

        return result

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=str(exc)
        )

