from __future__ import annotations

import re
from typing import Any


class ActionEngine:
    """
    Parses VLM output and extracts suggested
    CSS / React fixes.
    """

    def parse_vlm_output(
        self,
        vlm_result: dict[str, Any],
    ) -> dict[str, Any]:

        issues = vlm_result.get("issues", [])

        if not isinstance(issues, list):
            issues = []

        fixes: list[dict[str, Any]] = []

        for index, issue in enumerate(issues, start=1):

            if not isinstance(issue, dict):
                continue

            issue_id = issue.get(
                "id",
                f"issue-{index}",
            )

            suggested_fix = issue.get(
                "suggested_fix",
                "",
            )

            if not suggested_fix:
                continue

            fixes.append({
                "issue_id": issue_id,
                "type": issue.get(
                    "type",
                    "unknown",
                ),
                "severity": issue.get(
                    "severity",
                    "low",
                ),
                "element": issue.get(
                    "element",
                    None,
                ),
                "description": issue.get(
                    "description",
                    "",
                ),
                "fix_type": self.detect_fix_type(
                    suggested_fix
                ),
                "suggested_fix": suggested_fix,
                "code": self.extract_code(
                    suggested_fix
                ),
            })

        return {
            "status": "success",
            "total_issues": len(issues),
            "total_fixes": len(fixes),
            "fixes": fixes,
        }

    def detect_fix_type(
        self,
        text: str,
    ) -> str:

        text_lower = text.lower()

        react_keywords = [
            "react",
            "jsx",
            "tsx",
            "component",
            "useeffect",
            "usestate",
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
            "line-height",
            "overflow",
            "z-index",
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

        return "general"

    def extract_code(
        self,
        text: str,
    ) -> str | None:

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


_action_engine: ActionEngine | None = None


def extract_fixes(
    vlm_result: dict[str, Any],
) -> dict[str, Any]:

    global _action_engine

    if _action_engine is None:
        _action_engine = ActionEngine()

    return _action_engine.parse_vlm_output(
        vlm_result
    )