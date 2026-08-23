import os
from pathlib import Path

from playwright.async_api import async_playwright


BASE_URL = os.getenv(
    "BASE_URL",
    "https://www.saucedemo.com"
)

SCREENSHOT_DIR = Path("screenshots")
OUTPUT_DIR = Path("outputs")

SCREENSHOT_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)


async def capture_page(
    url: str = BASE_URL,
    viewport_width: int = 1280,
    viewport_height: int = 800,
    screenshot_name: str = "page.png"
):
    async with async_playwright() as p:

        browser = await p.chromium.launch(
            headless=True
        )

        page = await browser.new_page(
            viewport={
                "width": viewport_width,
                "height": viewport_height
            }
        )

        await page.goto(
            url,
            wait_until="networkidle"
        )

        await page.screenshot(
            path=str(SCREENSHOT_DIR / screenshot_name),
            full_page=True
        )

        html = await page.content()

        html_path = OUTPUT_DIR / (
            Path(screenshot_name).stem + ".html"
        )

        html_path.write_text(
            html,
            encoding="utf-8"
        )

        await browser.close()

        return {
            "url": url,
            "screenshot": str(
                SCREENSHOT_DIR / screenshot_name
            ),
            "html": str(html_path)
        }


async def run_checkout_flow():
    async with async_playwright() as p:

        browser = await p.chromium.launch(
            headless=True
        )

        page = await browser.new_page(
            viewport={
                "width": 1280,
                "height": 800
            }
        )

        # Login
        await page.goto(
            BASE_URL,
            wait_until="networkidle"
        )

        await page.fill(
            "#user-name",
            "standard_user"
        )

        await page.fill(
            "#password",
            "secret_sauce"
        )

        await page.click(
            "#login-button"
        )

        await page.wait_for_load_state(
            "networkidle"
        )

        await page.screenshot(
            path=str(
                SCREENSHOT_DIR / "01_products.png"
            ),
            full_page=True
        )

        # Add first product
        await page.click(
            "button:has-text('Add to cart')"
        )

        # Open cart
        await page.click(
            ".shopping_cart_link"
        )

        await page.wait_for_load_state(
            "networkidle"
        )

        await page.screenshot(
            path=str(
                SCREENSHOT_DIR / "02_cart.png"
            ),
            full_page=True
        )

        # Checkout
        await page.click(
            "#checkout"
        )

        await page.wait_for_load_state(
            "networkidle"
        )

        await page.screenshot(
            path=str(
                SCREENSHOT_DIR / "03_checkout.png"
            ),
            full_page=True
        )

        html = await page.content()

        html_path = OUTPUT_DIR / "checkout.html"

        html_path.write_text(
            html,
            encoding="utf-8"
        )

        await browser.close()

        return {
            "screenshot": "screenshots/03_checkout.png",
            "html": "outputs/checkout.html"
        }


async def capture_responsive_pages(
    url: str = BASE_URL
):
    viewports = [
        {
            "name": "desktop",
            "width": 1440,
            "height": 900
        },
        {
            "name": "tablet",
            "width": 768,
            "height": 1024
        },
        {
            "name": "mobile",
            "width": 390,
            "height": 844
        }
    ]

    results = []

    async with async_playwright() as p:

        browser = await p.chromium.launch(
            headless=True
        )

        for viewport in viewports:

            page = await browser.new_page(
                viewport={
                    "width": viewport["width"],
                    "height": viewport["height"]
                }
            )

            await page.goto(
                url,
                wait_until="networkidle"
            )

            screenshot_name = (
                f"{viewport['name']}.png"
            )

            screenshot_path = (
                SCREENSHOT_DIR / screenshot_name
            )

            await page.screenshot(
                path=str(screenshot_path),
                full_page=True
            )

            html = await page.content()

            html_path = (
                OUTPUT_DIR /
                f"{viewport['name']}.html"
            )

            html_path.write_text(
                html,
                encoding="utf-8"
            )

            results.append({
                "viewport": viewport["name"],
                "width": viewport["width"],
                "height": viewport["height"],
                "screenshot": str(screenshot_path),
                "html": str(html_path)
            })

            await page.close()

        await browser.close()

    return results