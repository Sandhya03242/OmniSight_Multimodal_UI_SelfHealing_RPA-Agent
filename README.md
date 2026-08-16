# OmniSight - Week 1: Browser Automation & CI/CD Gateway

**Multimodal UI Self-Healing & RPA Agent**

## Overview

This is the Week 1 implementation of the **OmniSight: Multimodal UI Self-Healing & RPA Agent** project.

The goal of Week 1 is to build the foundation for automated UI testing using **FastAPI and Playwright**.

OmniSight receives CI/CD build information through FastAPI, uses Playwright to automate a browser, and captures screenshots of different application states.

---

## Features

- FastAPI CI/CD webhook
- Playwright browser automation
- Headless Chromium execution
- Automated login and checkout flow
- Desktop viewport testing
- Mobile viewport testing
- Full-page screenshots
- Automatic screenshot directory creation

---

## Tech Stack

- Python
- FastAPI
- Uvicorn
- Playwright
- Chromium
- uv

---

## Project Structure

```text
OmniSight/
│
├── main.py
├── playwright_bot.py
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
```

---

## Installation

### Install Dependencies

Using `uv`:

```bash
uv add fastapi "uvicorn[standard]" playwright
```

### Install Chromium

```bash
uv run playwright install chromium
```

---

## Run FastAPI

Start the FastAPI server:

```bash
uv run uvicorn main:app --reload
```

API:

```text
http://127.0.0.1:8000
```

Swagger API documentation:

```text
http://127.0.0.1:8000/docs
```

---

## Run Playwright

Open another terminal:

```bash
uv run python playwright_bot.py
```

The automation performs the following flow:

```text
Open Website
     ↓
Login
     ↓
Products
     ↓
Add Product
     ↓
Cart
     ↓
Checkout
     ↓
Capture Screenshots
     ↓
Mobile Testing
```

---

## Screenshots

Screenshots are automatically saved in the `screenshots/` directory.

```text
screenshots/
├── 01_login.png
├── 02_products.png
├── 03_product_added.png
├── 04_cart.png
├── 05_checkout.png
└── 06_mobile_products.png
```

---

## FastAPI Build Event

OmniSight provides a CI/CD webhook endpoint:

```text
POST /build-event
```

### Example Request

```json
{
  "repository": "OmniSight",
  "branch": "main",
  "commit_sha": "abc123",
  "staging_url": "https://www.saucedemo.com",
  "build_status": "success"
}
```

The endpoint receives build information from the CI/CD pipeline.

---

## GitHub Workflow

```text
Developer Push
      ↓
GitHub
      ↓
CI/CD Pipeline
      ↓
FastAPI
      ↓
Build Event
      ↓
Playwright
      ↓
Browser Testing
      ↓
Screenshots
```

---

## Week 1 Architecture

```text
CI/CD
  ↓
FastAPI
  ↓
Build Event
  ↓
Playwright
  ↓
Browser Automation
  ↓
Screenshots
```

---

## Current Progress

- ✅ FastAPI CI/CD gateway
- ✅ Playwright browser automation
- ✅ Headless Chromium execution
- ✅ Desktop testing
- ✅ Mobile viewport testing
- ✅ Checkout flow automation
- ✅ Automated screenshots

---

## Week 1 Result

The basic browser automation and CI/CD gateway are working successfully.

```text
CI/CD
  ↓
FastAPI
  ↓
Playwright
  ↓
Browser
  ↓
Screenshots
```


