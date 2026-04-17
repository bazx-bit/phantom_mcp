import asyncio
import json
import os
import time
from typing import Dict, Any, Optional, List
from playwright.async_api import async_playwright, Page, BrowserContext, Browser


class GhostBrowserManager:
    """
    The core Playwright daemon for Site-Ghost.
    Manages a persistent headless Chromium session with:
    - Native video recording of every interaction
    - Console error/warning trapping
    - Precision DOM injection (dom_mapper.js)
    - Advanced interactions: scroll, hover, drag, select, wait, execute JS
    - Network request interception and logging
    - Performance metrics extraction
    """

    def __init__(self):
        self.playwright = None
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None
        self.console_logs: List[str] = []
        self.network_log: List[Dict] = []
        self.screenshots_dir = os.path.join(os.getcwd(), '.ghost', 'screenshots')
        self.recordings_dir = os.path.join(os.getcwd(), '.ghost', 'video_feeds')
        self.vision_dir = os.path.join(os.getcwd(), '.ghost', 'vision')
        os.makedirs(self.recordings_dir, exist_ok=True)
        os.makedirs(self.screenshots_dir, exist_ok=True)
        os.makedirs(self.vision_dir, exist_ok=True)

        # Vision State
        self.vision_active = False
        self.vision_task: Optional[asyncio.Task] = None
        self.vision_fps = 2.0
        self.vision_frames: List[str] = []
        self.max_vision_frames = 50

    # ─── LIFECYCLE ────────────────────────────────────────────────

    async def initialize(self):
        """Start the persistent Playwright daemon with video recording enabled."""
        if self.playwright:
            return  # Already running
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(
            headless=True,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--disable-web-security",
                "--no-sandbox"
            ]
        )
        self.context = await self.browser.new_context(
            record_video_dir=self.recordings_dir,
            record_video_size={"width": 1280, "height": 720},
            viewport={"width": 1280, "height": 720},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        self.page = await self.context.new_page()

        # Listen to console messages for AI Health Auditing
        self.page.on("console", self._handle_console_message)
        # Listen to network requests for performance auditing
        self.page.on("requestfinished", self._handle_network_request)
        self.page.on("requestfailed", self._handle_network_failure)

    def _handle_console_message(self, msg):
        if msg.type in ("error", "warning"):
            self.console_logs.append(f"[{msg.type.upper()}] {msg.text}")

    def _handle_network_request(self, request):
        self.network_log.append({
            "url": request.url[:120],
            "method": request.method,
            "status": "OK",
            "type": request.resource_type,
        })

    def _handle_network_failure(self, request):
        self.network_log.append({
            "url": request.url[:120],
            "method": request.method,
            "status": "FAILED",
            "type": request.resource_type,
        })

    async def close(self):
        """Shuts down the daemon gracefully and cleans up session data."""
        # Stop vision first
        await self.stop_vision()

        if self.context:
            await self.context.close()
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()
        self.playwright = None

        # Session Cleanup: Remove vision frames to save space
        try:
            for f in os.listdir(self.vision_dir):
                os.remove(os.path.join(self.vision_dir, f))
        except Exception:
            pass

    # ─── NAVIGATION ───────────────────────────────────────────────

    async def navigate(self, url: str) -> str:
        """Navigate to a URL and wait for the network to stop changing."""
        try:
            self.console_logs.clear()
            self.network_log.clear()
            await self.page.goto(url, wait_until="networkidle", timeout=20000)
            title = await self.page.title()
            return f"Navigated to {url} | Page Title: '{title}'"
        except Exception as e:
            return f"Navigation error: {str(e)}"

    # ─── DOM MAPPING ──────────────────────────────────────────────

    async def map_dom(self) -> Dict[str, Any]:
        """Injects dom_mapper.js to calculate exact precision tracking on all elements."""
        try:
            script_path = os.path.join(os.path.dirname(__file__), "dom_mapper.js")
            with open(script_path, "r") as f:
                mapper_script = f.read()

            result = await self.page.evaluate(mapper_script)
            elements = result.get("elements", [])
            animated_count = result.get("animatedCount", 0)

            screenshot_path = os.path.join(self.screenshots_dir, 'latest_snapshot.png')
            await self.page.screenshot(path=screenshot_path, full_page=False)

            return {
                "status": "success",
                "element_count": len(elements),
                "animated_count": animated_count,
                "data": elements,
                "screenshot_path": screenshot_path,
                "console_errors": self.console_logs.copy()
            }
        except Exception as e:
            return {"status": "error", "message": f"DOM Extraction failed: {str(e)}"}

    # ─── INTERACTIONS ─────────────────────────────────────────────

    async def perform_action(self, ghost_id: str, action: str, input_text: Optional[str] = None) -> Dict[str, str]:
        """
        Executes a targeted browser action on a specifically mapped ghost_id.
        Supports: click, type, hover, select, focus, check, uncheck
        """
        try:
            selector = f'[data-ghost-id="{ghost_id}"]'
            locator = self.page.locator(selector)

            if await locator.count() == 0:
                return {"status": "error", "message": f"Element {ghost_id} not found on page."}

            await asyncio.sleep(0.5)  # Pre-action video buffer

            if action == "click":
                await locator.click(timeout=5000)
                await asyncio.sleep(1.5)
                return {"status": "success", "message": f"Clicked {ghost_id}."}

            elif action == "type" and input_text:
                await locator.fill(input_text, timeout=5000)
                await asyncio.sleep(1)
                return {"status": "success", "message": f"Typed into {ghost_id}."}

            elif action == "hover":
                await locator.hover(timeout=5000)
                await asyncio.sleep(1.5)
                return {"status": "success", "message": f"Hovered over {ghost_id}. Check for dropdowns/tooltips."}

            elif action == "select" and input_text:
                await locator.select_option(input_text, timeout=5000)
                await asyncio.sleep(1)
                return {"status": "success", "message": f"Selected option '{input_text}' in {ghost_id}."}

            elif action == "focus":
                await locator.focus(timeout=5000)
                await asyncio.sleep(0.5)
                return {"status": "success", "message": f"Focused {ghost_id}."}

            elif action == "check":
                await locator.check(timeout=5000)
                return {"status": "success", "message": f"Checked {ghost_id}."}

            elif action == "uncheck":
                await locator.uncheck(timeout=5000)
                return {"status": "success", "message": f"Unchecked {ghost_id}."}

            return {"status": "error", "message": f"Unknown action: {action}"}

        except Exception as e:
            return {"status": "error", "message": f"Action '{action}' on {ghost_id} failed: {str(e)}"}

    # ─── SCROLLING (SMOOTH ANIMATION) ──────────────────────────────

    async def scroll_page(self, direction: str = "down", pixels: int = 500, smooth: bool = True) -> str:
        """Scroll the page with real smooth animation so the video captures motion."""
        try:
            if smooth:
                # Use CSS smooth scroll behavior for natural-looking motion
                if direction == "down":
                    await self.page.evaluate(f"window.scrollBy({{top: {pixels}, behavior: 'smooth'}})")
                elif direction == "up":
                    await self.page.evaluate(f"window.scrollBy({{top: -{pixels}, behavior: 'smooth'}})")
                elif direction == "bottom":
                    await self.page.evaluate("window.scrollTo({top: document.body.scrollHeight, behavior: 'smooth'})")
                elif direction == "top":
                    await self.page.evaluate("window.scrollTo({top: 0, behavior: 'smooth'})")
                else:
                    return f"Unknown direction: {direction}. Use 'up', 'down', 'top', 'bottom'."
                # Wait for smooth scroll animation to finish + lazy content
                await asyncio.sleep(1.5)
            else:
                # Instant jump (legacy)
                if direction == "down":
                    await self.page.evaluate(f"window.scrollBy(0, {pixels})")
                elif direction == "up":
                    await self.page.evaluate(f"window.scrollBy(0, -{pixels})")
                elif direction == "bottom":
                    await self.page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                elif direction == "top":
                    await self.page.evaluate("window.scrollTo(0, 0)")
                else:
                    return f"Unknown direction: {direction}."
                await asyncio.sleep(0.5)

            scroll_y = await self.page.evaluate("window.scrollY")
            page_height = await self.page.evaluate("document.body.scrollHeight")
            return f"Scrolled {direction} by {pixels}px. Position: {scroll_y}/{page_height}px."
        except Exception as e:
            return f"Scroll failed: {str(e)}"

    async def cinematic_scroll(self, step_px: int = 300, pause_ms: int = 800) -> Dict[str, Any]:
        """
        Performs a slow, cinematic top-to-bottom scroll of the entire page.
        Takes a viewport screenshot at every stop. The video recorder captures
        the entire journey as a smooth animation.
        Returns paths to all captured viewport screenshots.
        """
        try:
            # Go to top first
            await self.page.evaluate("window.scrollTo({top: 0, behavior: 'smooth'})")
            await asyncio.sleep(1)

            page_height = await self.page.evaluate("document.body.scrollHeight")
            viewport_h = await self.page.evaluate("window.innerHeight")
            current = 0
            frame_idx = 0
            snapshots = []

            while current < page_height - viewport_h:
                # Smooth scroll one step
                await self.page.evaluate(f"window.scrollBy({{top: {step_px}, behavior: 'smooth'}})")
                await asyncio.sleep(pause_ms / 1000.0)

                # Take a VIEWPORT screenshot (what a real user sees)
                path = os.path.join(self.screenshots_dir, f"cinematic_{frame_idx}.png")
                await self.page.screenshot(path=path, full_page=False)
                snapshots.append(path)

                current += step_px
                frame_idx += 1

            return {
                "status": "success",
                "frames": len(snapshots),
                "snapshots": snapshots,
                "page_height": page_height,
                "message": f"Cinematic scroll complete. {len(snapshots)} viewport snapshots captured."
            }
        except Exception as e:
            return {"status": "error", "message": f"Cinematic scroll failed: {str(e)}"}

    # ─── DRAG AND DROP ────────────────────────────────────────────

    async def drag_to(self, source_id: str, target_id: str) -> str:
        """Drag one ghost element onto another."""
        try:
            source = self.page.locator(f'[data-ghost-id="{source_id}"]')
            target = self.page.locator(f'[data-ghost-id="{target_id}"]')
            if await source.count() == 0:
                return f"Source {source_id} not found."
            if await target.count() == 0:
                return f"Target {target_id} not found."
            await source.drag_to(target, timeout=5000)
            await asyncio.sleep(1.5)
            return f"Dragged {source_id} onto {target_id}."
        except Exception as e:
            return f"Drag failed: {str(e)}"

    # ─── VIEWPORT CONTROL ────────────────────────────────────────

    async def set_viewport(self, width: int, height: int) -> str:
        """Change the browser viewport dimensions (for responsive testing)."""
        try:
            await self.page.set_viewport_size({"width": width, "height": height})
            await asyncio.sleep(0.5)
            return f"Viewport changed to {width}x{height}."
        except Exception as e:
            return f"Viewport change failed: {str(e)}"

    # ─── SCREENSHOT ───────────────────────────────────────────────

    async def take_screenshot(self, name: str = "capture", full_page: bool = False) -> str:
        """
        Take a named screenshot and return the path.
        Defaults to VIEWPORT-only (what a real user sees).
        Set full_page=True only for sitemap-style captures.
        """
        try:
            path = os.path.join(self.screenshots_dir, f"{name}.png")
            await self.page.screenshot(path=path, full_page=full_page)
            return path
        except Exception as e:
            return f"Screenshot failed: {str(e)}"

    # ─── LIVE JS INJECTION ────────────────────────────────────────

    async def execute_js(self, script: str) -> str:
        """Execute arbitrary JavaScript on the page and return the result."""
        try:
            result = await self.page.evaluate(script)
            return json.dumps(result, indent=2, default=str) if result else "(no return value)"
        except Exception as e:
            return f"JS execution error: {str(e)}"

    # ─── MUTATION OBSERVER DRAIN ──────────────────────────────────

    async def drain_mutations(self) -> List[Dict]:
        """Pull all DOM mutations captured by the injected MutationObserver."""
        try:
            mutations = await self.page.evaluate("window.__ghost_mutations || []")
            # Clear after draining
            await self.page.evaluate("window.__ghost_mutations = []")
            return mutations
        except Exception:
            return []

    # ─── NETWORK LOG ──────────────────────────────────────────────

    async def get_network_log(self) -> List[Dict]:
        """Return all network requests captured since last navigation."""
        return self.network_log.copy()

    # ─── PERFORMANCE METRICS ──────────────────────────────────────

    async def get_performance_metrics(self) -> Dict[str, Any]:
        """Extract Core Web Vitals and timing metrics from the page."""
        try:
            metrics = await self.page.evaluate("""
                () => {
                    const perf = performance.getEntriesByType('navigation')[0] || {};
                    const paint = performance.getEntriesByType('paint');
                    const fcp = paint.find(p => p.name === 'first-contentful-paint');
                    return {
                        domContentLoaded: Math.round(perf.domContentLoadedEventEnd - perf.startTime),
                        fullLoad: Math.round(perf.loadEventEnd - perf.startTime),
                        firstContentfulPaint: fcp ? Math.round(fcp.startTime) : null,
                        domInteractive: Math.round(perf.domInteractive - perf.startTime),
                        resourceCount: performance.getEntriesByType('resource').length,
                        totalTransferSize: performance.getEntriesByType('resource').reduce((sum, r) => sum + (r.transferSize || 0), 0),
                    };
                }
            """)
            return {"status": "success", "metrics": metrics}
        except Exception as e:
            return {"status": "error", "message": f"Perf extraction failed: {str(e)}"}

    # ─── COOKIE MANAGEMENT ────────────────────────────────────────

    async def get_cookies(self) -> List[Dict]:
        """Get all cookies for the current page."""
        try:
            return await self.context.cookies()
        except Exception:
            return []

    # ─── VISION SYSTEM (LIVE AI FEED) ─────────────────────────────

    async def start_vision(self, fps: float = 2.0) -> str:
        """Start the background high-precision frame capture."""
        if self.vision_active:
            self.vision_fps = fps # Update FPS if already running
            return f"Vision already active. Updated FPS to {fps}."
        
        self.vision_active = True
        self.vision_fps = max(0.5, min(fps, 10.0)) # Cap at 0.5-10 FPS
        self.vision_task = asyncio.create_task(self._vision_loop())
        return f"Vision started at {self.vision_fps} FPS."

    async def stop_vision(self) -> str:
        """Stop the background frame capture."""
        if not self.vision_active:
            return "Vision is not active."
        
        self.vision_active = False
        if self.vision_task:
            self.vision_task.cancel()
            try:
                await self.vision_task
            except asyncio.CancelledError:
                pass
        return "Vision stopped."

    async def _vision_loop(self):
        """Background loop to capture screenshots for AI timeline."""
        frame_idx = 0
        while self.vision_active:
            try:
                if self.page and not self.page.is_closed():
                    timestamp = int(time.time() * 1000)
                    filename = f"frame_{timestamp}_{frame_idx}.jpg"
                    path = os.path.join(self.vision_dir, filename)
                    
                    # Take a low-quality JPEG for "compression/compaction"
                    await self.page.screenshot(path=path, type="jpeg", quality=60)
                    
                    self.vision_frames.append(path)
                    
                    # Manage sliding window (buffer limit)
                    if len(self.vision_frames) > self.max_vision_frames:
                        old_frame = self.vision_frames.pop(0)
                        if os.path.exists(old_frame):
                            os.remove(old_frame)
                    
                    frame_idx += 1
            except Exception:
                pass
            
            await asyncio.sleep(1.0 / self.vision_fps)

    async def get_vision_timeline(self, limit: int = 10) -> List[str]:
        """Get the paths to the most recent N frames."""
        return self.vision_frames[-limit:]

    # ─── WAIT FOR SELECTOR ────────────────────────────────────────

    async def wait_for(self, css_selector: str, timeout_ms: int = 5000) -> str:
        """Wait for a CSS selector to appear on the page."""
        try:
            await self.page.wait_for_selector(css_selector, timeout=timeout_ms)
            return f"Selector '{css_selector}' appeared."
        except Exception as e:
            return f"Wait failed: {str(e)}"

    # ─── EXTRACT ALL LINKS ───────────────────────────────────────

    async def extract_links(self) -> List[Dict[str, str]]:
        """Extract all href links from the current page."""
        try:
            links = await self.page.evaluate("""
                () => Array.from(document.querySelectorAll('a[href]')).map(a => ({
                    text: a.innerText.trim().substring(0, 60),
                    href: a.href
                }))
            """)
            return links
        except Exception:
            return []

    # ─── VIDEO PATH ───────────────────────────────────────────────

    async def get_video_path(self) -> str:
        """Returns the current path to the ongoing video slice for this page."""
        if self.page:
            try:
                path = await self.page.video.path()
                return path
            except Exception:
                return "Video not active/available."
        return "No page active."
