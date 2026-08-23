import json
from pathlib import Path

from .models import AnalysisResult


OUTPUT_DIR = Path("outputs")
OUTPUT_DIR.mkdir(exist_ok=True)


def process_analysis(
    result: AnalysisResult
):
    issues = []

    for issue in result.issues:

        issues.append({
            "severity": issue.severity,
            "type": issue.issue_type,
            "description": issue.description,
            "affected_element": (
                issue.affected_element
            ),
            "evidence": issue.evidence
        })

    fixes = []

    for fix in result.suggested_fixes:

        fixes.append({
            "language": fix.language,
            "code": fix.code,
            "explanation": fix.explanation
        })

    output = {
        "summary": {
            "total_issues": len(issues),
            "total_fixes": len(fixes)
        },
        "issues": issues,
        "suggested_fixes": fixes
    }

    output_path = (
        OUTPUT_DIR / "analysis_result.json"
    )

    output_path.write_text(
        json.dumps(
            output,
            indent=4
        ),
        encoding="utf-8"
    )

    return output


def generate_fix_file(
    result: AnalysisResult
):

    generated_files = []

    for index, fix in enumerate(
        result.suggested_fixes,
        start=1
    ):

        extension = {
            "css": "css",
            "react": "jsx",
            "html": "html"
        }.get(
            fix.language.lower(),
            "txt"
        )

        filename = (
            f"suggested_fix_{index}.{extension}"
        )

        path = OUTPUT_DIR / filename

        path.write_text(
            fix.code,
            encoding="utf-8"
        )

        generated_files.append(
            str(path)
        )

    return generated_files