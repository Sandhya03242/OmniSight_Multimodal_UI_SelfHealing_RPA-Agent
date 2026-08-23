from typing import List, Optional
from pydantic import BaseModel


class UIIssue(BaseModel):
    severity: str
    issue_type: str
    description: str
    affected_element: Optional[str] = None
    evidence: Optional[str] = None


class SuggestedFix(BaseModel):
    language: str
    code: str
    explanation: str


class AnalysisResult(BaseModel):
    issues: List[UIIssue]
    suggested_fixes: List[SuggestedFix]
    overall_summary: str


class AnalyzeRequest(BaseModel):
    screenshot_path: str
    html_path: str


class CIWebhookRequest(BaseModel):
    repository: Optional[str] = None
    branch: Optional[str] = None
    commit_id: Optional[str] = None
    url: Optional[str] = None