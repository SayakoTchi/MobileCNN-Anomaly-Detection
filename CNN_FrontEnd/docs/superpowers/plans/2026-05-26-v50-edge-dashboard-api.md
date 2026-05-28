# V50 Edge Dashboard API Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the browser-side API service and dashboard UI wiring for the V50 edge node API.

**Architecture:** Flask serves one Jinja template. ES modules split network calls from DOM rendering so V50 API behavior is testable without a browser.

**Tech Stack:** Flask, Bootstrap, Vanilla JavaScript ES modules, Node built-in test assertions.

---

### Task 1: API Service Tests

**Files:**
- Create: `static/js/v50Api.test.mjs`
- Create: `static/js/v50Api.mjs`

- [ ] **Step 1: Write failing tests**

Create tests that import `V50ApiClient` and assert that `/ping`, `/api/config`, `/api/detect`, `/api/timeline`, `/api/model/swap`, and clip URL helpers call the expected endpoints.

- [ ] **Step 2: Run tests to verify RED**

Run: `node static/js/v50Api.test.mjs`

Expected: fail because `static/js/v50Api.mjs` does not exist yet.

- [ ] **Step 3: Implement API service**

Create `V50ApiClient` with timeout-aware `fetch`, JSON/text parsing, binary detect upload, and readable errors.

- [ ] **Step 4: Run tests to verify GREEN**

Run: `node static/js/v50Api.test.mjs`

Expected: all tests pass.

### Task 2: Dashboard UI Wiring

**Files:**
- Create: `static/js/dashboard.mjs`
- Modify: `templates/index.html`

- [ ] **Step 1: Add stable markup**

Replace placeholder/static event blocks with controls for V50 base URL, health check, threshold update, frame upload, model swap, recent events, history, anomaly cards, and status messages.

- [ ] **Step 2: Implement DOM controller**

Import `V50ApiClient`, bind buttons/forms, render timeline items, render clip images by absolute V50 URLs, and show API errors in alerts.

- [ ] **Step 3: Verify syntax**

Run: `node --check static/js/dashboard.mjs`

Expected: no syntax errors.

### Task 3: Flask Smoke Check

**Files:**
- Modify: `app.py` only if serving static assets needs adjustment.

- [ ] **Step 1: Compile Python**

Run: `python -m py_compile app.py`

Expected: exit code 0.

- [ ] **Step 2: Re-run JS tests**

Run: `node static/js/v50Api.test.mjs`

Expected: all tests pass.
