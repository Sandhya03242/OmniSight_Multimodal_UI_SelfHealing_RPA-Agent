import json
from pathlib import Path

import torch
from transformers import (
    AutoProcessor,
    AutoModelForMultimodalLM,
)

from .models import AnalysisResult
from .prompt import UI_ANALYSIS_PROMPT


MODEL_ID = "Qwen/Qwen3.5-0.8B"


print("Loading Qwen3.5-0.8B...")

processor = AutoProcessor.from_pretrained(
    MODEL_ID
)

model = AutoModelForMultimodalLM.from_pretrained(
    MODEL_ID,
    torch_dtype=torch.float32,
    device_map="cpu"
)

model.eval()

print("Qwen3.5-0.8B loaded.")


async def analyze_ui(
    screenshot_path: str,
    html_path: str
) -> AnalysisResult:

    screenshot = Path(screenshot_path)
    html_file = Path(html_path)

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

    # Keep HTML small for faster inference
    html = html[:6000]

    prompt = f"""
{UI_ANALYSIS_PROMPT}

Analyze the webpage screenshot.

Use the HTML only as supporting information.

RAW HTML:
{html}

Return ONLY valid JSON.
"""

    print("Sending screenshot to Qwen3.5-0.8B...")

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

    # Qwen3.5 recommended multimodal processing
    inputs = processor.apply_chat_template(
        messages,
        add_generation_prompt=True,
        tokenize=True,
        return_dict=True,
        return_tensors="pt",
    )

    # CPU
    inputs = inputs.to("cpu")

    with torch.inference_mode():

        generated_ids = model.generate(
            **inputs,
            max_new_tokens=256,
            do_sample=False,
            use_cache=True
        )

    input_length = inputs["input_ids"].shape[-1]

    generated_ids_trimmed = generated_ids[
        :, input_length:
    ]

    content = processor.batch_decode(
        generated_ids_trimmed,
        skip_special_tokens=True
    )[0].strip()

    if not content:
        raise ValueError(
            "Qwen3.5-0.8B returned an empty response."
        )

    print(
        "\n========== QWEN3.5 RESPONSE =========="
    )

    print(content)

    print(
        "========================================\n"
    )

    data = extract_json(content)

    return AnalysisResult.model_validate(data)


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
            "Invalid JSON returned by Qwen3.5-0.8B:\n\n"
            f"{content}"
        ) from exc