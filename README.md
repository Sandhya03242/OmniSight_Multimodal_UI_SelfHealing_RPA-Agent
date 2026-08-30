# OmniSight — Week 1, Week 2 & Week 3

## Multimodal UI Self-Healing & RPA Agent

OmniSight is a multimodal UI testing system that combines **Playwright, FastAPI, and a Vision-Language Model (Qwen3.5-0.8B)** to automate browser testing, capture screenshots and HTML, detect UI issues, generate suggested code fixes, and perform a self-healing validation loop.

> **Current scope:** UI issue detection, fix generation, and self-healing validation.

---

# Architecture

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
           │
           ▼
      Self-Healing Loop
           │
           ▼
      Apply Fix
           │
           ▼
    Playwright Re-test
           │
      ┌────┴────┐
      ▼         ▼
   Fixed      Still Broken
                 │
                 ▼
              Re-analyze
```

---

# Tech Stack

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

# Project Structure

```text
OmniSight/
│
├── app/
│   ├── main.py
│   ├── models.py
│   ├── prompt.py
│   ├── vision_analyzer.py
│   ├── action_engine.py
│   ├── playwright_bot.py
│   └── self_healing.py
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

# Example Detection

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

# Week 3 — Self-Healing UI Loop

Week 3 extends OmniSight from **detecting and suggesting fixes** to automatically validating whether a generated fix actually resolves the detected UI problem.

The self-healing system follows a closed-loop process:

```text
Capture
   ↓
Analyze
   ↓
Detect Issue
   ↓
Generate Fix
   ↓
Apply Fix
   ↓
Re-run Playwright
   ↓
Capture New Screenshot + HTML
   ↓
Analyze Again
   ↓
Issue Resolved?
  ┌───────┴───────┐
 YES              NO
  │                │
  ▼                ▼
Success       Generate New Fix
                  │
                  ▼
              Retry Loop
```

### Self-Healing Loop

The self-healing module:

* Receives detected UI issues
* Reads the generated fix
* Applies the suggested modification
* Re-runs the browser test
* Captures the updated screenshot and HTML
* Sends the updated state back to the Vision-Language Model
* Compares the new result with the original issue
* Determines whether the issue has been resolved

### `/self-heal`

```text
POST /self-heal
```

Example flow:

```text
Initial UI
    ↓
Screenshot + HTML
    ↓
Qwen3.5-0.8B
    ↓
UI Issue
    ↓
Action Engine
    ↓
Suggested Fix
    ↓
Apply Fix
    ↓
Playwright Re-test
    ↓
New Screenshot + HTML
    ↓
Qwen3.5-0.8B
    ↓
Validation
```

### Example

Initial detection:

```json
{
  "severity": "high",
  "issue_type": "sensitive_information_exposure",
  "description": "Password field is visible as plain text",
  "affected_element": "input"
}
```

Generated fix:

```html
<input type="password">
```

After applying the fix, Playwright captures the updated page.

The Vision-Language Model analyzes the new state:

```json
{
  "status": "resolved",
  "issue_type": "sensitive_information_exposure",
  "confidence": 0.92
}
```

The self-healing loop then stops because the issue has been successfully resolved.

---

## Retry Protection

To prevent an infinite healing loop, the system uses a maximum retry count.

```text
Maximum retries
      ↓
   3 attempts
```

Example:

```text
Attempt 1 → Fix → Re-test → Failed
Attempt 2 → Fix → Re-test → Failed
Attempt 3 → Fix → Re-test → Failed
                              ↓
                         Stop + Report
```

If the issue cannot be resolved within the retry limit, OmniSight reports the issue instead of continuously modifying the application.

---

## Self-Healing Result

The system produces a healing result such as:

```json
{
  "status": "resolved",
  "attempts": 1,
  "issue_type": "layout_overlap",
  "fix_type": "css",
  "fix_file": "outputs/suggested_fix_1.css"
}
```

For an unsuccessful healing attempt:

```json
{
  "status": "failed",
  "attempts": 3,
  "issue_type": "layout_overlap",
  "reason": "Issue still detected after maximum retries"
}
```

---

# Week 3 Pipeline

The complete Week 3 pipeline is:

```text
Website
   ↓
Playwright
   ↓
Screenshot + HTML
   ↓
Qwen3.5-0.8B
   ↓
Issue Detection
   ↓
Action Engine
   ↓
Fix Generation
   ↓
Self-Healing Engine
   ↓
Apply Fix
   ↓
Playwright Re-test
   ↓
New Screenshot + HTML
   ↓
Qwen3.5-0.8B Validation
   ↓
┌──────────────────────┐
│ Issue Resolved?      │
└──────────┬───────────┘
           │
     ┌─────┴─────┐
     ▼           ▼
    YES          NO
     │           │
     ▼           ▼
  Success      Retry
                 │
                 ▼
          Maximum Retries?
                 │
           ┌─────┴─────┐
           ▼           ▼
          YES          NO
           │           │
           ▼           └──→ Generate New Fix
         Failure
```

---

# Installation

```bash
git clone https://github.com/Sandhya03242/OmniSight.git
cd OmniSight

uv sync

playwright install chromium
```

If the virtual environment is not created automatically, run:

```bash
uv venv
uv sync
```

### Run

Start the FastAPI server:

```bash
uv run uvicorn app.main:app --reload
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
      ↓
POST /self-heal
      ↓
Apply Fix
      ↓
Playwright Re-test
      ↓
Validation
      ↓
Resolved / Failed
```

For responsive testing:

```text
POST /responsive-test
```

For checkout automation:

```text
POST /checkout-flow
```

For self-healing:

```text
POST /self-heal
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

## Week 3

* [x] Self-healing architecture
* [x] Automated fix application
* [x] Playwright re-testing
* [x] Post-fix screenshot capture
* [x] Post-fix HTML capture
* [x] Re-analysis after fix
* [x] Fix validation
* [x] Retry mechanism
* [x] Maximum retry protection
* [x] Healing result reporting
* [x] Resolved / failed status

---

# OmniSight Evolution

```text
Week 1
Browser Automation
        ↓
Week 2
Multimodal UI Detection
        ↓
Week 3
Self-Healing Automation
```

OmniSight therefore evolves from a **browser automation system** into a **multimodal UI testing and self-healing agent** capable of detecting UI problems, generating fixes, applying them, and validating the result through an automated feedback loop.





