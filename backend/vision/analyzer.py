from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

import torch
from PIL import Image
from transformers import AutoModelForMultimodalLM, AutoProcessor

from backend.vision.image_chunker import optimize_screenshot
from backend.vision.prompt import (
    HEALING_PROMPT,
    VERIFICATION_PROMPT,
    VISION_PROMPT,
)


# ============================================================
# CONFIGURATION
# ============================================================

MODEL_ID = "Qwen/Qwen3.5-0.8B"

MAX_HTML_LENGTH = 6000
MAX_SOURCE_LENGTH = 10000
MAX_NEW_TOKENS = 500

ENABLE_IMAGE_OPTIMIZATION = True
HTML_REDUCTION_ENABLED = True


# ============================================================
# VISION ANALYZER
# ============================================================

class VisionAnalyzer:

    def __init__(
        self,
        model_id: str = MODEL_ID,
    ) -> None:

        self.model_id = model_id

        print("=" * 60)
        print("Loading OmniSight Vision Model")
        print("=" * 60)

        print(f"Model: {model_id}")
        print("Device: CPU")

        print("Loading processor...")

        self.processor = AutoProcessor.from_pretrained(
            model_id
        )

        print("Loading multimodal model...")

        self.model = AutoModelForMultimodalLM.from_pretrained(
            model_id,
            dtype=torch.float32,
            device_map="cpu",
        )

        self.model.eval()

        print("Vision model loaded successfully.")

        print(
            f"[WEEK 4] Image optimization: "
            f"{ENABLE_IMAGE_OPTIMIZATION}"
        )

        print(
            f"[WEEK 4] HTML reduction: "
            f"{HTML_REDUCTION_ENABLED}"
        )

    # ========================================================
    # MODEL GENERATION
    # ========================================================

    def _generate(
        self,
        image: Image.Image,
        prompt: str,
    ) -> str:

        messages = [
            {
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "image": image,
                    },
                    {
                        "type": "text",
                        "text": prompt,
                    },
                ],
            }
        ]

        inputs = self.processor.apply_chat_template(
            messages,
            add_generation_prompt=True,
            tokenize=True,
            return_dict=True,
            return_tensors="pt",
        )

        inputs = {
            key: value.to("cpu")
            if hasattr(value, "to")
            else value
            for key, value in inputs.items()
        }

        with torch.no_grad():

            outputs = self.model.generate(
                **inputs,
                max_new_tokens=MAX_NEW_TOKENS,
                do_sample=False,
            )

        input_length = inputs[
            "input_ids"
        ].shape[-1]

        generated_tokens = outputs[
            0
        ][input_length:]

        response = self.processor.decode(
            generated_tokens,
            skip_special_tokens=True,
        ).strip()

        return response

    # ========================================================
    # IMAGE OPTIMIZATION
    # ========================================================

    def _prepare_image(
        self,
        screenshot_path: str | Path,
    ) -> tuple[Image.Image, dict[str, Any]]:

        screenshot_file = Path(
            screenshot_path
        )

        if not screenshot_file.exists():

            raise FileNotFoundError(
                f"Screenshot not found: "
                f"{screenshot_file}"
            )

        if ENABLE_IMAGE_OPTIMIZATION:

            print("=" * 60)
            print("WEEK 4 IMAGE OPTIMIZATION")
            print("=" * 60)

            optimization = optimize_screenshot(
                screenshot_file
            )

            focused_path = Path(
                optimization["focused"]["path"]
            )

            image = Image.open(
                focused_path
            ).convert("RGB")

            print(
                "[OPTIMIZATION] Original image: "
                f"{optimization['original']['width']}x"
                f"{optimization['original']['height']}"
            )

            print(
                "[OPTIMIZATION] Focused image: "
                f"{optimization['focused']['width']}x"
                f"{optimization['focused']['height']}"
            )

            print(
                "[OPTIMIZATION] Bounding box: "
                f"{optimization.get('bbox')}"
            )

            print(
                "[OPTIMIZATION] "
                "Sending focused image to VLM"
            )

            return image, optimization

        image = Image.open(
            screenshot_file
        ).convert("RGB")

        return image, {
            "status": "disabled",
            "original": {
                "path": str(screenshot_file),
                "width": image.width,
                "height": image.height,
            },
            "focused": {
                "path": str(screenshot_file),
                "width": image.width,
                "height": image.height,
            },
        }

    # ========================================================
    # HTML REDUCTION
    # ========================================================

    def _reduce_html(
        self,
        html: str,
        max_length: int = MAX_HTML_LENGTH,
    ) -> tuple[str, dict[str, Any]]:

        original_length = len(html)

        if not HTML_REDUCTION_ENABLED:

            reduced = html[:max_length]

            return reduced, {
                "enabled": False,
                "original_length": original_length,
                "reduced_length": len(reduced),
            }

        reduced = re.sub(
            r"<script\b[^>]*>.*?</script>",
            "",
            html,
            flags=re.IGNORECASE | re.DOTALL,
        )

        reduced = re.sub(
            r"<style\b[^>]*>.*?</style>",
            "",
            reduced,
            flags=re.IGNORECASE | re.DOTALL,
        )

        reduced = re.sub(
            r"<!--.*?-->",
            "",
            reduced,
            flags=re.DOTALL,
        )

        reduced = re.sub(
            r"\s+",
            " ",
            reduced,
        ).strip()

        reduced = reduced[:max_length]

        print(
            "[OPTIMIZATION] HTML reduced: "
            f"{original_length} → {len(reduced)} chars"
        )

        return reduced, {
            "enabled": True,
            "original_length": original_length,
            "reduced_length": len(reduced),
        }

    # ========================================================
    # LOAD HTML
    # ========================================================

    def _load_html(
        self,
        html_path: str | Path,
    ) -> tuple[str, dict[str, Any]]:

        html_file = Path(
            html_path
        )

        if not html_file.exists():

            raise FileNotFoundError(
                f"HTML file not found: "
                f"{html_file}"
            )

        html = html_file.read_text(
            encoding="utf-8",
            errors="ignore",
        )

        return self._reduce_html(
            html
        )

    # ========================================================
    # UI ANALYSIS
    # ========================================================

    def analyze(
        self,
        screenshot_path: str,
        html_path: str,
    ) -> dict[str, Any]:

        screenshot_file = Path(
            screenshot_path
        )

        html_file = Path(
            html_path
        )

        if not screenshot_file.exists():

            raise FileNotFoundError(
                f"Screenshot not found: "
                f"{screenshot_file}"
            )

        if not html_file.exists():

            raise FileNotFoundError(
                f"HTML file not found: "
                f"{html_file}"
            )

        print("=" * 60)
        print("Starting UI Analysis")
        print("=" * 60)

        print(
            f"Screenshot: {screenshot_file}"
        )

        print(
            f"HTML: {html_file}"
        )

        image, optimization = self._prepare_image(
            screenshot_file
        )

        html, html_optimization = self._load_html(
            html_file
        )

        prompt = (
            VISION_PROMPT
            + "\n\nOPTIMIZATION CONTEXT:\n"
            + (
                "Analyze the focused screenshot together "
                "with the reduced HTML. Identify only "
                "real visual UI problems. "
                "Do not report normal UI elements as issues."
            )
            + "\n\nREDUCED HTML:\n"
            + html
        )

        print(
            "[OPTIMIZATION] "
            "Image + reduced HTML prepared."
        )

        print("Preparing model input...")

        print(
            "Running Qwen3.5-0.8B inference..."
        )

        response = self._generate(
            image=image,
            prompt=prompt,
        )

        print("=" * 60)
        print("RAW MODEL RESPONSE")
        print("=" * 60)

        print(response)

        issues = self._parse_response(
            response
        )

        print("=" * 60)
        print(
            f"Detected Issues: {len(issues)}"
        )
        print("=" * 60)

        return {
            "status": "success",
            "model": self.model_id,
            "screenshot": str(
                screenshot_file
            ),
            "html": str(
                html_file
            ),
            "optimization": {
                "image": optimization,
                "html": html_optimization,
            },
            "issues": issues,
            "raw_response": response,
        }

    # ========================================================
    # GENERATE HEALING FIX
    # ========================================================

    def generate_healing_fix(
        self,
        screenshot_path: str,
        issue: dict[str, Any],
        source_code: str,
    ) -> dict[str, Any]:

        screenshot_file = Path(
            screenshot_path
        )

        if not screenshot_file.exists():

            raise FileNotFoundError(
                f"Screenshot not found: "
                f"{screenshot_file}"
            )

        # Keep complete source for validation.
        original_source_code = source_code

        # Only limit source sent to VLM.
        model_source_code = source_code[
            :MAX_SOURCE_LENGTH
        ]

        image, optimization = self._prepare_image(
            screenshot_file
        )

        issue_json = json.dumps(
            issue,
            indent=2,
            ensure_ascii=False,
        )

        print("=" * 60)
        print("GENERATING HEALING FIX")
        print("=" * 60)

        print(
            f"[HEALING] Source length: "
            f"{len(model_source_code)} chars"
        )

        prompt = (
            HEALING_PROMPT
            + "\n\nDETECTED ISSUE:\n"
            + issue_json
            + "\n\nACTUAL SOURCE CODE:\n"
            + model_source_code
            + "\n\nSTRICT SOURCE PATCH RULES:\n"
            + "1. Return ONLY valid JSON.\n"
            + "2. Return a 'fixes' array.\n"
            + "3. 'old' MUST be exact source code copied "
            + "from ACTUAL SOURCE CODE.\n"
            + "4. 'new' MUST be actual replacement source code.\n"
            + "5. 'old' and 'new' MUST be different.\n"
            + "6. NEVER put the issue description into 'old'.\n"
            + "7. NEVER put the issue description into 'new'.\n"
            + "8. The old string MUST exist literally "
            + "inside the source.\n"
            + "9. Make the smallest possible source change.\n"
            + "10. Prefer existing JSX/Tailwind className "
            + "changes.\n"
            + "11. Do not invent selectors or classes "
            + "unless they are valid Tailwind classes.\n"
            + "12. Do not return CSS explanations instead "
            + "of source.\n"
            + "13. Do not return markdown.\n"
            + "14. If no exact safe patch can be created, "
            + "return {\"fixes\":[]}.\n\n"
            + "Required JSON format:\n"
            + '{'
            + '"fixes":['
            + '{'
            + '"old":"exact source code",'
            + '"new":"replacement source code",'
            + '"reason":"short reason"'
            + '}'
            + ']'
            + '}'
        )

        print(
            "[VLM] Generating source patch..."
        )

        response = self._generate(
            image=image,
            prompt=prompt,
        )

        print("=" * 60)
        print("RAW HEALING RESPONSE")
        print("=" * 60)

        print(response)

        fixes = self._parse_source_fixes(
            response=response,
            source_code=original_source_code,
        )

        # ====================================================
        # DETERMINISTIC FALLBACK
        # ====================================================

        if not fixes:

            print(
                "[VLM] No valid exact source patch found."
            )

            print(
                "[HEALING] Checking deterministic "
                "source fallback..."
            )

            fixes = self._generate_fallback_fixes(
                issue=issue,
                source_code=original_source_code,
            )

        if fixes:

            print(
                f"[VLM] Number of fixes: "
                f"{len(fixes)}"
            )

            for index, fix in enumerate(
                fixes,
                start=1,
            ):

                print(
                    f"[VLM] Fix {index}:"
                )

                print(
                    f"  OLD: {fix['old']}"
                )

                print(
                    f"  NEW: {fix['new']}"
                )

            return {
                "status": "success",
                "fix_type": "source",
                "element": issue.get(
                    "element"
                ),
                "description": issue.get(
                    "description",
                    "",
                ),
                "code": None,
                "fixes": fixes,
                "candidate": True,
                "raw_response": response,
                "optimization": optimization,
            }

        print(
            "[HEALING] No usable source fix."
        )

        return {
            "status": "failed",
            "fix_type": "source",
            "element": issue.get(
                "element"
            ),
            "description": issue.get(
                "description",
                "",
            ),
            "code": None,
            "fixes": [],
            "candidate": False,
            "raw_response": response,
            "optimization": optimization,
        }

    # ========================================================
    # PARSE SOURCE FIXES
    # ========================================================

    def _parse_source_fixes(
        self,
        response: str,
        source_code: str,
    ) -> list[dict[str, str]]:

        response = self._remove_code_fences(
            response
        )

        data = self._extract_json_object(
            response
        )

        if not isinstance(
            data,
            dict,
        ):

            return []

        raw_fixes = data.get(
            "fixes",
            [],
        )

        if not isinstance(
            raw_fixes,
            list,
        ):

            return []

        valid_fixes: list[dict[str, str]] = []

        for index, item in enumerate(
            raw_fixes,
            start=1,
        ):

            if not isinstance(
                item,
                dict,
            ):
                continue

            old = item.get(
                "old"
            )

            new = item.get(
                "new"
            )

            reason = item.get(
                "reason",
                "",
            )

            if not isinstance(
                old,
                str,
            ):

                print(
                    f"[VLM] Fix {index} rejected: "
                    "'old' is not source text."
                )

                continue

            if not isinstance(
                new,
                str,
            ):

                print(
                    f"[VLM] Fix {index} rejected: "
                    "'new' is not source text."
                )

                continue

            old = old.strip()
            new = new.strip()

            if not old or not new:

                print(
                    f"[VLM] Fix {index} rejected: "
                    "empty old/new."
                )

                continue

            if old == new:

                print(
                    f"[VLM] Fix {index} rejected: "
                    "old and new are identical."
                )

                continue

            # CRITICAL:
            # old must actually exist in source.
            if old not in source_code:

                print(
                    f"[VLM] Fix {index} rejected: "
                    "old pattern not found in source."
                )

                continue

            valid_fixes.append(
                {
                    "old": old,
                    "new": new,
                    "reason": str(
                        reason
                    ),
                }
            )

        return valid_fixes

    # ========================================================
    # DETERMINISTIC FALLBACK
    # ========================================================

    def _generate_fallback_fixes(
        self,
        issue: dict[str, Any],
        source_code: str,
    ) -> list[dict[str, str]]:

        issue_text = " ".join(
            [
                str(
                    issue.get(
                        "type",
                        "",
                    )
                ),
                str(
                    issue.get(
                        "description",
                        "",
                    )
                ),
                str(
                    issue.get(
                        "element",
                        "",
                    )
                ),
                str(
                    issue.get(
                        "suggested_fix",
                        "",
                    )
                ),
            ]
        ).lower()

        print(
            "[FALLBACK] Issue context:"
        )

        print(
            issue_text
        )

        is_overlap = any(
            keyword in issue_text
            for keyword in (
                "overlap",
                "overlapping",
                "collide",
                "collision",
                "positioned directly",
                "cover",
                "covers",
            )
        )

        is_product_issue = any(
            keyword in issue_text
            for keyword in (
                "product",
                "product card",
                "add to cart",
                "product title",
                "product image",
                "card",
            )
        )

        # ====================================================
        # 1. PRODUCT CARD STRUCTURAL FIX
        #
        # This MUST come before image-height fixes.
        #
        # For issues such as:
        #
        # "Smart Watch title overlaps product image"
        #
        # or:
        #
        # "Add to Cart button overlaps image"
        #
        # normal vertical flex flow is a safer deterministic
        # fix than blindly changing image height.
        # ====================================================

        if is_overlap and is_product_issue:

            product_card_patterns = [

                (
                    'className="bg-white rounded-xl shadow-md"',
                    'className="bg-white rounded-xl shadow-md flex flex-col"',
                    (
                        "Convert the product card into a "
                        "vertical flex container so the "
                        "image, title, content and button "
                        "remain in normal document flow."
                    ),
                ),

                (
                    'className="bg-white rounded-xl shadow-md overflow-hidden"',
                    'className="bg-white rounded-xl shadow-md flex flex-col overflow-hidden"',
                    (
                        "Add a vertical flex layout to the "
                        "existing product card while "
                        "preserving overflow clipping."
                    ),
                ),

                (
                    'className="bg-white rounded-xl shadow-md overflow-hidden"',
                    'className="bg-white rounded-xl shadow-md flex flex-col"',
                    (
                        "Add a vertical flex layout to "
                        "prevent product elements from "
                        "overlapping."
                    ),
                ),

                (
                    'className="bg-white rounded-lg shadow-md"',
                    'className="bg-white rounded-lg shadow-md flex flex-col"',
                    (
                        "Use vertical flex layout for "
                        "normal product-card content flow."
                    ),
                ),

                (
                    'className="bg-white rounded-lg shadow-lg"',
                    'className="bg-white rounded-lg shadow-lg flex flex-col"',
                    (
                        "Use vertical flex layout to "
                        "prevent card content overlap."
                    ),
                ),
            ]

            for old, new, reason in product_card_patterns:

                if old in source_code:

                    print(
                        "[FALLBACK] Product card "
                        "flex-column layout detected."
                    )

                    print(
                        f"[FALLBACK] OLD: {old}"
                    )

                    print(
                        f"[FALLBACK] NEW: {new}"
                    )

                    return [
                        {
                            "old": old,
                            "new": new,
                            "reason": reason,
                        }
                    ]

        # ====================================================
        # 2. RESPONSIVE GRID
        # ====================================================

        grid_fixes = [

            (
                'className="grid grid-cols-4 gap-0 w-[1200px]"',
                (
                    'className="grid grid-cols-1 '
                    'sm:grid-cols-2 lg:grid-cols-4 '
                    'gap-6 w-full"'
                ),
                (
                    "Replace fixed-width product grid "
                    "with a responsive Tailwind grid."
                ),
            ),

            (
                'className="grid grid-cols-4 gap-0"',
                (
                    'className="grid grid-cols-1 '
                    'sm:grid-cols-2 lg:grid-cols-4 '
                    'gap-6"'
                ),
                (
                    "Make the product grid responsive "
                    "across desktop and mobile."
                ),
            ),

            (
                'className="grid grid-cols-4 w-[1200px]"',
                (
                    'className="grid grid-cols-1 '
                    'sm:grid-cols-2 lg:grid-cols-4 '
                    'gap-6 w-full"'
                ),
                (
                    "Remove the fixed-width layout and "
                    "use responsive grid columns."
                ),
            ),

            (
                'className="grid grid-cols-3 gap-0"',
                (
                    'className="grid grid-cols-1 '
                    'sm:grid-cols-2 lg:grid-cols-3 '
                    'gap-6"'
                ),
                (
                    "Make the three-column grid "
                    "responsive."
                ),
            ),
        ]

        if any(
            keyword in issue_text
            for keyword in (
                "responsive",
                "mobile",
                "tablet",
                "grid",
                "screen width",
            )
        ):

            for old, new, reason in grid_fixes:

                if old in source_code:

                    print(
                        "[FALLBACK] Responsive grid "
                        "source pattern found."
                    )

                    return [
                        {
                            "old": old,
                            "new": new,
                            "reason": reason,
                        }
                    ]

        # ====================================================
        # 3. FIXED WIDTH
        # ====================================================

        fixed_width_fixes = [

            (
                "w-[1200px]",
                "w-full",
                (
                    "Replace the fixed 1200px width "
                    "with a responsive full-width layout."
                ),
            ),

            (
                "w-[1000px]",
                "w-full",
                (
                    "Replace the fixed 1000px width "
                    "with a responsive full-width layout."
                ),
            ),

            (
                "w-[900px]",
                "w-full",
                (
                    "Replace the fixed 900px width "
                    "with a responsive full-width layout."
                ),
            ),

            (
                "w-[700px]",
                "w-full max-w-[700px]",
                (
                    "Keep the maximum width while "
                    "allowing responsive shrinking."
                ),
            ),

            (
                "w-[600px]",
                "w-full max-w-[600px]",
                (
                    "Keep the maximum width while "
                    "allowing responsive shrinking."
                ),
            ),
        ]

        if any(
            keyword in issue_text
            for keyword in (
                "fixed width",
                "too wide",
                "screen overflow",
                "horizontal overflow",
            )
        ):

            for old, new, reason in fixed_width_fixes:

                if old in source_code:

                    print(
                        "[FALLBACK] Fixed-width "
                        "source pattern found."
                    )

                    return [
                        {
                            "old": old,
                            "new": new,
                            "reason": reason,
                        }
                    ]

        # ====================================================
        # 4. PRODUCT IMAGE HEIGHT
        # ====================================================

        image_fixes = [

            (
                'className="w-full h-14 object-cover"',
                'className="w-full h-48 object-cover"',
            ),

            (
                'className="w-full h-16 object-cover"',
                'className="w-full h-48 object-cover"',
            ),

            (
                'className="w-full h-20 object-cover"',
                'className="w-full h-48 object-cover"',
            ),

            (
                'className="w-full h-24 object-cover"',
                'className="w-full h-48 object-cover"',
            ),

            (
                'className="h-14 w-full object-cover"',
                'className="h-48 w-full object-cover"',
            ),

            (
                'className="h-16 w-full object-cover"',
                'className="h-48 w-full object-cover"',
            ),

            (
                'className="h-20 w-full object-cover"',
                'className="h-48 w-full object-cover"',
            ),
        ]

        if any(
            keyword in issue_text
            for keyword in (
                "image",
                "photo",
                "picture",
                "image height",
                "image size",
            )
        ):

            for old, new in image_fixes:

                if old in source_code:

                    print(
                        "[FALLBACK] Product image "
                        "source pattern found."
                    )

                    return [
                        {
                            "old": old,
                            "new": new,
                            "reason": (
                                "Increase the product image "
                                "height to provide enough "
                                "space for surrounding content."
                            ),
                        }
                    ]

        # ====================================================
        # 5. GENERIC HEIGHT FIX
        # ====================================================

        height_fixes = [

            (
                "h-[56px]",
                "h-48",
            ),

            (
                "h-[60px]",
                "h-48",
            ),

            (
                "h-14",
                "h-48",
            ),

            (
                "h-16",
                "h-48",
            ),

        ]

        if any(
            keyword in issue_text
            for keyword in (
                "height",
                "too small",
                "overlap",
            )
        ):

            for old, new in height_fixes:

                if old in source_code:

                    print(
                        "[FALLBACK] Generic height "
                        "source pattern found."
                    )

                    return [
                        {
                            "old": old,
                            "new": new,
                            "reason": (
                                "Increase the constrained "
                                "element height to reduce "
                                "visual collision."
                            ),
                        }
                    ]

        # ====================================================
        # 6. OVERFLOW
        # ====================================================

        if any(
            keyword in issue_text
            for keyword in (
                "clipped",
                "cut off",
                "hidden",
                "overflow",
            )
        ):

            if "overflow-hidden" in source_code:

                print(
                    "[FALLBACK] Overflow source "
                    "pattern found."
                )

                return [
                    {
                        "old": "overflow-hidden",
                        "new": "overflow-visible",
                        "reason": (
                            "Allow the affected content "
                            "to remain visible instead "
                            "of being clipped."
                        ),
                    }
                ]

        # ====================================================
        # 7. BUTTON SPACING
        # ====================================================

        if any(
            keyword in issue_text
            for keyword in (
                "button",
                "add to cart",
            )
        ):

            button_spacing = [

                (
                    "mt-0",
                    "mt-4",
                ),

                (
                    "mt-1",
                    "mt-4",
                ),

                (
                    "mt-2",
                    "mt-4",
                ),
            ]

            for old, new in button_spacing:

                if old in source_code:

                    print(
                        "[FALLBACK] Button spacing "
                        "source pattern found."
                    )

                    return [
                        {
                            "old": old,
                            "new": new,
                            "reason": (
                                "Increase spacing above "
                                "the button to separate "
                                "it from surrounding content."
                            ),
                        }
                    ]

        print(
            "[FALLBACK] No safe source fix found."
        )

        return []

    # ========================================================
    # VERIFY FIX
    # ========================================================

    def verify_fix(
        self,
        screenshot_path: str,
        html_path: str,
        original_issue: dict[str, Any],
    ) -> dict[str, Any]:

        screenshot_file = Path(
            screenshot_path
        )

        html_file = Path(
            html_path
        )

        if not screenshot_file.exists():

            raise FileNotFoundError(
                f"Screenshot not found: "
                f"{screenshot_file}"
            )

        if not html_file.exists():

            raise FileNotFoundError(
                f"HTML file not found: "
                f"{html_file}"
            )

        image, optimization = self._prepare_image(
            screenshot_file
        )

        html, html_optimization = self._load_html(
            html_file
        )

        issue_json = json.dumps(
            original_issue,
            indent=2,
            ensure_ascii=False,
        )

        prompt = (
            VERIFICATION_PROMPT
            + "\n\nORIGINAL ISSUE:\n"
            + issue_json
            + "\n\nREDUCED NEW HTML:\n"
            + html
            + "\n\nSTRICT VERIFICATION RULES:\n"
            + "1. Compare the current screenshot "
            + "against the original issue.\n"
            + "2. Do not mark fixed merely because "
            + "HTML changed.\n"
            + "3. Inspect the actual visual layout.\n"
            + "4. If the original overlap is still visible, "
            + "return fixed=false.\n"
            + "5. Return fixed=true only when the original "
            + "visual problem is actually resolved.\n"
            + "6. Return ONLY valid JSON.\n"
            + "\nRequired format:\n"
            + '{'
            + '"fixed":true,'
            + '"reason":"short explanation"'
            + '}'
        )

        print("=" * 60)
        print("VERIFYING HEALING")
        print("=" * 60)

        response = self._generate(
            image=image,
            prompt=prompt,
        )

        print("=" * 60)
        print("RAW VERIFICATION RESPONSE")
        print("=" * 60)

        print(response)

        result = self._parse_verification_response(
            response
        )

        result["optimization"] = {
            "image": optimization,
            "html": html_optimization,
        }

        return result

    # ========================================================
    # VERIFY HEALING
    # ========================================================

    def verify_healing(
        self,
        screenshot_path: str,
        html_path: str,
        original_issue: dict[str, Any],
    ) -> dict[str, Any]:

        return self.verify_fix(
            screenshot_path=screenshot_path,
            html_path=html_path,
            original_issue=original_issue,
        )

    # ========================================================
    # PARSE UI RESPONSE
    # ========================================================

    def _parse_response(
        self,
        response: str,
    ) -> list[dict[str, Any]]:

        response = response.strip()

        if not response:
            return []

        response = self._remove_code_fences(
            response
        )

        try:

            data = json.loads(
                response
            )

            if isinstance(
                data,
                dict,
            ):

                issues = data.get(
                    "issues",
                    [],
                )

                if isinstance(
                    issues,
                    list,
                ):

                    return self._clean_issues(
                        issues
                    )

            if isinstance(
                data,
                list,
            ):

                return self._clean_issues(
                    data
                )

        except json.JSONDecodeError:
            pass

        data = self._extract_json_object(
            response
        )

        if isinstance(
            data,
            dict,
        ):

            issues = data.get(
                "issues",
                [],
            )

            if isinstance(
                issues,
                list,
            ):

                return self._clean_issues(
                    issues
                )

        return []

    # ========================================================
    # CLEAN ISSUES
    # ========================================================

    def _clean_issues(
        self,
        issues: list[Any],
    ) -> list[dict[str, Any]]:

        cleaned = []

        for index, issue in enumerate(
            issues,
            start=1,
        ):

            if not isinstance(
                issue,
                dict,
            ):

                continue

            description = str(
                issue.get(
                    "description",
                    "",
                )
            ).strip()

            if not description:
                continue

            severity = str(
                issue.get(
                    "severity",
                    "medium",
                )
            ).lower()

            if severity not in (
                "low",
                "medium",
                "high",
                "critical",
            ):
                severity = "medium"

            cleaned.append(
                {
                    "id": str(
                        issue.get(
                            "id",
                            f"issue-{index}",
                        )
                    ),
                    "type": str(
                        issue.get(
                            "type",
                            "visual issue",
                        )
                    ),
                    "severity": severity,
                    "description": description,
                    "element": issue.get(
                        "element"
                    ),
                    "suggested_fix": issue.get(
                        "suggested_fix"
                    ),
                }
            )

        return cleaned

    # ========================================================
    # PARSE VERIFICATION RESPONSE
    # ========================================================

    def _parse_verification_response(
        self,
        response: str,
    ) -> dict[str, Any]:

        response = self._remove_code_fences(
            response
        )

        data = self._extract_json_object(
            response
        )

        if not isinstance(
            data,
            dict,
        ):

            return {
                "status": "failed",
                "fixed": False,
                "reason": (
                    "Could not parse "
                    "verification response."
                ),
                "raw_response": response,
            }

        fixed = data.get(
            "fixed",
            False,
        )

        if isinstance(
            fixed,
            str,
        ):

            fixed = (
                fixed.lower().strip()
                in {
                    "true",
                    "yes",
                    "fixed",
                    "1",
                }
            )

        else:

            fixed = bool(
                fixed
            )

        return {
            "status": "success",
            "fixed": fixed,
            "reason": str(
                data.get(
                    "reason",
                    "",
                )
            ),
            "raw_response": response,
        }

    # ========================================================
    # JSON EXTRACTION
    # ========================================================

    def _extract_json_object(
        self,
        response: str,
    ) -> dict[str, Any] | None:

        response = response.strip()

        if not response:
            return None

        try:

            data = json.loads(
                response
            )

            if isinstance(
                data,
                dict,
            ):

                return data

        except json.JSONDecodeError:
            pass

        start = response.find(
            "{"
        )

        if start == -1:
            return None

        depth = 0
        in_string = False
        escaped = False

        for index in range(
            start,
            len(response),
        ):

            char = response[index]

            if escaped:

                escaped = False
                continue

            if char == "\\":

                escaped = True
                continue

            if char == '"':

                in_string = not in_string
                continue

            if in_string:
                continue

            if char == "{":

                depth += 1

            elif char == "}":

                depth -= 1

                if depth == 0:

                    candidate = response[
                        start:index + 1
                    ]

                    try:

                        data = json.loads(
                            candidate
                        )

                        if isinstance(
                            data,
                            dict,
                        ):

                            return data

                    except json.JSONDecodeError:
                        return None

        return None

    # ========================================================
    # REMOVE CODE FENCES
    # ========================================================

    def _remove_code_fences(
        self,
        text: str,
    ) -> str:

        text = text.strip()

        text = re.sub(
            r"^```(?:json)?\s*",
            "",
            text,
            flags=re.IGNORECASE,
        )

        text = re.sub(
            r"\s*```$",
            "",
            text,
            flags=re.IGNORECASE,
        )

        return text.strip()


# ============================================================
# SINGLETON
# ============================================================

_analyzer: VisionAnalyzer | None = None


def get_analyzer() -> VisionAnalyzer:

    global _analyzer

    if _analyzer is None:

        _analyzer = VisionAnalyzer()

    return _analyzer


# ============================================================
# PUBLIC API
# ============================================================

def analyze_ui(
    screenshot_path: str,
    html_path: str,
) -> dict[str, Any]:

    return get_analyzer().analyze(
        screenshot_path=screenshot_path,
        html_path=html_path,
    )


def generate_healing_fix(
    screenshot_path: str,
    issue: dict[str, Any],
    source_code: str,
) -> dict[str, Any]:

    return get_analyzer().generate_healing_fix(
        screenshot_path=screenshot_path,
        issue=issue,
        source_code=source_code,
    )


def verify_healing(
    screenshot_path: str,
    html_path: str,
    original_issue: dict[str, Any],
) -> dict[str, Any]:

    return get_analyzer().verify_fix(
        screenshot_path=screenshot_path,
        html_path=html_path,
        original_issue=original_issue,
    )


# ============================================================
# DIRECT TEST
# ============================================================

if __name__ == "__main__":

    screenshot = (
        "screenshots/01_home.png"
    )

    html = (
        "outputs/01_home.html"
    )

    result = analyze_ui(
        screenshot_path=screenshot,
        html_path=html,
    )

    print(
        json.dumps(
            result,
            indent=2,
            ensure_ascii=False,
        )
    )