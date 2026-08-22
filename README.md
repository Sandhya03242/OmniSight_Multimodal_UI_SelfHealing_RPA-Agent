# OmniSight - Week 1 & Week 2

## Multimodal UI Self-Healing & RPA Agent

## Overview

OmniSight is a **Multimodal UI Self-Healing & RPA Agent** designed to automate UI testing, capture webpage states, analyze UI structure, and build the foundation for intelligent UI issue detection and self-healing.

### Week 1

Week 1 focuses on building the foundation for automated browser testing using **FastAPI** and **Playwright**.

OmniSight receives CI/CD build information through FastAPI, launches a headless Chromium browser using Playwright, automates a login and checkout workflow, and captures screenshots of different application states.

### Week 2

Week 2 extends the project by preparing the system for **multimodal UI analysis**.

During this stage, OmniSight captures the raw HTML of the webpage and introduces a structured UI analysis prompt. The screenshot and HTML will later be provided together to an AI model for UI defect detection and automated fix generation.

---

# Features

## Week 1 Features

- FastAPI CI/CD webhook
- Playwright browser automation
- Headless Chromium execution
- Automated login flow
- Automated product selection
- Automated cart flow
- Automated checkout flow
- Desktop viewport testing
- Mobile viewport testing
- Full-page screenshots
- Automatic screenshot directory creation

## Week 2 Features

- Raw HTML capture
- Screenshot and HTML collection
- Structured UI analysis prompt
- Preparation for multimodal AI analysis
- Preparation for UI issue detection
- Preparation for automated code fix generation

---

# Tech Stack

- Python
- FastAPI
- Uvicorn
- Playwright
- Chromium
- uv

---

# Project Structure

```text
OmniSight/
│
├── main.py
├── playwright_bot.py
├── prompt.py
│
├── screenshots/
│   ├── 01_login.png
│   ├── 02_products.png
│   ├── 03_product_added.png
│   ├── 04_cart.png
│   ├── 05_checkout.png
│   └── 06_mobile_products.png
│
├── README.md
└── pyproject.toml





# UI Analysis Prompt

The prompt.py file contains a structured prompt for the future AI model.

The AI will be instructed to analyze both the screenshot and raw HTML and return information such as:

Whether a UI issue was detected
Issue severity
Issue type
Detailed description
Affected HTML element
Possible root cause
Recommended UI or CSS fix