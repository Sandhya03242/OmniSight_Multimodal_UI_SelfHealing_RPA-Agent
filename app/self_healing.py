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
    html_path: str,
):
    """
    Apply AI-generated CSS to the webpage,
    capture a new screenshot, and verify
    the result using the VLM.
    """

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

        await page.goto(
            url,
            wait_until="networkidle"
        )

        # Apply generated CSS directly to the page
        await page.add_style_tag(
            content=css_code
        )

        screenshot_path = (
            SCREENSHOT_DIR /
            "self_healed.png"
        )

        await page.screenshot(
            path=str(screenshot_path),
            full_page=True
        )

        await browser.close()

    # Verify the modified UI
    result = await analyze_ui(
        screenshot_path=str(screenshot_path),
        html_path=html_path
    )

    return result


async def self_healing_loop(
    url: str,
    css_code: str,
    html_path: str,
    max_retries: int = MAX_RETRIES,
):
    """
    Self-healing loop:

    1. Apply AI-generated fix
    2. Capture new screenshot
    3. Analyze the result
    4. Repeat if the issue remains
    """

    history = []

    for attempt in range(1, max_retries + 1):

        print(
            f"\n===== SELF-HEALING ATTEMPT {attempt} ====="
        )

        result = await apply_css_and_verify(
            url=url,
            css_code=css_code,
            html_path=html_path,
        )

        history.append({
            "attempt": attempt,
            "issues": [
                issue.model_dump()
                for issue in result.issues
            ]
        })

        # No issues means the UI is considered fixed
        if not result.issues:

            print(
                "UI FIX VERIFIED SUCCESSFULLY"
            )

            output = {
                "status": "fixed",
                "attempts": attempt,
                "history": history,
            }

            save_result(output)

            return output

        print(
            f"{len(result.issues)} issue(s) still detected."
        )

        # Use the next generated fix if available
        if result.suggested_fixes:

            css_code = result.suggested_fixes[0].code

        else:

            print(
                "No additional fix generated."
            )
            break

    output = {
        "status": "not_fixed",
        "attempts": len(history),
        "history": history,
    }

    save_result(output)

    return output


def save_result(result: dict):

    output_path = (
        OUTPUT_DIR /
        "self_healing_result.json"
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