import json
from pathlib import Path


ROOT_DIR = (
    Path(__file__)
    .resolve()
    .parents[2]
)


FIX_DIR = (
    ROOT_DIR
    / "backend"
    / "outputs"
    / "fixes"
)


FIX_DIR.mkdir(
    parents=True,
    exist_ok=True,
)


def generate_fix(
    analysis,
):

    fixes = []

    for issue in analysis.get(
        "issues",
        []
    ):

        issue_type = issue.get(
            "type"
        )

        element = issue.get(
            "element"
        )

        if (
            issue_type
            == "hidden_element"
            and element
            == "#continue"
        ):

            fixes.append({

                "type":
                    "css",

                "element":
                    "#continue",

                "code":
                    """
#continue {
    display: block !important;
    visibility: visible !important;
    opacity: 1 !important;
}
""",

                "reason":
                    "Restore Continue button visibility.",
            })

        elif (
            issue_type
            == "horizontal_overflow"
        ):

            fixes.append({

                "type":
                    "css",

                "element":
                    "page",

                "code":
                    """
* {
    box-sizing: border-box;
}

html,
body {
    max-width: 100%;
    overflow-x: hidden;
}
""",

                "reason":
                    "Prevent horizontal overflow.",
            })

    result = {

        "status":
            (
                "fix_generated"
                if fixes
                else "no_fix_required"
            ),

        "fixes":
            fixes,
    }

    output = (
        FIX_DIR
        / "latest_fix.json"
    )

    output.write_text(
        json.dumps(
            result,
            indent=4,
        ),
        encoding="utf-8",
    )

    return result