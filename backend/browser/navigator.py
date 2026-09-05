from pathlib import Path

from playwright.async_api import async_playwright


BASE_URL = "http://localhost:5173"

ROOT = Path(__file__).resolve().parents[2]

SCREENSHOTS = ROOT / "screenshots"
OUTPUTS = ROOT / "outputs"

DEVICES = {
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


async def capture_page(
    page,
    device,
    name,
):
    screenshot_path = (
        SCREENSHOTS
        / device
        / f"{name}.png"
    )

    html_path = (
        OUTPUTS
        / device
        / f"{name}.html"
    )

    screenshot_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    html_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    await page.screenshot(
        path=str(
            screenshot_path
        ),
        full_page=True,
    )

    html = await page.content()

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


async def run_browser(
    device,
    size,
):
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True
        )

        context = await browser.new_context(
            viewport=size
        )

        page = await context.new_page()

        await page.goto(
            BASE_URL,
            wait_until="networkidle",
        )

        home = await capture_page(
            page,
            device,
            "home",
        )

        await page.click(
            ".add-to-cart"
        )

        cart = await capture_page(
            page,
            device,
            "cart",
        )

        await browser.close()

        return {
            "device": device,
            "success": True,
            "pages": {
                "home": home,
                "cart": cart,
            },
        }


async def run_navigation():
    results = {}

    for device, size in DEVICES.items():
        try:
            results[device] = await run_browser(
                device,
                size,
            )

        except Exception as exc:
            results[device] = {
                "device": device,
                "success": False,
                "error": str(exc),
            }

    return {
        "success": all(
            item["success"]
            for item in results.values()
        ),
        "devices": results,
    }


if __name__ == "__main__":
    import asyncio

    result = asyncio.run(
        run_navigation()
    )

    print(result)