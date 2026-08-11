# OmniSight - Week 1: Browser Automation with Playwright

## Overview

This is the Week 1 implementation of the **OmniSight: Multimodal UI Self-Healing & RPA Agent** project.

The objective of this module is to automate browser interactions using Playwright and capture screenshots of a web page. This serves as the foundation for future AI-powered UI testing and self-healing automation.

---

## Features

- Launch Chromium browser
- Navigate to a website
- Capture full-page screenshots
- Run in headless mode
- Automatically create the screenshots directory

---

## Tech Stack

- Python 3.11+
- Playwright
- Chromium

---

## Project Structure

```
OmniSight_Multimodal_UI_SelfHealing_RPA-Agent/
│
├── playwright_bot.py
├── screenshots/
│   └── homepage.png
├── README.md
└── pyproject.toml
```

---

## Installation

### Clone the Repository

```bash
git clone https://github.com/your-username/OmniSight_Multimodal_UI_SelfHealing_RPA-Agent.git

cd OmniSight_Multimodal_UI_SelfHealing_RPA-Agent
```

### Install Dependencies

Using **uv**

```bash
uv sync
```

Install Playwright browsers

```bash
uv run python -m playwright install
```

---

## Run the Project

```bash
uv run python playwright_bot.py
```

---

## Output

The script will:

1. Launch Chromium.
2. Open the target website.
3. Capture a full-page screenshot.
4. Save the image inside the `screenshots` folder.

Example output:

```text
Screenshot Saved
```

Generated file:

```
screenshots/
└── homepage.png
```

---

## Current Progress

- ✅ Browser automation
- ✅ Headless execution
- ✅ Screenshot capture
- ✅ Responsive viewport

---

## Future Enhancements

- Capture HTML source
- Integrate Vision Language Models (GPT-4o / LLaVA)
- Detect UI issues automatically
- Generate CSS fixes
- Self-healing UI workflow
- GitHub Pull Request automation

