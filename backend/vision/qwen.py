import torch

from pathlib import Path
from PIL import Image

from transformers import (
    AutoProcessor,
    AutoModelForMultimodalLM,
)


# =====================================================
# MODEL CONFIGURATION
# =====================================================

MODEL_ID = "Qwen/Qwen3.5-0.8B"

DEVICE = "cpu"

DTYPE = torch.float32


# =====================================================
# MODEL DIRECTORIES
# =====================================================

ROOT_DIR = Path(__file__).resolve().parents[2]

OUTPUT_DIR = (
    ROOT_DIR
    / "backend"
    / "outputs"
    / "analysis"
)

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True,
)


# =====================================================
# LOAD PROCESSOR
# =====================================================

print("\n")
print("=" * 70)
print("              OMNISIGHT QWEN ENGINE")
print("=" * 70)

print(
    "\n[QWEN] Model:",
    MODEL_ID,
)

print(
    "[QWEN] Device:",
    DEVICE,
)

print(
    "[QWEN] Loading processor..."
)


processor = AutoProcessor.from_pretrained(
    MODEL_ID
)


print(
    "[QWEN] Processor loaded."
)


# =====================================================
# LOAD MODEL
# =====================================================

print(
    "\n[QWEN] Loading model..."
)

model = AutoModelForMultimodalLM.from_pretrained(

    MODEL_ID,

    dtype=DTYPE,

    device_map=DEVICE,
)


model.eval()


print(
    "[QWEN] Model loaded successfully."
)

print(
    "[QWEN] OmniSight vision engine ready."
)

print(
    "=" * 70
)

print("\n")


# =====================================================
# IMAGE VALIDATION
# =====================================================


def load_image(
    screenshot_path,
):

    path = Path(
        screenshot_path
    )

    if not path.exists():

        raise FileNotFoundError(
            f"Screenshot not found: {path}"
        )

    try:

        image = Image.open(
            path
        ).convert("RGB")

    except Exception as error:

        raise RuntimeError(
            f"Unable to open screenshot: {error}"
        )

    return image


# =====================================================
# BUILD PROMPT
# =====================================================


def build_prompt(
    html,
    viewport,
):

    html_content = html[:6000]

    prompt = f"""
You are OmniSight, an autonomous UI testing
and self-healing agent.

Your task is to analyze a web application's
screenshot together with its HTML structure.

APPLICATION:
SauceDemo

VIEWPORT:
{viewport}

HTML:
{html_content}

==================================================
UI AUDIT
==================================================

Look for REAL UI problems.

Check the following:

1. Hidden buttons
2. Invisible controls
3. Horizontal overflow
4. Vertical overflow
5. Clipped text
6. Overlapping elements
7. Broken alignment
8. Incorrect spacing
9. Responsive design problems
10. Missing controls
11. Broken forms
12. Accessibility problems
13. Buttons outside the viewport
14. Elements extending beyond their container
15. Checkout flow problems

==================================================
IMPORTANT ELEMENT
==================================================

The checkout Continue button is:

#continue

Determine whether:

- the element exists
- the element is visible
- the element is usable
- the element is inside the viewport

==================================================
EVIDENCE RULE
==================================================

Only report a problem if there is evidence
from the screenshot, HTML, or viewport information.

Do NOT invent problems.

If there is no real problem, return:

{{
    "status": "passed",
    "issues": []
}}

If problems exist, return:

{{
    "status": "issues_found",
    "issues": [
        {{
            "type": "hidden_element",
            "severity": "high",
            "element": "#continue",
            "description": "Checkout Continue button is hidden.",
            "evidence": "The screenshot does not show the Continue button and the HTML/CSS indicates that the element is hidden.",
            "suggested_fix": "#continue {{ display: block !important; visibility: visible !important; opacity: 1 !important; }}"
        }}
    ]
}}

==================================================
ALLOWED ISSUE TYPES
==================================================

Use one of:

- hidden_element
- invisible_control
- horizontal_overflow
- vertical_overflow
- clipped_content
- overlapping_element
- alignment_error
- spacing_error
- responsive_issue
- missing_control
- accessibility_issue
- checkout_issue

==================================================
SEVERITY
==================================================

Use:

- low
- medium
- high
- critical

==================================================
OUTPUT FORMAT
==================================================

Return ONLY valid JSON.

Do not use Markdown.

Do not use ```json.

Do not add explanations outside JSON.

JSON schema:

{{
    "status": "passed" | "issues_found",
    "issues": [
        {{
            "type": "string",
            "severity": "low | medium | high | critical",
            "element": "string",
            "description": "string",
            "evidence": "string",
            "suggested_fix": "string"
        }}
    ]
}}
"""

    return prompt


# =====================================================
# CREATE QWEN MESSAGES
# =====================================================


def build_messages(
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

    return messages


# =====================================================
# PREPARE INPUTS
# =====================================================


def prepare_inputs(
    messages,
):

    inputs = (
        processor
        .apply_chat_template(

            messages,

            add_generation_prompt=True,

            tokenize=True,

            return_dict=True,

            return_tensors="pt",
        )
    )


    prepared_inputs = {}

    for key, value in inputs.items():

        if hasattr(
            value,
            "to",
        ):

            prepared_inputs[key] = (
                value.to(DEVICE)
            )

        else:

            prepared_inputs[key] = value


    return prepared_inputs


# =====================================================
# GENERATE RESPONSE
# =====================================================


def generate_response(
    inputs,
):

    print(
        "[QWEN] Running vision analysis..."
    )

    with torch.no_grad():

        outputs = model.generate(

            **inputs,

            max_new_tokens=300,

            do_sample=False,
        )


    input_length = (
        inputs[
            "input_ids"
        ].shape[-1]
    )


    generated_tokens = (
        outputs[0][
            input_length:
        ]
    )


    response = processor.decode(

        generated_tokens,

        skip_special_tokens=True,
    )


    return response.strip()


# =====================================================
# MAIN ANALYSIS FUNCTION
# =====================================================


def analyze_screenshot(

    screenshot_path,

    html,

    viewport,
):

    print("\n")
    print(
        "[QWEN] ====================================="
    )

    print(
        "[QWEN] Starting UI analysis"
    )

    print(
        "[QWEN] Screenshot:",
        screenshot_path,
    )

    print(
        "[QWEN] Viewport:",
        viewport,
    )

    # -------------------------------------------------
    # LOAD IMAGE
    # -------------------------------------------------

    image = load_image(
        screenshot_path
    )

    # -------------------------------------------------
    # BUILD PROMPT
    # -------------------------------------------------

    prompt = build_prompt(

        html=html,

        viewport=viewport,
    )

    # -------------------------------------------------
    # BUILD MESSAGES
    # -------------------------------------------------

    messages = build_messages(

        image=image,

        prompt=prompt,
    )

    # -------------------------------------------------
    # PREPARE MODEL INPUT
    # -------------------------------------------------

    inputs = prepare_inputs(
        messages
    )

    # -------------------------------------------------
    # RUN MODEL
    # -------------------------------------------------

    response = generate_response(
        inputs
    )

    # -------------------------------------------------
    # PRINT RESPONSE
    # -------------------------------------------------

    print(
        "\n[QWEN] Raw response:"
    )

    print(
        response
    )

    print(
        "\n[QWEN] Analysis completed."
    )

    print(
        "[QWEN] ====================================="
    )

    return response