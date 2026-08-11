from playwright.sync_api import sync_playwright
import os

# Create the screenshots folder if it doesn't already exist
os.makedirs("screenshots", exist_ok=True)


def capture_homepage():
    # Start Playwright
    with sync_playwright() as p:
        
        # Launch Chromium browser in headless mode
        browser = p.chromium.launch(headless=True)

        # Create a new browser page with a 1280x720 viewport
        page = browser.new_page(
            viewport={"width": 1280, "height": 720}
        )

        # Open the Shopify homepage
        page.goto("https://www.shopify.com")

        # Take a full-page screenshot and save it
        # inside the screenshots folder
        page.screenshot(
            path="screenshots/homepage.png",
            full_page=True
        )

        # Print confirmation message
        print("Screenshot Saved")

        # Close the browser
        browser.close()


# Run the function only when this file is executed directly
if __name__ == "__main__":
    capture_homepage()