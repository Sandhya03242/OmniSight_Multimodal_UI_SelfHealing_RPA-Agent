import json
from pathlib import Path

import torch
from transformers import (
    Qwen2VLForConditionalGeneration,
    AutoProcessor,
)

from .models import AnalysisResult
from .prompt import UI_ANALYSIS_PROMPT


MODEL_ID = "Qwen/Qwen2-VL-2B-Instruct"


print("Loading Qwen2-VL-2B-Instruct...")

processor = AutoProcessor.from_pretrained(
    MODEL_ID
)

model = Qwen2VLForConditionalGeneration.from_pretrained(
    MODEL_ID,
    torch_dtype=torch.float32,
    device_map="cpu"
)

model.eval()

print("Qwen2-VL loaded.")


async def analyze_ui(
    screenshot_path: str,
    html_path: str
) -> AnalysisResult:

    screenshot = Path(
        screenshot_path
    )

    html_file = Path(
        html_path
    )

    if not screenshot.exists():
        raise FileNotFoundError(
            f"Screenshot not found: {screenshot}"
        )

    if not html_file.exists():
        raise FileNotFoundError(
            f"HTML file not found: {html_file}"
        )

    html = html_file.read_text(
        encoding="utf-8"
    )

    # Keep HTML small for CPU inference
    html = html[:10000]

    prompt = f"""
{UI_ANALYSIS_PROMPT}

Analyze the webpage screenshot.

Use the HTML only as supporting information.

RAW HTML:
{html}

Return ONLY valid JSON.
"""

    print(
        "Sending screenshot to Qwen2-VL..."
    )

    messages = [
        {
            "role": "user",
            "content": [
                {
                    "type": "image",
                    "image": str(screenshot)
                },
                {
                    "type": "text",
                    "text": prompt
                }
            ]
        }
    ]

    text = processor.apply_chat_template(
        messages,
        tokenize=False,
        add_generation_prompt=True
    )

    inputs = processor(
        text=[text],
        images=[str(screenshot)],
        padding=True,
        return_tensors="pt"
    )

    with torch.no_grad():

        generated_ids = model.generate(
            **inputs,
            max_new_tokens=512
        )

    generated_ids_trimmed = [
        output_ids[len(input_ids):]
        for input_ids, output_ids
        in zip(
            inputs["input_ids"],
            generated_ids
        )
    ]

    content = processor.batch_decode(
        generated_ids_trimmed,
        skip_special_tokens=True
    )[0]

    if not content:
        raise ValueError(
            "Qwen2-VL returned an empty response."
        )

    print(
        "\n========== QWEN2-VL RESPONSE =========="
    )

    print(content)

    print(
        "========================================\n"
    )

    data = extract_json(content)

    return AnalysisResult.model_validate(
        data
    )


def extract_json(
    content: str
) -> dict:

    content = content.strip()

    # ```json ... ```
    if "```json" in content:

        start = content.find(
            "```json"
        ) + len("```json")

        end = content.find(
            "```",
            start
        )

        if end != -1:

            content = content[
                start:end
            ].strip()

    # ``` ... ```
    elif "```" in content:

        start = content.find(
            "```"
        ) + 3

        end = content.find(
            "```",
            start
        )

        if end != -1:

            content = content[
                start:end
            ].strip()

    # JSON surrounded by text
    if not content.startswith("{"):

        start = content.find("{")
        end = content.rfind("}")

        if start != -1 and end != -1:

            content = content[
                start:end + 1
            ]

    try:

        return json.loads(content)

    except json.JSONDecodeError as exc:

        raise ValueError(
            "Invalid JSON returned by Qwen2-VL:\n\n"
            f"{content}"
        ) from exc