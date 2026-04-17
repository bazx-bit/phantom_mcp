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
            description="Scroll the page. Directions: 'up', 'down', 'top', 'bottom'. Specify pixels for up/down.",
            inputSchema={
                "type": "object",
                "properties": {
                    "direction": {"type": "string", "enum": ["up", "down", "top", "bottom"]},
                    "pixels": {"type": "integer", "description": "Pixels to scroll (default 500)."}
                },
                "required": ["direction"]
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
            arguments["direction"], arguments.get("pixels", 500)
        )
        return [types.TextContent(type="text", text=result)]

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

    elif name == "ghost_vision_timeline":
        frames = await browser_manager.get_vision_timeline(arguments.get("limit", 10))
        if not frames:
            return [types.TextContent(type="text", text="No vision frames captured. Did you start_vision?")]
        text = f"Captured {len(frames)} frames:\n" + "\n".join([f"  - {f}" for f in frames])
        return [types.TextContent(type="text", text=text)]

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
