from __future__ import annotations

from pathlib import Path
from typing import Any

from PIL import Image, ImageChops


# ============================================================
# CONFIGURATION
# ============================================================

SCREENSHOTS_DIR = Path("screenshots")
CHUNKS_DIR = Path("outputs/chunks")

DEFAULT_MAX_SIZE = (1024, 1024)

# Padding around detected/cropped regions
DEFAULT_PADDING = 30


# ============================================================
# DIRECTORY
# ============================================================

def ensure_chunk_directory() -> Path:
    """Create the directory used for optimized image chunks."""
    CHUNKS_DIR.mkdir(parents=True, exist_ok=True)
    return CHUNKS_DIR


# ============================================================
# IMAGE INFORMATION
# ============================================================

def get_image_info(image_path: str | Path) -> dict[str, Any]:
    """Return basic information about a screenshot."""

    path = Path(image_path)

    if not path.exists():
        raise FileNotFoundError(f"Image not found: {path}")

    with Image.open(path) as image:
        return {
            "path": str(path),
            "width": image.width,
            "height": image.height,
            "format": image.format,
            "mode": image.mode,
        }


# ============================================================
# RESIZE
# ============================================================

def resize_image(
    image: Image.Image,
    max_size: tuple[int, int] = DEFAULT_MAX_SIZE,
) -> Image.Image:
    """
    Resize an image while preserving its aspect ratio.

    The image is only reduced if it is larger than max_size.
    """

    resized = image.copy()
    resized.thumbnail(max_size, Image.Resampling.LANCZOS)

    return resized


# ============================================================
# BOUNDING BOX
# ============================================================

def clamp_bbox(
    bbox: tuple[int, int, int, int],
    width: int,
    height: int,
) -> tuple[int, int, int, int]:
    """Keep a bounding box inside the image boundaries."""

    left, top, right, bottom = bbox

    left = max(0, min(left, width))
    top = max(0, min(top, height))
    right = max(left, min(right, width))
    bottom = max(top, min(bottom, height))

    return left, top, right, bottom


def add_padding(
    bbox: tuple[int, int, int, int],
    width: int,
    height: int,
    padding: int = DEFAULT_PADDING,
) -> tuple[int, int, int, int]:
    """Expand a bounding box with safe padding."""

    left, top, right, bottom = bbox

    bbox = (
        left - padding,
        top - padding,
        right + padding,
        bottom + padding,
    )

    return clamp_bbox(bbox, width, height)


# ============================================================
# CROP
# ============================================================

def crop_region(
    image_path: str | Path,
    bbox: tuple[int, int, int, int],
    output_path: str | Path | None = None,
    padding: int = DEFAULT_PADDING,
    max_size: tuple[int, int] = DEFAULT_MAX_SIZE,
) -> Path:
    """
    Crop a specific region from a screenshot.

    bbox format:
        (left, top, right, bottom)
    """

    path = Path(image_path)

    if not path.exists():
        raise FileNotFoundError(f"Image not found: {path}")

    ensure_chunk_directory()

    with Image.open(path) as image:
        image = image.convert("RGB")

        bbox = add_padding(
            bbox,
            image.width,
            image.height,
            padding,
        )

        cropped = image.crop(bbox)

        cropped = resize_image(
            cropped,
            max_size=max_size,
        )

        if output_path is None:
            output_path = (
                CHUNKS_DIR
                / f"{path.stem}_focused.png"
            )

        output_path = Path(output_path)
        output_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        cropped.save(
            output_path,
            format="PNG",
            optimize=True,
        )

    print(
        f"[OPTIMIZATION] Focused region saved: "
        f"{output_path}"
    )

    return output_path


# ============================================================
# CENTER CROP
# ============================================================

def center_crop(
    image_path: str | Path,
    output_path: str | Path | None = None,
    crop_ratio: float = 0.70,
    max_size: tuple[int, int] = DEFAULT_MAX_SIZE,
) -> Path:
    """
    Crop the central portion of a screenshot.

    Useful as a fallback when no anomaly bounding box
    is available.
    """

    if not 0.1 <= crop_ratio <= 1.0:
        raise ValueError(
            "crop_ratio must be between 0.1 and 1.0"
        )

    path = Path(image_path)

    if not path.exists():
        raise FileNotFoundError(f"Image not found: {path}")

    ensure_chunk_directory()

    with Image.open(path) as image:
        image = image.convert("RGB")

        width, height = image.size

        crop_width = int(width * crop_ratio)
        crop_height = int(height * crop_ratio)

        left = (width - crop_width) // 2
        top = (height - crop_height) // 2

        bbox = (
            left,
            top,
            left + crop_width,
            top + crop_height,
        )

        cropped = image.crop(bbox)

        cropped = resize_image(
            cropped,
            max_size=max_size,
        )

        if output_path is None:
            output_path = (
                CHUNKS_DIR
                / f"{path.stem}_center.png"
            )

        output_path = Path(output_path)

        cropped.save(
            output_path,
            format="PNG",
            optimize=True,
        )

    print(
        f"[OPTIMIZATION] Center crop saved: "
        f"{output_path}"
    )

    return output_path


# ============================================================
# GRID CHUNKS
# ============================================================

def create_grid_chunks(
    image_path: str | Path,
    rows: int = 2,
    columns: int = 2,
    max_size: tuple[int, int] = DEFAULT_MAX_SIZE,
) -> list[Path]:
    """
    Split a screenshot into multiple chunks.

    Example:

        +---------+---------+
        | chunk 1 | chunk 2 |
        +---------+---------+
        | chunk 3 | chunk 4 |
        +---------+---------+
    """

    if rows < 1 or columns < 1:
        raise ValueError(
            "rows and columns must be >= 1"
        )

    path = Path(image_path)

    if not path.exists():
        raise FileNotFoundError(f"Image not found: {path}")

    ensure_chunk_directory()

    output_paths: list[Path] = []

    with Image.open(path) as image:
        image = image.convert("RGB")

        width, height = image.size

        chunk_width = width // columns
        chunk_height = height // rows

        for row in range(rows):
            for column in range(columns):

                left = column * chunk_width
                top = row * chunk_height

                right = (
                    width
                    if column == columns - 1
                    else (column + 1) * chunk_width
                )

                bottom = (
                    height
                    if row == rows - 1
                    else (row + 1) * chunk_height
                )

                chunk = image.crop(
                    (left, top, right, bottom)
                )

                chunk = resize_image(
                    chunk,
                    max_size=max_size,
                )

                output_path = (
                    CHUNKS_DIR
                    / (
                        f"{path.stem}"
                        f"_chunk_r{row + 1}"
                        f"_c{column + 1}.png"
                    )
                )

                chunk.save(
                    output_path,
                    format="PNG",
                    optimize=True,
                )

                output_paths.append(output_path)

                print(
                    f"[OPTIMIZATION] Chunk created: "
                    f"{output_path}"
                )

    return output_paths


# ============================================================
# FOCUSED SCREENSHOT
# ============================================================

def create_focused_chunk(
    image_path: str | Path,
    bbox: tuple[int, int, int, int] | None = None,
    output_path: str | Path | None = None,
) -> Path:
    """
    Main optimization function.

    If a bounding box is provided:
        crop that exact UI region.

    Otherwise:
        use a central crop as fallback.
    """

    if bbox is not None:
        return crop_region(
            image_path=image_path,
            bbox=bbox,
            output_path=output_path,
        )

    return center_crop(
        image_path=image_path,
        output_path=output_path,
    )


# ============================================================
# MULTIPLE FOCUSED REGIONS
# ============================================================

def create_multiple_chunks(
    image_path: str | Path,
    regions: list[tuple[int, int, int, int]],
) -> list[Path]:
    """
    Create multiple focused chunks from one screenshot.

    regions example:

    [
        (100, 200, 1200, 600),
        (100, 600, 1200, 850),
    ]
    """

    output_paths: list[Path] = []

    path = Path(image_path)

    for index, bbox in enumerate(regions, start=1):

        output_path = (
            CHUNKS_DIR
            / f"{path.stem}_region_{index}.png"
        )

        result = crop_region(
            image_path=image_path,
            bbox=bbox,
            output_path=output_path,
        )

        output_paths.append(result)

    return output_paths


# ============================================================
# SIMPLE ANOMALY REGION HEURISTIC
# ============================================================

def detect_content_region(
    image_path: str | Path,
) -> tuple[int, int, int, int]:
    """
    Lightweight fallback region detector.

    It removes large uniform borders/background areas
    and returns the bounding box of meaningful pixels.

    This is intentionally simple and CPU-friendly.
    """

    path = Path(image_path)

    if not path.exists():
        raise FileNotFoundError(f"Image not found: {path}")

    with Image.open(path) as image:
        image = image.convert("RGB")

        # Sample the top-left pixel as a likely background.
        background = Image.new(
            "RGB",
            image.size,
            image.getpixel((0, 0)),
        )

        difference = ImageChops.difference(
            image,
            background,
        )

        # Increase small differences.
        difference = difference.point(
            lambda value: 255 if value > 20 else 0
        )

        bbox = difference.getbbox()

        if bbox is None:
            return (
                0,
                0,
                image.width,
                image.height,
            )

        return bbox


# ============================================================
# OPTIMIZE SCREENSHOT
# ============================================================

def optimize_screenshot(
    image_path: str | Path,
    bbox: tuple[int, int, int, int] | None = None,
) -> dict[str, Any]:
    """
    Main entry point used by the Week 4 optimization layer.

    Returns information about the original screenshot
    and optimized focused screenshot.
    """

    path = Path(image_path)

    info = get_image_info(path)

    print(
        f"[OPTIMIZATION] Original image: "
        f"{info['width']}x{info['height']}"
    )

    if bbox is None:
        bbox = detect_content_region(path)

    focused_path = crop_region(
        image_path=path,
        bbox=bbox,
    )

    focused_info = get_image_info(
        focused_path
    )

    print(
        f"[OPTIMIZATION] Focused image: "
        f"{focused_info['width']}x"
        f"{focused_info['height']}"
    )

    return {
        "original": {
            "path": str(path),
            "width": info["width"],
            "height": info["height"],
        },
        "focused": {
            "path": str(focused_path),
            "width": focused_info["width"],
            "height": focused_info["height"],
        },
        "bbox": bbox,
        "status": "optimized",
    }


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    print("=" * 60)
    print("OMNISIGHT - IMAGE CHUNKER")
    print("=" * 60)

    # Change this to an existing screenshot if needed.
    test_image = (
        SCREENSHOTS_DIR
        / "healing_latest_desktop.png"
    )

    if test_image.exists():

        result = optimize_screenshot(
            test_image
        )

        print()
        print("[RESULT]")
        print(result)

    else:

        print(
            f"[INFO] Test image not found: "
            f"{test_image}"
        )

        print(
            "[INFO] Run the Playwright navigation/healing "
            "capture first."
        )