from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any

from playwright.async_api import (
    Browser,
    Page,
    async_playwright,
)


# ============================================================
# CONFIGURATION
# ============================================================

SCREENSHOT_DIR = Path("screenshots")
OUTPUT_DIR = Path("outputs")

BASE_URL = "http://localhost:5173"

VIEWPORTS: dict[str, dict[str, int]] = {
    "desktop": {
        "width": 1440,
        "height": 900,
    },
    "tablet": {
        "width": 768,
        "height": 1024,
    },
    "mobile": {
        "width": 390,
        "height": 844,
    },
}


# ============================================================
# DIRECTORY SETUP
# ============================================================

def ensure_directories() -> None:
    SCREENSHOT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )


# ============================================================
# PAGE CAPTURE
# ============================================================

async def capture_page(
    page: Page,
    name: str,
) -> dict[str, Any]:
    """
    Capture screenshot and raw HTML for the current page.
    """

    ensure_directories()

    screenshot_path = (
        SCREENSHOT_DIR / f"{name}.png"
    )

    html_path = (
        OUTPUT_DIR / f"{name}.html"
    )

    await page.screenshot(
        path=str(screenshot_path),
        full_page=True,
    )

    html = await page.content()

    html_path.write_text(
        html,
        encoding="utf-8",
    )

    return {
        "name": name,
        "screenshot": str(
            screenshot_path
        ),
        "html": str(
            html_path
        ),
    }


# ============================================================
# SAFE CLICK
# ============================================================

async def click_if_exists(
    page: Page,
    selector: str,
    timeout: int = 3000,
) -> bool:
    """
    Click an element if it exists.
    """

    try:
        locator = page.locator(selector)

        if await locator.count() == 0:
            return False

        await locator.first.click(
            timeout=timeout
        )

        return True

    except Exception:
        return False


# ============================================================
# SAFE FILL
# ============================================================

async def fill_if_exists(
    page: Page,
    selector: str,
    value: str,
    timeout: int = 3000,
) -> bool:
    """
    Fill an input if it exists.
    """

    try:
        locator = page.locator(selector)

        if await locator.count() == 0:
            return False

        await locator.first.fill(
            value,
            timeout=timeout,
        )

        return True

    except Exception:
        return False


# ============================================================
# PAGE WAIT
# ============================================================

async def _wait_for_page(
    page: Page,
    milliseconds: int = 1000,
) -> None:

    try:
        await page.wait_for_load_state(
            "networkidle",
            timeout=10000,
        )
    except Exception:
        pass

    await page.wait_for_timeout(
        milliseconds
    )


# ============================================================
# WEEK 1
# COMPLETE BROWSER AUTOMATION
# ============================================================

async def run_browser_flow(
    url: str = BASE_URL,
) -> dict[str, Any]:
    """
    Complete Week 1 browser automation.

    Flow:
        Home
        Products
        Add product
        Cart
        Checkout
        Checkout form
        Order complete
        Responsive screenshots
    """

    ensure_directories()

    screenshots: list[dict[str, Any]] = []

    async with async_playwright() as playwright:

        browser: Browser = await playwright.chromium.launch(
            headless=True
        )

        try:

            page = await browser.new_page(
                viewport=VIEWPORTS["desktop"]
            )

            # ==================================================
            # 01 HOME
            # ==================================================

            await page.goto(
                url,
                wait_until="networkidle",
                timeout=60000,
            )

            await _wait_for_page(page)

            result = await capture_page(
                page,
                "01_home",
            )

            screenshots.append(
                {
                    **result,
                    "viewport": VIEWPORTS[
                        "desktop"
                    ],
                }
            )

            # ==================================================
            # 02 PRODUCTS
            # ==================================================

            await click_if_exists(
                page,
                "text=Shop Now",
            )

            await _wait_for_page(page)

            result = await capture_page(
                page,
                "02_products",
            )

            screenshots.append(
                {
                    **result,
                    "viewport": VIEWPORTS[
                        "desktop"
                    ],
                }
            )

            # ==================================================
            # 03 CART ITEM
            # ==================================================

            add_button = page.locator(
                ".add-to-cart"
            )

            if await add_button.count() > 0:

                await add_button.first.click()

            else:

                await click_if_exists(
                    page,
                    "text=Add to Cart",
                )

            await _wait_for_page(page)

            result = await capture_page(
                page,
                "03_cart_item",
            )

            screenshots.append(
                {
                    **result,
                    "viewport": VIEWPORTS[
                        "desktop"
                    ],
                }
            )

            # ==================================================
            # 04 CART
            # ==================================================

            await click_if_exists(
                page,
                "text=/Cart/",
            )

            await _wait_for_page(page)

            result = await capture_page(
                page,
                "04_cart",
            )

            screenshots.append(
                {
                    **result,
                    "viewport": VIEWPORTS[
                        "desktop"
                    ],
                }
            )

            # ==================================================
            # 05 CHECKOUT
            # ==================================================

            await click_if_exists(
                page,
                "text=Checkout",
            )

            await _wait_for_page(page)

            result = await capture_page(
                page,
                "05_checkout",
            )

            screenshots.append(
                {
                    **result,
                    "viewport": VIEWPORTS[
                        "desktop"
                    ],
                }
            )

            # ==================================================
            # 06 CHECKOUT FORM
            # ==================================================

            await fill_if_exists(
                page,
                'input[name="firstName"]',
                "Omni",
            )

            await fill_if_exists(
                page,
                'input[name="lastName"]',
                "Sight",
            )

            await fill_if_exists(
                page,
                'input[name="email"]',
                "omnisight@example.com",
            )

            await fill_if_exists(
                page,
                'input[name="address"]',
                "123 AI Street",
            )

            await _wait_for_page(page)

            result = await capture_page(
                page,
                "06_checkout_form",
            )

            screenshots.append(
                {
                    **result,
                    "viewport": VIEWPORTS[
                        "desktop"
                    ],
                }
            )

            # ==================================================
            # 07 ORDER COMPLETE
            # ==================================================

            await click_if_exists(
                page,
                "text=/Place Order|Complete Order|Confirm Order/",
            )

            await _wait_for_page(page)

            result = await capture_page(
                page,
                "07_order_complete",
            )

            screenshots.append(
                {
                    **result,
                    "viewport": VIEWPORTS[
                        "desktop"
                    ],
                }
            )

            await page.close()

            # ==================================================
            # RESPONSIVE DESKTOP
            # ==================================================

            page = await browser.new_page(
                viewport=VIEWPORTS["desktop"]
            )

            await page.goto(
                url,
                wait_until="networkidle",
                timeout=60000,
            )

            await _wait_for_page(page)

            result = await capture_page(
                page,
                "responsive_desktop",
            )

            screenshots.append(
                {
                    **result,
                    "viewport": VIEWPORTS[
                        "desktop"
                    ],
                }
            )

            await page.close()

            # ==================================================
            # RESPONSIVE TABLET
            # ==================================================

            page = await browser.new_page(
                viewport=VIEWPORTS["tablet"]
            )

            await page.goto(
                url,
                wait_until="networkidle",
                timeout=60000,
            )

            await _wait_for_page(page)

            result = await capture_page(
                page,
                "responsive_tablet",
            )

            screenshots.append(
                {
                    **result,
                    "viewport": VIEWPORTS[
                        "tablet"
                    ],
                }
            )

            await page.close()

            # ==================================================
            # RESPONSIVE MOBILE
            # ==================================================

            page = await browser.new_page(
                viewport=VIEWPORTS["mobile"]
            )

            await page.goto(
                url,
                wait_until="networkidle",
                timeout=60000,
            )

            await _wait_for_page(page)

            result = await capture_page(
                page,
                "responsive_mobile",
            )

            screenshots.append(
                {
                    **result,
                    "viewport": VIEWPORTS[
                        "mobile"
                    ],
                }
            )

            await page.close()

        finally:

            await browser.close()

    return {
        "status": "success",
        "url": url,
        "screenshots": screenshots,
        "html_files": [
            item["html"]
            for item in screenshots
        ],
    }


# ============================================================
# WEEK 3
# FRESH HEALING CAPTURE
# ============================================================

async def run_healing_test(
    url: str = BASE_URL,
) -> dict[str, Any]:
    """
    Fresh browser capture for the Week 3
    LangGraph self-healing workflow.

    IMPORTANT:
    This function does NOT execute the Week 1
    checkout flow.

    It only captures:
        - Desktop
        - Mobile

    This allows the healing graph to detect a
    visual problem, modify source code, restart
    the browser, and verify the result.
    """

    ensure_directories()

    timestamp = datetime.now().strftime(
        "%Y%m%d_%H%M%S_%f"
    )

    screenshots: list[dict[str, Any]] = []

    async with async_playwright() as playwright:

        browser: Browser = await playwright.chromium.launch(
            headless=True
        )

        try:

            # ==================================================
            # HEALING DESKTOP
            # ==================================================

            page = await browser.new_page(
                viewport=VIEWPORTS["desktop"]
            )

            await page.goto(
                url,
                wait_until="networkidle",
                timeout=60000,
            )

            await _wait_for_page(
                page,
                milliseconds=1500,
            )

            desktop_name = (
                f"healing_{timestamp}_desktop"
            )

            result = await capture_page(
                page,
                desktop_name,
            )

            screenshots.append(
                {
                    **result,
                    "viewport": VIEWPORTS[
                        "desktop"
                    ],
                }
            )

            await page.close()

            # ==================================================
            # HEALING MOBILE
            # ==================================================

            page = await browser.new_page(
                viewport=VIEWPORTS["mobile"]
            )

            await page.goto(
                url,
                wait_until="networkidle",
                timeout=60000,
            )

            await _wait_for_page(
                page,
                milliseconds=1500,
            )

            mobile_name = (
                f"healing_{timestamp}_mobile"
            )

            result = await capture_page(
                page,
                mobile_name,
            )

            screenshots.append(
                {
                    **result,
                    "viewport": VIEWPORTS[
                        "mobile"
                    ],
                }
            )

            await page.close()

        finally:

            await browser.close()

    return {
        "status": "success",
        "url": url,
        "screenshots": screenshots,
        "html_files": [
            item["html"]
            for item in screenshots
        ],
    }


# ============================================================
# WEEK 3 ALIAS
# ============================================================

async def capture_healing_state(
    url: str = BASE_URL,
) -> dict[str, Any]:

    return await run_healing_test(
        url
    )


# ============================================================
# SYNC WRAPPERS
# ============================================================

def run_navigation(
    url: str = BASE_URL,
) -> dict[str, Any]:
    """
    Synchronous compatibility wrapper.

    Prefer run_browser_flow() from FastAPI.
    """

    import asyncio

    return asyncio.run(
        run_browser_flow(url)
    )


def run_healing_navigation(
    url: str = BASE_URL,
) -> dict[str, Any]:
    """
    Synchronous compatibility wrapper
    for the Week 3 healing capture.
    """

    import asyncio

    return asyncio.run(
        run_healing_test(url)
    )


# ============================================================
# LOCAL TEST
# ============================================================

if __name__ == "__main__":

    import asyncio

    result = asyncio.run(
        run_healing_test(BASE_URL)
    )

    print("\n" + "=" * 60)
    print("OMNISIGHT HEALING NAVIGATION")
    print("=" * 60)

    print(
        f"Status: {result.get('status')}"
    )

    print(
        f"URL: {result.get('url')}"
    )

    print(
        f"Screenshots: "
        f"{len(result.get('screenshots', []))}"
    )

    for item in result.get(
        "screenshots",
        [],
    ):

        print(
            f"\n[{item['name']}]"
        )

        print(
            f"Screenshot: "
            f"{item['screenshot']}"
        )

        print(
            f"HTML: "
            f"{item['html']}"
        )

        print(
            f"Viewport: "
            f"{item['viewport']}"
        )

    print("=" * 60)