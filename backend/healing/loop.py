import json
import re
from pathlib import Path

from playwright.async_api import async_playwright


BASE_URL = "http://localhost:5173"

ROOT = Path(__file__).resolve().parents[2]

SCREENSHOTS = ROOT / "screenshots"
OUTPUTS = ROOT / "outputs"


def clean_css(css):
    if not css:
        return ""

    css = re.sub(
        r"```(?:css|CSS)?",
        "",
        css,
    )

    css = css.replace(
        "```",
        "",
    )

    css = css.strip()

    if "{" not in css:
        return ""

    if "}" not in css:
        return ""

    return css


async def apply_css_and_capture(
    css,
    device="mobile",
    filename="healed.png",
):
    screenshot_dir = (
        SCREENSHOTS / device
    )

    screenshot_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    screenshot_path = (
        screenshot_dir / filename
    )

    viewports = {
        "desktop": {
            "width": 1920,
            "height": 1080,
        },
        "tablet": {
            "width": 768,
            "height": 1024,
        },
        "mobile": {
            "width": 375,
            "height": 812,
        },
    }

    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True
        )

        context = await browser.new_context(
            viewport=viewports[device]
        )

        page = await context.new_page()

        await page.goto(
            BASE_URL,
            wait_until="networkidle",
        )

        css = clean_css(css)

        if css:
            await page.add_style_tag(
                content=css
            )

        await page.screenshot(
            path=str(
                screenshot_path
            ),
            full_page=True,
        )

        html = await page.content()

        await browser.close()

    html_path = (
        OUTPUTS
        / device
        / filename.replace(
            ".png",
            ".html",
        )
    )

    html_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    html_path.write_text(
        html,
        encoding="utf-8",
    )

    return {
        "screenshot": str(
            screenshot_path
        ),
        "html": str(
            html_path
        ),
    }


def save_healing_result(
    result,
    filename="healing_result.json",
):
    OUTPUTS.mkdir(
        parents=True,
        exist_ok=True,
    )

    path = OUTPUTS / filename

    path.write_text(
        json.dumps(
            result,
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    return path