<div align="center">

# 👻 Site-Ghost

### The AI-Powered Agentic Browser Auditor

**15 MCP Tools · 11 Expert Skills · Playwright Video Recording · Precision DOM Mapping**

[![Python](https://img.shields.io/badge/Python-3.10+-3776AB.svg?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![Playwright](https://img.shields.io/badge/Engine-Playwright-2EAD33.svg?style=for-the-badge&logo=playwright&logoColor=white)](https://playwright.dev)
[![MCP](https://img.shields.io/badge/Protocol-MCP-FF6B6B.svg?style=for-the-badge)](https://modelcontextprotocol.io)
[![Tests](https://img.shields.io/badge/Tests-26%2F26_Passed-00C851.svg?style=for-the-badge)](.)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](LICENSE)

</div>

---

Site-Ghost is a **headless Chromium daemon** that gives AI coding assistants (Cursor, Claude Desktop, Gemini CLI) superhuman browser control. Unlike screenshot-based browser tools that "guess" where elements are, Site-Ghost injects a **Precision DOM Mapper** directly into every page — giving the AI exact pixel coordinates, computed styles, animation states, and live mutation tracking.

Every interaction is automatically **video-recorded** as `.webm` snippets. The AI doesn't just "see" a static screenshot — it watches transitions happen in real time.

## How It's Different

| Feature | Standard Tools | Site-Ghost |
|---------|---------------|------------|
| Element targeting | Accessibility tree (imprecise) | **Exact (x,y) + bounding box** |
| Style awareness | None | **Font, color, padding, z-index** |
| Animation detection | None | **CSS animation + transition tracking** |
| Live DOM changes | None | **MutationObserver injection** |
| Interaction recording | Screenshot | **Full Playwright video** |
| Network monitoring | None | **All requests + failures** |
| Performance metrics | None | **Core Web Vitals (FCP, LCP)** |
| Console errors | None | **Live error/warning capture** |
| JS injection | None | **Execute arbitrary JS on page** |

---

## ⚡ Quick Start

Phantom MCP is distributed as an executable Python package. You can install and run it natively on **Windows, macOS, and Linux** using either `uv` or `pip`.

### 1. The Zero-Install Way (Recommended)
If you have [`uv`](https://docs.astral.sh/uv/) installed (the modern, ultra-fast Python package manager used by Claude/Cursor), you don't even need to download the repository. Just add this to your AI config:

**Cursor / Claude Desktop Config:**
```json
{
  "mcpServers": {
    "phantom-mcp": {
      "command": "uvx",
      "args": ["phantom-mcp"]
    }
  }
}
```

### 2. The Global Pip Install
If you prefer to install it permanently on your system so the command `phantom-mcp` is globally available everywhere:

```bash
# Windows / macOS / Linux
pip install git+https://github.com/bazx-bit/phantom_mcp.git
playwright install chromium
```

Then add this to your AI:

**Gemini CLI:**
```bash
gemini mcp add phantom-mcp -- phantom-mcp
```

**Cursor / Claude Desktop Config:**
```json
{
  "mcpServers": {
    "phantom-mcp": {
      "command": "phantom-mcp",
      "args": []
    }
  }
}
```

Then just ask your AI:
> "Assume the Visual Forensics Analyst persona and audit https://example.com for design quality."

---

## 🔧 15 MCP Tools

### Navigation & Observation
| Tool | Description |
|------|-------------|
| `ghost_goto` | Navigate to any URL (waits for network idle) |
| `ghost_map_dom` | Inject precision mapper — coordinates, styles, animations |
| `ghost_extract_links` | Extract all anchor links from the page |
| `ghost_screenshot` | Take a named screenshot (full page or viewport) |
| `ghost_video_status` | Get the path to the current `.webm` recording |

### Interaction
| Tool | Description |
|------|-------------|
| `ghost_interact` | Click, type, hover, select, focus, check, uncheck |
| `ghost_scroll` | Scroll up/down/top/bottom by pixel count |
| `ghost_drag` | Drag one element onto another |
| `ghost_viewport` | Resize viewport (mobile, tablet, desktop, ultrawide) |
| `ghost_wait_for` | Wait for a CSS selector to appear |

### Intelligence
| Tool | Description |
|------|-------------|
| `ghost_execute_js` | Inject and run arbitrary JavaScript on the live page |
| `ghost_drain_mutations` | Pull DOM changes from the injected MutationObserver |
| `ghost_network_log` | Get all HTTP requests since last navigation |
| `ghost_performance` | Extract Core Web Vitals (FCP, load time, transfer size) |
| `ghost_cookies` | Read all cookies set by the page |

---

## 🧠 11 Expert Skills

Skills are opinionated AI personas loaded via MCP Prompts. Each one transforms the AI into a hyper-specialized auditor with a strict workflow, scoring rubric, and output template.

| Skill | Persona | What it does |
|-------|---------|-------------|
| `aesthetic_auditor` | Senior Design Critic | Typography, color, spacing, responsive, animation polish |
| `animation_auditor` | Motion Design Engineer | Scroll triggers, micro-interactions, GPU acceleration |
| `interaction_tester` | QA Automation Engineer | Click every button, fill every form, break every flow |
| `deep_crawler` | Web Crawler Intelligence | Breadth-first sitemap, orphan pages, hidden endpoints |
| `performance_profiler` | Performance Engineer | Core Web Vitals, render-blocking, image optimization |
| `accessibility_auditor` | WCAG 2.2 Expert | ARIA, keyboard nav, contrast ratios, landmarks |
| `security_scanner` | White-Hat Pen Tester | Exposed .env, hardcoded secrets, CSRF, cookie flags |
| `responsive_stress_test` | Device Compat. Engineer | 12 viewports from Apple Watch to ultrawide |
| `conversion_optimizer` | CRO Growth Strategist | 3-second test, CTA audit, trust signals, friction |
| `visual_regression` | Regression Test Engine | Multi-viewport baseline capture and comparison |
| `competitor_analysis` | Competitive Intel Analyst | Side-by-side comparison across perf, design, content |

---

## 🏗️ Project Structure

```
site-ghost/
├── engine/                         # Core Playwright browser daemon
│   └── src/
│       ├── server.py               # MCP Server — 15 tools + skill loader
│       ├── ghost_browser.py        # Async Playwright manager
│       └── dom_mapper.js           # Precision JS payload
├── skills/                         # AI persona prompts (auto-discovered)
│   ├── aesthetic_auditor.md
│   ├── animation_auditor.md
│   ├── interaction_tester.md
│   ├── deep_crawler.md
│   ├── performance_profiler.md
│   ├── accessibility_auditor.md
│   ├── security_scanner.md
│   ├── responsive_stress_test.md
│   ├── conversion_optimizer.md
│   ├── visual_regression.md
│   └── competitor_analysis.md
├── test/                           # Test infrastructure
│   ├── engine_test.py              # 26-test verification suite
│   ├── fixtures/                   # Test HTML pages
│   └── helpers/                    # Test utilities
├── references/                     # Design reference documents
│   ├── issue-taxonomy.md           # Categorized UX/UI issue types
│   └── scoring-rubrics.md          # Standard scoring thresholds
├── .github/workflows/test.yml      # CI configuration
├── ARCHITECTURE.md                 # Why decisions were made
├── CONTRIBUTING.md                 # Development workflow
├── CHANGELOG.md                    # Release history
├── TODO.md                         # Roadmap
├── LICENSE                         # MIT
├── VERSION                         # 1.0.0
├── setup.bat                       # Windows setup
├── setup.sh                        # macOS/Linux setup
├── pyproject.toml
└── README.md
```

---

## 🧪 Test Results

```
👻 SITE-GHOST ENGINE TEST SUITE
============================================================
[1/10]  Initializing Playwright daemon...   ✅✅
[2/10]  Navigation...                       ✅✅
[3/10]  Precision DOM Mapping...            ✅✅✅✅
[4/10]  Interactions (hover, click)...      ✅✅
[5/10]  Scroll control...                   ✅✅
[6/10]  Viewport control...                 ✅✅
[7/10]  Named screenshot...                 ✅
[8/10]  Live JavaScript injection...        ✅✅
[9/10]  Performance metrics...              ✅✅✅
[10/10] Link extraction & Network log...    ✅✅✅✅✅
============================================================
👻 RESULTS: 26/26 passed | 0 failed
🎉 ALL TESTS PASSED — ENGINE IS COMBAT-READY
```

---

## 📚 Documentation

| Document | Description |
|----------|-------------|
| [ARCHITECTURE.md](ARCHITECTURE.md) | Why every design decision was made |
| [CONTRIBUTING.md](CONTRIBUTING.md) | How to add skills and tools |
| [CHANGELOG.md](CHANGELOG.md) | Release history |
| [TODO.md](TODO.md) | Roadmap and known limitations |

---

## 📄 License

MIT — Use it, fork it, ship it.

---

<div align="center">
<sub>Built by <a href="https://forgexdev.online">forgexdev.online</a></sub>
</div>
