from pathlib import Path

from PIL import Image


OUTPUT_DIR = Path("outputs")
OUTPUT_DIR.mkdir(exist_ok=True)


def get_image_size(
    image_path: str
):
    """
    Return image width and height.
    """

    image = Image.open(
        image_path
    )

    return {
        "width": image.width,
        "height": image.height
    }


def crop_region(
    image_path: str,
    x: int,
    y: int,
    width: int,
    height: int,
    output_name: str = "cropped_ui.png"
):
    """
    Crop a suspicious UI region.
    """

    image = Image.open(
        image_path
    )

    image_width, image_height = image.size

    # Keep crop inside image boundaries
    left = max(0, x)
    top = max(0, y)

    right = min(
        image_width,
        x + width
    )

    bottom = min(
        image_height,
        y + height
    )

    if left >= right or top >= bottom:
        raise ValueError(
            "Invalid crop coordinates."
        )

    cropped = image.crop(
        (
            left,
            top,
            right,
            bottom
        )
    )

    output_path = (
        OUTPUT_DIR /
        output_name
    )

    cropped.save(
        output_path
    )

    return {
        "path": str(output_path),
        "width": cropped.width,
        "height": cropped.height
    }