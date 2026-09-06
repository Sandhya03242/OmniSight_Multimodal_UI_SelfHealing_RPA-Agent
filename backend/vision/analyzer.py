from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

import torch
from PIL import Image
from transformers import AutoModelForMultimodalLM, AutoProcessor

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


# ============================================================
# VISION ANALYZER
# ============================================================

class VisionAnalyzer:
    """
    OmniSight multimodal UI analyzer.

    Responsibilities:

    1. Analyze screenshot + HTML
    2. Detect UI issues
    3. Generate candidate healing fixes
    4. Verify the healed UI
    """

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

        self.processor = AutoProcessor.from_pretrained(
            model_id
        )

        self.model = AutoModelForMultimodalLM.from_pretrained(
            model_id,
            torch_dtype=torch.float32,
            device_map="cpu",
        )

        self.model.eval()

        print("Vision model loaded successfully.")
        print("=" * 60)

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
    # WEEK 2
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

        image = Image.open(
            screenshot_file
        ).convert("RGB")

        html = html_file.read_text(
            encoding="utf-8",
            errors="ignore",
        )

        html = html[:MAX_HTML_LENGTH]

        prompt = (
            VISION_PROMPT
            + "\n\nRAW HTML:\n"
            + html
        )

        print("Preparing model input...")
        print("Running Qwen3.5-0.8B inference...")

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
            "issues": issues,
            "raw_response": response,
        }

    # ========================================================
    # WEEK 3
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

        image = Image.open(
            screenshot_file
        ).convert("RGB")

        issue_json = json.dumps(
            issue,
            indent=2,
            ensure_ascii=False,
        )

        source_code = source_code[
            :MAX_SOURCE_LENGTH
        ]

        prompt = (
            HEALING_PROMPT
            + "\n\nDETECTED ISSUE:\n"
            + issue_json
            + "\n\nSOURCE CODE:\n"
            + source_code
        )

        print("=" * 60)
        print("GENERATING HEALING FIX")
        print("=" * 60)

        response = self._generate(
            image=image,
            prompt=prompt,
        )

        print("=" * 60)
        print("RAW HEALING RESPONSE")
        print("=" * 60)

        print(response)

        result = self._parse_healing_response(
            response
        )

        # ====================================================
        # IMPORTANT
        #
        # This is only a CANDIDATE fix.
        #
        # graph.py must validate it before applying.
        # ====================================================

        result["candidate"] = True

        return result

    # ========================================================
    # WEEK 3
    # VERIFY HEALING
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

        image = Image.open(
            screenshot_file
        ).convert("RGB")

        html = html_file.read_text(
            encoding="utf-8",
            errors="ignore",
        )

        html = html[:MAX_HTML_LENGTH]

        issue_json = json.dumps(
            original_issue,
            indent=2,
            ensure_ascii=False,
        )

        prompt = (
            VERIFICATION_PROMPT
            + "\n\nORIGINAL ISSUE:\n"
            + issue_json
            + "\n\nNEW HTML:\n"
            + html
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

        return result

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

        # ----------------------------------------------------
        # Direct JSON
        # ----------------------------------------------------

        try:

            data = json.loads(
                response
            )

            if isinstance(data, dict):

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

        # ----------------------------------------------------
        # Embedded JSON object
        # ----------------------------------------------------

        object_start = response.find("{")
        object_end = response.rfind("}")

        if (
            object_start != -1
            and object_end != -1
            and object_end > object_start
        ):

            try:

                data = json.loads(
                    response[
                        object_start:
                        object_end + 1
                    ]
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

            except json.JSONDecodeError:
                pass

        # ----------------------------------------------------
        # Embedded JSON array
        # ----------------------------------------------------

        array_start = response.find("[")
        array_end = response.rfind("]")

        if (
            array_start != -1
            and array_end != -1
            and array_end > array_start
        ):

            try:

                data = json.loads(
                    response[
                        array_start:
                        array_end + 1
                    ]
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
                            "unknown",
                        )
                    ),
                    "severity": str(
                        issue.get(
                            "severity",
                            "low",
                        )
                    ),
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
    # PARSE HEALING RESPONSE
    # ========================================================

    def _parse_healing_response(
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
                "fix_type": "unknown",
                "element": None,
                "description": "",
                "code": None,
                "candidate": False,
                "raw_response": response,
            }

        code = data.get(
            "code"
        )

        if code is not None:
            code = str(code).strip()

        return {
            "status": "success",
            "fix_type": str(
                data.get(
                    "fix_type",
                    "css",
                )
            ),
            "element": data.get(
                "element"
            ),
            "description": str(
                data.get(
                    "description",
                    "",
                )
            ),
            "code": code,
            "candidate": True,
            "raw_response": response,
        }

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
                    "VLM verification response "
                    "could not be parsed."
                ),
                "raw_response": response,
            }

        fixed_value = data.get(
            "fixed",
            False,
        )

        # ----------------------------------------------------
        # Normalize boolean
        # ----------------------------------------------------

        if isinstance(
            fixed_value,
            str,
        ):

            fixed_value = (
                fixed_value.lower()
                in {
                    "true",
                    "yes",
                    "fixed",
                    "1",
                }
            )

        else:

            fixed_value = bool(
                fixed_value
            )

        return {
            "status": "success",
            "fixed": fixed_value,
            "reason": str(
                data.get(
                    "reason",
                    "",
                )
            ),
            "raw_response": response,
        }

    # ========================================================
    # EXTRACT JSON OBJECT
    # ========================================================

    def _extract_json_object(
        self,
        response: str,
    ) -> dict[str, Any] | None:

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

        start = response.find("{")
        end = response.rfind("}")

        if (
            start == -1
            or end == -1
            or end <= start
        ):
            return None

        try:

            data = json.loads(
                response[
                    start:
                    end + 1
                ]
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
    # REMOVE MARKDOWN FENCES
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
# WEEK 2 API
# ============================================================

def analyze_ui(
    screenshot_path: str,
    html_path: str,
) -> dict[str, Any]:

    return get_analyzer().analyze(
        screenshot_path=screenshot_path,
        html_path=html_path,
    )


# ============================================================
# WEEK 3 API
# ============================================================

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
# LOCAL TEST
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