# Site-Ghost Reference: Issue Taxonomy

This document categorizes common UX/UI issues that the AI auditor should detect,
organized by severity and type.

## Visual Issues

| ID | Issue | Severity | How to Detect |
|----|-------|----------|---------------|
| V-01 | Text overlapping another element | Critical | Bounding box intersection in ghost_map_dom() |
| V-02 | Image not loading (broken src) | High | `<img>` with naturalWidth === 0 |
| V-03 | Inconsistent padding between sections | Medium | Compare y-gaps between sequential sections |
| V-04 | Text too small on mobile (<14px) | Medium | fontSize from styles at 375px viewport |
| V-05 | Low contrast text | Medium | color vs backgroundColor ratio < 4.5:1 |
| V-06 | Horizontal overflow | High | `document.body.scrollWidth > window.innerWidth` |
| V-07 | Missing favicon | Low | No `<link rel="icon">` in head |
| V-08 | Blurry images (upscaled) | Medium | naturalWidth < clientWidth |

## Functional Issues

| ID | Issue | Severity | How to Detect |
|----|-------|----------|---------------|
| F-01 | Button with no click handler | Critical | ghost_interact → no mutations, no navigation |
| F-02 | Form submit does nothing | Critical | Click submit → no network request, no state change |
| F-03 | Link goes to 404 | High | ghost_goto(href) → page title contains "404" |
| F-04 | JavaScript error on page load | High | Console log contains [ERROR] |
| F-05 | Search returns no results for common terms | Medium | Type "test" → empty results |
| F-06 | Dropdown doesn't open | High | ghost_interact(hover/click) → no mutations |

## UX Issues

| ID | Issue | Severity | How to Detect |
|----|-------|----------|---------------|
| U-01 | No visible focus indicator | High | Tab through elements → no visual change |
| U-02 | Touch target too small (<44px) | Medium | Bounding box width/height from ghost_map_dom() |
| U-03 | No loading state | Medium | Click action → blank delay before response |
| U-04 | No error message on invalid form input | Medium | Submit invalid data → no validation text |
| U-05 | Keyboard trap in modal | Critical | Tab cycles inside modal, can't escape |

## Performance Issues

| ID | Issue | Severity | How to Detect |
|----|-------|----------|---------------|
| P-01 | FCP > 3 seconds | Critical | ghost_performance() → firstContentfulPaint |
| P-02 | Total transfer > 3MB | High | ghost_performance() → totalTransferSize |
| P-03 | Render-blocking JS | Medium | ghost_execute_js() → scripts without async/defer |
| P-04 | Images without lazy loading | Low | `<img>` without loading="lazy" below fold |
| P-05 | DOM node count > 2000 | Medium | ghost_execute_js() → querySelectorAll('*').length |
