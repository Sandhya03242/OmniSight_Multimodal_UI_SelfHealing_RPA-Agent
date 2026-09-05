import json
from pathlib import Path

import torch
from PIL import Image
from transformers import (
    AutoModelForMultimodalLM,
    AutoProcessor,
)


MODEL_ID = "Qwen/Qwen3.5-0.8B"

ROOT = Path(__file__).resolve().parents[2]
OUTPUTS = ROOT / "outputs"

processor = AutoProcessor.from_pretrained(
    MODEL_ID
)

model = AutoModelForMultimodalLM.from_pretrained(
    MODEL_ID,
    torch_dtype=torch.float32,
    device_map="cpu",
)


def prepare_inputs(
    image,
    prompt,
):
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

    inputs = processor.apply_chat_template(
        messages,
        add_generation_prompt=True,
        tokenize=True,
        return_dict=True,
        return_tensors="pt",
    )

    inputs = {
        key: value.to(model.device)
        if hasattr(value, "to")
        else value
        for key, value in inputs.items()
    }

    return inputs


def generate(
    inputs,
    max_new_tokens=500,
):
    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=max_new_tokens,
            do_sample=False,
        )

    generated = outputs[0][
        inputs["input_ids"].shape[-1]:
    ]

    response = processor.decode(
        generated,
        skip_special_tokens=True,
    )

    return response


def parse_response(
    response,
):
    response = response.strip()

    try:
        return json.loads(response)

    except json.JSONDecodeError:
        start = response.find("{")
        end = response.rfind("}")

        if start != -1 and end != -1:
            try:
                return json.loads(
                    response[
                        start:end + 1
                    ]
                )
            except json.JSONDecodeError:
                pass

    return {
        "issues": [],
        "raw_response": response,
    }


def analyze_ui(
    screenshot_path: str,
    html: str,
):
    image = Image.open(
        screenshot_path
    ).convert("RGB")

    html = html[:6000]

    prompt = f"""
You are OmniSight, an automated UI quality analyzer.

Analyze BOTH:

1. The provided screenshot.
2. The provided raw HTML.

Identify visible UI problems.

Look specifically for:

- overlapping text
- overlapping elements
- broken layout
- incorrect spacing
- poor color contrast
- invisible text
- clipped text
- clipped elements
- buttons overlapping
- incorrect alignment
- oversized elements
- undersized elements
- mobile responsiveness problems
- horizontal overflow

Use the screenshot to determine what is visually wrong.

Use the HTML to identify the element responsible
for the problem.

For every detected issue, provide a practical
CSS or React/Tailwind fix.

Return ONLY valid JSON.

Use exactly this structure:

{{
  "issues": [
    {{
      "type": "string",
      "description": "string",
      "severity": "low|medium|high",
      "selector": "string",
      "css_fix": "string",
      "react_fix": "string"
    }}
  ]
}}

If there are no problems, return:

{{
  "issues": []
}}

Raw HTML:

{html}
"""

    inputs = prepare_inputs(
        image,
        prompt,
    )

    response = generate(
        inputs,
        max_new_tokens=500,
    )

    return parse_response(
        response
    )


def analyze_crop(
    screenshot_path: str,
    html: str,
    selector: str,
):
    image = Image.open(
        screenshot_path
    ).convert("RGB")

    html = html[:4000]

    prompt = f"""
You are OmniSight, an automated UI anomaly
detection agent.

Analyze ONLY the provided UI component crop.

Component selector:

{selector}

Determine whether this component has a visible
UI problem.

Check:

- spacing
- alignment
- clipping
- overflow
- text visibility
- contrast
- element sizing
- overlapping elements
- responsiveness
- broken layout

Use the HTML only to understand the component.

Do NOT report problems outside the provided crop.

Return ONLY valid JSON.

Use exactly this structure:

{{
  "anomaly": true,
  "type": "string",
  "description": "string",
  "severity": "low|medium|high",
  "selector": "{selector}",
  "css_fix": "string",
  "react_fix": "string"
}}

If there is no anomaly:

{{
  "anomaly": false,
  "type": "",
  "description": "",
  "severity": "low",
  "selector": "{selector}",
  "css_fix": "",
  "react_fix": ""
}}

HTML:

{html}
"""

    inputs = prepare_inputs(
        image,
        prompt,
    )

    response = generate(
        inputs,
        max_new_tokens=300,
    )

    result = parse_response(
        response
    )

    if "anomaly" not in result:
        result["anomaly"] = False

    return result


def analyze_crops(
    crops,
    html,
):
    results = []

    for crop in crops:
        analysis = analyze_crop(
            crop["path"],
            html,
            crop["selector"],
        )

        results.append({
            "selector": crop[
                "selector"
            ],
            "index": crop[
                "index"
            ],
            "screenshot": crop[
                "path"
            ],
            "analysis": analysis,
        })

    anomalies = []

    for result in results:
        analysis = result.get(
            "analysis",
            {},
        )

        if analysis.get(
            "anomaly",
            False,
        ):
            anomalies.append(
                result
            )

    return {
        "total_components": len(
            results
        ),
        "total_anomalies": len(
            anomalies
        ),
        "anomalies": anomalies,
        "results": results,
    }


def verify_ui(
    screenshot_path,
    html_path,
    original_analysis,
):
    image = Image.open(
        screenshot_path
    ).convert("RGB")

    html = Path(
        html_path
    ).read_text(
        encoding="utf-8"
    )

    html = html[:6000]

    issues = original_analysis.get(
        "issues",
        []
    )

    prompt = f"""
You are OmniSight, an automated UI verification agent.

The original UI contained these detected issues:

{json.dumps(issues, indent=2)}

A CSS fix was applied to the page.

Analyze the NEW screenshot and HTML.

Determine whether the original UI problems
have actually been fixed.

Check:

- spacing
- alignment
- responsiveness
- horizontal overflow
- clipping
- overlapping elements
- element sizing
- visibility
- layout

Compare the new UI against the original issues.

Return ONLY valid JSON.

Use exactly this structure:

{{
  "fixed": true,
  "confidence": 0.95,
  "message": "The UI issue has been fixed"
}}

OR:

{{
  "fixed": false,
  "confidence": 0.40,
  "message": "The UI issue is still present"
}}

Original issues:

{json.dumps(issues, indent=2)}

HTML:

{html}
"""

    inputs = prepare_inputs(
        image,
        prompt,
    )

    response = generate(
        inputs,
        max_new_tokens=200,
    )

    return parse_response(
        response
    )


def save_analysis(
    analysis,
    filename="ui_analysis.json",
):
    OUTPUTS.mkdir(
        parents=True,
        exist_ok=True,
    )

    path = OUTPUTS / filename

    path.write_text(
        json.dumps(
            analysis,
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    return path