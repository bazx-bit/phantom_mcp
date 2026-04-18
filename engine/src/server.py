import asyncio
import glob
import json
import os
import nest_asyncio
import mcp.types as types
from mcp.server import Server
from mcp.server.stdio import stdio_server
from ghost_browser import GhostBrowserManager

nest_asyncio.apply()

app = Server("Site-Ghost")
browser_manager = GhostBrowserManager()

SKILLS_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "skills")

# ─── TOOLS ────────────────────────────────────────────────────────

@app.list_tools()
async def list_tools() -> list[types.Tool]:
    return [
        # Navigation
        types.Tool(
            name="ghost_goto",
            description="Navigate the headless Chromium to a URL. Waits for network idle.",
            inputSchema={
                "type": "object",
                "properties": {
                    "url": {"type": "string", "description": "Full URL to navigate to."}
                },
                "required": ["url"]
            }
        ),
        # DOM Mapping
        types.Tool(
            name="ghost_map_dom",
            description="Inject precision DOM mapper. Returns every visible element with exact (x,y) coordinates, dimensions, fonts, colors, z-index, and animation state. Also takes an annotated screenshot with magenta (interactive) and cyan (animated) overlays. Installs a MutationObserver for live tracking.",
            inputSchema={"type": "object", "properties": {}}
        ),
        # Interact
        types.Tool(
            name="ghost_interact",
            description="Perform a precise action on a mapped ghost_id. Actions: click, type, hover, select, focus, check, uncheck.",
            inputSchema={
                "type": "object",
                "properties": {
                    "ghost_id": {"type": "string", "description": "The ghost ID (e.g. g5) from ghost_map_dom."},
                    "action": {"type": "string", "enum": ["click", "type", "hover", "select", "focus", "check", "uncheck"]},
                    "input_text": {"type": "string", "description": "Text to type or option to select."}
                },
                "required": ["ghost_id", "action"]
            }
        ),
        # Scroll
        types.Tool(
            name="ghost_scroll",
            description="Smooth-scroll the page like a real user. Directions: 'up', 'down', 'top', 'bottom'. The video recorder will capture the animation.",
            inputSchema={
                "type": "object",
                "properties": {
                    "direction": {"type": "string", "enum": ["up", "down", "top", "bottom"]},
                    "pixels": {"type": "integer", "description": "Pixels to scroll (default 500)."},
                    "smooth": {"type": "boolean", "description": "Smooth animated scroll (default true). Set false for instant jump."}
                },
                "required": ["direction"]
            }
        ),
        # Cinematic Scroll
        types.Tool(
            name="ghost_cinematic_scroll",
            description="Performs a slow, cinematic top-to-bottom scroll of the ENTIRE page. Takes a viewport screenshot at every stop. The video recorder captures the whole journey as a beautiful animation. Use this for full-page audits.",
            inputSchema={
                "type": "object",
                "properties": {
                    "step_px": {"type": "integer", "description": "Pixels per scroll step (default 300)."},
                    "pause_ms": {"type": "integer", "description": "Milliseconds to pause at each stop (default 800)."}
                }
            }
        ),
        # Drag
        types.Tool(
            name="ghost_drag",
            description="Drag one element onto another using ghost_ids.",
            inputSchema={
                "type": "object",
                "properties": {
                    "source_id": {"type": "string"},
                    "target_id": {"type": "string"}
                },
                "required": ["source_id", "target_id"]
            }
        ),
        # Viewport
        types.Tool(
            name="ghost_viewport",
            description="Change viewport size for responsive testing. Common: mobile (375x812), tablet (768x1024), desktop (1280x720).",
            inputSchema={
                "type": "object",
                "properties": {
                    "width": {"type": "integer"},
                    "height": {"type": "integer"}
                },
                "required": ["width", "height"]
            }
        ),
        # Screenshot
        types.Tool(
            name="ghost_screenshot",
            description="Take a named screenshot. Returns the absolute file path.",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "Filename without extension."},
                    "full_page": {"type": "boolean", "description": "Capture full page or viewport only."}
                },
                "required": ["name"]
            }
        ),
        # Execute JS
        types.Tool(
            name="ghost_execute_js",
            description="Inject and execute arbitrary JavaScript on the live page. Returns the result. Use this to probe animations, test DOM mutations, check localStorage, or alter styles in real-time.",
            inputSchema={
                "type": "object",
                "properties": {
                    "script": {"type": "string", "description": "JavaScript code to execute."}
                },
                "required": ["script"]
            }
        ),
        # Drain Mutations
        types.Tool(
            name="ghost_drain_mutations",
            description="Pull all DOM mutations captured by the injected MutationObserver since the last drain. Shows elements that were added, removed, or changed attributes.",
            inputSchema={"type": "object", "properties": {}}
        ),
        # Network Log
        types.Tool(
            name="ghost_network_log",
            description="Get all network requests since last navigation. Shows URL, method, status, and resource type. Use to find failed API calls, slow resources, or mixed content.",
            inputSchema={"type": "object", "properties": {}}
        ),
        # Performance
        types.Tool(
            name="ghost_performance",
            description="Extract Core Web Vitals: DOM Content Loaded, Full Load, First Contentful Paint, DOM Interactive, resource count, total transfer size.",
            inputSchema={"type": "object", "properties": {}}
        ),
        # Cookies
        types.Tool(
            name="ghost_cookies",
            description="Get all cookies set by the current page.",
            inputSchema={"type": "object", "properties": {}}
        ),
        # Wait For
        types.Tool(
            name="ghost_wait_for",
            description="Wait for a CSS selector to appear on page. Useful after clicking to wait for modals, dropdowns, or lazy content.",
            inputSchema={
                "type": "object",
                "properties": {
                    "selector": {"type": "string", "description": "CSS selector to wait for."},
                    "timeout_ms": {"type": "integer", "description": "Max wait time in milliseconds (default 5000)."}
                },
                "required": ["selector"]
            }
        ),
        # Extract Links
        types.Tool(
            name="ghost_extract_links",
            description="Extract all anchor links from the current page. Returns text and href for each link. Essential for crawling and sitemap discovery.",
            inputSchema={"type": "object", "properties": {}}
        ),
        # Video Status
        types.Tool(
            name="ghost_video_status",
            description="Get the file path of the currently recording .webm video snippet.",
            inputSchema={"type": "object", "properties": {}}
        ),
        # Vision System (Keyframes)
        types.Tool(
            name="ghost_vision_start",
            description="Start high-precision background frame capture (Vision Mode). Enables AI to see animations and loading states frame-by-frame.",
            inputSchema={
                "type": "object",
                "properties": {
                    "fps": {"type": "number", "description": "Frames per second (0.5 to 10.0). Default 2.0."}
                }
            }
        ),
        types.Tool(
            name="ghost_vision_stop",
            description="Stop the background frame capture.",
            inputSchema={"type": "object", "properties": {}}
        ),
        types.Tool(
            name="ghost_vision_timeline",
            description="Retrieve a sequence of the most recent keyframes captured in Vision Mode. Use this to analyze what happened between browser actions.",
            inputSchema={
                "type": "object",
                "properties": {
                    "limit": {"type": "integer", "description": "Number of recent frames to retrieve (max 50). Default 10."}
                }
            }
        ),
        # Frame Context Reader
        types.Tool(
            name="ghost_frame_context",
            description="Read the full JSON context packet for a specific cinematic frame. Use this in the analysis loop to understand exactly what is visible at each scroll position — elements, animations, errors, network.",
            inputSchema={
                "type": "object",
                "properties": {
                    "frame_index": {"type": "integer", "description": "The frame number to read context for (from cinematic_scroll results)."}
                },
                "required": ["frame_index"]
            }
        ),
        # Full Page Analysis
        types.Tool(
            name="ghost_analyze_page",
            description="Perform a full cinematic scan of the page. Scrolls top-to-bottom, captures viewport screenshots with rich JSON context at every stop. Returns a structured per-frame manifest for sequential AI analysis. Use this to audit an entire page section-by-section.",
            inputSchema={
                "type": "object",
                "properties": {
                    "url": {"type": "string", "description": "URL to navigate to and analyze."},
                    "step_px": {"type": "integer", "description": "Pixels per scroll step (default 350)."},
                    "pause_ms": {"type": "integer", "description": "Pause at each stop in ms (default 800)."}
                },
                "required": ["url"]
            }
        ),
        # ─── MULTI-TAB & COMPARISON ─────────────────────
        types.Tool(
            name="ghost_tab_open",
            description="Open a new named browser tab and navigate to a URL. Use named tabs to work with multiple pages at once.",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "A short name for this tab (e.g. 'competitor', 'my_site')."},
                    "url": {"type": "string", "description": "The URL to open."}
                },
                "required": ["name", "url"]
            }
        ),
        types.Tool(
            name="ghost_tab_switch",
            description="Switch to a different named tab. All subsequent tools will operate on this tab.",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "Name of the tab to switch to."}
                },
                "required": ["name"]
            }
        ),
        types.Tool(
            name="ghost_tab_close",
            description="Close a named tab.",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "Name of the tab to close."}
                },
                "required": ["name"]
            }
        ),
        types.Tool(
            name="ghost_tab_list",
            description="List all open tabs with their names, URLs, and which one is active.",
            inputSchema={"type": "object", "properties": {}}
        ),
        types.Tool(
            name="ghost_compare",
            description="Open two websites side-by-side in separate tabs, audit both (performance, content structure, tech stack, SEO, errors), and generate a structured diff report. This is the ultimate competitor analysis tool.",
            inputSchema={
                "type": "object",
                "properties": {
                    "url_a": {"type": "string", "description": "First site URL (e.g. your site)."},
                    "url_b": {"type": "string", "description": "Second site URL (e.g. competitor)."}
                },
                "required": ["url_a", "url_b"]
            }
        ),
    ]


# ─── TOOL DISPATCHER ─────────────────────────────────────────────

@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[types.TextContent]:
    await browser_manager.initialize()

    if name == "ghost_goto":
        result = await browser_manager.navigate(arguments["url"])
        return [types.TextContent(type="text", text=result)]

    elif name == "ghost_map_dom":
        result = await browser_manager.map_dom()
        if result["status"] == "error":
            return [types.TextContent(type="text", text=result["message"])]

        elements = result["data"]
        lines = []
        for el in elements:
            label = "🌀" if el["type"] == "animated" else ("⚡" if el["type"] == "interactive" else "📦")
            line = f"{label} [{el['id']}] {el['tagName']} '{el['text']}' @ ({el['x']},{el['y']}) {el['width']}x{el['height']}"
            if el["styles"].get("animation", "none") != "none":
                line += f" anim:{el['styles']['animation']}"
            lines.append(line)

        header = (
            f"DOM Map Complete | {result['element_count']} nodes | {result['animated_count']} animated\n"
            f"Screenshot: {result['screenshot_path']}\n"
            f"Console Errors: {len(result['console_errors'])}\n"
        )
        if result["console_errors"]:
            header += "\n".join(result["console_errors"][:10]) + "\n"
        header += "\n" + "\n".join(lines)
        return [types.TextContent(type="text", text=header)]

    elif name == "ghost_interact":
        result = await browser_manager.perform_action(
            arguments["ghost_id"], arguments["action"], arguments.get("input_text")
        )
        video_path = await browser_manager.get_video_path()
        return [types.TextContent(type="text", text=f"{result['message']}\nVideo: {video_path}")]

    elif name == "ghost_scroll":
        result = await browser_manager.scroll_page(
            arguments["direction"], arguments.get("pixels", 500), arguments.get("smooth", True)
        )
        return [types.TextContent(type="text", text=result)]

    elif name == "ghost_cinematic_scroll":
        result = await browser_manager.cinematic_scroll(
            arguments.get("step_px", 300), arguments.get("pause_ms", 800)
        )
        if result["status"] == "error":
            return [types.TextContent(type="text", text=result["message"])]
        # Build a per-frame summary for the AI
        lines = [f"{result['message']}\nPage Height: {result['page_height']}px\n"]
        lines.append("FRAME MANIFEST (use ghost_frame_context to read full context for any frame):")
        for f in result["frames"]:
            s = f["summary"]
            lines.append(f"  Frame {s['frame']} | {s['scroll_percent']}% | {s['elements']} elements | {s['animations']} anims | {s['errors']} errors | img: {f['image']}")
        return [types.TextContent(type="text", text="\n".join(lines))]

    elif name == "ghost_drag":
        result = await browser_manager.drag_to(arguments["source_id"], arguments["target_id"])
        return [types.TextContent(type="text", text=result)]

    elif name == "ghost_viewport":
        result = await browser_manager.set_viewport(arguments["width"], arguments["height"])
        return [types.TextContent(type="text", text=result)]

    elif name == "ghost_screenshot":
        path = await browser_manager.take_screenshot(
            arguments["name"], arguments.get("full_page", True)
        )
        return [types.TextContent(type="text", text=f"Screenshot saved: {path}")]

    elif name == "ghost_execute_js":
        result = await browser_manager.execute_js(arguments["script"])
        return [types.TextContent(type="text", text=f"JS Result:\n{result}")]

    elif name == "ghost_drain_mutations":
        mutations = await browser_manager.drain_mutations()
        if not mutations:
            return [types.TextContent(type="text", text="No DOM mutations detected since last check.")]
        lines = [f"[{m['type']}] {m['target']} @ {m['time']}" for m in mutations[:30]]
        return [types.TextContent(type="text", text=f"{len(mutations)} mutations captured:\n" + "\n".join(lines))]

    elif name == "ghost_network_log":
        log = await browser_manager.get_network_log()
        if not log:
            return [types.TextContent(type="text", text="No network requests logged.")]
        lines = []
        failed = 0
        for r in log:
            status = r.get("status", "?")
            if status == "FAILED":
                failed += 1
            lines.append(f"[{status}] {r['method']} {r['type']} {r['url']}")
        header = f"{len(log)} requests | {failed} failed\n"
        return [types.TextContent(type="text", text=header + "\n".join(lines[:40]))]

    elif name == "ghost_performance":
        result = await browser_manager.get_performance_metrics()
        if result["status"] == "error":
            return [types.TextContent(type="text", text=result["message"])]
        m = result["metrics"]
        text = (
            f"⚡ Core Web Vitals:\n"
            f"  DOM Content Loaded: {m.get('domContentLoaded', '?')}ms\n"
            f"  Full Page Load:     {m.get('fullLoad', '?')}ms\n"
            f"  First Contentful Paint: {m.get('firstContentfulPaint', '?')}ms\n"
            f"  DOM Interactive:    {m.get('domInteractive', '?')}ms\n"
            f"  Resources Loaded:   {m.get('resourceCount', '?')}\n"
            f"  Total Transfer:     {round(m.get('totalTransferSize', 0) / 1024, 1)}KB"
        )
        return [types.TextContent(type="text", text=text)]

    elif name == "ghost_cookies":
        result = await browser_manager.get_cookies()
        return [types.TextContent(type="text", text=json.dumps(result, indent=2))]

    elif name == "ghost_wait_for":
        result = await browser_manager.wait_for(
            arguments["selector"], arguments.get("timeout_ms", 5000)
        )
        return [types.TextContent(type="text", text=result)]

    elif name == "ghost_extract_links":
        links = await browser_manager.extract_links()
        if not links:
            return [types.TextContent(type="text", text="No links found on page.")]
        lines = [f"  [{l['text']}]({l['href']})" for l in links[:50]]
        return [types.TextContent(type="text", text=f"{len(links)} links found:\n" + "\n".join(lines))]

    elif name == "ghost_video_status":
        path = await browser_manager.get_video_path()
        return [types.TextContent(type="text", text=f"Active Video: {path}")]

    elif name == "ghost_vision_start":
        result = await browser_manager.start_vision(arguments.get("fps", 2.0))
        return [types.TextContent(type="text", text=result)]

    elif name == "ghost_vision_stop":
        result = await browser_manager.stop_vision()
        return [types.TextContent(type="text", text=result)]

    elif name == \"ghost_vision_timeline\":
        frames = await browser_manager.get_vision_timeline(arguments.get("limit", 10))
        if not frames:
            return [types.TextContent(type="text", text="No vision frames captured. Did you start_vision?")]
        text = f"Captured {len(frames)} frames:\n" + "\n".join([f"  - {f}" for f in frames])
        return [types.TextContent(type="text", text=text)]

    elif name == "ghost_frame_context":
        frame_idx = arguments["frame_index"]
        json_path = os.path.join(browser_manager.screenshots_dir, f"cinematic_{frame_idx}.json")
        if not os.path.exists(json_path):
            return [types.TextContent(type="text", text=f"No context found for frame {frame_idx}. Run ghost_cinematic_scroll or ghost_analyze_page first.")]
        with open(json_path, "r", encoding="utf-8") as f:
            context = json.load(f)
        # Format the context for the AI to read as structured text
        img_path = os.path.join(browser_manager.screenshots_dir, f"cinematic_{frame_idx}.png")
        lines = [
            f"=== FRAME {frame_idx} CONTEXT ===",
            f"Scroll: {context['scroll_y']}px / {context['page_height']}px ({context['scroll_percent']}%)",
            f"Screenshot: {img_path}",
            f"Visible Elements: {context['visible_element_count']}",
        ]
        for el in context.get("visible_elements", []):
            txt = el.get("text", "")[:50]
            tag = el.get("tag", "?")
            bounds = el.get("bounds", {})
            line = f"  [{tag}] \"{txt}\" @ ({bounds.get('x',0)},{bounds.get('y',0)}) {bounds.get('w',0)}x{bounds.get('h',0)}"
            if el.get("href"):
                line += f" -> {el['href'][:60]}"
            lines.append(line)
        if context.get("active_animations"):
            lines.append(f"\nActive Animations: {len(context['active_animations'])}")
            for a in context["active_animations"]:
                lines.append(f"  🌀 {a['name']} on {a['target']} ({a['state']})")
        if context.get("console_errors"):
            lines.append(f"\nConsole Errors ({context['console_error_count']} total):")
            for err in context["console_errors"]:
                lines.append(f"  ❌ {err}")
        return [types.TextContent(type="text", text="\n".join(lines))]

    elif name == "ghost_analyze_page":
        url = arguments["url"]
        step = arguments.get("step_px", 350)
        pause = arguments.get("pause_ms", 800)

        # Navigate first
        nav_result = await browser_manager.navigate(url)

        # Run cinematic scroll with context capture
        result = await browser_manager.cinematic_scroll(step_px=step, pause_ms=pause)
        if result["status"] == "error":
            return [types.TextContent(type="text", text=f"Analysis failed: {result['message']}")]

        # Get performance metrics
        perf = await browser_manager.get_performance_metrics()

        # Build the analysis manifest
        lines = [
            f"🔍 PAGE ANALYSIS: {url}",
            f"{nav_result}",
            f"",
            f"{result['message']}",
            f"Page Height: {result['page_height']}px",
            f"",
        ]

        # Performance summary
        if perf.get("status") == "success":
            m = perf["metrics"]
            lines.append("⚡ PERFORMANCE:")
            lines.append(f"  FCP: {m.get('firstContentfulPaint', '?')}ms | Load: {m.get('fullLoad', '?')}ms | Resources: {m.get('resourceCount', '?')}")
            lines.append("")

        # Frame manifest
        lines.append("📋 FRAME-BY-FRAME MANIFEST:")
        lines.append("(Process each frame sequentially. Use ghost_frame_context(N) to read the full context for frame N.)")
        lines.append("")
        for f in result["frames"]:
            s = f["summary"]
            flag = "🔴" if s["errors"] > 0 else ("🌀" if s["animations"] > 0 else "✅")
            lines.append(f"  {flag} Frame {s['frame']:>2d} | {s['scroll_percent']:>5.1f}% | {s['elements']:>2d} elements | {s['animations']} anims | {s['errors']} errors")
        lines.append("")
        lines.append("💡 ANALYSIS PROTOCOL:")
        lines.append("  1. Start with Frame 0 → call ghost_frame_context(0)")
        lines.append("  2. Study the visible elements, check for issues")
        lines.append("  3. Move to Frame 1 → call ghost_frame_context(1)")
        lines.append("  4. Compare with previous frame. Note what changed.")
        lines.append("  5. Continue until the last frame.")
        lines.append("  6. Compile your findings into a final report.")

        return [types.TextContent(type="text", text="\n".join(lines))]

    # ─── MULTI-TAB & COMPARISON DISPATCHERS ─────────────────────

    elif name == "ghost_tab_open":
        result = await browser_manager.open_tab(arguments["name"], arguments["url"])
        return [types.TextContent(type="text", text=result)]

    elif name == "ghost_tab_switch":
        result = await browser_manager.switch_tab(arguments["name"])
        return [types.TextContent(type="text", text=result)]

    elif name == "ghost_tab_close":
        result = await browser_manager.close_tab(arguments["name"])
        return [types.TextContent(type="text", text=result)]

    elif name == "ghost_tab_list":
        tabs = browser_manager.list_tabs()
        if not tabs:
            return [types.TextContent(type="text", text="No tabs open.")]
        lines = ["Open Tabs:"]
        for t in tabs:
            marker = "→" if t["active"] else " "
            lines.append(f"  {marker} [{t['name']}] {t['url']} — \"{t['title']}\"")
        return [types.TextContent(type="text", text="\n".join(lines))]

    elif name == "ghost_compare":
        result = await browser_manager.compare_sites(arguments["url_a"], arguments["url_b"])
        if result["status"] == "error":
            return [types.TextContent(type="text", text=f"Comparison failed: {result['message']}")]

        a = result["comparisons"]["site_a"]
        b = result["comparisons"]["site_b"]
        diff = result["diff"]

        lines = [
            "═" * 60,
            "🔍 SITE COMPARISON REPORT",
            "═" * 60,
            f"",
            f"  SITE A: {a['url']}",
            f"  Title:  {a['title']}",
            f"  Tech:   {', '.join(a['tech']['frameworks']) or 'None detected'}",
            f"  ©:      {a['tech'].get('copyright_year', '?')}",
            f"",
            f"  SITE B: {b['url']}",
            f"  Title:  {b['title']}",
            f"  Tech:   {', '.join(b['tech']['frameworks']) or 'None detected'}",
            f"  ©:      {b['tech'].get('copyright_year', '?')}",
            f"",
            "─" * 60,
            "⚡ PERFORMANCE HEAD-TO-HEAD:",
            f"{'Metric':<25} {'Site A':>10} {'Site B':>10} {'Winner':>8}",
            "─" * 60,
        ]
        for d in diff:
            m = d["metric"]
            va = str(d.get("site_a", "?"))
            vb = str(d.get("site_b", "?"))
            w = d.get("winner", "")
            lines.append(f"  {m:<23} {va:>10} {vb:>10} {w:>8}")

        lines.append("")
        lines.append("─" * 60)
        lines.append("📊 CONTENT STRUCTURE:")
        lines.append(f"  Page Height:   A={a['structure'].get('page_height', '?')}px  |  B={b['structure'].get('page_height', '?')}px")
        lines.append(f"  Headings (H1-3): A={len(a['structure'].get('headings', []))}  |  B={len(b['structure'].get('headings', []))}")
        lines.append("")
        lines.append("  Site A Headings:")
        for h in a["structure"].get("headings", [])[:8]:
            lines.append(f"    [{h['tag']}] {h['text']}")
        lines.append("  Site B Headings:")
        for h in b["structure"].get("headings", [])[:8]:
            lines.append(f"    [{h['tag']}] {h['text']}")

        lines.append("")
        lines.append("─" * 60)
        lines.append("🛡️ SEO & HEALTH:")
        lines.append(f"  Meta Desc:  A={'✅' if a['structure'].get('has_meta_description') else '❌'}  |  B={'✅' if b['structure'].get('has_meta_description') else '❌'}")
        lines.append(f"  OG Image:   A={'✅' if a['structure'].get('has_og_image') else '❌'}  |  B={'✅' if b['structure'].get('has_og_image') else '❌'}")
        lines.append(f"  JS Errors:  A={a['console_errors']}  |  B={b['console_errors']}")
        lines.append(f"  Failed Req: A={a['failed_requests']}  |  B={b['failed_requests']}")

        lines.append("")
        lines.append("─" * 60)
        lines.append("📸 HERO SCREENSHOTS:")
        lines.append(f"  Site A: {a['hero_screenshot']}")
        lines.append(f"  Site B: {b['hero_screenshot']}")
        lines.append("═" * 60)

        return [types.TextContent(type="text", text="\n".join(lines))]

    raise ValueError(f"Unknown tool: {name}")


# ─── PROMPTS (SKILLS) ────────────────────────────────────────────

def _load_skills() -> dict[str, dict]:
    """Load all .md files from the skills/ directory as MCP Prompts."""
    skills = {}
    if not os.path.isdir(SKILLS_DIR):
        return skills
    for filepath in glob.glob(os.path.join(SKILLS_DIR, "*.md")):
        name = os.path.splitext(os.path.basename(filepath))[0]
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
        # Extract the first line as the title
        first_line = content.split("\n")[0].strip().lstrip("#").strip()
        skills[name] = {"title": first_line, "content": content, "path": filepath}
    return skills


@app.list_prompts()
async def list_prompts() -> list[types.Prompt]:
    skills = _load_skills()
    prompts = []
    for name, data in skills.items():
        prompts.append(types.Prompt(
            name=name,
            description=data["title"],
            arguments=[
                types.PromptArgument(
                    name="url",
                    description="Target URL to audit (optional).",
                    required=False
                )
            ]
        ))
    return prompts


@app.get_prompt()
async def get_prompt(name: str, arguments: dict | None) -> types.GetPromptResult:
    skills = _load_skills()
    if name not in skills:
        raise ValueError(f"Unknown skill: {name}. Available: {', '.join(skills.keys())}")

    content = skills[name]["content"]
    url = (arguments or {}).get("url", "")
    if url:
        content += f"\n\n**Target URL for this session:** `{url}`"

    return types.GetPromptResult(
        description=skills[name]["title"],
        messages=[
            types.PromptMessage(
                role="user",
                content=types.TextContent(type="text", text=content)
            )
        ]
    )


# ─── MAIN ─────────────────────────────────────────────────────────

async def main():
    async with stdio_server() as (read_stream, write_stream):
        await app.run(read_stream, write_stream, app.create_initialization_options())

if __name__ == "__main__":
    asyncio.run(main())
