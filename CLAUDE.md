# Site-Ghost Development

## Commands

```bash
pip install -e ".[dev]"  # install for development
python test/engine_test.py  # run full engine test suite (26 tests)
python scripts/skill_check.py  # validate all skills in skills/ directory
python demo.py  # run live demo against stripe.com
```

## Project Structure

```
site-ghost/
├── engine/src/          # Core logic (server, browser manager, DOM mapper)
│   ├── server.py        # MCP Server entry point
│   ├── ghost_browser.py # Playwright manager
│   └── dom_mapper.js    # Precision JS payload
├── skills/              # AI persona prompts (auto-loaded as MCP Prompts)
├── test/                # Test suite + fixtures
├── scripts/             # Quality & dev tooling
├── examples/            # Advanced usage demonstrations
├── bin/                 # CLI wrappers
├── references/          # Scoring rubrics & taxonomy docs
└── .ghost/              # Runtime artifacts (screenshots, videos)
```

## Skill Workflow

Skills are Markdown files in `skills/`. `server.py` auto-discovers these at runtime.

1. **Create** a new `.md` in `skills/`.
2. **Validate** using `python scripts/skill_check.py`.
3. **Restart** the MCP server to see the new prompt.

Required headings for every skill:
- `# 🔮 Title`
- `## Prime Directive`
- `## Workflow`
- `## Scoring Rubric`

## Browser Interaction

Site-Ghost uses **Precision DOM Mapping**. Unlike accessibility-based tools, it injects JS to get pixel-perfect coordinates and CSS metrics. 

- Use `ghost_map_dom` to refresh the interactive map.
- Coordinates are captured in `(x,y)` absolute page units.
- Video recordings are saved to `.ghost/video_feeds/`.

## Quality Gate

All PRs must pass:
1. `python test/engine_test.py` (Core Browser Logic)
2. `python scripts/skill_check.py` (Markdown Quality)
3. No manual edits to `CHANGELOG.md` without a version bump in `VERSION`.
