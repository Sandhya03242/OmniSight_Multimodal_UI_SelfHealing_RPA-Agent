# OmniSight — Week 1 & Week 2

## Multimodal UI Self-Healing & RPA Agent

OmniSight is a **Multimodal UI Self-Healing & RPA Agent** designed to automate browser testing, capture webpage states, analyze UI issues using a Vision-Language Model (VLM), and generate structured suggestions for fixing detected UI problems.

---

## Project Overview

Traditional UI testing depends heavily on hardcoded DOM selectors. A small frontend change can break automated tests and require manual maintenance.

OmniSight addresses this problem by combining:

- **Playwright** for browser automation
- **FastAPI** for the backend/API gateway
- **Vision-Language Models (VLMs)** for visual UI analysis
- **HTML analysis** as supporting context
- **Pydantic** for structured model output
- **Action Engine** for processing AI-generated analysis

---

## Architecture

```text
                    ┌─────────────────────┐
                    │     Target Web      │
                    │   SauceDemo / App   │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │      Playwright     │
                    │ Browser Automation  │
                    └──────────┬──────────┘
                               │
                       ┌───────┴───────┐
                       ▼               ▼
                  Screenshot         HTML
                       │               │
                       └───────┬───────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │      VLM Engine     │
                    │ Qwen2-VL-2B-Instruct│
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │   UI Analysis JSON  │
                    │ Issues + Suggestions│
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │    Action Engine    │
                    │   CSS / React Fixes │
                    └─────────────────────┘
```

---

# Week 1 — Browser Automation & API Scaffolding

## Status

**Completed**

## Objectives

Week 1 focused on building the foundation for automated browser testing.

## Implemented

- FastAPI backend
- Playwright browser automation
- Headless Chromium
- Automated webpage navigation
- Screenshot capture
- Raw HTML capture
- `/capture` API endpoint
- Swagger/OpenAPI documentation

---

## Week 1 Capture Flow

```text
POST /capture
      |
      v
Playwright
      |
      +------------------+
      |                  |
      v                  v
 Screenshot            HTML
      |                  |
      v                  v
screenshots/          outputs/
page.png              page.html
```

---

## Example `/capture` Request

```json
{
  "url": "https://www.saucedemo.com"
}
```

## Example Response

```json
{
  "url": "https://www.saucedemo.com",
  "screenshot": "screenshots\\page.png",
  "html": "outputs\\page.html"
}
```

---

# Week 2 — Multimodal UI Analysis

## Status

**Implementation Completed**

**VLM Validation Pending**

Week 2 extends the Week 1 browser automation pipeline by introducing multimodal AI analysis.

The VLM receives:

1. A screenshot of the webpage
2. Raw HTML as supporting context

The model analyzes the webpage for potential visual and structural UI problems.

---

## VLM Engine

The current implementation uses:

```text
Qwen/Qwen2-VL-2B-Instruct
```

The model is loaded using **Hugging Face Transformers**.

---

## Why a Vision-Language Model?

A normal text-based LLM cannot directly reason about the visual appearance of a webpage.

A Vision-Language Model can analyze issues such as:

- Hidden buttons
- Overlapping elements
- Misaligned components
- Incorrect spacing
- Text clipping
- Layout problems
- Contrast problems
- Responsive UI issues
- Elements outside the viewport
- Visual inconsistencies

---

# Week 2 Pipeline

```text
screenshots/page.png
        |
        v
+----------------------+
|                      |
|      Qwen2-VL        |
|         2B           |
|                      |
+----------+-----------+
           |
           |
outputs/page.html
           |
           v
   Multimodal Analysis
           |
           v
       JSON Output
           |
           v
     AnalysisResult
           |
           v
    Suggested Fixes
```

---

## Multimodal Prompting

The model receives both the screenshot and HTML.

Example prompt:

```text
Analyze the webpage screenshot.

Use the HTML only as supporting information.

RAW HTML:
<html>
...
</html>

Return ONLY valid JSON.
```

The screenshot provides the primary visual context, while the HTML helps identify affected elements.

---

# Structured Output

The VLM response is parsed into a structured Pydantic model.

Example:

```json
{
  "issues": [
    {
      "severity": "high",
      "issue_type": "layout",
      "description": "The submit button is partially outside the visible viewport.",
      "affected_element": "button.submit",
      "evidence": "The button is clipped on the right side."
    }
  ],
  "suggested_fixes": [
    {
      "language": "css",
      "code": ".submit { width: 100%; }",
      "explanation": "Adjust the button width to prevent viewport overflow."
    }
  ]
}
```

---

# Action Engine

The Week 2 Action Engine processes the VLM response.

It performs the following steps:

1. Receives the VLM response
2. Extracts JSON
3. Removes Markdown code fences
4. Handles natural-language text around JSON
5. Parses the JSON
6. Validates the JSON using Pydantic
7. Returns structured UI issues
8. Returns suggested fixes

---

# JSON Extraction

The backend supports VLM responses containing Markdown code blocks.

Example:

````text
```json
{
  "issues": []
}
```