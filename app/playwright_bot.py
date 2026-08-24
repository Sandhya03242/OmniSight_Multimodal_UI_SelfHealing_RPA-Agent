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
    """
    Capture the complete webpage and HTML.
    """

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

        # Full-page screenshot
        await page.screenshot(
            path=str(
                SCREENSHOT_DIR / screenshot_name
            ),
            full_page=True
        )

        # Capture HTML
        html = await page.content()

        html_path = (
            OUTPUT_DIR /
            f"{Path(screenshot_name).stem}.html"
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


async def run_checkout_flow( url: str = BASE_URL):
    """
    Complete mock e-commerce checkout flow.

    SauceDemo:
    Login
    -> Products
    -> Cart
    -> Checkout
    -> Checkout Overview
    """

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

        # ==========================================
        # 1. LOGIN PAGE
        # ==========================================

        await page.goto(
            url,
            wait_until="networkidle"
        )

        await page.screenshot(
            path=str(
                SCREENSHOT_DIR / "01_login.png"
            ),
            full_page=True
        )

        # ==========================================
        # 2. LOGIN
        # ==========================================

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
                SCREENSHOT_DIR / "02_products.png"
            ),
            full_page=True
        )

        # ==========================================
        # 3. ADD PRODUCT
        # ==========================================

        await page.click(
            "button:has-text('Add to cart')"
        )

        await page.screenshot(
            path=str(
                SCREENSHOT_DIR / "03_product_added.png"
            ),
            full_page=True
        )

        # ==========================================
        # 4. OPEN CART
        # ==========================================

        await page.click(
            ".shopping_cart_link"
        )

        await page.wait_for_load_state(
            "networkidle"
        )

        await page.screenshot(
            path=str(
                SCREENSHOT_DIR / "04_cart.png"
            ),
            full_page=True
        )

        # ==========================================
        # 5. CHECKOUT PAGE
        # ==========================================

        await page.click(
            "#checkout"
        )

        await page.wait_for_load_state(
            "networkidle"
        )

        await page.screenshot(
            path=str(
                SCREENSHOT_DIR / "05_checkout_info.png"
            ),
            full_page=True
        )

        # ==========================================
        # 6. CHECKOUT INFORMATION
        # ==========================================

        await page.fill(
            "#first-name",
            "Test"
        )

        await page.fill(
            "#last-name",
            "User"
        )

        await page.fill(
            "#postal-code",
            "679001"
        )

        await page.click(
            "#continue"
        )

        await page.wait_for_load_state(
            "networkidle"
        )

        await page.screenshot(
            path=str(
                SCREENSHOT_DIR / "06_checkout_overview.png"
            ),
            full_page=True
        )

        # ==========================================
        # 7. CAPTURE FINAL HTML
        # ==========================================

        html = await page.content()

        html_path = (
            OUTPUT_DIR /
            "checkout_overview.html"
        )

        html_path.write_text(
            html,
            encoding="utf-8"
        )

        await browser.close()

        return {
            "flow": "checkout",
            "screenshots": [
                "screenshots/01_login.png",
                "screenshots/02_products.png",
                "screenshots/03_product_added.png",
                "screenshots/04_cart.png",
                "screenshots/05_checkout_info.png",
                "screenshots/06_checkout_overview.png"
            ],
            "html": "outputs/checkout_overview.html"
        }


async def capture_responsive_pages(
    url: str = BASE_URL
):
    """
    Capture the complete webpage at
    desktop, tablet, and mobile sizes.
    """

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
                SCREENSHOT_DIR /
                screenshot_name
            )

            # Full-page responsive screenshot
            await page.screenshot(
                path=str(screenshot_path),
                full_page=True
            )

            # Capture HTML
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
                "screenshot": str(
                    screenshot_path
                ),
                "html": str(html_path)
            })

            await page.close()

        await browser.close()

    return results