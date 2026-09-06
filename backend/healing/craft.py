from __future__ import annotations

import json
import re
from typing import Any

from backend.actions.engine import ActionEngine


class FixCrafter:
    """
    Converts VLM issues into executable CSS/React fixes.

    Week 3 - Self-Healing
    """

    def __init__(self) -> None:
        self.action_engine = ActionEngine()

    # ========================================================
    # CRAFT FIXES
    # ========================================================

    def craft_fixes(
        self,
        vlm_result: dict[str, Any],
    ) -> dict[str, Any]:

        issues = vlm_result.get("issues", [])

        if not isinstance(issues, list):
            issues = []

        fixes: list[dict[str, Any]] = []

        for index, issue in enumerate(
            issues,
            start=1,
        ):

            if not isinstance(issue, dict):
                continue

            issue_id = issue.get(
                "id",
                f"issue-{index}",
            )

            suggested_fix = str(
                issue.get(
                    "suggested_fix",
                    "",
                )
            )

            description = str(
                issue.get(
                    "description",
                    "",
                )
            )

            element = issue.get(
                "element",
                None,
            )

            fix_type = self._detect_fix_type(
                suggested_fix
            )

            code = self._extract_code(
                suggested_fix
            )

            # ------------------------------------------------
            # Generate executable fix when VLM returned
            # only natural language.
            # ------------------------------------------------

            if not code:
                code = self._generate_fix_code(
                    issue=issue,
                    fix_type=fix_type,
                )

            fixes.append(
                {
                    "issue_id": issue_id,
                    "type": issue.get(
                        "type",
                        "unknown",
                    ),
                    "severity": issue.get(
                        "severity",
                        "low",
                    ),
                    "element": element,
                    "description": description,
                    "fix_type": fix_type,
                    "suggested_fix": suggested_fix,
                    "code": code,
                }
            )

        executable_fixes = [
            fix
            for fix in fixes
            if fix.get("code")
        ]

        return {
            "status": "success",
            "total_issues": len(issues),
            "total_fixes": len(fixes),
            "executable_fixes": len(
                executable_fixes
            ),
            "fixes": fixes,
        }

    # ========================================================
    # FIX TYPE
    # ========================================================

    def _detect_fix_type(
        self,
        text: str,
    ) -> str:

        text_lower = text.lower()

        react_keywords = [
            "react",
            "jsx",
            "tsx",
            "component",
            "usestate",
            "useeffect",
        ]

        css_keywords = [
            "css",
            "scss",
            "padding",
            "margin",
            "color",
            "background",
            "display",
            "position",
            "width",
            "height",
            "font",
            "overflow",
            "flex",
            "grid",
        ]

        if any(
            keyword in text_lower
            for keyword in react_keywords
        ):
            return "react"

        if any(
            keyword in text_lower
            for keyword in css_keywords
        ):
            return "css"

        return "css"

    # ========================================================
    # EXTRACT CODE FROM VLM RESPONSE
    # ========================================================

    def _extract_code(
        self,
        text: str,
    ) -> str | None:

        if not text:
            return None

        code_blocks = re.findall(
            r"```(?:css|scss|jsx|tsx|react|javascript|js)?\s*(.*?)```",
            text,
            flags=re.IGNORECASE | re.DOTALL,
        )

        if code_blocks:
            return code_blocks[0].strip()

        css_match = re.search(
            r"[.#]?[a-zA-Z][a-zA-Z0-9_-]*\s*\{.*?\}",
            text,
            flags=re.DOTALL,
        )

        if css_match:
            return css_match.group(0).strip()

        jsx_match = re.search(
            r"<[A-Z][^>]*>.*?</[A-Z][^>]*>",
            text,
            flags=re.DOTALL,
        )

        if jsx_match:
            return jsx_match.group(0).strip()

        return None

    # ========================================================
    # GENERATE EXECUTABLE FIX
    # ========================================================

    def _generate_fix_code(
        self,
        issue: dict[str, Any],
        fix_type: str,
    ) -> str | None:

        issue_type = str(
            issue.get(
                "type",
                "",
            )
        ).lower()

        description = str(
            issue.get(
                "description",
                "",
            )
        ).lower()

        suggested_fix = str(
            issue.get(
                "suggested_fix",
                "",
            )
        ).lower()

        combined = (
            description
            + " "
            + suggested_fix
        )

        # ----------------------------------------------------
        # RESPONSIVE WIDTH / OVERFLOW
        # ----------------------------------------------------

        if (
            "overflow" in combined
            or "outside the page" in combined
            or "1200px" in combined
            or "mobile" in combined
        ):

            return (
                ".grid {\n"
                "    width: 100%;\n"
                "    grid-template-columns: "
                "repeat(1, minmax(0, 1fr));\n"
                "}\n"
            )

        # ----------------------------------------------------
        # IMAGE / CARD HEIGHT
        # ----------------------------------------------------

        if (
            "image" in combined
            and (
                "cut off" in combined
                or "height" in combined
                or "container" in combined
            )
        ):

            return (
                "img {\n"
                "    width: 100%;\n"
                "    height: 224px;\n"
                "    object-fit: cover;\n"
                "}\n"
            )

        # ----------------------------------------------------
        # OVERLAP
        # ----------------------------------------------------

        if (
            issue_type == "overlap"
            or "overlap" in combined
        ):

            return (
                ".element {\n"
                "    position: relative;\n"
                "    z-index: 1;\n"
                "}\n"
            )

        # ----------------------------------------------------
        # SPACING
        # ----------------------------------------------------

        if (
            "spacing" in combined
            or "padding" in combined
            or "margin" in combined
        ):

            return (
                ".element {\n"
                "    margin: 0;\n"
                "    padding: 1rem;\n"
                "}\n"
            )

        # ----------------------------------------------------
        # CONTRAST
        # ----------------------------------------------------

        if "contrast" in combined:

            return (
                ".element {\n"
                "    color: #111827;\n"
                "    background-color: #ffffff;\n"
                "}\n"
            )

        return None

    # ========================================================
    # VALIDATE
    # ========================================================

    def validate_fixes(
        self,
        fixes_result: dict[str, Any],
    ) -> dict[str, Any]:

        fixes = fixes_result.get(
            "fixes",
            [],
        )

        valid_fixes: list[dict[str, Any]] = []

        for fix in fixes:

            if not isinstance(
                fix,
                dict,
            ):
                continue

            code = fix.get("code")

            if (
                isinstance(code, str)
                and code.strip()
            ):
                valid_fixes.append(fix)

        return {
            "status": "success",
            "valid": len(valid_fixes) > 0,
            "total": len(fixes),
            "executable": len(valid_fixes),
            "fixes": valid_fixes,
        }


# ============================================================
# SINGLETON
# ============================================================

_crafter: FixCrafter | None = None


def craft_fixes(
    vlm_result: dict[str, Any],
) -> dict[str, Any]:

    global _crafter

    if _crafter is None:
        _crafter = FixCrafter()

    return _crafter.craft_fixes(
        vlm_result
    )


def validate_crafted_fixes(
    fixes_result: dict[str, Any],
) -> dict[str, Any]:

    global _crafter

    if _crafter is None:
        _crafter = FixCrafter()

    return _crafter.validate_fixes(
        fixes_result
    )


# ============================================================
# LOCAL TEST
# ============================================================

if __name__ == "__main__":

    sample = {
        "issues": [
            {
                "id": "issue-1",
                "type": "overlap",
                "severity": "high",
                "description": (
                    "The product image is cut off "
                    "at the bottom of the card."
                ),
                "element": "Travel Backpack",
                "suggested_fix": (
                    "Increase the card height or "
                    "adjust the image height."
                ),
            }
        ]
    }

    result = craft_fixes(sample)

    print(
        json.dumps(
            result,
            indent=2,
        )
    )