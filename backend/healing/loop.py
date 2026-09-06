from __future__ import annotations

from pathlib import Path
from typing import Any

from backend.healing.craft import craft_fixes
from backend.healing.source_fixer import apply_source_fix
from backend.vision.analyzer import analyze_ui


class HealingLoop:
    """
    OmniSight Week 3 - Self-Healing Loop.

    Flow:
        Analyze
            ↓
        Generate Fix
            ↓
        Apply Fix
            ↓
        Re-analyze
            ↓
        Verify
    """

    def __init__(
        self,
        project_root: str = "demo-store",
        max_attempts: int = 3,
    ) -> None:

        self.project_root = Path(
            project_root
        )

        self.max_attempts = max(
            1,
            max_attempts,
        )

    # ========================================================
    # RUN SELF-HEALING
    # ========================================================

    def run(
        self,
        url: str,
        screenshot_path: str,
        html_path: str,
    ) -> dict[str, Any]:

        attempts = 0
        all_fixes: list[dict[str, Any]] = []

        try:

            # ------------------------------------------------
            # Initial VLM analysis
            # ------------------------------------------------

            vision_result = analyze_ui(
                screenshot_path=screenshot_path,
                html_path=html_path,
            )

            issues = vision_result.get(
                "issues",
                [],
            )

            if not issues:

                return {
                    "status": "success",
                    "url": url,
                    "attempts": 0,
                    "issues_found": 0,
                    "fixes_generated": 0,
                    "fixed": True,
                    "message": (
                        "No UI issues detected."
                    ),
                    "fixes": [],
                }

            initial_issue_count = len(
                issues
            )

            # ------------------------------------------------
            # Healing attempts
            # ------------------------------------------------

            while (
                attempts < self.max_attempts
            ):

                attempts += 1

                print()
                print("=" * 60)
                print(
                    f"OMNISIGHT HEALING ATTEMPT "
                    f"{attempts}/{self.max_attempts}"
                )
                print("=" * 60)

                # --------------------------------------------
                # Generate executable fixes
                # --------------------------------------------

                fix_result = craft_fixes(
                    vision_result
                )

                fixes = fix_result.get(
                    "fixes",
                    [],
                )

                if not fixes:

                    return {
                        "status": "failed",
                        "url": url,
                        "attempts": attempts,
                        "issues_found": (
                            initial_issue_count
                        ),
                        "fixes_generated": 0,
                        "fixed": False,
                        "message": (
                            "No executable fixes "
                            "could be generated."
                        ),
                        "fixes": all_fixes,
                    }

                # --------------------------------------------
                # Apply fixes
                # --------------------------------------------

                applied_any = False

                for fix in fixes:

                    if not fix.get("code"):
                        continue

                    print(
                        f"Applying fix: "
                        f"{fix.get('issue_id')}"
                    )

                    apply_result = apply_source_fix(
                        fix=fix,
                        project_root=str(
                            self.project_root
                        ),
                    )

                    if (
                        apply_result.get("status")
                        == "success"
                    ):

                        applied_any = True

                        all_fixes.append(
                            {
                                **fix,
                                "apply_result": (
                                    apply_result
                                ),
                            }
                        )

                if not applied_any:

                    return {
                        "status": "failed",
                        "url": url,
                        "attempts": attempts,
                        "issues_found": (
                            initial_issue_count
                        ),
                        "fixes_generated": len(
                            fixes
                        ),
                        "fixed": False,
                        "message": (
                            "Generated fixes could "
                            "not be applied."
                        ),
                        "fixes": all_fixes,
                    }

                # --------------------------------------------
                # Re-run analysis
                #
                # IMPORTANT:
                # Playwright must generate the new screenshot
                # and HTML before this analysis.
                #
                # The API endpoint can perform that step
                # between attempts.
                # --------------------------------------------

                new_screenshot = (
                    self._get_latest_screenshot()
                )

                new_html = (
                    self._get_latest_html()
                )

                if (
                    new_screenshot is None
                    or new_html is None
                ):

                    return {
                        "status": "success",
                        "url": url,
                        "attempts": attempts,
                        "issues_found": (
                            initial_issue_count
                        ),
                        "fixes_generated": len(
                            all_fixes
                        ),
                        "fixed": True,
                        "message": (
                            "Source fix applied "
                            "successfully. Re-test "
                            "is required."
                        ),
                        "fixes": all_fixes,
                    }

                # --------------------------------------------
                # VLM verification
                # --------------------------------------------

                verification = analyze_ui(
                    screenshot_path=(
                        new_screenshot
                    ),
                    html_path=new_html,
                )

                remaining_issues = (
                    verification.get(
                        "issues",
                        [],
                    )
                )

                if not remaining_issues:

                    return {
                        "status": "success",
                        "url": url,
                        "attempts": attempts,
                        "issues_found": (
                            initial_issue_count
                        ),
                        "fixes_generated": len(
                            all_fixes
                        ),
                        "fixed": True,
                        "verification": {
                            "fixed": True,
                            "reason": (
                                "The VLM found "
                                "no remaining UI "
                                "issues after "
                                "healing."
                            ),
                        },
                        "fixes": all_fixes,
                    }

                # --------------------------------------------
                # Continue healing
                # --------------------------------------------

                vision_result = verification

            # ------------------------------------------------
            # Maximum attempts reached
            # ------------------------------------------------

            return {
                "status": "success",
                "url": url,
                "attempts": attempts,
                "issues_found": (
                    initial_issue_count
                ),
                "fixes_generated": len(
                    all_fixes
                ),
                "fixed": False,
                "verification": {
                    "fixed": False,
                    "reason": (
                        "UI issues remain after "
                        f"{self.max_attempts} "
                        "healing attempts."
                    ),
                },
                "fixes": all_fixes,
            }

        except Exception as exc:

            return {
                "status": "failed",
                "url": url,
                "attempts": attempts,
                "issues_found": 0,
                "fixes_generated": len(
                    all_fixes
                ),
                "fixed": False,
                "error": str(exc),
                "fixes": all_fixes,
            }

    # ========================================================
    # FIND LATEST SCREENSHOT
    # ========================================================

    def _get_latest_screenshot(
        self,
    ) -> str | None:

        screenshots_dir = Path(
            "screenshots"
        )

        if not screenshots_dir.exists():
            return None

        files = sorted(
            screenshots_dir.glob("*.png"),
            key=lambda path: path.stat().st_mtime,
            reverse=True,
        )

        if not files:
            return None

        return str(files[0])

    # ========================================================
    # FIND LATEST HTML
    # ========================================================

    def _get_latest_html(
        self,
    ) -> str | None:

        outputs_dir = Path(
            "outputs"
        )

        if not outputs_dir.exists():
            return None

        files = sorted(
            outputs_dir.glob("*.html"),
            key=lambda path: path.stat().st_mtime,
            reverse=True,
        )

        if not files:
            return None

        return str(files[0])


# ============================================================
# SINGLETON
# ============================================================

_healing_loop: HealingLoop | None = None


def run_healing_loop(
    url: str,
    screenshot_path: str,
    html_path: str,
    max_attempts: int = 3,
    project_root: str = "demo-store",
) -> dict[str, Any]:

    global _healing_loop

    if (
        _healing_loop is None
        or _healing_loop.max_attempts
        != max_attempts
        or str(_healing_loop.project_root)
        != project_root
    ):

        _healing_loop = HealingLoop(
            project_root=project_root,
            max_attempts=max_attempts,
        )

    return _healing_loop.run(
        url=url,
        screenshot_path=screenshot_path,
        html_path=html_path,
    )


# ============================================================
# LOCAL TEST
# ============================================================

if __name__ == "__main__":

    result = run_healing_loop(
        url="http://localhost:5173",
        screenshot_path="screenshots/01_home.png",
        html_path="outputs/01_home.html",
    )

    print()
    print("=" * 60)
    print("OMNISIGHT HEALING RESULT")
    print("=" * 60)
    print(result)