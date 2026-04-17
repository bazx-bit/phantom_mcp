# Architecture

This document explains **why** Site-Ghost is built the way it is. For setup and usage, see the README. For contributing, see CONTRIBUTING.md.

## The core idea

Site-Ghost gives AI coding assistants (Cursor, Claude Desktop, Gemini CLI) a persistent headless browser and a set of opinionated auditing skills. The browser is the hard part — everything else is Markdown.

The key insight: standard AI browser tools rely on accessibility trees or static screenshots. Both are imprecise. An accessibility tree doesn't tell you that two elements overlap. A screenshot doesn't tell you the font size. Site-Ghost injects a **Precision DOM Mapper** directly into the page — giving the AI exact pixel coordinates, computed styles, animation states, and live mutation tracking.

```
AI Assistant                       Site-Ghost
───────────                       ──────────
                                  ┌─────────────────────────┐
  MCP Tool Call: ghost_map_dom    │  server.py (MCP Server)  │
  ────────────────────────────→   │  • dispatches tool call  │
                                  │  • manages browser state │
                                  └──────────┬──────────────┘
                                             │ async
                                  ┌──────────▼──────────────┐
                                  │  ghost_browser.py        │
                                  │  • persistent Chromium   │
                                  │  • video recording       │
                                  │  • console/network trap  │
                                  └──────────┬──────────────┘
                                             │ CDP
                                  ┌──────────▼──────────────┐
                                  │  Chromium (headless)      │
                                  │  • dom_mapper.js injected │
                                  │  • MutationObserver live  │
                                  │  • .webm video recording  │
                                  └──────────────────────────┘
```

First call starts everything (~3s). Every call after: ~200-500ms.

## Why Python + Playwright (not Bun/Node)

1. **MCP-native.** The `mcp` Python SDK is the canonical implementation. No JSON-RPC wiring, no custom HTTP server. `stdio_server()` handles everything.

2. **Async-first.** Python's `asyncio` + Playwright's async API means the browser daemon never blocks.  Video recording, console listening, and network logging all happen concurrently without threads.

3. **Zero-compile deployment.** No `bun build --compile`, no binary distribution. `pip install` + `playwright install chromium` and you're running. Works on Windows, macOS, and Linux identically.

4. **Skills are just Markdown.** The `skills/` directory is auto-discovered at runtime. Drop a `.md` file, restart the server, the AI sees a new prompt. No build step, no code generation.

## The ghost_id system

Ghost IDs (`g1`, `g2`, `g3`) are how the agent addresses page elements without writing CSS selectors.

### How it works

```
1. AI calls: ghost_map_dom()
2. Server injects dom_mapper.js into the live page
3. JS scans every visible element, assigns data-ghost-id="g1", "g2", ...
4. For each: calculates exact bounding box, computed styles, animation state
5. Draws magenta (interactive) or cyan (animated) overlays on the page
6. Takes a full-page screenshot with overlays visible
7. Returns structured JSON to the AI with coordinates and styles
8. AI calls: ghost_interact("g5", "click")
9. Server finds [data-ghost-id="g5"] → Playwright locator → click()
```

### Why DOM injection, not Locators

The original pirating-dom (gstack) uses Playwright's accessibility tree + `getByRole()` Locators. This is clean but misses:

- **Visual information.** The accessibility tree doesn't contain font sizes, colors, padding, or z-index. Site-Ghost needs this for aesthetic auditing.
- **Animation state.** CSS `animation-name` and `transition-duration` are invisible to ARIA.
- **Precise coordinates.** `getBoundingClientRect()` gives sub-pixel accuracy. ARIA doesn't.

The tradeoff: DOM injection can be blocked by strict CSP headers. For sites with `script-src 'none'`, the mapper will fail. This is acceptable — auditing a site with zero JS execution is a fundamentally different problem.

## Video recording

Playwright's `record_video_dir` option auto-records every page session as `.webm`. This is not per-action — it's continuous. The AI can reference the video path via `ghost_video_status()` to review transitions that static screenshots miss:

- Modal open/close animations
- Scroll-triggered reveals
- Form validation flows
- Page transition effects

Videos are saved to `.ghost/video_feeds/` and accumulate. They are never auto-deleted.

## The skill system

Skills are Markdown files in `skills/`. Each one is an opinionated system prompt that transforms the AI into a specialized auditor persona.

```
skills/
├── aesthetic_auditor.md        → Senior Design Critic
├── animation_auditor.md        → Motion Design Engineer
├── interaction_tester.md       → QA Automation Engineer
├── deep_crawler.md             → Web Crawler Intelligence
├── performance_profiler.md     → Performance Engineer
├── accessibility_auditor.md    → WCAG 2.2 Expert
├── security_scanner.md         → White-Hat Pen Tester
├── responsive_stress_test.md   → Device Compatibility Eng.
├── conversion_optimizer.md     → CRO Growth Strategist
├── visual_regression.md        → Regression Test Engine
└── competitor_analysis.md      → Competitive Intel Analyst
```

`server.py` reads this directory at runtime via `glob.glob()`. Each `.md` file becomes an MCP Prompt. The AI can select a skill, and the full markdown content is injected as a system message. Skills can reference any of the 15 tools — they are workflows, not permissions.

## Error philosophy

Errors are for AI agents, not humans. Every error message must be actionable:

- "Element not found" → "Element g42 not found on page. Run ghost_map_dom() to refresh the element map."
- "Navigation timeout" → "Navigation error: Timeout 20000ms exceeded. The page may be slow or unresponsive."

The agent should read the error and know what to do next without human intervention.

## What's intentionally not here

- **No persistent daemon.** Unlike gstack's HTTP server model, Site-Ghost uses MCP stdio. The browser lives for the duration of the MCP session. This is simpler and avoids orphaned processes.
- **No compiled binary.** Python source runs directly. No build step. Trade-off: ~100ms slower startup vs. zero deployment complexity.
- **No cookie import from real browsers.** We don't decrypt Chrome/Firefox cookie databases. If auth is needed, the AI can log in via `ghost_interact()`.
- **No iframe support.** `dom_mapper.js` runs in the top frame only. Cross-frame auditing is not yet implemented.
