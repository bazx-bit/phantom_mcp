# TODO

Tracked features, improvements, and known limitations for Site-Ghost.

## v1.1 — Browser Engine

- [ ] **iframe support.** `dom_mapper.js` currently runs only in the top frame. Cross-frame auditing requires `page.frames()` iteration and separate ghost_id namespaces per frame (e.g., `f1-g3`).
- [ ] **Cookie import from real browsers.** Decrypt Chrome/Firefox cookie databases (DPAPI on Windows, Keychain on macOS) to auto-authenticate without manual login flows.
- [ ] **Tab management.** Support multiple tabs with `ghost_new_tab()`, `ghost_switch_tab()`, `ghost_close_tab()`.
- [ ] **File upload.** Support `ghost_upload(ghost_id, file_path)` using Playwright's `set_input_files()`.
- [ ] **PDF generation.** `ghost_pdf(name)` to render the current page as PDF.

## v1.1 — DOM Mapper

- [ ] **Shadow DOM penetration.** Scan inside shadow roots for components using Web Components.
- [ ] **CSS Grid/Flexbox detection.** Report which layout mode each container uses.
- [ ] **Font loading detection.** Detect FOIT/FOUT (Flash of Invisible/Unstyled Text) by checking `document.fonts.ready`.
- [ ] **Contrast ratio calculation.** Compute WCAG contrast ratios directly in `dom_mapper.js` instead of relying on the AI to estimate from raw colors.

## v1.1 — Skills

- [ ] **SEO deep auditor.** Structured data (JSON-LD), Open Graph tags, Twitter cards, canonical URLs, hreflang.
- [ ] **Brand consistency checker.** Compare logo usage, color consistency, and font consistency across all pages.
- [ ] **Load test simulator.** Use `ghost_execute_js` to simulate rapid DOM changes and measure FPS drops.
- [ ] **Dark mode auditor.** Toggle `prefers-color-scheme: dark` and audit the dark mode implementation.

## v1.2 — Infrastructure

- [ ] **Eval framework.** LLM-as-judge to score skill quality (like gstack's Tier 3 testing).
- [ ] **Baseline snapshots.** Store DOM fingerprints + screenshots as versioned baselines for regression testing.
- [ ] **Report export.** Generate HTML reports with embedded screenshots and interactive charts.
- [ ] **Plugin system.** Allow users to drop custom skills into `~/.site-ghost/skills/` for personal workflows.

## Known Limitations

- **CSP-strict sites.** Sites with `script-src 'none'` will block `dom_mapper.js` injection. No workaround without disabling browser security.
- **Heavy SPAs.** Single-page apps with client-side routing may lose ghost_ids after internal navigation. Re-run `ghost_map_dom()` after each navigation.
- **Video file size.** Playwright records at full resolution. Long sessions produce large `.webm` files. Manual cleanup of `.ghost/video_feeds/` may be needed.
