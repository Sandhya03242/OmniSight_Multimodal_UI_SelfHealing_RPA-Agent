import json
from pathlib import Path

from playwright.async_api import async_playwright

from .vision_analyzer import analyze_ui


MAX_RETRIES = 3

OUTPUT_DIR = Path("outputs")
SCREENSHOT_DIR = Path("screenshots")

OUTPUT_DIR.mkdir(exist_ok=True)
SCREENSHOT_DIR.mkdir(exist_ok=True)


async def apply_css_and_verify(
    url: str,
    css_code: str,
    attempt: int,
):
    """
    Apply AI-generated CSS to the webpage,
    capture the modified UI, and ask the VLM
    to verify whether the issue is resolved.
    """

    screenshot_path = (
        SCREENSHOT_DIR
        / f"self_healed_attempt_{attempt}.png"
    )

    html_path = (
        OUTPUT_DIR
        / f"self_healed_attempt_{attempt}.html"
    )

    async with async_playwright() as p:

        browser = await p.chromium.launch(
            headless=True
        )

        page = await browser.new_page(
            viewport={
                "width": 390,
                "height": 844
            }
        )

        try:

            # Open website
            await page.goto(
                url,
                wait_until="networkidle"
            )

            # Apply AI-generated CSS
            await page.add_style_tag(
                content=css_code
            )

            # Capture modified UI
            await page.screenshot(
                path=str(screenshot_path),
                full_page=True
            )

            # Capture updated DOM
            html = await page.content()

            html_path.write_text(
                html,
                encoding="utf-8"
            )

        finally:

            await browser.close()

    # Send modified UI back to VLM
    result = await analyze_ui(
        screenshot_path=str(screenshot_path),
        html_path=str(html_path)
    )

    return {
        "result": result,
        "screenshot": str(screenshot_path),
        "html": str(html_path)
    }


async def self_healing_loop(
    url: str,
    css_code: str,
    html_path: str,
    max_retries: int = MAX_RETRIES,
):
    """
    Agentic self-healing loop.

    Plan
      ↓
    Execute
      ↓
    Evaluate
      ↓
    Retry
    """

    history = []

    current_css = css_code

    for attempt in range(
        1,
        max_retries + 1
    ):

        print(
            f"\n========== "
            f"SELF-HEALING ATTEMPT "
            f"{attempt}/{max_retries}"
            f" =========="
        )

        # ---------------------------------
        # Execute
        # ---------------------------------

        try:

            verification = (
                await apply_css_and_verify(
                    url=url,
                    css_code=current_css,
                    attempt=attempt
                )
            )

        except Exception as exc:

            print(
                f"Attempt failed: {exc}"
            )

            history.append({
                "attempt": attempt,
                "status": "error",
                "error": str(exc)
            })

            continue

        result = verification["result"]

        issues = [
            issue.model_dump()
            for issue in result.issues
        ]

        # ---------------------------------
        # Record result
        # ---------------------------------

        history.append({
            "attempt": attempt,
            "issues": issues,
            "screenshot": verification[
                "screenshot"
            ],
            "html": verification[
                "html"
            ]
        })

        # ---------------------------------
        # Evaluate
        # ---------------------------------

        if not result.issues:

            print(
                "\nUI FIX VERIFIED SUCCESSFULLY"
            )

            output = {
                "status": "fixed",
                "attempts": attempt,
                "history": history
            }

            save_result(output)

            return output

        print(
            f"{len(result.issues)} "
            f"issue(s) still detected."
        )

        # ---------------------------------
        # Retry with new AI-generated fix
        # ---------------------------------

        if result.suggested_fixes:

            next_css = None

            for fix in result.suggested_fixes:

                if fix.language.lower() == "css":

                    next_css = fix.code
                    break

            if next_css:

                current_css = next_css

                print(
                    "New CSS fix generated."
                )

            else:

                print(
                    "No CSS fix available."
                )

                break

        else:

            print(
                "No additional fix generated."
            )

            break

    # -------------------------------------
    # Maximum retries reached
    # -------------------------------------

    output = {
        "status": "not_fixed",
        "attempts": len(history),
        "history": history
    }

    save_result(output)

    return output


def save_result(
    result: dict
):

    output_path = (
        OUTPUT_DIR
        / "self_healing_result.json"
    )

    output_path.write_text(
        json.dumps(
            result,
            indent=4
        ),
        encoding="utf-8"
    )

    print(
        f"Result saved to {output_path}"
    )