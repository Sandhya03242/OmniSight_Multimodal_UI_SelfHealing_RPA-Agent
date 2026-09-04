import json
from pathlib import Path

from backend.vision.qwen import (
    analyze_screenshot,
)

from backend.action.extractor import (
    extract_json,
)


ROOT_DIR = (
    Path(__file__)
    .resolve()
    .parents[2]
)


ANALYSIS_DIR = (
    ROOT_DIR
    / "backend"
    / "outputs"
    / "analysis"
)


ANALYSIS_DIR.mkdir(
    parents=True,
    exist_ok=True,
)


def analyze_ui(
    screenshot_path,
    html_path,
    browser_result,
):

    html = Path(
        html_path
    ).read_text(
        encoding="utf-8"
    )

    dimensions = (
        browser_result
        .get(
            "dimensions",
            {}
        )
    )

    issues = []

    # ----------------------------
    # Deterministic check
    # ----------------------------

    viewport_width = (
        dimensions.get(
            "viewportWidth",
            0
        )
    )

    document_width = (
        dimensions.get(
            "documentWidth",
            0
        )
    )

    if (
        document_width
        >
        viewport_width
    ):

        issues.append({

            "type":
                "horizontal_overflow",

            "severity":
                "high",

            "element":
                "page",

            "description":
                "Document width exceeds viewport.",

            "evidence":
                (
                    f"document={document_width}, "
                    f"viewport={viewport_width}"
                ),

            "suggested_fix":
                """
html,
body {
    max-width: 100%;
    overflow-x: hidden;
}
""",
        })

    # ----------------------------
    # Hidden button check
    # ----------------------------

    if (
        browser_result
        .get(
            "continue_visible"
        )
        is False
    ):

        issues.append({

            "type":
                "hidden_element",

            "severity":
                "high",

            "element":
                "#continue",

            "description":
                "Checkout Continue button is hidden.",

            "evidence":
                "Playwright reports #continue as invisible.",

            "suggested_fix":
                """
#continue {
    display: block !important;
    visibility: visible !important;
    opacity: 1 !important;
}
""",
        })

    # ----------------------------
    # Qwen
    # ----------------------------

    qwen_response = (
        analyze_screenshot(
            screenshot_path,
            html,
            dimensions,
        )
    )

    qwen_result = (
        extract_json(
            qwen_response
        )
    )

    # ----------------------------
    # Merge
    # ----------------------------

    for issue in qwen_result.get(
        "issues",
        []
    ):

        exists = any(

            existing.get(
                "type"
            )
            == issue.get(
                "type"
            )

            and

            existing.get(
                "element"
            )
            == issue.get(
                "element"
            )

            for existing
            in issues
        )

        if not exists:

            issues.append(
                issue
            )

    result = {

        "status":
            (
                "issues_found"
                if issues
                else "passed"
            ),

        "issues":
            issues,

        "qwen":
            qwen_result,

        "screenshot":
            str(screenshot_path),

        "html":
            str(html_path),

        "viewport":
            dimensions,
    }

    output = (
        ANALYSIS_DIR
        / "latest_analysis.json"
    )

    output.write_text(
        json.dumps(
            result,
            indent=4,
        ),
        encoding="utf-8",
    )

    return result