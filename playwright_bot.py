from playwright.sync_api import sync_playwright
import os


os.makedirs("screenshots", exist_ok=True)

def capture_homepage():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)

        page = browser.new_page(
            viewport={"width": 1280, "height": 720}
        )

        page.goto("https://www.shopify.com")

        page.screenshot(
            path="screenshots/homepage.png",
            full_page=True
        )

        print("Screenshot Saved")

        browser.close()

if __name__ == "__main__":
    capture_homepage()