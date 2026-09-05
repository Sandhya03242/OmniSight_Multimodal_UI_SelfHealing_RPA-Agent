from pathlib import Path

from playwright.async_api import async_playwright


BASE_URL = "http://localhost:5173"

ROOT = Path(__file__).resolve().parents[2]
CROPS = ROOT / "outputs" / "crops"

VIEWPORTS = {
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

SELECTORS = [
    "header",
    "main",
    ".product-grid",
    ".product-grid > div",
    ".product-title",
    ".add-to-cart",
    "section",
    "footer",
]


async def capture_component_crops(
    device="mobile",
):
    if device not in VIEWPORTS:
        raise ValueError(
            f"Unsupported device: {device}"
        )

    device_dir = CROPS / device
    device_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    viewport = VIEWPORTS[device]

    crops = []

    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True
        )

        context = await browser.new_context(
            viewport=viewport
        )

        page = await context.new_page()

        await page.goto(
            BASE_URL,
            wait_until="networkidle",
        )

        for selector_index, selector in enumerate(
            SELECTORS
        ):
            locator = page.locator(selector)

            try:
                count = await locator.count()
            except Exception:
                continue

            for element_index in range(count):
                element = locator.nth(
                    element_index
                )

                try:
                    if not await element.is_visible():
                        continue

                    box = await element.bounding_box()

                    if not box:
                        continue

                    width = int(box["width"])
                    height = int(box["height"])

                    if width < 20 or height < 20:
                        continue

                    screenshot_path = (
                        device_dir
                        / (
                            f"component_"
                            f"{selector_index}_"
                            f"{element_index}.png"
                        )
                    )

                    await element.screenshot(
                        path=str(
                            screenshot_path
                        )
                    )

                    crops.append({
                        "selector": selector,
                        "index": element_index,
                        "path": str(
                            screenshot_path
                        ),
                        "x": int(box["x"]),
                        "y": int(box["y"]),
                        "width": width,
                        "height": height,
                    })

                except Exception:
                    continue

        await browser.close()

    return crops


async def generate_chunks(
    device="mobile",
):
    crops = await capture_component_crops(
        device
    )

    return {
        "device": device,
        "total_crops": len(crops),
        "crops": crops,
    }


if __name__ == "__main__":
    import asyncio

    result = asyncio.run(
        generate_chunks("mobile")
    )

    print(
        f"Generated {result['total_crops']} crops"
    )

    for crop in result["crops"]:
        print(
            crop["selector"],
            "->",
            crop["path"],
        )