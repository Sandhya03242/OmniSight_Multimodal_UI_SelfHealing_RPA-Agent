import json
from pathlib import Path

from fastapi import FastAPI
from pydantic import BaseModel

from backend.browser.navigator import run_navigation
from backend.vision.analyzer import (
    analyze_ui,
    analyze_crops,
    save_analysis,
)
from backend.vision.cropper import generate_chunks
from backend.action.engine import extract_fixes, save_fixes
from backend.healing.graph import run_healing_agent
from backend.healing.loop import save_healing_result
from backend.healing.source_fixer import apply_css_to_source
from backend.github.integration import create_pull_request


ROOT = Path(__file__).resolve().parent
OUTPUTS = ROOT / "outputs"


app = FastAPI(
    title="OmniSight",
    version="4.0.0",
)


class WebhookEvent(BaseModel):
    event: str
    status: str = "success"
    branch: str = "main"


class AnalyzeRequest(BaseModel):
    screenshot: str
    html: str


class Week4Request(BaseModel):
    screenshot: str
    html: str
    device: str = "mobile"


class HealRequest(BaseModel):
    screenshot: str
    html: str
    source_file: str = "demo-store/src/index.css"
    create_pr: bool = False
    max_iterations: int = 2


@app.get("/")
def home():
    return {
        "project": "OmniSight",
        "week": 4,
        "status": "running",
        "agent": "LangGraph",
        "model": "Qwen/Qwen3.5-0.8B",
    }


@app.get("/health")
def health():
    return {
        "status": "healthy"
    }


@app.post("/api/week1/run")
async def run_week1():
    result = await run_navigation()

    return {
        "success": result["success"],
        "message": "Browser automation completed",
        "result": result,
    }


@app.post("/api/ci/webhook")
async def ci_webhook(
    payload: WebhookEvent,
):
    if payload.status != "success":
        return {
            "success": False,
            "message": "Build failed",
            "branch": payload.branch,
        }

    result = await run_navigation()

    return {
        "success": result["success"],
        "message": "CI/CD webhook received",
        "event": payload.event,
        "branch": payload.branch,
        "result": result,
    }


@app.post("/api/week2/analyze")
def analyze_week2(
    request: AnalyzeRequest,
):
    screenshot_path = ROOT / request.screenshot
    html_path = ROOT / request.html

    if not screenshot_path.exists():
        return {
            "success": False,
            "message": "Screenshot not found",
        }

    if not html_path.exists():
        return {
            "success": False,
            "message": "HTML not found",
        }

    html = html_path.read_text(
        encoding="utf-8"
    )

    analysis = analyze_ui(
        str(screenshot_path),
        html,
    )

    analysis_path = save_analysis(
        analysis
    )

    fixes = extract_fixes(
        analysis
    )

    fixes_path = save_fixes(
        fixes
    )

    return {
        "success": True,
        "message": "UI analysis completed",
        "analysis": analysis,
        "fixes": fixes,
        "files": {
            "analysis": str(
                analysis_path
            ),
            "fixes": str(
                fixes_path
            ),
        },
    }


@app.post("/api/week3/heal")
async def heal_week3(
    request: HealRequest,
):
    screenshot_path = ROOT / request.screenshot
    html_path = ROOT / request.html

    if not screenshot_path.exists():
        return {
            "success": False,
            "message": "Screenshot not found",
        }

    if not html_path.exists():
        return {
            "success": False,
            "message": "HTML not found",
        }

    result = await run_healing_agent(
        str(screenshot_path),
        str(html_path),
        request.max_iterations,
    )

    healing_path = save_healing_result(
        result
    )

    source_result = None
    github_result = None

    if result.get("healed", False):
        css_fix = result.get(
            "css_fix",
            "",
        )

        if css_fix:
            source_result = apply_css_to_source(
                css_fix,
                request.source_file,
            )

            if (
                request.create_pr
                and source_result.get(
                    "success",
                    False,
                )
            ):
                try:
                    github_result = create_pull_request(
                        source_result["file"],
                        css_fix,
                        "Automatically detected UI defect",
                    )

                except Exception as exc:
                    github_result = {
                        "success": False,
                        "error": str(exc),
                    }

    return {
        "success": True,
        "message": "OmniSight agent completed",
        "agent": {
            "framework": "LangGraph",
            "model": "Qwen/Qwen3.5-0.8B",
            "healed": result.get(
                "healed",
                False,
            ),
            "iteration": result.get(
                "iteration",
                0,
            ),
        },
        "healing": result,
        "source": source_result,
        "github": github_result,
        "files": {
            "healing": str(
                healing_path
            ),
        },
    }


@app.post("/api/week4/analyze")
async def analyze_week4(
    request: Week4Request,
):
    screenshot_path = ROOT / request.screenshot
    html_path = ROOT / request.html

    if not screenshot_path.exists():
        return {
            "success": False,
            "message": "Screenshot not found",
        }

    if not html_path.exists():
        return {
            "success": False,
            "message": "HTML not found",
        }

    if request.device not in {
        "desktop",
        "tablet",
        "mobile",
    }:
        return {
            "success": False,
            "message": (
                "Invalid device. "
                "Use desktop, tablet or mobile."
            ),
        }

    html = html_path.read_text(
        encoding="utf-8"
    )

    chunks = await generate_chunks(
        request.device
    )

    analysis = analyze_crops(
        chunks["crops"],
        html,
    )

    output_path = (
        OUTPUTS / "week4_analysis.json"
    )

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    output_path.write_text(
        json.dumps(
            analysis,
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    return {
        "success": True,
        "message": (
            "Week 4 optimized UI analysis completed"
        ),
        "optimization": {
            "method": "DOM component cropping",
            "device": request.device,
            "total_crops": chunks[
                "total_crops"
            ],
        },
        "analysis": analysis,
        "output": str(
            output_path
        ),
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
    )