from pathlib import Path

from playwright.sync_api import sync_playwright


# ============================================================
# CONFIGURATION
# ============================================================

BASE_URL = "https://www.saucedemo.com"

USERNAME = "standard_user"
PASSWORD = "secret_sauce"

SCREENSHOT_DIR = Path("backend/screenshots")
HTML_DIR = Path("backend/outputs/html")


# ============================================================
# CREATE DIRECTORIES
# ============================================================

SCREENSHOT_DIR.mkdir(
    parents=True,
    exist_ok=True,
)

HTML_DIR.mkdir(
    parents=True,
    exist_ok=True,
)


# ============================================================
# SAVE SCREENSHOT
# ============================================================

def save_screenshot(
    page,
    filename: str,
):
    """
    Save the current page screenshot.
    """

    path = SCREENSHOT_DIR / filename

    page.screenshot(
        path=str(path),
        full_page=True,
    )

    return path


# ============================================================
# SAVE HTML
# ============================================================

def save_html(
    page,
    filename: str,
):
    """
    Save the current page HTML.
    """

    path = HTML_DIR / filename

    path.write_text(
        page.content(),
        encoding="utf-8",
    )

    return path


# ============================================================
# GET PAGE DIMENSIONS
# ============================================================

def get_page_dimensions(page):
    """
    Get browser viewport and document dimensions.
    """

    return page.evaluate(
        """
        () => ({
            viewport_width: window.innerWidth,
            viewport_height: window.innerHeight,
            document_width: document.documentElement.scrollWidth,
            document_height: document.documentElement.scrollHeight
        })
        """
    )


# ============================================================
# LOGIN
# ============================================================

def login(page):
    """
    Login to SauceDemo.
    """

    print("[NAVIGATION] Opening SauceDemo...")

    page.goto(
        BASE_URL,
        wait_until="domcontentloaded",
        timeout=30000,
    )

    print("[NAVIGATION] Filling username...")

    page.locator(
        "#user-name"
    ).fill(USERNAME)

    print("[NAVIGATION] Filling password...")

    page.locator(
        "#password"
    ).fill(PASSWORD)

    print("[NAVIGATION] Clicking login...")

    page.locator(
        "#login-button"
    ).click()

    page.wait_for_load_state(
        "domcontentloaded"
    )

    # Confirm login
    page.locator(
        ".inventory_list"
    ).wait_for(
        state="visible",
        timeout=10000,
    )

    print("[NAVIGATION] Login successful")


# ============================================================
# OPEN CHECKOUT
# ============================================================

def open_checkout(page):
    """
    Add a product and navigate to checkout.
    """

    print("[NAVIGATION] Adding product...")

    page.locator(
        ".inventory_item"
    ).first.locator(
        "button"
    ).click()

    print("[NAVIGATION] Product added")

    # Go to cart
    print("[NAVIGATION] Opening cart...")

    page.locator(
        ".shopping_cart_link"
    ).click()

    page.wait_for_load_state(
        "domcontentloaded"
    )

    # Checkout
    print("[NAVIGATION] Opening checkout...")

    page.locator(
        "#checkout"
    ).click()

    page.wait_for_load_state(
        "domcontentloaded"
    )

    # Fill checkout form
    print("[NAVIGATION] Filling checkout form...")

    page.locator(
        "#first-name"
    ).fill("Omni")

    page.locator(
        "#last-name"
    ).fill("Sight")

    page.locator(
        "#postal-code"
    ).fill("682001")

    print("[NAVIGATION] Clicking continue...")

    page.locator(
        "#continue"
    ).click()

    page.wait_for_load_state(
        "domcontentloaded"
    )

    print("[NAVIGATION] Checkout opened")


# ============================================================
# RUN ONE DEVICE
# ============================================================

def run_week1_device(
    browser,
    device_name: str,
    width: int,
    height: int,
):
    """
    Run the complete Week-1 navigation flow
    for one viewport.
    """

    print()
    print("=" * 60)
    print(
        f"[{device_name.upper()}] "
        f"Starting {width}x{height}"
    )
    print("=" * 60)

    context = browser.new_context(
        viewport={
            "width": width,
            "height": height,
        }
    )

    page = context.new_page()

    try:

        # ====================================================
        # LOGIN
        # ====================================================

        login(page)

        # ====================================================
        # PRODUCTS
        # ====================================================

        print(
            f"[{device_name}] Capturing products..."
        )

        products_screenshot = save_screenshot(
            page,
            f"{device_name}_products.png",
        )

        products_html = save_html(
            page,
            f"{device_name}_products.html",
        )

        print(
            f"[{device_name}] Products captured"
        )

        # ====================================================
        # ADD PRODUCT
        # ====================================================

        print(
            f"[{device_name}] Adding product..."
        )

        page.locator(
            ".inventory_item"
        ).first.locator(
            "button"
        ).click()

        print(
            f"[{device_name}] Product added"
        )

        # ====================================================
        # CART
        # ====================================================

        print(
            f"[{device_name}] Opening cart..."
        )

        page.locator(
            ".shopping_cart_link"
        ).click()

        page.wait_for_load_state(
            "domcontentloaded"
        )

        cart_screenshot = save_screenshot(
            page,
            f"{device_name}_cart.png",
        )

        cart_html = save_html(
            page,
            f"{device_name}_cart.html",
        )

        print(
            f"[{device_name}] Cart captured"
        )

        # ====================================================
        # CHECKOUT
        # ====================================================

        print(
            f"[{device_name}] Opening checkout..."
        )

        page.locator(
            "#checkout"
        ).click()

        page.wait_for_load_state(
            "domcontentloaded"
        )

        # Fill checkout
        page.locator(
            "#first-name"
        ).fill("Omni")

        page.locator(
            "#last-name"
        ).fill("Sight")

        page.locator(
            "#postal-code"
        ).fill("682001")

        # Continue
        page.locator(
            "#continue"
        ).click()

        page.wait_for_load_state(
            "domcontentloaded"
        )

        checkout_screenshot = save_screenshot(
            page,
            f"{device_name}_checkout.png",
        )

        checkout_html = save_html(
            page,
            f"{device_name}_checkout.html",
        )

        print(
            f"[{device_name}] Checkout captured"
        )

        # ====================================================
        # DIMENSIONS
        # ====================================================

        dimensions = get_page_dimensions(
            page
        )

        print(
            f"[{device_name}] Dimensions: "
            f"{dimensions}"
        )

        # ====================================================
        # CONTINUE BUTTON
        # ====================================================

        continue_visible = page.locator(
            "#continue"
        ).is_visible()

        print(
            f"[{device_name}] "
            f"Continue visible: "
            f"{continue_visible}"
        )

        # ====================================================
        # RESULT
        # ====================================================

        result = {
            "status": "passed",

            "viewport": {
                "width": width,
                "height": height,
            },

            "screenshots": {
                "products": str(
                    products_screenshot
                ),
                "cart": str(
                    cart_screenshot
                ),
                "checkout": str(
                    checkout_screenshot
                ),
            },

            "html": {
                "products": str(
                    products_html
                ),
                "cart": str(
                    cart_html
                ),
                "checkout": str(
                    checkout_html
                ),
            },

            "dimensions": dimensions,

            "continue_visible": (
                continue_visible
            ),
        }

        print(
            f"[{device_name}] "
            f"Navigation PASSED"
        )

        return result

    except Exception as error:

        print(
            f"[{device_name}] "
            f"Navigation FAILED"
        )

        print(
            f"[{device_name}] "
            f"ERROR: {repr(error)}"
        )

        return {
            "status": "failed",
            "viewport": {
                "width": width,
                "height": height,
            },
            "error": repr(error),
        }

    finally:

        context.close()

        print(
            f"[{device_name}] "
            f"Browser context closed"
        )


# ============================================================
# WEEK 1 NAVIGATION
# ============================================================

def run_week1():
    """
    Run OmniSight Week-1 navigation across
    desktop, tablet and mobile.
    """

    print()
    print("=" * 60)
    print("[NAVIGATION] Starting Playwright")
    print("=" * 60)

    results = {}

    # ========================================================
    # START PLAYWRIGHT
    # ========================================================

    with sync_playwright() as p:

        print(
            "[NAVIGATION] Launching Chromium..."
        )

        browser = p.chromium.launch(
            headless=True
        )

        print(
            "[NAVIGATION] Chromium launched"
        )

        try:

            # =================================================
            # DESKTOP
            # =================================================

            results["desktop"] = (
                run_week1_device(
                    browser,
                    "desktop",
                    1920,
                    1080,
                )
            )

            # =================================================
            # TABLET
            # =================================================

            results["tablet"] = (
                run_week1_device(
                    browser,
                    "tablet",
                    768,
                    1024,
                )
            )

            # =================================================
            # MOBILE
            # =================================================

            results["mobile"] = (
                run_week1_device(
                    browser,
                    "mobile",
                    375,
                    812,
                )
            )

        finally:

            browser.close()

            print(
                "[NAVIGATION] Chromium closed"
            )

    # ========================================================
    # FINAL RESULT
    # ========================================================

    print()
    print("=" * 60)
    print("[NAVIGATION] Navigation completed")
    print("=" * 60)

    return results


# ============================================================
# FASTAPI-SAFE WRAPPER
# ============================================================

def run_navigation_sync():
    """
    Entry point used by FastAPI.

    Playwright runs through its synchronous API,
    avoiding the Windows async subprocess issue.
    """

    print(
        "\n[NAVIGATION] Starting sync Playwright..."
    )

    result = run_week1()

    print(
        "[NAVIGATION] Sync navigation completed"
    )

    return result