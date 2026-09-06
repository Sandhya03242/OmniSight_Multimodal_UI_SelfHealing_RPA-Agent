# OmniSight — Multimodal UI Self-Healing & RPA Agent

> **A multimodal AI-powered autonomous QA agent that detects UI issues, generates fixes, verifies the result, and integrates the changes with GitHub.**

## 🚀 Overview

**OmniSight** is a multimodal UI testing and self-healing automation system designed to reduce the maintenance required by traditional UI testing.

Traditional UI automation depends heavily on fixed selectors and manual maintenance. When the UI changes, tests can fail even when the application functionality is still correct.

OmniSight combines:

* Playwright browser automation
* Screenshot and HTML capture
* Vision-Language Model (Qwen)
* Image optimization
* HTML reduction
* LangGraph-based orchestration
* Automated source-code healing
* Visual verification
* GitHub integration
* React QA dashboard

The system behaves like an autonomous QA engineer:

```text
Application
    ↓
Playwright
    ↓
Screenshot + HTML
    ↓
Image Optimization + HTML Reduction
    ↓
Qwen Vision-Language Model
    ↓
UI Issue Detection
    ↓
Fix Generation
    ↓
Source Code Patch
    ↓
Playwright Retest
    ↓
VLM Verification
    ↓
GitHub Commit / Pull Request
    ↓
QA Dashboard
```

---

# ✨ Features

## 1. Browser Automation

OmniSight uses Playwright to:

* Launch a browser
* Navigate to the application
* Execute UI flows
* Capture screenshots
* Capture HTML
* Test desktop layouts
* Test mobile layouts

Supported test viewport examples:

```text
Desktop: 1440 × 900
Mobile:   390 × 844
```

---

## 2. Multimodal UI Analysis

The system provides the Vision-Language Model with:

* Optimized screenshots
* Reduced HTML
* UI context

The model identifies visual problems such as:

* Overlapping text
* Incorrect spacing
* Broken layouts
* Misaligned components
* Component visibility issues
* Responsive UI problems

Example detected issue:

```text
Type: overlapping text
Severity: medium
Element: Product title

Issue:
The "Smart Watch" product title overlaps the image of the watch.
```

---

# 🧠 Vision-Language Model

OmniSight currently uses:

```text
Qwen/Qwen3.5-0.8B
```

The model runs locally through Hugging Face Transformers.

The current configuration is CPU-compatible and does not require a CUDA GPU.

---

# 🖼️ Image Optimization

Large screenshots are optimized before being sent to the VLM.

Example:

```text
Original image
1440 × 1132

        ↓

Focused image
1024 × 796
```

The system also identifies a bounding box around the relevant UI region.

Example:

```text
Bounding box:
[0, 27, 1440, 1090]
```

This reduces unnecessary visual information and improves model efficiency.

---

# 📄 HTML Reduction

Raw HTML is reduced before being passed to the model.

Example:

```text
Original HTML:
17645 characters

        ↓

Reduced HTML:
2994 characters
```

This reduces the amount of irrelevant DOM information sent to the VLM.

---

# 🤖 Self-Healing Agent

The self-healing system is orchestrated using LangGraph.

The workflow contains:

```text
CAPTURE
   ↓
ANALYZE
   ↓
EXTRACT FIX
   ↓
APPLY SOURCE FIX
   ↓
RETEST
   ↓
VERIFY
   ↓
PUBLISH
```

If verification fails, the graph can retry the healing process according to the configured maximum attempts.

---

# 🔍 Visual Verification

After applying a fix, OmniSight runs the application again and captures fresh evidence.

The VLM then compares the original problem with the new state.

Example:

```json
{
  "fixed": true,
  "reason": "The previously overflowing element is no longer visible.",
  "new_issue": "None"
}
```

Only after successful verification does the workflow proceed to publishing.

---

# 🐙 GitHub Integration

OmniSight integrates with GitHub using PyGithub.

The system can:

* Connect to a repository
* Check branches
* Detect source changes
* Update source files
* Commit healing changes
* Create Pull Requests when configured
* Support QA approval/rejection workflows

Example commit:

```text
fix: apply OmniSight self-healing UI fix
```

Current direct-commit mode:

```text
Healing branch: main
Base branch:    main
```

When both branches are `main`, the system commits directly instead of creating a Pull Request.

---

# 📊 QA Dashboard

OmniSight includes a React-based QA dashboard.

Dashboard:

```text
http://localhost:5174
```

The dashboard communicates with the FastAPI backend and provides:

* Detected issues
* Severity
* Healing status
* Suggested fixes
* GitHub information
* QA approval
* QA rejection

---

# ⚡ FastAPI Backend

The backend runs on:

```text
http://localhost:8000
```

Swagger documentation:

```text
http://localhost:8000/docs
```

Important endpoints:

| Method | Endpoint                 | Purpose                        |
| ------ | ------------------------ | ------------------------------ |
| GET    | `/health`                | API health                     |
| POST   | `/navigation/run`        | Browser automation             |
| POST   | `/vision/analyze`        | VLM analysis                   |
| POST   | `/actions/extract-fixes` | Generate fixes                 |
| POST   | `/healing/run`           | Complete self-healing workflow |
| GET    | `/healing/status`        | Healing status                 |
| GET    | `/optimization/status`   | Optimization status            |
| GET    | `/dashboard/issues`      | Dashboard issues               |
| GET    | `/dashboard/status`      | Dashboard status               |
| POST   | `/github/pr/approve`     | QA approval                    |
| POST   | `/github/pr/reject`      | QA rejection                   |
| POST   | `/webhook`               | CI/CD webhook                  |

---

# 📁 Project Structure

```text
OmniSight_Multimodal_UI_SelfHealing_RPA-Agent/
│
├── backend/
│   ├── automation/
│   │   └── playwright_runner.py
│   │
│   ├── vision/
│   │   ├── analyzer.py
│   │   ├── image_chunker.py
│   │   └── prompt.py
│   │
│   ├── actions/
│   │   └── ...
│   │
│   └── github/
│       └── ...
│
├── demo-store/
│   ├── src/
│   │   └── App.jsx
│   ├── package.json
│   └── ...
│
├── dashboard/
│   ├── src/
│   │   ├── App.jsx
│   │   └── index.css
│   ├── package.json
│   └── vite.config.js
│
├── screenshots/
│
├── outputs/
│   └── chunks/
│
├── graph.py
├── main.py
├── pyproject.toml
├── README.md
└── tests/
```

---

# 🛠️ Installation

## Python Environment

This project uses `uv`.

Initialize the environment:

```bash
uv sync
```

Install Playwright browsers:

```bash
uv run playwright install chromium
```

---

# 📦 Environment Variables

Create a `.env` file if required:

```env
GITHUB_TOKEN=your_github_token
GITHUB_REPOSITORY=Sandhya03242/OmniSight_Multimodal_UI_SelfHealing_RPA-Agent
GITHUB_BASE_BRANCH=main
```

Do not commit `.env` or GitHub credentials to the repository.

---

# ▶️ Running the Project

## Terminal 1 — Demo Store

```bash
cd demo-store
npm install
npm run dev
```

Application:

```text
http://localhost:5173
```

---

## Terminal 2 — FastAPI

From the project root:

```bash
uv run uvicorn main:app --reload --port 8000
```

API:

```text
http://localhost:8000
```

Swagger:

```text
http://localhost:8000/docs
```

---

## Terminal 3 — Dashboard

```bash
cd dashboard
npm install
npm run dev
```

Dashboard:

```text
http://localhost:5174
```

---

# 🧪 Testing

OmniSight has been tested module-by-module and end-to-end.

## Health Check

```bash
curl http://localhost:8000/health
```

Expected:

```json
{
  "status": "ok"
}
```

---

## Browser Automation

```bash
curl -X POST http://localhost:8000/navigation/run ^
  -H "Content-Type: application/json" ^
  -d "{\"url\":\"http://localhost:5173\"}"
```

Expected:

```text
HTTP 200
```

with desktop/mobile screenshots and HTML files.

---

## VLM Analysis

Use:

```text
POST /vision/analyze
```

with a generated screenshot and HTML file.

Expected:

```text
status: issue_found
```

when a UI problem is detected.

---

## Self-Healing

```text
POST /healing/run
```

Request:

```json
{
  "url": "http://localhost:5173",
  "max_attempts": 2
}
```

Expected workflow:

```text
Capture
→ Analyze
→ Fix
→ Retest
→ Verify
→ Publish
```

---

# ✅ Test Results

The following components have been successfully tested:

```text
FastAPI                         ✅
Playwright                     ✅
Desktop screenshots            ✅
Mobile screenshots             ✅
HTML capture                   ✅
Qwen VLM analysis              ✅
Image optimization             ✅
HTML reduction                 ✅
Self-healing workflow          ✅
Visual verification            ✅
GitHub integration             ✅
Healing status API             ✅
Optimization status API        ✅
Dashboard issues API            ✅
Dashboard status API            ✅
GitHub approval API             ✅
GitHub rejection API            ✅
End-to-end healing             ✅
```

Example successful result:

```text
Status:       published
Attempt:      1
Issues:       1
Fixed:        true
GitHub:       success
```

---

# 🔗 System URLs

| Service    | URL                          |
| ---------- | ---------------------------- |
| Demo Store | `http://localhost:5173`      |
| FastAPI    | `http://localhost:8000`      |
| Swagger    | `http://localhost:8000/docs` |
| Dashboard  | `http://localhost:5174`      |

---

# 🎯 Project Goals

OmniSight demonstrates how modern AI can be combined with browser automation and agentic workflows to build autonomous QA systems.

The project focuses on:

* Multimodal AI
* Vision-Language Models
* Autonomous agents
* UI testing
* RPA
* Self-healing software
* Browser automation
* Source-code modification
* Automated verification
* GitHub automation
* QA dashboards

---

# 🏆 Final Architecture

```text
                     ┌──────────────────┐
                     │   Mock E-Commerce│
                     │      React       │
                     └────────┬─────────┘
                              │
                              ▼
                     ┌──────────────────┐
                     │    Playwright    │
                     │ Browser Agent    │
                     └────────┬─────────┘
                              │
                    Screenshot + HTML
                              │
                              ▼
              ┌────────────────────────────┐
              │     Optimization Layer     │
              │                            │
              │ Image Focus + HTML Reduce  │
              └──────────────┬─────────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │    Qwen VLM     │
                    │ Visual Analysis  │
                    └────────┬────────┘
                             │
                         UI Issues
                             │
                             ▼
                    ┌─────────────────┐
                    │ LangGraph Agent │
                    │ Self-Healing    │
                    └────────┬────────┘
                             │
                       Source Fix
                             │
                             ▼
                    ┌─────────────────┐
                    │   Verification  │
                    │   Playwright +  │
                    │      VLM        │
                    └────────┬────────┘
                             │
                         Fixed = True
                             │
                             ▼
                    ┌─────────────────┐
                    │     GitHub      │
                    │ Commit / PR     │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │  React QA       │
                    │   Dashboard     │
                    └─────────────────┘
```

---

# 👩‍💻 Project

**OmniSight — Multimodal UI Self-Healing & RPA Agent**

Built with:

```text
Python
FastAPI
Playwright
LangGraph
Qwen Vision-Language Model
Hugging Face Transformers
PyGithub
React
Vite
```

---

## ⭐ Conclusion

OmniSight demonstrates a complete autonomous UI QA pipeline that can:

```text
SEE
 ↓
UNDERSTAND
 ↓
DETECT
 ↓
HEAL
 ↓
VERIFY
 ↓
PUBLISH
```

The system combines multimodal AI reasoning with browser automation and agentic orchestration to reduce manual UI testing and maintenance.
