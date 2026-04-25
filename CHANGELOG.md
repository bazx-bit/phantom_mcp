# Changelog

All notable changes to Site-Ghost are documented in this file.

## [1.2.0] - 2026-04-25

### Added — Phantom Forge Release
- **Phantom Architect Skill**: Agentic developer persona for high-fidelity cloning vs clean development decisions.
- **Creative Director Skill**: Design-heavy persona focused on award-winning aesthetics and kinetic DNA.
- **DNA Extractor Tool** (`ghost_extract_dna`): Captures exact easing, duration, and GSAP timeline physics from any site.
- **Clone Engine Tool** (`ghost_clone_engine`): Full SPA cloning with Brain Surgeon proxy for offline analysis.
- **ForgeX Showcase**: Cinematic HTML demonstration of engine capabilities.

### Fixed
- **Windows UTF-8 Encoding**: Added explicit encoding support to scripts/tests to prevent `UnicodeEncodeError` in Windows terminals.
- **Skill Quality Gate**: Updated all core skills with mandatory `Prime Directive`, `Workflow`, and `Scoring Rubric` headers.

## [1.1.0] - 2026-04-21

### Added
- **Agentic Eye Deployment**: Finalized high-fidelity vision integration.
- **ghost_status tool**: Track daemon health and resource usage.

## [1.0.0] - 2026-04-16

### Added — Core Engine
- **Precision DOM Mapper** (`dom_mapper.js`): Injects into pages to extract exact bounding boxes, computed styles, animation states, and z-index for every visible element. Draws magenta overlays on interactive elements and cyan on animated elements.
- **MutationObserver Injection**: The DOM mapper installs a persistent `MutationObserver` on `document.body` to track live DOM changes (element additions, removals, attribute changes).
- **Async Playwright Manager** (`ghost_browser.py`): Persistent headless Chromium daemon with:
  - Native `.webm` video recording of every session
  - Console error/warning trapping
  - Network request logging (success + failure)
  - 15 interaction methods: navigate, map_dom, click, type, hover, select, focus, check, uncheck, scroll, drag, viewport, screenshot, execute_js, wait_for

### Added — MCP Server
- **15 MCP Tools** exposed via `server.py`:
  - Navigation: `ghost_goto`, `ghost_extract_links`
  - DOM: `ghost_map_dom`, `ghost_wait_for`
  - Interaction: `ghost_interact`, `ghost_scroll`, `ghost_drag`
  - Viewport: `ghost_viewport`, `ghost_screenshot`
  - Intelligence: `ghost_execute_js`, `ghost_drain_mutations`, `ghost_network_log`, `ghost_performance`, `ghost_cookies`
  - Recording: `ghost_video_status`
- **MCP Prompts (Skills)**: Auto-discovers `skills/*.md` files and exposes them as selectable AI personas via `list_prompts()` / `get_prompt()`

### Added — 11 Expert Skills
- `aesthetic_auditor` — Typography, color, spacing, responsive, animation polish (0-100 score)
- `animation_auditor` — Scroll triggers, micro-interactions, GPU acceleration, reduced motion
- `interaction_tester` — Click every button, fill every form, break every flow (5-15 bugs)
- `deep_crawler` — Breadth-first sitemap, orphan pages, hidden endpoints, SEO meta
- `performance_profiler` — Core Web Vitals, render-blocking, image optimization, DOM bloat
- `accessibility_auditor` — WCAG 2.2 AA: ARIA, keyboard nav, contrast, landmarks, touch targets
- `security_scanner` — Exposed .env, hardcoded secrets, CSRF, cookie flags, mixed content
- `responsive_stress_test` — 12 viewports from Apple Watch to ultrawide
- `conversion_optimizer` — 3-second test, CTA audit, trust signals, friction analysis
- `visual_regression` — Multi-viewport baseline capture and comparison
- `competitor_analysis` — Side-by-side perf, design, content, tech stack comparison

### Added — Project Infrastructure
- `ARCHITECTURE.md` — Design decisions and technical rationale
- `CONTRIBUTING.md` — Development workflow and skill authoring guide
- `CHANGELOG.md` — This file
- `.github/workflows/test.yml` — CI test runner
- `test/engine_test.py` — 26-test verification suite (26/26 passing)
- Professional directory structure: `engine/src/`, `skills/`, `test/`, `bin/`, `scripts/`, `references/`

### Fixed
- Playwright `request.response()` is async in Python — fixed network handler to avoid `AttributeError: 'coroutine' object has no attribute 'status'`
