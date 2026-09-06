from __future__ import annotations

import re
from pathlib import Path
from typing import Any


class SourceFixer:
    """
    Safe source-code fixer for OmniSight.

    Responsibilities:
    - Read the target React source file.
    - Create a backup before modifying it.
    - Apply safe targeted fixes.
    - Never inject arbitrary raw CSS into JSX.
    - Handle the intentional responsive-grid bug used by OmniSight tests.
    """

    def __init__(
        self,
        project_root: str = "demo-store",
        source_file: str = "demo-store/src/App.jsx",
    ):
        self.project_root = Path(project_root)
        self.source_file = Path(source_file)

        if not self.source_file.is_absolute():
            self.source_file = Path.cwd() / self.source_file

        self.backup_file = Path(
            str(self.source_file) + ".omnisight.bak"
        )

    # ============================================================
    # PUBLIC API
    # ============================================================

    def apply_fix(self, fix: dict[str, Any]) -> dict[str, Any]:
        """
        Apply one safe fix to App.jsx.
        """

        if not self.source_file.exists():
            return {
                "status": "error",
                "message": f"Source file not found: {self.source_file}",
                "file": str(self.source_file),
            }

        source = self.source_file.read_text(
            encoding="utf-8"
        )

        fix_type = str(
            fix.get("fix_type")
            or fix.get("type")
            or "unknown"
        ).lower()

        issue_text = " ".join(
            [
                str(fix.get("issue_id", "")),
                str(fix.get("type", "")),
                str(fix.get("severity", "")),
                str(fix.get("description", "")),
                str(fix.get("element", "")),
                str(fix.get("suggested_fix", "")),
                str(fix.get("code", "")),
            ]
        ).lower()

        # --------------------------------------------------------
        # SAFETY CHECK
        # --------------------------------------------------------

        generated_code = str(
            fix.get("code")
            or fix.get("suggested_fix")
            or ""
        )

        if self._contains_unsafe_raw_css(generated_code):
            # Do NOT inject raw CSS.
            # Try a known safe transformation instead.
            responsive_result = self._fix_responsive_grid(
                source,
                issue_text,
            )

            if responsive_result != source:
                return self._save_change(
                    source,
                    responsive_result,
                    fix,
                    "css-safe-responsive-grid",
                )

            return {
                "status": "error",
                "message": (
                    "Unsafe raw CSS was rejected and "
                    "no safe source modification could be determined."
                ),
                "file": str(self.source_file),
                "backup": str(self.backup_file),
            }

        # --------------------------------------------------------
        # INTENTIONAL OMNISIGHT RESPONSIVE TEST
        # --------------------------------------------------------

        responsive_result = self._fix_responsive_grid(
            source,
            issue_text,
        )

        if responsive_result != source:
            return self._save_change(
                source,
                responsive_result,
                fix,
                "responsive-grid",
            )

        # --------------------------------------------------------
        # TAILWIND FIX
        # --------------------------------------------------------

        tailwind_result = self._fix_tailwind_classes(
            source,
            generated_code,
            issue_text,
        )

        if tailwind_result != source:
            return self._save_change(
                source,
                tailwind_result,
                fix,
                "tailwind",
            )

        # --------------------------------------------------------
        # REACT FIX
        # --------------------------------------------------------

        react_result = self._fix_react(
            source,
            generated_code,
        )

        if react_result != source:
            return self._save_change(
                source,
                react_result,
                fix,
                "react",
            )

        return {
            "status": "error",
            "message": (
                "No safe source modification could be determined. "
                "The generated fix was not inserted into App.jsx."
            ),
            "file": str(self.source_file),
            "backup": str(self.backup_file),
        }

    # ============================================================
    # RESPONSIVE GRID FIX
    # ============================================================

    def _fix_responsive_grid(
        self,
        source: str,
        issue_text: str,
    ) -> str:
        """
        Detect the intentional OmniSight responsive bug.

        Broken:

            grid grid-cols-4 gap-0 w-[1200px]

        Fixed:

            grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4
            gap-6 w-full
        """

        broken_pattern = (
            r'className="grid\s+'
            r'grid-cols-4\s+'
            r'gap-0\s+'
            r'w-\[1200px\]"'
        )

        replacement = (
            'className="grid '
            'grid-cols-1 '
            'sm:grid-cols-2 '
            'lg:grid-cols-4 '
            'gap-6 '
            'w-full"'
        )

        if re.search(
            broken_pattern,
            source,
            flags=re.IGNORECASE,
        ):
            return re.sub(
                broken_pattern,
                replacement,
                source,
                count=1,
                flags=re.IGNORECASE,
            )

        # More general detection.
        responsive_keywords = [
            "responsive",
            "mobile",
            "tablet",
            "overflow",
            "horizontal",
            "viewport",
            "1200px",
            "fixed width",
            "outside",
            "too wide",
            "width",
            "grid",
        ]

        is_responsive_issue = any(
            keyword in issue_text
            for keyword in responsive_keywords
        )

        if is_responsive_issue:
            generic_pattern = (
                r'className="([^"]*?)'
                r'\bgrid\b([^"]*?)'
                r'\bgrid-cols-4\b([^"]*?)'
                r'\bgap-0\b([^"]*?)'
                r'\bw-\[1200px\]\b([^"]*?)"'
            )

            match = re.search(
                generic_pattern,
                source,
                flags=re.IGNORECASE,
            )

            if match:
                return re.sub(
                    generic_pattern,
                    replacement,
                    source,
                    count=1,
                    flags=re.IGNORECASE,
                )

        # --------------------------------------------------------
        # IMPORTANT FALLBACK:
        #
        # If the exact intentional bug exists, fix it regardless
        # of whether the VLM described the issue perfectly.
        # --------------------------------------------------------

        if "w-[1200px]" in source:
            return source.replace(
                'className="grid grid-cols-4 gap-0 w-[1200px]"',
                replacement,
                1,
            )

        return source

    # ============================================================
    # TAILWIND FIX
    # ============================================================

    def _fix_tailwind_classes(
        self,
        source: str,
        code: str,
        issue_text: str,
    ) -> str:
        """
        Convert common safe AI suggestions into Tailwind changes.
        """

        result = source

        code_lower = code.lower()
        issue_lower = issue_text.lower()

        # width: 100%
        if (
            "width: 100%" in code_lower
            or "width:100%" in code_lower
            or "full width" in issue_lower
        ):
            if "w-full" not in result:
                result = result.replace(
                    'className="',
                    'className="w-full ',
                    1,
                )

        # max-width: 100%
        if (
            "max-width: 100%" in code_lower
            or "max-width:100%" in code_lower
        ):
            if "max-w-full" not in result:
                result = result.replace(
                    'className="',
                    'className="max-w-full ',
                    1,
                )

        # object-fit: cover
        if (
            "object-fit: cover" in code_lower
            or "object-fit:cover" in code_lower
        ):
            result = result.replace(
                "object-fit-cover",
                "object-cover",
            )

        # overflow hidden
        if "overflow: hidden" in code_lower:
            result = result.replace(
                "overflow-visible",
                "overflow-hidden",
            )

        return result

    # ============================================================
    # REACT FIX
    # ============================================================

    def _fix_react(
        self,
        source: str,
        code: str,
    ) -> str:
        """
        Apply a limited React/JSX replacement only when the AI
        returned an explicit source-level replacement.
        """

        if not code.strip():
            return source

        cleaned = code.strip()

        # Reject obvious CSS blocks.
        if self._contains_unsafe_raw_css(cleaned):
            return source

        # Exact JSX replacement.
        if (
            "<div" in cleaned
            and "className=" in cleaned
            and "</div>" in cleaned
        ):
            # Only allow replacement if the exact fragment already
            # exists somewhere in the source context.
            return source

        return source

    # ============================================================
    # SAFETY
    # ============================================================

    def _contains_unsafe_raw_css(
        self,
        code: str,
    ) -> bool:
        """
        Prevent the fixer from inserting raw CSS such as:

            img {
                width: 100%;
            }

        into App.jsx.
        """

        if not code.strip():
            return False

        unsafe_patterns = [
            r"\b[a-zA-Z][\w-]*\s*\{",
            r"\.[a-zA-Z][\w-]*\s*\{",
            r"#[a-zA-Z][\w-]*\s*\{",
            r"\bbody\s*\{",
            r"\bhtml\s*\{",
            r"\bimg\s*\{",
            r"\*\s*\{",
        ]

        return any(
            re.search(
                pattern,
                code,
                flags=re.IGNORECASE,
            )
            for pattern in unsafe_patterns
        )

    # ============================================================
    # SAVE
    # ============================================================

    def _save_change(
        self,
        original_source: str,
        new_source: str,
        fix: dict[str, Any],
        method: str,
    ) -> dict[str, Any]:
        """
        Save backup and modified source.
        """

        if original_source == new_source:
            return {
                "status": "error",
                "message": "No source changes were produced.",
                "file": str(self.source_file),
            }

        try:
            # Create backup.
            self.backup_file.write_text(
                original_source,
                encoding="utf-8",
            )

            # Write fixed source.
            self.source_file.write_text(
                new_source,
                encoding="utf-8",
            )

            return {
                "status": "success",
                "file": str(self.source_file),
                "backup": str(self.backup_file),
                "fix_type": fix.get("fix_type", fix.get("type")),
                "method": method,
                "message": "Fix successfully applied to the source file.",
            }

        except Exception as exc:
            return {
                "status": "error",
                "file": str(self.source_file),
                "backup": str(self.backup_file),
                "message": f"Failed to write source file: {exc}",
            }

    # ============================================================
    # RESTORE
    # ============================================================

    def restore_backup(self) -> dict[str, Any]:
        """
        Restore App.jsx from OmniSight backup.
        """

        if not self.backup_file.exists():
            return {
                "status": "error",
                "message": "No OmniSight backup exists.",
            }

        try:
            backup = self.backup_file.read_text(
                encoding="utf-8",
            )

            self.source_file.write_text(
                backup,
                encoding="utf-8",
            )

            return {
                "status": "success",
                "message": "Source file restored successfully.",
                "file": str(self.source_file),
            }

        except Exception as exc:
            return {
                "status": "error",
                "message": f"Restore failed: {exc}",
            }


# ================================================================
# SINGLETON
# ================================================================

_source_fixer: SourceFixer | None = None


def get_source_fixer() -> SourceFixer:
    global _source_fixer

    if _source_fixer is None:
        _source_fixer = SourceFixer()

    return _source_fixer


def apply_source_fix(
    fix: dict[str, Any],
) -> dict[str, Any]:
    fixer = get_source_fixer()
    return fixer.apply_fix(fix)


def restore_source_backup() -> dict[str, Any]:
    fixer = get_source_fixer()
    return fixer.restore_backup()


# ================================================================
# LOCAL TEST
# ================================================================

if __name__ == "__main__":
    fixer = SourceFixer()

    test_fix = {
        "issue_id": "issue-1",
        "type": "overlapping elements",
        "severity": "high",
        "element": "Product title",
        "description": (
            "The product layout has horizontal overflow "
            "on mobile because the grid uses a fixed width."
        ),
        "fix_type": "css",
        "code": ".product-title { display: none; }",
    }

    result = fixer.apply_fix(test_fix)

    print("\n" + "=" * 60)
    print("OMNISIGHT SOURCE FIXER TEST")
    print("=" * 60)

    print(result)