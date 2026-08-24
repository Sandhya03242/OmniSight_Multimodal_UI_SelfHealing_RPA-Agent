# OmniSight — Week 1 & Week 2

## Multimodal UI Self-Healing & RPA Agent

OmniSight is a **Multimodal UI Self-Healing & RPA Agent** that combines browser automation, responsive UI testing, vision-language models, and automated code-fix generation.

The project currently covers:

- **Week 1:** Browser Automation & FastAPI API Scaffolding
- **Week 2:** Multimodal UI Analysis & Action Engine

---

## Project Architecture

```
                         OmniSight
                            │
                            ▼
                       FastAPI API
                            │
             ┌──────────────┼──────────────┐
             │              │              │
             ▼              ▼              ▼
         Capture       Responsive      Checkout
             │           Testing         Flow
             └──────────────┼──────────────┘
                            ▼
                       Playwright
                            │
                    ┌───────┴───────┐
                    ▼               ▼
               Screenshot         HTML
                    │               │
                    └───────┬───────┘
                            ▼
                    Qwen3.5-0.8B VLM
                            │
                            ▼
                     UI Analysis
                            │
                            ▼
                     AnalysisResult
                            │
                            ▼
                      Action Engine
                       ┌────┴────┐
                       ▼         ▼
                 JSON Report   Code Fixes
```

---

## Tech Stack

- Python
- FastAPI
- Uvicorn
- Playwright
- Pydantic
- PyTorch
- Hugging Face Transformers
- Qwen3.5-0.8B
- HTML
- CSS
- React/JSX

---

## Project Structure

```
OmniSight/
│
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── models.py
│   ├── prompt.py
│   ├── vision_analyzer.py
│   ├── action_engine.py
│   └── playwright_bot.py
│
├── screenshots/
│
├── outputs/
│
├── requirements.txt
│
└── README.md
```

---

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/Sandhya03242/OmniSight.git
cd OmniSight
```

### 2. Create Virtual Environment

**Windows**

```bash
python -m venv venv
venv\Scripts\activate
```

**Linux / macOS**

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

If Playwright browsers are not installed:

```bash
playwright install chromium
```

---

## Requirements

Example `requirements.txt`:

```text
fastapi
uvicorn
playwright
pydantic
torch
transformers
accelerate
Pillow
```

---

## Start the FastAPI Server

From the project root:

```bash
uvicorn app.main:app --reload
```

The server will run at:

```
http://127.0.0.1:8000
```

Swagger documentation:

```
http://127.0.0.1:8000/docs
```

---

## Health Check

Open:

```
GET /
```

Expected response:

```json
{
  "project": "OmniSight",
  "status": "running",
  "description": "Multimodal UI Self-Healing and RPA Agent"
}
```

Health endpoint:

```
GET /health
```

Expected response:

```json
{
  "status": "healthy"
}
```

---

## Week 1 — Browser Automation

### 1. Capture a Website

Use:

```
POST /capture
```

Request:

```json
{
  "url": "https://www.saucedemo.com"
}
```

The Playwright automation will:

1. Open the website.
2. Wait for the page to load.
3. Capture a full-page screenshot.
4. Capture the raw HTML.
5. Save both files.

Example output:

```json
{
  "url": "https://www.saucedemo.com",
  "screenshot": "screenshots/page.png",
  "html": "outputs/page.html"
}
```

### 2. Responsive Testing

Use:

```
POST /responsive-test
```

Request:

```json
{
  "url": "https://www.saucedemo.com"
}
```

OmniSight tests:

| Viewport | Size |
|----------|------|
| Desktop  | 1440 × 900 |
| Tablet   | 768 × 1024 |
| Mobile   | 390 × 844 |

Screenshots and HTML files are generated for each viewport.

Example:

```
screenshots/
├── desktop.png
├── tablet.png
└── mobile.png

outputs/
├── desktop.html
├── tablet.html
└── mobile.html
```

### 3. Automated Checkout Flow

Use:

```
POST /checkout-flow
```

The current demonstration flow uses SauceDemo.

The automation performs:

```
Login → Products → Add Product → Cart → Checkout
```

Screenshots are captured at important states.

Example:

```
screenshots/
├── 01_products.png
├── 02_cart.png
└── 03_checkout.png
```

---

## Week 1 Verification

Run the following checks:

```bash
uvicorn app.main:app --reload
```

Then open:

```
http://127.0.0.1:8000/docs
```

Test:

```
GET /
GET /health
POST /capture
POST /responsive-test
POST /checkout-flow
```

Verify that `screenshots/` contains screenshots and `outputs/` contains HTML files.

---

## Week 2 — Multimodal UI Analysis

Week 2 integrates a Vision-Language Model to analyze webpage screenshots together with raw HTML.

The model receives:

```
Screenshot + HTML + UI Analysis Prompt
```

and produces:

```
UI Issues + Suggested Fixes
```

### Vision-Language Model

Current model:

```
Qwen/Qwen3.5-0.8B
```

The model analyzes the webpage screenshot and uses HTML as supporting context.

The analysis looks for issues such as:

- Hidden buttons
- Overlapping elements
- Broken alignment
- Text clipping
- Poor contrast
- Responsive layout problems

### Multimodal Prompt

The analysis prompt instructs the model to return structured JSON:

```json
{
  "issues": [
    {
      "severity": "high",
      "issue_type": "visual",
      "description": "Description of the UI issue",
      "affected_element": "element",
      "evidence": "Visual evidence"
    }
  ],
  "suggested_fixes": [
    {
      "language": "css",
      "code": "CSS fix",
      "explanation": "Why this fixes the issue"
    }
  ]
}
```

### Analyze a Screenshot + HTML

Use:

```
POST /analyze
```

Request:

```json
{
  "screenshot": "screenshots/page.png",
  "html": "outputs/page.html"
}
```

The analysis pipeline is:

```
Screenshot + HTML
        ↓
   Qwen3.5-0.8B
        ↓
   UI Analysis
        ↓
   JSON Extraction
        ↓
   Pydantic Validation
        ↓
   Action Engine
```

### Action Engine

The Action Engine processes the model output.

It generates:

```
outputs/analysis_result.json
```

The JSON contains:

```json
{
  "summary": {
    "total_issues": 1,
    "total_fixes": 1
  },
  "issues": [],
  "suggested_fixes": []
}
```

It also generates suggested code files.

Examples:

```
outputs/
├── suggested_fix_1.css
├── suggested_fix_2.jsx
└── suggested_fix_3.html
```

Supported fix languages:

- CSS
- React / JSX
- HTML

---

## Week 2 Verification

Start the server:

```bash
uvicorn app.main:app --reload
```

Open:

```
http://127.0.0.1:8000/docs
```

First generate a screenshot and HTML:

```
POST /capture
```

Example:

```json
{
  "url": "https://www.saucedemo.com"
}
```

Then send the generated files to:

```
POST /analyze
```

Example:

```json
{
  "screenshot": "screenshots/page.png",
  "html": "outputs/page.html"
}
```

Check:

```
outputs/analysis_result.json
outputs/suggested_fix_*.css
outputs/suggested_fix_*.jsx
outputs/suggested_fix_*.html
```

---

## Testing With Another Website

The generic capture endpoint is not limited to SauceDemo. You can provide another accessible URL:

```json
{
  "url": "https://example.com"
}
```

Then:

```
POST /capture → Screenshot + HTML → POST /analyze → Qwen3.5-0.8B → UI Issues + Suggested Fixes
```

The generic analysis does not require SauceDemo-specific selectors.

The current `/checkout-flow` endpoint is a demonstration RPA workflow specifically implemented for SauceDemo.

---

## Current Status

### Week 1

- [x] Playwright browser automation
- [x] Headless Chromium
- [x] Website navigation
- [x] Full-page screenshots
- [x] HTML capture
- [x] Responsive testing
- [x] Mock e-commerce checkout flow
- [x] FastAPI API server
- [x] Health check
- [x] Capture endpoint
- [x] Responsive test endpoint
- [x] Checkout endpoint

### Week 2

- [x] Vision-Language Model integration
- [x] Screenshot input
- [x] Raw HTML input
- [x] Multimodal UI analysis prompt
- [x] UI issue detection
- [x] Structured Pydantic models
- [x] JSON extraction
- [x] Analysis result generation
- [x] Suggested CSS fixes
- [x] Suggested React/JSX fixes
- [x] Suggested HTML fixes
- [x] Automated output files

### Next Step

- [ ] Improve VLM inference latency
- [ ] Prevent truncated JSON responses
- [ ] GitHub API integration
- [ ] Automated branch creation
- [ ] Automated commit
- [ ] Pull Request generation
- [ ] Automated self-healing workflow

---

## Complete Workflow

```
                 Website URL
                     │
                     ▼
                 Playwright
                     │
          ┌──────────┴──────────┐
          ▼                     ▼
      Screenshot               HTML
          │                     │
          └──────────┬──────────┘
                     ▼
              Qwen3.5-0.8B
                     │
                     ▼
              UI QA Analysis
                     │
                     ▼
              Structured JSON
                     │
                     ▼
                Action Engine
                 │          │
                 ▼          ▼
          Analysis JSON   Code Fixes
                            │
                     ┌──────┼──────┐
                     ▼      ▼      ▼
                    CSS   React   HTML
```

---

## Project Goal

OmniSight aims to evolve into an autonomous UI quality and self-healing system that can:

1. Open a website automatically.
2. Capture screenshots and HTML.
3. Detect visual and responsive UI defects.
4. Identify affected elements.
5. Generate code fixes.
6. Apply fixes automatically.
7. Create GitHub commits and pull requests.
8. Validate the repaired UI through automated browser testing.

---

## Development Progress

### Week 1

Built the foundation for browser automation and API integration using **Playwright and FastAPI**.

### Week 2

Integrated a **Vision-Language Model** to analyze screenshots and HTML, detect UI issues, and generate structured CSS/React/HTML fixes through the Action Engine.

---

## Run

```bash
uvicorn app.main:app --reload
```

Open:

```
http://127.0.0.1:8000/docs
```

Start with:

```
POST /capture
```

and then:

```
POST /analyze
```

This completes the current **Week 1 + Week 2 OmniSight pipeline**.