from __future__ import annotations

from pydantic import BaseModel, Field


# ============================================================
# WEEK 1 - BROWSER AUTOMATION
# ============================================================

class NavigationRequest(BaseModel):
    url: str = "http://localhost:5173"


class ScreenshotResult(BaseModel):
    name: str
    path: str
    viewport: dict[str, int]


class NavigationResult(BaseModel):
    status: str
    url: str
    screenshots: list[ScreenshotResult] = Field(
        default_factory=list
    )
    html_files: list[str] = Field(
        default_factory=list
    )
    error: str | None = None


# ============================================================
# WEEK 1 - CI/CD WEBHOOK
# ============================================================

class WebhookRequest(BaseModel):
    event: str = "build.completed"
    url: str = "http://localhost:5173"


# ============================================================
# WEEK 2 - VISION ANALYSIS
# ============================================================

class VisionRequest(BaseModel):
    screenshot_path: str
    html_path: str


class UIIssue(BaseModel):
    id: str
    type: str
    severity: str
    description: str
    element: str | None = None
    suggested_fix: str | None = None


class VisionAnalysisResult(BaseModel):
    status: str
    model: str
    screenshot: str
    html: str
    issues: list[UIIssue] = Field(
        default_factory=list
    )
    raw_response: str | None = None


# ============================================================
# WEEK 3 - SELF-HEALING
# ============================================================

class HealingRequest(BaseModel):
    url: str = "http://localhost:5173"
    screenshot_path: str = "screenshots/01_home.png"
    html_path: str = "outputs/01_home.html"
    max_attempts: int = 3


class HealingFix(BaseModel):
    issue_id: str
    fix_type: str
    element: str | None = None
    description: str = ""
    suggested_fix: str = ""
    code: str | None = None


class HealingVerification(BaseModel):
    fixed: bool
    reason: str = ""


class HealingResult(BaseModel):
    status: str
    url: str
    attempts: int = 0
    issues_found: int = 0
    fixes_generated: int = 0
    fixed: bool = False
    verification: HealingVerification | None = None
    fixes: list[HealingFix] = Field(
        default_factory=list
    )
    error: str | None = None