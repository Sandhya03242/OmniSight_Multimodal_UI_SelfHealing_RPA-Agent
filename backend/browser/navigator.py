from __future__ import annotations

from pathlib import Path
from typing import Any

from playwright.async_api import async_playwright


SCREENSHOT_DIR = Path("screenshots")
OUTPUT_DIR = Path("outputs")

SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


VIEWPORTS = {
    "desktop": {"width": 1440, "height": 900},
    "tablet": {"width": 768, "height": 1024},
    "mobile": {"width": 390, "height": 844},
}


async def capture_page(
    page,
    name: str,
    viewport: dict[str, int],
) -> dict[str, Any]:

    screenshot_path = SCREENSHOT_DIR / f"{name}.png"
    html_path = OUTPUT_DIR / f"{name}.html"

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
        "path": str(screenshot_path),
        "html": str(html_path),
        "viewport": viewport,
    }


async def click_if_exists(
    page,
    selectors: list[str],
) -> bool:

    for selector in selectors:
        try:
            locator = page.locator(selector).first

            if await locator.count() > 0:
                await locator.wait_for(
                    state="visible",
                    timeout=3000,
                )
                await locator.click()
                await page.wait_for_timeout(500)
                return True

        except Exception:
            continue

    return False


async def run_browser_flow(
    url: str = "http://localhost:5173",
) -> dict[str, Any]:

    screenshots = []
    html_files = []

    async with async_playwright() as playwright:

        browser = await playwright.chromium.launch(
            headless=True
        )

        page = await browser.new_page(
            viewport=VIEWPORTS["desktop"]
        )

        try:

            # ==================================================
            # 1. OPEN HOME PAGE
            # ==================================================

            await page.goto(
                url,
                wait_until="domcontentloaded",
            )

            await page.wait_for_timeout(1000)

            result = await capture_page(
                page,
                "01_home",
                VIEWPORTS["desktop"],
            )

            screenshots.append({
                "name": result["name"],
                "path": result["path"],
                "viewport": result["viewport"],
            })

            html_files.append(result["html"])

            # ==================================================
            # 2. SHOP NOW
            # ==================================================

            shop_now = page.get_by_role(
                "button",
                name="Shop Now",
            )

            if await shop_now.count() > 0:

                await shop_now.first.click()

                await page.wait_for_timeout(700)

            result = await capture_page(
                page,
                "02_products",
                VIEWPORTS["desktop"],
            )

            screenshots.append({
                "name": result["name"],
                "path": result["path"],
                "viewport": result["viewport"],
            })

            html_files.append(result["html"])

            # ==================================================
            # 3. ADD PRODUCT TO CART
            # ==================================================

            added = await click_if_exists(
                page,
                [
                    "button:has-text('Add to Cart')",
                    "button:has-text('Add to cart')",
                    "[aria-label*='Add to Cart']",
                    "[aria-label*='Add to cart']",
                ],
            )

            if not added:

                buttons = page.get_by_role("button")

                count = await buttons.count()

                for i in range(count):

                    try:
                        button = buttons.nth(i)
                        text = (
                            await button.inner_text()
                        ).strip().lower()

                        if (
                            "add" in text
                            and "cart" in text
                        ):
                            await button.click()
                            added = True
                            break

                    except Exception:
                        continue

            await page.wait_for_timeout(500)

            result = await capture_page(
                page,
                "03_cart_item",
                VIEWPORTS["desktop"],
            )

            screenshots.append({
                "name": result["name"],
                "path": result["path"],
                "viewport": result["viewport"],
            })

            html_files.append(result["html"])

            # ==================================================
            # 4. OPEN CART
            # ==================================================

            await click_if_exists(
                page,
                [
                    "a:has-text('Cart')",
                    "button:has-text('Cart')",
                    "[href*='cart']",
                ],
            )

            await page.wait_for_timeout(700)

            result = await capture_page(
                page,
                "04_cart",
                VIEWPORTS["desktop"],
            )

            screenshots.append({
                "name": result["name"],
                "path": result["path"],
                "viewport": result["viewport"],
            })

            html_files.append(result["html"])

            # ==================================================
            # 5. CHECKOUT
            # ==================================================

            await click_if_exists(
                page,
                [
                    "button:has-text('Checkout')",
                    "a:has-text('Checkout')",
                    "[href*='checkout']",
                ],
            )

            await page.wait_for_timeout(700)

            result = await capture_page(
                page,
                "05_checkout",
                VIEWPORTS["desktop"],
            )

            screenshots.append({
                "name": result["name"],
                "path": result["path"],
                "viewport": result["viewport"],
            })

            html_files.append(result["html"])

            # ==================================================
            # 6. FILL CHECKOUT FORM
            # ==================================================

            fields = [
                (
                    "input[name='name']",
                    "OmniSight User",
                ),
                (
                    "input[name='email']",
                    "test@example.com",
                ),
                (
                    "input[name='address']",
                    "123 Demo Street",
                ),
                (
                    "input[name='city']",
                    "Kochi",
                ),
                (
                    "input[name='zip']",
                    "682001",
                ),
                (
                    "input[name='postalCode']",
                    "682001",
                ),
            ]

            for selector, value in fields:

                try:

                    field = page.locator(
                        selector
                    ).first

                    if await field.count() > 0:
                        await field.fill(value)

                except Exception:
                    continue

            result = await capture_page(
                page,
                "06_checkout_form",
                VIEWPORTS["desktop"],
            )

            screenshots.append({
                "name": result["name"],
                "path": result["path"],
                "viewport": result["viewport"],
            })

            html_files.append(result["html"])

            # ==================================================
            # 7. COMPLETE ORDER
            # ==================================================

            await click_if_exists(
                page,
                [
                    "button:has-text('Place Order')",
                    "button:has-text('Place order')",
                    "button:has-text('Complete Order')",
                    "button:has-text('Complete order')",
                    "button:has-text('Confirm')",
                    "button:has-text('Pay')",
                ],
            )

            await page.wait_for_timeout(1000)

            result = await capture_page(
                page,
                "07_order_complete",
                VIEWPORTS["desktop"],
            )

            screenshots.append({
                "name": result["name"],
                "path": result["path"],
                "viewport": result["viewport"],
            })

            html_files.append(result["html"])

            # ==================================================
            # 8. RESPONSIVE SCREENSHOTS
            # ==================================================

            for device, viewport in VIEWPORTS.items():

                await page.set_viewport_size(
                    viewport
                )

                await page.goto(
                    url,
                    wait_until="domcontentloaded",
                )

                await page.wait_for_timeout(500)

                result = await capture_page(
                    page,
                    f"responsive_{device}",
                    viewport,
                )

                screenshots.append({
                    "name": result["name"],
                    "path": result["path"],
                    "viewport": result["viewport"],
                })

                html_files.append(result["html"])

            return {
                "status": "success",
                "url": url,
                "screenshots": screenshots,
                "html_files": html_files,
            }

        except Exception as exc:

            return {
                "status": "failed",
                "url": url,
                "screenshots": screenshots,
                "html_files": html_files,
                "error": str(exc),
            }

        finally:

            await browser.close()


if __name__ == "__main__":

    import asyncio

    result = asyncio.run(
        run_browser_flow()
    )

    print(result)