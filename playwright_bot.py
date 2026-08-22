import os
from datetime import datetime
from playwright.sync_api import sync_playwright


BASE_URL = "https://www.saucedemo.com"

SCREENSHOT_DIR = "screenshots"
HTML_DIR = "html_states"


def run_browser_test(base_url: str = BASE_URL):

    os.makedirs(SCREENSHOT_DIR, exist_ok=True)
    os.makedirs(HTML_DIR, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    results = {
        "status": "started",
        "screenshots": [],
        "html_files": [],
        "states": []
    }

    with sync_playwright() as p:

        browser = p.chromium.launch(headless=True)

        page = browser.new_page(
            viewport={
                "width": 1280,
                "height": 720
            }
        )

        try:

            page.goto(
                base_url,
                wait_until="networkidle"
            )

            page.screenshot(
                path=f"{SCREENSHOT_DIR}/01_login_{timestamp}.png",
                full_page=True
            )

            html = page.content()

            html_path = f"{HTML_DIR}/01_login_{timestamp}.html"

            with open(html_path, "w", encoding="utf-8") as file:
                file.write(html)

            results["screenshots"].append(
                f"{SCREENSHOT_DIR}/01_login_{timestamp}.png"
            )

            results["html_files"].append(html_path)

            results["states"].append("login")


            page.fill(
                "#user-name",
                "standard_user"
            )

            page.fill(
                "#password",
                "secret_sauce"
            )

            page.click("#login-button")

            page.wait_for_load_state("networkidle")


            screenshot_path = (
                f"{SCREENSHOT_DIR}/02_products_{timestamp}.png"
            )

            html_path = (
                f"{HTML_DIR}/02_products_{timestamp}.html"
            )

            page.screenshot(
                path=screenshot_path,
                full_page=True
            )

            html = page.content()

            with open(html_path, "w", encoding="utf-8") as file:
                file.write(html)

            results["screenshots"].append(screenshot_path)
            results["html_files"].append(html_path)
            results["states"].append("products")


            page.click(
                "button[data-test='add-to-cart-sauce-labs-backpack']"
            )

            page.click(".shopping_cart_link")

            page.wait_for_load_state("networkidle")



            screenshot_path = (
                f"{SCREENSHOT_DIR}/03_cart_{timestamp}.png"
            )

            html_path = (
                f"{HTML_DIR}/03_cart_{timestamp}.html"
            )

            page.screenshot(
                path=screenshot_path,
                full_page=True
            )

            html = page.content()

            with open(html_path, "w", encoding="utf-8") as file:
                file.write(html)

            results["screenshots"].append(screenshot_path)
            results["html_files"].append(html_path)
            results["states"].append("cart")


            page.click("#checkout")

            page.fill(
                "#first-name",
                "Omni"
            )

            page.fill(
                "#last-name",
                "Sight"
            )

            page.fill(
                "#postal-code",
                "680001"
            )

            page.click("#continue")


            screenshot_path = (
                f"{SCREENSHOT_DIR}/04_checkout_{timestamp}.png"
            )

            html_path = (
                f"{HTML_DIR}/04_checkout_{timestamp}.html"
            )

            page.screenshot(
                path=screenshot_path,
                full_page=True
            )

            html = page.content()

            with open(html_path, "w", encoding="utf-8") as file:
                file.write(html)

            results["screenshots"].append(screenshot_path)
            results["html_files"].append(html_path)
            results["states"].append("checkout")

            results["status"] = "completed"

        except Exception as e:

            results["status"] = "failed"
            results["error"] = str(e)

        finally:

            browser.close()

    return results


if __name__ == "__main__":

    result = run_browser_test()

    print("\nOmniSight Browser Test")
    print("======================")
    print(f"Status: {result['status']}")

    print("\nScreenshots:")
    for screenshot in result["screenshots"]:
        print(f" - {screenshot}")

    print("\nHTML files:")
    for html_file in result["html_files"]:
        print(f" - {html_file}")