# OmniSight — Week 1 & Week 2

## Multimodal UI Self-Healing & RPA Agent

OmniSight is a multimodal UI testing system that combines **Playwright, FastAPI, and a Vision-Language Model (Qwen3.5-0.8B)** to automate browser testing, capture screenshots and HTML, detect UI issues, and generate suggested code fixes.

> **Current scope:** UI issue detection and fix generation.

---

## Architecture

```text
Website
   │
   ▼
FastAPI
   │
   ▼
Playwright
   │
   ├── Screenshot
   └── HTML
        │
        ▼
  Qwen3.5-0.8B
        │
        ▼
   UI Analysis
        │
        ▼
 AnalysisResult
        │
        ▼
 Action Engine
        │
     ┌──┴──┐
     ▼     ▼
   JSON   Code Fix
````

---

## Tech Stack

* Python
* FastAPI
* Uvicorn
* Playwright
* Pydantic
* PyTorch
* Hugging Face Transformers
* Qwen3.5-0.8B
* HTML / CSS / JSX

---

## Project Structure

```text
OmniSight/
│
├── app/
│   ├── main.py
│   ├── models.py
│   ├── prompt.py
│   ├── vision_analyzer.py
│   ├── action_engine.py
│   └── playwright_bot.py
│
├── screenshots/
├── outputs/
├── requirements.txt
└── README.md
```

---

# Week 1 — Browser Automation

Week 1 focuses on browser automation and API scaffolding.

### Playwright

Playwright:

* Opens the website
* Performs browser actions
* Captures screenshots
* Captures raw HTML
* Tests different screen sizes
* Automates a checkout workflow

### `/capture`

Captures one webpage state.

```text
POST /capture
```

```json
{
  "url": "https://www.saucedemo.com"
}
```

Output:

```text
screenshots/page.png
outputs/page.html
```

### `/responsive-test`

Tests the webpage at three viewport sizes:

| Device  | Size       |
| ------- | ---------- |
| Desktop | 1440 × 900 |
| Tablet  | 768 × 1024 |
| Mobile  | 390 × 844  |

Each viewport produces:

```text
Screenshot + HTML
```

This helps detect responsive problems such as:

* Text clipping
* Overlapping elements
* Broken alignment
* Layout problems

### `/checkout-flow`

Automates:

```text
Login
  ↓
Products
  ↓
Add Product
  ↓
Cart
  ↓
Checkout
```

Screenshots are captured at important states.

---

# Week 2 — Multimodal UI Analysis

Week 2 integrates the Vision-Language Model.

The model receives:

```text
Screenshot + HTML + UI Analysis Prompt
```

and produces:

```text
UI Issues + Suggested Fixes
```

### Vision Model

```text
Qwen/Qwen3.5-0.8B
```

The screenshot is the **primary visual input** and HTML is used as supporting information.

The model checks for:

* Visual issues
* Alignment problems
* Text clipping
* Overlapping elements
* Poor contrast
* Responsive issues
* Sensitive information exposure

### HTML Limitation

For faster CPU inference, the HTML context is currently limited:

```python
html = html[:6000]
```

---

## `/analyze`

Analyzes a screenshot and HTML file.

```text
POST /analyze
```

```json
{
  "screenshot": "screenshots/page.png",
  "html": "outputs/page.html"
}
```

Pipeline:

```text
Screenshot + HTML
       ↓
Qwen3.5-0.8B
       ↓
JSON Extraction
       ↓
Pydantic Validation
       ↓
Action Engine
```

---

## Example Detection

The model can detect an exposed password field:

```json
{
  "severity": "high",
  "issue_type": "sensitive_information_exposure",
  "description": "Password field is visible as plain text",
  "affected_element": "input"
}
```

Suggested fix:

```html
<input type="password">
```

---

# Action Engine

The Action Engine processes the model output and generates:

```text
outputs/analysis_result.json
```

It also creates suggested fix files:

```text
outputs/
├── suggested_fix_1.css
├── suggested_fix_2.jsx
└── suggested_fix_3.html
```

Supported fix types:

* CSS
* HTML
* React / JSX

---

# Installation

```bash
git clone https://github.com/Sandhya03242/OmniSight.git
cd OmniSight

python -m venv venv
venv\Scripts\activate

pip install -r requirements.txt

playwright install chromium
```

---

# Run

Start the server:

```bash
uvicorn app.main:app --reload
```

Open Swagger:

```text
http://127.0.0.1:8000/docs
```

Recommended flow:

```text
POST /capture
      ↓
Screenshot + HTML
      ↓
POST /analyze
      ↓
UI Issues + Suggested Fixes
```

For responsive testing:

```text
POST /responsive-test
```

For the checkout automation:

```text
POST /checkout-flow
```

---

# Current Status

## Week 1

* [x] Playwright browser automation
* [x] Screenshot capture
* [x] HTML capture
* [x] Responsive testing
* [x] Checkout automation
* [x] FastAPI API
* [x] Swagger documentation

## Week 2

* [x] Qwen3.5-0.8B integration
* [x] Screenshot analysis
* [x] HTML context
* [x] UI issue detection
* [x] Pydantic validation
* [x] JSON extraction
* [x] Action Engine
* [x] CSS/HTML/JSX fix generation




