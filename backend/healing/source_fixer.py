from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def apply_css_to_source(
    css_fix,
    source_file="demo-store/src/index.css",
):
    path = ROOT / source_file

    if not path.exists():
        raise FileNotFoundError(
            f"Source file not found: {path}"
        )

    css_fix = css_fix.strip()

    if not css_fix:
        return {
            "success": False,
            "changed": False,
            "file": str(path),
            "message": "Empty CSS fix",
        }

    existing = path.read_text(
        encoding="utf-8"
    )

    marker = (
        "/* OmniSight Self-Healing Fix */"
    )

    if marker in existing:
        existing = existing.split(
            marker
        )[0].rstrip()

    updated = (
        existing
        + "\n\n"
        + marker
        + "\n"
        + css_fix
        + "\n"
    )

    path.write_text(
        updated,
        encoding="utf-8",
    )

    return {
        "success": True,
        "changed": True,
        "file": str(path),
    }