import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
OUTPUTS = ROOT / "outputs"


def extract_fixes(analysis):
    issues = analysis.get(
        "issues",
        []
    )

    fixes = []

    for issue in issues:
        css_fix = issue.get(
            "css_fix",
            ""
        )

        react_fix = issue.get(
            "react_fix",
            ""
        )

        if not css_fix and not react_fix:
            continue

        fixes.append({
            "type": issue.get(
                "type",
                "unknown",
            ),
            "severity": issue.get(
                "severity",
                "medium",
            ),
            "selector": issue.get(
                "selector",
                "",
            ),
            "description": issue.get(
                "description",
                "",
            ),
            "css_fix": css_fix,
            "react_fix": react_fix,
        })

    return {
        "total_issues": len(issues),
        "total_fixes": len(fixes),
        "fixes": fixes,
    }


def save_fixes(
    fixes,
    filename="fixes.json",
):
    OUTPUTS.mkdir(
        parents=True,
        exist_ok=True,
    )

    path = OUTPUTS / filename

    path.write_text(
        json.dumps(
            fixes,
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    return path