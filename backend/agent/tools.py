from langchain_core.tools import tool


@tool
def detect_issue(status: str):
    """
    Determine whether OmniSight detected a UI issue.

    Args:
        status: Analysis status returned by the vision audit.

    Returns:
        ISSUE_FOUND when issues are detected, otherwise NO_ISSUE.
    """
    if status == "issues_found":
        return "ISSUE_FOUND"

    return "NO_ISSUE"


@tool
def select_fix(issue_type: str):
    """
    Select the appropriate CSS fix for a detected UI issue.

    Args:
        issue_type: Type of UI issue detected by OmniSight.

    Returns:
        CSS code that can be injected to repair the issue.
    """

    if issue_type == "hidden_element":
        return """
#continue {
    display: block !important;
    visibility: visible !important;
    opacity: 1 !important;
}
"""

    if issue_type == "horizontal_overflow":
        return """
* {
    box-sizing: border-box;
}

html,
body {
    max-width: 100%;
    overflow-x: hidden;
}
"""

    return ""


@tool
def verification_decision(
    passed: bool,
    attempt: int,
    max_attempts: int,
):
    """
    Decide whether the self-healing agent should pass, retry, or fail.

    Args:
        passed: Whether the repaired UI passed verification.
        attempt: Current healing attempt number.
        max_attempts: Maximum number of allowed attempts.

    Returns:
        PASS, RETRY, or FAILED.
    """

    if passed:
        return "PASS"

    if attempt < max_attempts:
        return "RETRY"

    return "FAILED"