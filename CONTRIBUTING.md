# Contributing to Site-Ghost

Thanks for wanting to make Site-Ghost better. Whether you're adding a new skill, improving the DOM mapper, or fixing a bug in the engine — this guide gets you running fast.

## Quick start

```bash
git clone https://github.com/bazx-bit/site-ghost.git
cd site-ghost
pip install -e ".[dev]"
playwright install chromium
```

Now edit any skill in `skills/`, edit the engine in `engine/src/`, and test with:

```bash
python test/engine_test.py
```

## Project structure

```
site-ghost/
├── engine/                    # Core Playwright browser daemon
│   └── src/
│       ├── server.py          # MCP Server — tool dispatch + skill loading
│       ├── ghost_browser.py   # Async Playwright manager (15 capabilities)
│       └── dom_mapper.js      # Precision JS payload injected into pages
├── skills/                    # AI persona prompts (auto-discovered)
│   ├── aesthetic_auditor.md
│   ├── animation_auditor.md
│   └── ... (11 total)
├── test/                      # Test infrastructure
│   ├── engine_test.py         # 26-test verification suite
│   ├── fixtures/              # Test HTML pages
│   └── helpers/               # Test utilities
├── references/                # Design reference documents
├── bin/                       # Utility scripts
├── scripts/                   # Build and CI scripts
├── .github/workflows/         # CI configuration
├── ARCHITECTURE.md            # Why decisions were made
├── CONTRIBUTING.md            # This file
├── CHANGELOG.md               # Release history
├── LICENSE                    # MIT
├── VERSION                    # Current version
├── pyproject.toml             # Python dependencies
└── README.md                  # Setup and usage
```

## Day-to-day workflow

### Adding a new skill

1. Create a new `.md` file in `skills/`:
   ```bash
   touch skills/my_new_skill.md
   ```

2. Follow this structure:
   ```markdown
   # 🔮 Skill Name

   You are a **[Persona]**. Your job is...

   ## Prime Directive
   **[The one rule this AI must never break]**

   ## Workflow
   ### Phase 1: ...
   ### Phase 2: ...

   ## Scoring Rubric (0-100)
   | Category | Weight |
   |----------|--------|

   ## Output Format
   ```

3. The skill is automatically discovered by `server.py` on next startup. No code changes needed.

### Adding a new browser tool

1. Add the method to `engine/src/ghost_browser.py`
2. Add the MCP tool definition to `list_tools()` in `engine/src/server.py`
3. Add the dispatch case to `call_tool()` in `engine/src/server.py`
4. Add a test in `test/engine_test.py`
5. Run the test suite to verify

### Modifying the DOM mapper

1. Edit `engine/src/dom_mapper.js`
2. The script is a self-executing IIFE that returns data to Python
3. It must return a `{ elements: [...], animatedCount: N }` object
4. Test by running `python test/engine_test.py`

## Testing

### Running tests

```bash
# Set encoding for Windows
$env:PYTHONIOENCODING="utf-8"

# Run the full suite
python test/engine_test.py
```

### Test coverage

The test suite verifies:
- Browser initialization and shutdown
- Navigation and page title extraction
- DOM mapping with element coordinates
- Interactions (hover, click)
- Scroll control (up, down, top, bottom)
- Viewport resizing (mobile, desktop)
- Named screenshots
- Live JavaScript injection
- Performance metric extraction
- Link extraction
- Network request logging
- Video recording
- MutationObserver drain
- Skill file loading

## Skill quality guidelines

Every skill should:
1. **Have a Prime Directive** — one sentence that defines the AI's mindset
2. **Use workflows with exact tool calls** — show the AI exactly what to run
3. **Include a scoring rubric** — quantifiable, not subjective
4. **Define output format** — markdown template the AI must follow
5. **List strict rules** — non-negotiable constraints

## Things to know

- **Skills are just Markdown.** Drop a `.md` in `skills/`, restart, done.
- **The engine is async.** All browser methods use `async/await`.
- **Videos accumulate.** `.ghost/video_feeds/` is never auto-cleaned.
- **Windows encoding.** Set `PYTHONIOENCODING=utf-8` for emoji output.
