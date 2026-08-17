from playwright.sync_api import sync_playwright
import os


BASE_URL = "https://www.saucedemo.com"


def save_html(page, filename):
    html = page.content()

    with open(
        f"screenshots/{filename}",
        "w",
        encoding="utf-8"
    ) as f:
        f.write(html)


def run_browser():

    os.makedirs("screenshots", exist_ok=True)

    with sync_playwright() as p:

        browser = p.chromium.launch(headless=True)

        desktop = browser.new_page(
            viewport={
                "width": 1280,
                "height": 720
            }
        )

        # 1. Open website
        desktop.goto(BASE_URL)

        desktop.screenshot(
            path="screenshots/01_login.png",
            full_page=True
        )

        save_html(desktop, "01_login.html")

        # 2. Login
        desktop.fill("#user-name", "standard_user")
        desktop.fill("#password", "secret_sauce")
        desktop.click("#login-button")

        desktop.wait_for_load_state("networkidle")

        desktop.screenshot(
            path="screenshots/02_products.png",
            full_page=True
        )

        save_html(desktop, "02_products.html")

        # 3. Add product to cart
        desktop.click("#add-to-cart-sauce-labs-backpack")

        desktop.screenshot(
            path="screenshots/03_product_added.png",
            full_page=True
        )

        save_html(desktop, "03_product_added.html")

        # 4. Open cart
        desktop.click(".shopping_cart_link")

        desktop.wait_for_load_state("networkidle")

        desktop.screenshot(
            path="screenshots/04_cart.png",
            full_page=True
        )

        save_html(desktop, "04_cart.html")

        # 5. Checkout
        desktop.click("#checkout")

        desktop.fill("#first-name", "Test")
        desktop.fill("#last-name", "User")
        desktop.fill("#postal-code", "679001")

        desktop.screenshot(
            path="screenshots/05_checkout.png",
            full_page=True
        )

        save_html(desktop, "05_checkout.html")

        # 6. Mobile responsive screenshot
        mobile = browser.new_page(
            viewport={
                "width": 390,
                "height": 844
            }
        )

        mobile.goto(BASE_URL)

        mobile.fill("#user-name", "standard_user")
        mobile.fill("#password", "secret_sauce")
        mobile.click("#login-button")

        mobile.wait_for_load_state("networkidle")

        mobile.screenshot(
            path="screenshots/06_mobile_products.png",
            full_page=True
        )

        save_html(mobile, "06_mobile_products.html")

        print("Browser automation completed successfully.")
        print("Screenshots and HTML saved in ./screenshots/")

        browser.close()


if __name__ == "__main__":
    run_browser()