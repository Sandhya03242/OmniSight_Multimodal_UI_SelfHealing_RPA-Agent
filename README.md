# OmniSight — Multimodal UI Self-Healing & RPA Agent

OmniSight is an AI-powered autonomous QA and UI self-healing system that combines **Playwright browser automation, Vision-Language Models (VLMs), FastAPI, agentic workflows, image optimization, HTML reduction, and GitHub integration**.

The system behaves like an autonomous QA engineer:

```text
Application
     ↓
Playwright Automation
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
Source Code Modification
     ↓
Retest + Verification
     ↓
GitHub Integration
     ↓
QA Dashboard
```

---

# 🎥 Demo Video

Watch the complete OmniSight demonstration:

**[▶️ Watch OmniSight Demo](./demo/Omnsight.mp4)**

The demo demonstrates the complete self-healing workflow:

```text
UI Bug
  ↓
Playwright Capture
  ↓
Screenshot + HTML
  ↓
Image + HTML Optimization
  ↓
Qwen VLM Analysis
  ↓
UI Issue Detection
  ↓
AI Fix Generation
  ↓
Source Code Modification
  ↓
Retesting
  ↓
Verification
  ↓
GitHub Integration
  ↓
QA Dashboard
```

> **Demo file:** `demo/Omnsight.mp4`

---

# 🚀 Features

* Browser automation with Playwright
* Responsive screenshot capture
* HTML/DOM capture
* FastAPI CI/CD webhook
* Qwen Vision-Language Model analysis
* Screenshot + HTML multimodal prompting
* UI anomaly detection
* Image optimization and focused cropping
* HTML reduction
* AI-generated source-code fixes
* Autonomous self-healing loop
* Retesting and verification
* Retry mechanism
* GitHub integration
* QA approval/rejection workflow
* React QA dashboard
* Automated API testing

---

# 🧠 Vision-Language Model

OmniSight uses:

```text
Qwen/Qwen3.5-0.8B
```

The VLM receives:

```text
Screenshot
+
Reduced HTML
```

and analyzes the interface for problems such as:

* Overlapping text
* Broken layouts
* Incorrect positioning
* Missing elements
* Responsive UI problems
* Visual inconsistencies

Example detected issue:

```json
{
  "id": "1",
  "type": "overlapping text",
  "severity": "medium",
  "description": "The 'Smart Watch' product title overlaps the image of the watch.",
  "element": "Product title",
  "suggested_fix": "Increase the card height to accommodate the image and text."
}
```

---

# 📸 Image Optimization

Large screenshots are optimized before being sent to the VLM.

```text
Original Screenshot

1440 × 1132
       ↓
Anomaly Detection
       ↓
Focused Crop

1024 × 796
       ↓
Qwen VLM
```

This reduces unnecessary visual information and improves VLM processing efficiency.

Endpoint:

```http
GET /optimization/status
```

---

# 📄 HTML Reduction

Raw HTML can contain a large amount of unnecessary information.

OmniSight reduces the HTML before VLM analysis.

Example:

```text
Original HTML

17,645 characters
       ↓
HTML Reduction
       ↓
2,994 characters
```

This improves:

* Token efficiency
* Processing speed
* Prompt quality
* VLM analysis

---

# 🤖 Self-Healing Agent

The self-healing system follows an autonomous loop:

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
Retest
   ↓
Verify
   ↓
   ├── Fixed → Publish
   │
   └── Not Fixed → Retry
```

The maximum number of attempts can be configured.

Example:

```json
{
  "url": "http://localhost:5173",
  "max_attempts": 2
}
```

---

# 🔧 Source Code Healing

The system can identify the source file responsible for the UI.

Example:

```text
demo-store/src/App.jsx
```

A generated fix can modify the React/Tailwind source.

Example:

```diff
- className="bg-white rounded-xl shadow-md overflow-hidden"
+ className="bg-white rounded-xl shadow-md"
```

After modification, OmniSight can retest the application.

---

# 🔄 Verification

After applying a fix, OmniSight performs another analysis.

```text
Issue still exists
        ↓
      Retry
```

or:

```text
Issue resolved
        ↓
      Publish
```

This prevents blindly accepting an AI-generated modification.

---

# 🐙 GitHub Integration

OmniSight integrates with GitHub using PyGithub.

The system can:

* Update source files
* Commit fixes
* Create healing branches
* Create pull requests
* Record commit information
* Support QA approval/rejection

Example commit:

```text
fix: apply OmniSight self-healing UI fix
```

If the healing and base branches are configured as the same branch, OmniSight uses direct-commit mode instead of creating a pull request.

---

# 📊 QA Dashboard

OmniSight includes a React dashboard for QA managers.

Dashboard:

```text
http://localhost:5174
```

The dashboard displays:

* Detected UI issues
* Severity
* Issue description
* Suggested fixes
* Screenshot evidence
* Healing status
* GitHub information
* QA approval
* QA rejection

Workflow:

```text
AI detects issue
       ↓
QA Dashboard
       ↓
Review Issue
       ↓
Approve / Reject
```

---

# 📅 Development Timeline

## Week 1 — Browser Automation & API

Implemented:

* FastAPI server
* Webhook receiver
* Playwright automation
* Browser navigation
* Checkout automation
* Screenshot capture
* HTML capture
* Responsive screenshots

Main endpoint:

```http
POST /navigation/run
```

---

## Week 2 — Multimodal UI Analysis

Implemented:

* Qwen VLM integration
* Screenshot analysis
* HTML analysis
* Screenshot + HTML prompting
* UI issue detection
* Severity classification
* Suggested fixes
* Image optimization
* HTML reduction

Main endpoint:

```http
POST /vision/analyze
```

---

## Week 3 — Self-Healing & GitHub

Implemented:

* Fix extraction
* Source-code modification
* Retesting
* Verification
* Retry mechanism
* GitHub integration
* Commit creation
* Pull-request workflow

Main endpoint:

```http
POST /healing/run
```

---

## Week 4 — Dashboard & Optimization

Implemented:

* React QA dashboard
* Issue visualization
* QA approval
* QA rejection
* GitHub status
* Image chunking/cropping
* HTML reduction
* Optimization monitoring
* End-to-end workflow

---

# 📁 Project Structure

```text
OmniSight_Multimodal_UI_SelfHealing_RPA-Agent/
│
├── main.py
├── graph.py
├── navigation.py
├── vision_analyzer.py
├── action_engine.py
├── github_integration.py
├── optimizer.py
│
├── tests/
│   └── test_api.py
│
├── screenshots/
│   └── *.png
│
├── outputs/
│   ├── *.html
│   └── chunks/
│       └── *.png
│
├── demo/
│   └── Omnsight.mp4
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
├── pyproject.toml
├── uv.lock
├── .env
├── .gitignore
└── README.md
```

---

# ⚙️ Installation

## 1. Clone the repository

```bash
git clone https://github.com/Sandhya03242/OmniSight_Multimodal_UI_SelfHealing_RPA-Agent.git
cd OmniSight_Multimodal_UI_SelfHealing_RPA-Agent
```

---

## 2. Install Python dependencies

The project uses `uv`.

```bash
uv sync
```

If required:

```bash
uv add fastapi uvicorn playwright requests pytest
```

---

## 3. Install Playwright

```bash
uv run playwright install chromium
```

---

# 🔐 Environment Variables

Create a `.env` file:

```env
GITHUB_TOKEN=your_github_token
GITHUB_REPOSITORY=Sandhya03242/OmniSight_Multimodal_UI_SelfHealing_RPA-Agent
GITHUB_BASE_BRANCH=main
GITHUB_HEALING_BRANCH=main
```

**Never commit `.env` or GitHub tokens to GitHub.**

Make sure `.env` is included in `.gitignore`.

---

# ▶️ Running the Project

OmniSight uses three applications.

## 1. Start Mock Store

Open a terminal:

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

## 2. Start FastAPI

From the OmniSight root directory:

```bash
uv run python -m uvicorn main:app --reload --port 8000
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

## 3. Start React Dashboard

Open another terminal:

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

# 🔌 API Endpoints

| Method | Endpoint                 | Purpose                    |
| ------ | ------------------------ | -------------------------- |
| GET    | `/`                      | API information            |
| GET    | `/health`                | Health check               |
| POST   | `/navigation/run`        | Playwright navigation      |
| POST   | `/vision/analyze`        | VLM UI analysis            |
| POST   | `/actions/extract-fixes` | Generate fixes             |
| POST   | `/webhook`               | CI/CD webhook              |
| POST   | `/healing/run`           | Full self-healing pipeline |
| GET    | `/healing/status`        | Healing status             |
| GET    | `/optimization/status`   | Optimization status        |
| GET    | `/dashboard/issues`      | Detected issues            |
| GET    | `/dashboard/status`      | Dashboard/project status   |
| POST   | `/github/pr/approve`     | QA approval                |
| POST   | `/github/pr/reject`      | QA rejection               |

---

# 🧪 Complete API Testing

Swagger UI:

```text
http://localhost:8000/docs
```

The following endpoints should be tested in order.

---

## 1. GET `/`

Execute:

```http
GET /
```

Expected:

```json
{
  "message": "OmniSight API is running",
  "version": "4.0.0"
}
```

**Result: PASS ✅**

---

## 2. GET `/health`

Execute:

```http
GET /health
```

Expected:

```json
{
  "status": "healthy"
}
```

**Result: PASS ✅**

---

## 3. POST `/navigation/run`

Request:

```json
{
  "url": "http://localhost:5173",
  "max_attempts": 2
}
```

Expected:

```text
200 OK
```

The endpoint should perform Playwright browser navigation and generate:

```text
Screenshot
HTML
Responsive screenshots
```

**Result: PASS ✅**

---

## 4. POST `/vision/analyze`

Use the screenshot and HTML generated by the navigation endpoint.

Example:

```json
{
  "screenshot_path": "screenshots\\healing_desktop.png",
  "html_path": "outputs\\healing_desktop.html"
}
```

Expected:

```text
200 OK
```

The response should contain VLM analysis and detected issues.

**Result: PASS ✅**

---

## 5. POST `/actions/extract-fixes`

Request:

```json
{
  "screenshot_path": "screenshots\\healing_desktop.png",
  "html_path": "outputs\\healing_desktop.html"
}
```

Expected:

```text
200 OK
```

The response should contain issue/fix information.

**Result: PASS ✅**

---

## 6. POST `/webhook`

Request:

```json
{
  "event": "build",
  "url": "http://localhost:5173",
  "branch": "main"
}
```

Expected:

```json
{
  "status": "received",
  "event": "build",
  "url": "http://localhost:5173",
  "branch": "main",
  "message": "OmniSight webhook received successfully."
}
```

**Result: PASS ✅**

---

# ⭐ 7. POST `/healing/run`

This is the main end-to-end test.

Request:

```json
{
  "url": "http://localhost:5173",
  "max_attempts": 2
}
```

Pipeline:

```text
Playwright
    ↓
Screenshot + HTML
    ↓
Image Optimization
    ↓
HTML Reduction
    ↓
Qwen VLM
    ↓
Issue Detection
    ↓
Fix Generation
    ↓
Source Healing
    ↓
Retest
    ↓
Verification
    ↓
GitHub
```

Expected successful status:

```text
published
```

**Result: PASS ✅**

---

## 8. GET `/healing/status`

Execute after `/healing/run`.

Example:

```json
{
  "status": "published",
  "attempt": 1,
  "fixed": true,
  "error": ""
}
```

**Result: PASS ✅**

---

## 9. GET `/optimization/status`

Expected information includes:

```json
{
  "image_optimization": {
    "original": {
      "width": 1440,
      "height": 1132
    },
    "focused": {
      "width": 1024,
      "height": 796
    },
    "bbox": [0, 27, 1440, 1090],
    "status": "optimized"
  },
  "html_reduction": {
    "enabled": true,
    "original_length": 17645,
    "reduced_length": 2994
  },
  "enabled": true
}
```

**Result: PASS ✅**

---

## 10. GET `/dashboard/issues`

Expected:

```json
{
  "status": "success",
  "count": 1,
  "issues": []
}
```

The issue object contains information such as:

```text
id
type
severity
description
element
suggested_fix
status
screenshot
```

**Result: PASS ✅**

---

## 11. GET `/dashboard/status`

Expected:

```json
{
  "project": "OmniSight",
  "version": "4.0.0",
  "healing_status": "published",
  "issues_detected": 1,
  "fixed": true
}
```

**Result: PASS ✅**

---

## 12. POST `/github/pr/approve`

Test request:

```json
{
  "issue_id": "1",
  "pr_number": 0,
  "comment": "Approved for testing"
}
```

Expected:

```json
{
  "status": "approved",
  "issue_id": "1",
  "pr_number": 0,
  "message": "QA approval recorded successfully."
}
```

**Result: PASS ✅**

> `pr_number: 0` is only a test value when using the current direct-commit configuration. It does not represent an actual GitHub PR #0.

---

## 13. POST `/github/pr/reject`

Test request:

```json
{
  "issue_id": "1",
  "pr_number": 0,
  "comment": "Rejected for testing"
}
```

Expected:

```json
{
  "status": "rejected",
  "issue_id": "1",
  "pr_number": 0,
  "message": "QA rejection recorded successfully."
}
```

**Result: PASS ✅**

---

# 🧪 Automated Testing

The project also includes:

```text
tests/test_api.py
```

Install testing dependencies:

```bash
uv add requests pytest
```

Run all tests:

```bash
uv run pytest tests/test_api.py -v
```

Run navigation test:

```bash
uv run pytest tests/test_api.py -v -k navigation
```

Run complete healing test:

```bash
uv run pytest tests/test_api.py -v -k full_healing
```

The full healing test can take several minutes because the local VLM performs inference.

---

# ✅ Final Testing Checklist

| #  | Endpoint                      | Status |
| -- | ----------------------------- | ------ |
| 1  | `GET /`                       | ✅ PASS |
| 2  | `GET /health`                 | ✅ PASS |
| 3  | `POST /navigation/run`        | ✅ PASS |
| 4  | `POST /vision/analyze`        | ✅ PASS |
| 5  | `POST /actions/extract-fixes` | ✅ PASS |
| 6  | `POST /webhook`               | ✅ PASS |
| 7  | `POST /healing/run`           | ✅ PASS |
| 8  | `GET /healing/status`         | ✅ PASS |
| 9  | `GET /optimization/status`    | ✅ PASS |
| 10 | `GET /dashboard/issues`       | ✅ PASS |
| 11 | `GET /dashboard/status`       | ✅ PASS |
| 12 | `POST /github/pr/approve`     | ✅ PASS |
| 13 | `POST /github/pr/reject`      | ✅ PASS |

---

# 📈 Example Optimization Result

Before optimization:

```text
Screenshot:
1440 × 1132

HTML:
17,645 characters
```

After optimization:

```text
Focused Screenshot:
1024 × 796

Reduced HTML:
2,994 characters
```

---

# 🏗️ System Architecture

```text
                    ┌─────────────────────┐
                    │     CI/CD Pipeline  │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │       FastAPI       │
                    │    CI/CD Gateway    │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │      Playwright     │
                    │   Browser Automation│
                    └──────────┬──────────┘
                               │
                    ┌──────────┴──────────┐
                    ▼                     ▼
              Screenshot                HTML
                    │                     │
                    ▼                     ▼
             Image Optimizer       HTML Reducer
                    │                     │
                    └──────────┬──────────┘
                               ▼
                    ┌─────────────────────┐
                    │      Qwen VLM       │
                    │   Visual Analysis    │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │   Issue Detection   │
                    │   + Fix Generation  │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │    Source Healing   │
                    │       App.jsx       │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │ Retest + Verification│
                    └──────────┬──────────┘
                               │
                    ┌──────────┴──────────┐
                    ▼                     ▼
                 Fixed               Not Fixed
                    │                     │
                    ▼                     ▼
                 GitHub              Retry Loop
                    │
                    ▼
             ┌───────────────────┐
             │    QA Dashboard   │
             └───────────────────┘
```

---

# 🛠️ Technology Stack

| Category             | Technology           |
| -------------------- | -------------------- |
| Programming Language | Python               |
| Backend              | FastAPI              |
| Browser Automation   | Playwright           |
| AI/VLM               | Qwen                 |
| Agent Workflow       | LangGraph            |
| Frontend             | React                |
| Build Tool           | Vite                 |
| Source Healing       | Python               |
| GitHub Integration   | PyGithub             |
| Package Manager      | uv                   |
| Testing              | Pytest               |
| API Testing          | Requests             |
| UI                   | React / Tailwind CSS |
| Version Control      | Git/GitHub           |

---

# 🎯 Project Objective

Traditional UI automation depends heavily on fixed selectors:

```text
button.login-button
```

If the application changes:

```text
button.login-button
        ↓
button.primary-login
```

the automation can fail.

OmniSight combines:

```text
DOM understanding
+
Visual understanding
+
AI reasoning
+
Autonomous remediation
```

to detect UI problems and attempt to repair them automatically.

---

# 🌟 Key Innovation

Traditional workflow:

```text
Test Failure
     ↓
Developer investigates
     ↓
Developer fixes
     ↓
Developer retests
```

OmniSight:

```text
Test Failure
     ↓
AI investigates
     ↓
AI generates fix
     ↓
AI applies fix
     ↓
AI retests
     ↓
AI verifies
     ↓
GitHub integration
     ↓
QA review
```

---

# 📌 Final Pipeline

```text
Playwright
    ↓
Screenshot + HTML
    ↓
Image + HTML Optimization
    ↓
Qwen VLM
    ↓
Issue Detection
    ↓
Fix Generation
    ↓
Source Code Healing
    ↓
Retesting
    ↓
Verification
    ↓
GitHub
    ↓
QA Dashboard
```

---

# ✅ Project Completion

## Week 1

```text
✅ FastAPI
✅ Playwright
✅ Browser navigation
✅ Checkout automation
✅ Screenshot capture
✅ HTML capture
```

## Week 2

```text
✅ Qwen VLM
✅ Screenshot analysis
✅ HTML analysis
✅ UI issue detection
✅ Image optimization
✅ HTML reduction
```

## Week 3

```text
✅ Fix generation
✅ Source modification
✅ Retesting
✅ Verification
✅ Retry loop
✅ GitHub integration
```

## Week 4

```text
✅ React QA Dashboard
✅ Issue visualization
✅ QA approval
✅ QA rejection
✅ Optimization monitoring
✅ End-to-end workflow
```

---

# 👩‍💻 Author

**Sandhya S**

GitHub:

https://github.com/Sandhya03242

---


