import asyncio
import json
import os
import time
from typing import Dict, Any, Optional, List
from datetime import datetime
from playwright.async_api import async_playwright, Page, BrowserContext, Browser
try:
    from .ghost_reporter import GhostReporter
    from .ghost_deconstructor import GhostDeconstructor
except (ImportError, ValueError):
    from ghost_reporter import GhostReporter
    from ghost_deconstructor import GhostDeconstructor


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
        self.reports_dir = os.path.join(os.getcwd(), '.ghost', 'reports')
        self.clones_dir = os.path.join(os.getcwd(), '.ghost', 'clones')

        # Ensure the full phantom architecture exists
        for d in [self.screenshots_dir, self.recordings_dir, self.vision_dir, self.reports_dir, self.clones_dir]:
            os.makedirs(d, exist_ok=True)

        # Vision State
        self.vision_active = False
        self.vision_task: Optional[asyncio.Task] = None
        self.vision_fps = 2.0
        self.vision_frames: List[str] = []
        self.max_vision_frames = 50

        # Multi-Tab State
        self.tabs: Dict[str, Page] = {}       # name -> Page
        self.tab_data: Dict[str, Dict] = {}   # name -> {console_logs, network_log}
        self.active_tab: Optional[str] = None

        # Reporting & Audit State
        self.reporter = GhostReporter(self.reports_dir)
        self.deconstructor = GhostDeconstructor()
        self.last_audit_data: Optional[Dict[str, Any]] = None

    # ─── LIFECYCLE ────────────────────────────────────────────────

    def _cleanup_old_files(self):
        """Wipe old screenshots and videos from previous sessions to save disk space."""
        for d in [self.screenshots_dir, self.recordings_dir, self.vision_dir]:
            if os.path.exists(d):
                for filename in os.listdir(d):
                    file_path = os.path.join(d, filename)
                    try:
                        if os.path.isfile(file_path):
                            os.unlink(file_path)
                    except Exception:
                        pass

    async def initialize(self):
        """Start the persistent Playwright daemon with video recording enabled."""
        if self.playwright:
            return  # Already running
            
        self._cleanup_old_files()
        
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


        # Close all tabs
        for name, page in self.tabs.items():
            try:
                await page.close()
            except Exception:
                pass
        self.tabs.clear()
        self.tab_data.clear()
        self.active_tab = None

        if self.context:
            await self.context.close()
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()
        self.playwright = None

        # Session Cleanup: Remove vision frames
        try:
            for f in os.listdir(self.vision_dir):
                os.remove(os.path.join(self.vision_dir, f))
        except Exception:
            pass

    # ─── TAB MANAGEMENT ────────────────────────────────────────

    async def open_tab(self, name: str, url: str) -> str:
        """Open a new named tab and navigate to a URL."""
        try:
            page = await self.context.new_page()
            # Set up listeners for this tab
            tab_logs = []
            tab_network = []
            page.on("console", lambda msg: tab_logs.append(f"[{msg.type.upper()}] {msg.text}") if msg.type in ("error", "warning") else None)
            page.on("requestfinished", lambda req: tab_network.append({"url": req.url[:120], "method": req.method, "status": "OK", "type": req.resource_type}))
            page.on("requestfailed", lambda req: tab_network.append({"url": req.url[:120], "method": req.method, "status": "FAILED", "type": req.resource_type}))

            await page.goto(url, wait_until="networkidle", timeout=25000)
            title = await page.title()

            self.tabs[name] = page
            self.tab_data[name] = {"console_logs": tab_logs, "network_log": tab_network, "url": url, "title": title}
            self.active_tab = name
            self.page = page  # Set as active page so all tools work on it
            return f"Tab '{name}' opened: {url} | Title: '{title}'"
        except Exception as e:
            return f"Tab open failed: {str(e)}"

    async def switch_tab(self, name: str) -> str:
        """Switch the active tab."""
        if name not in self.tabs:
            return f"Tab '{name}' not found. Available: {', '.join(self.tabs.keys())}"
        self.active_tab = name
        self.page = self.tabs[name]
        self.console_logs = self.tab_data[name]["console_logs"]
        self.network_log = self.tab_data[name]["network_log"]
        return f"Switched to tab '{name}' ({self.tab_data[name]['url']})"

    async def close_tab(self, name: str) -> str:
        """Close a named tab."""
        if name not in self.tabs:
            return f"Tab '{name}' not found."
        await self.tabs[name].close()
        del self.tabs[name]
        del self.tab_data[name]
        if self.active_tab == name:
            self.active_tab = next(iter(self.tabs), None)
            self.page = self.tabs.get(self.active_tab) if self.active_tab else self.page
        return f"Tab '{name}' closed."

    def list_tabs(self) -> List[Dict[str, str]]:
        """List all open tabs."""
        return [{"name": n, "url": d["url"], "title": d["title"], "active": n == self.active_tab} for n, d in self.tab_data.items()]

    # ─── SIDE-BY-SIDE COMPARISON ────────────────────────────────

    async def compare_sites(self, url_a: str, url_b: str) -> Dict[str, Any]:
        """
        Open two sites in separate tabs, audit both, and generate a
        structured comparison report with performance, content, and
        visual differences.
        """
        try:
            report = {"url_a": url_a, "url_b": url_b, "status": "success"}

            # ── Open both tabs ──
            await self.open_tab("site_a", url_a)
            await self.open_tab("site_b", url_b)

            comparisons = {}

            for label in ["site_a", "site_b"]:
                await self.switch_tab(label)
                url = self.tab_data[label]["url"]
                title = self.tab_data[label]["title"]

                # Performance
                perf = await self.get_performance_metrics()
                perf_data = perf.get("metrics", {}) if perf.get("status") == "success" else {}

                # Hero screenshot
                hero_path = os.path.join(self.screenshots_dir, f"compare_{label}_hero.png")
                await self.page.screenshot(path=hero_path, full_page=False)

                # Content structure
                structure = await self.page.evaluate("""
                    () => {
                        const headings = Array.from(document.querySelectorAll('h1,h2,h3')).map(h => ({tag: h.tagName, text: h.innerText.trim().substring(0, 80)}));
                        const links = document.querySelectorAll('a[href]').length;
                        const images = document.querySelectorAll('img').length;
                        const forms = document.querySelectorAll('form').length;
                        const buttons = document.querySelectorAll('button').length;
                        const scripts = document.querySelectorAll('script').length;
                        const meta_desc = document.querySelector('meta[name="description"]');
                        const og_image = document.querySelector('meta[property="og:image"]');
                        return {
                            headings, links, images, forms, buttons, scripts,
                            has_meta_description: !!meta_desc,
                            meta_description: meta_desc ? meta_desc.content.substring(0, 120) : null,
                            has_og_image: !!og_image,
                            page_height: document.body.scrollHeight
                        };
                    }
                """)

                # Tech stack detection
                tech = await self.page.evaluate("""
                    () => {
                        const detected = [];
                        if (window.React || document.querySelector('[data-reactroot]')) detected.push('React');
                        if (window.__NEXT_DATA__) detected.push('Next.js');
                        if (window.__NUXT__) detected.push('Nuxt');
                        if (document.querySelector('[data-v-]')) detected.push('Vue');
                        if (window.angular || document.querySelector('[ng-app]')) detected.push('Angular');
                        if (document.querySelector('script[src*="jquery"]')) detected.push('jQuery');
                        if (document.querySelector('script[src*="gtag"]') || document.querySelector('script[src*="analytics"]')) detected.push('Google Analytics');
                        if (document.querySelector('link[href*="tailwind"]') || document.querySelector('[class*="tw-"]')) detected.push('Tailwind');
                        if (document.querySelector('link[href*="bootstrap"]')) detected.push('Bootstrap');
                        const copyright = document.body.innerText.match(/©\s*(\d{4})/); 
                        return { frameworks: detected, copyright_year: copyright ? copyright[1] : null };
                    }
                """)

                errors = self.tab_data[label]["console_logs"]
                network = self.tab_data[label]["network_log"]

                comparisons[label] = {
                    "url": url,
                    "title": title,
                    "hero_screenshot": hero_path,
                    "performance": perf_data,
                    "structure": structure,
                    "tech": tech,
                    "console_errors": len(errors),
                    "network_requests": len(network),
                    "failed_requests": len([r for r in network if r["status"] == "FAILED"]),
                }

            report["comparisons"] = comparisons

            # ── Generate Diff ──
            a = comparisons["site_a"]
            b = comparisons["site_b"]
            diff = []

            # Performance diff
            for metric in ["domContentLoaded", "fullLoad", "firstContentfulPaint", "resourceCount", "totalTransferSize"]:
                val_a = a["performance"].get(metric, 0)
                val_b = b["performance"].get(metric, 0)
                if val_a and val_b:
                    winner = "A" if val_a < val_b else "B" if val_b < val_a else "TIE"
                    diff.append({"metric": metric, "site_a": val_a, "site_b": val_b, "winner": winner})

            # Content diff
            for key in ["links", "images", "forms", "buttons", "scripts"]:
                diff.append({"metric": key, "site_a": a["structure"].get(key, 0), "site_b": b["structure"].get(key, 0)})

            # SEO diff
            diff.append({"metric": "has_meta_description", "site_a": a["structure"].get("has_meta_description"), "site_b": b["structure"].get("has_meta_description")})
            diff.append({"metric": "has_og_image", "site_a": a["structure"].get("has_og_image"), "site_b": b["structure"].get("has_og_image")})

            # Error diff
            diff.append({"metric": "console_errors", "site_a": a["console_errors"], "site_b": b["console_errors"]})
            diff.append({"metric": "failed_requests", "site_a": a["failed_requests"], "site_b": b["failed_requests"]})

            report["diff"] = diff
            report["message"] = "Comparison complete."
            
            # Register for reporting
            self.last_audit_data = report

            # Clean up comparison tabs
            await self.close_tab("site_a")
            await self.close_tab("site_b")

            return report

        except Exception as e:
            return {"status": "error", "message": f"Comparison failed: {str(e)}"}

    async def run_full_audit(self) -> Dict[str, Any]:
        """
        Perform a comprehensive forensic audit of the current page.
        Gathers performance, structural, and technical metadata.
        """
        try:
            url = self.page.url
            title = await self.page.title()

            # 1. Performance
            perf = await self.get_performance_metrics()
            perf_data = perf.get("metrics", {}) if perf.get("status") == "success" else {}

            # 2. Hero Screenshot
            hero_path = os.path.join(self.screenshots_dir, "audit_hero.png")
            await self.page.screenshot(path=hero_path, full_page=False)

            # 3. DOM Mapping (Basic count)
            dom = await self.map_dom()
            element_count = dom.get("element_count", 0)

            # 4. Content Structure & Semantic Scan
            structure = await self.page.evaluate("""
                () => {
                    const headings = Array.from(document.querySelectorAll('h1,h2,h3,h4,h5,h6')).map(h => ({
                        tag: h.tagName, 
                        text: h.innerText.trim().substring(0, 100),
                        level: parseInt(h.tagName[1])
                    }));
                    
                    const links = Array.from(document.querySelectorAll('a[href]'));
                    const mixed_content = links.filter(a => a.href.startsWith('http://')).map(a => a.href).slice(0, 5);
                    
                    const semantic_tags = {
                        main: document.querySelectorAll('main').length,
                        article: document.querySelectorAll('article').length,
                        section: document.querySelectorAll('section').length,
                        header: document.querySelectorAll('header').length,
                        footer: document.querySelectorAll('footer').length,
                        nav: document.querySelectorAll('nav').length,
                        aside: document.querySelectorAll('aside').length
                    };

                    const meta_desc = document.querySelector('meta[name="description"]');
                    const og_image = document.querySelector('meta[property="og:image"]');
                    
                    return {
                        headings, 
                        link_count: links.length, 
                        mixed_content,
                        semantic_tags,
                        images: document.querySelectorAll('img').length,
                        has_meta_description: !!meta_desc,
                        meta_description: meta_desc ? meta_desc.content.substring(0, 120) : null,
                        has_og_image: !!og_image,
                        page_height: document.body.scrollHeight
                    };
                }
            """)

            # 5. Tech Stack
            tech = await self.page.evaluate("""
                () => {
                    const detected = [];
                    if (window.React || document.querySelector('[data-reactroot]')) detected.push('React');
                    if (window.__NEXT_DATA__) detected.push('Next.js');
                    if (window.__NUXT__) detected.push('Nuxt');
                    if (document.querySelector('[data-v-]')) detected.push('Vue');
                    if (window.angular || document.querySelector('[ng-app]')) detected.push('Angular');
                    if (document.querySelector('script[src*="jquery"]')) detected.push('jQuery');
                    if (document.querySelector('script[src*="gtag"]') || document.querySelector('script[src*="analytics"]')) detected.push('Google Analytics');
                    if (document.querySelector('link[href*="tailwind"]') || document.querySelector('[class*="tw-"]')) detected.push('Tailwind');
                    if (document.querySelector('link[href*="bootstrap"]')) detected.push('Bootstrap');
                    const copyright = document.body.innerText.match(/©\s*(\d{4})/); 
                    return { frameworks: detected, copyright_year: copyright ? copyright[1] : null };
                }
            """)

            # 6. AI Readiness Check
            ai_readiness = {"llms_txt": False, "robots_ai_rules": []}
            try:
                base_url = "/".join(url.split("/")[:3])
                # Check llms.txt
                resp = await self.page.request.get(f"{base_url}/llms.txt")
                if resp.status == 200:
                    ai_readiness["llms_txt"] = True
                
                # Check robots.txt for AI bots
                resp_robots = await self.page.request.get(f"{base_url}/robots.txt")
                if resp_robots.status == 200:
                    robots_text = await resp_robots.text()
                    for bot in ["GPTBot", "CCBot", "PerplexityBot"]:
                        if bot in robots_text:
                            ai_readiness["robots_ai_rules"].append(bot)
            except:
                pass

            # 7. UI/UX Deconstruction
            deconstruction = await self.deconstruct_ui()

            audit_result = {
                "url": url,
                "title": title,
                "hero_screenshot": hero_path,
                "performance": perf_data,
                "structure": structure,
                "tech": tech,
                "ai_readiness": ai_readiness,
                "deconstruction": deconstruction,
                "element_count": element_count,
                "console_errors": len(self.console_logs),
                "network_requests": len(self.network_log),
                "failed_requests": len([r for r in self.network_log if r["status"] == "FAILED"]),
                "timestamp": datetime.now().isoformat()
            }

            # Register for reporter
            self.last_audit_data = audit_result
            return audit_result

        except Exception as e:
            return {"status": "error", "message": f"Audit failed: {str(e)}"}

    async def generate_pdf(self, html_path: str, output_path: str) -> str:
        """Renders a local HTML file to a professional PDF using Playwright."""
        try:
            # We use a secondary page/context to avoid messing with the active audit session
            temp_page = await self.context.new_page()
            await temp_page.goto(f"file:///{os.path.abspath(html_path)}", wait_until="networkidle")
            
            # PDF Options for Professional Layout
            await temp_page.pdf(
                path=output_path,
                format="A4",
                print_background=True,
                margin={"top": "0px", "right": "0px", "bottom": "0px", "left": "0px"},
                display_header_footer=False
            )
            await temp_page.close()
            return output_path
        except Exception as e:
            raise Exception(f"PDF generation failed: {str(e)}")

    async def deconstruct_ui(self) -> Dict[str, Any]:
        """
        Runs a deep architectural and design deconstruction of the current page.
        Identifies design tokens (palette, typography), layout logic (flex/grid), 
        and component roles to generate a 'Kinetic Soul' profile of the UI.
        """
        try:
            script = self.deconstructor.get_deconstruction_script()
            raw_data = await self.page.evaluate(script)
            
            # Enrich with analysis
            final_data = self.deconstructor.analyze_results(raw_data)
            
            # Store for potential reporting
            self.last_decon_data = final_data
            return final_data
        except Exception as e:
            return {"status": "error", "message": f"Deconstruction failed: {str(e)}"}

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

            # ── Activate Virtual Mouse Cursor ──
            box = await locator.bounding_box()
            if box:
                target_x = box["x"] + box["width"] / 2
                target_y = box["y"] + box["height"] / 2
                await self.page.evaluate(
                    """([x, y]) => {
                        let cursor = document.getElementById('__ghost_cursor__');
                        if (!cursor) {
                            cursor = document.createElement('div');
                            cursor.id = '__ghost_cursor__';
                            // A high-end neon laser-pointer style cursor
                            cursor.style.cssText = 'position:fixed; top:0; left:0; width:18px; height:18px; border-radius:50%; background:rgba(255, 0, 85, 0.6); border:2px solid #fff; z-index:2147483647; pointer-events:none; transition: all 0.6s cubic-bezier(0.16, 1, 0.3, 1); transform:translate(-50%, -50%); box-shadow: 0 0 15px #FF0055, 0 0 5px #fff;';
                            document.body.appendChild(cursor);
                        }
                        // Move cursor
                        cursor.style.left = x + 'px';
                        cursor.style.top = y + 'px';
                    }""",
                    [target_x, target_y]
                )
                await asyncio.sleep(0.5)  # Wait for cursor to travel there

            if action == "click":
                # Simulate physical click ripple
                await self.page.evaluate("""() => {
                    const c = document.getElementById('__ghost_cursor__');
                    if (c) {
                        c.style.transform = 'translate(-50%, -50%) scale(2)';
                        c.style.background = 'rgba(255, 255, 255, 0.9)';
                        c.style.boxShadow = '0 0 40px #FF0055, 0 0 10px #fff';
                        setTimeout(() => {
                            c.style.transform = 'translate(-50%, -50%) scale(1)';
                            c.style.background = 'rgba(255, 0, 85, 0.6)';
                            c.style.boxShadow = '0 0 15px #FF0055, 0 0 5px #fff';
                        }, 250);
                    }
                }""")
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
            # High-precision wait: Ensure fonts and images are fully decoded
            # to guarantee the AI sees exactly what is intended.
            await self.page.evaluate("""() => {
                return Promise.all([
                    document.fonts.ready,
                    ...Array.from(document.querySelectorAll('img')).map(img => {
                        if (img.complete) return Promise.resolve();
                        return new Promise(resolve => { img.onload = img.onerror = resolve; });
                    })
                ]);
            }""")
            await asyncio.sleep(0.3)  # Ensure compositor commits frame

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

    # ─── AGENTIC VISION: REAL-TIME EYE ──────────────────────────

    async def look_at_viewport(self) -> Dict[str, Any]:
        """
        Instantly captures the current viewport.
        Returns base64 image data and a lightweight map of visible interactive elements.
        This provides the AI with immediate, real-time 'sight'.
        """
        if not self.page or self.page.is_closed():
            return {"status": "error", "message": "No active page."}

        try:
            # 1. Take a fast, compressed JPEG snapshot
            screenshot_bytes = await self.page.screenshot(type="jpeg", quality=60)
            
            # 2. Extract quick DOM geometry for interactive elements
            elements = await self.page.evaluate("""
                () => {
                    const interactives = Array.from(document.querySelectorAll('a, button, input, select, textarea, [role="button"], [tabindex]'));
                    return interactives.map((el, i) => {
                        const rect = el.getBoundingClientRect();
                        // Only return if visible in current viewport
                        if (rect.width > 0 && rect.height > 0 && rect.top >= 0 && rect.bottom <= window.innerHeight) {
                            return {
                                tag: el.tagName.toLowerCase(),
                                text: el.innerText ? el.innerText.trim().substring(0, 30) : (el.value ? el.value.substring(0, 30) : ''),
                                x: Math.round(rect.x),
                                y: Math.round(rect.y),
                                w: Math.round(rect.width),
                                h: Math.round(rect.height)
                            };
                        }
                        return null;
                    }).filter(Boolean);
                }
            """)
            
            # 3. Get scroll progress
            scroll = await self.page.evaluate("() => ({y: window.scrollY, max: document.body.scrollHeight - window.innerHeight})")
            progress = round((scroll['y'] / max(1, scroll['max'])) * 100) if scroll['max'] > 0 else 0

            import base64
            b64_image = base64.b64encode(screenshot_bytes).decode('utf-8')

            return {
                "status": "success",
                "image_b64": b64_image,
                "elements": elements,
                "scroll_progress": progress
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}

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

    # ─── ENGINE STATUS ───────────────────────────────────────────

    def get_status(self) -> Dict[str, Any]:
        """Returns the current operational status and directory paths."""
        return {
            "status": "active",
            "cwd": os.getcwd(),
            "phantom_root": os.path.join(os.getcwd(), ".ghost"),
            "directories": {
                "screenshots": self.screenshots_dir,
                "video": self.recordings_dir,
                "vision": self.vision_dir,
                "reports": self.reports_dir,
                "clones": self.clones_dir
            },
            "active_tab": self.active_tab,
            "tab_count": len(self.tabs)
        }

    # ─── ULTIMATE GHOST CLONER (CONTAINER MODE) ───────────────────

    async def steal_container(self, name: str) -> str:
        """
        Creates the Ultimate .ghost Container.
        Bypasses SPA 404s using a Brain Surgeon proxy and bypasses CORS using a specialized App Launcher.
        """
        if not self.page: return "❌ No active page to clone."
        try:
            import re
            clean_name = "".join(c for c in name if c.isalnum() or c in ('-', '_')) or "site"
            container_dir = os.path.join(self.clones_dir, f"{clean_name}.ghost")
            os.makedirs(container_dir, exist_ok=True)
            
            # Extract live URL and Path
            current_url = self.page.url
            from urllib.parse import urlparse
            parsed_url = urlparse(current_url)
            live_pathname = parsed_url.path or "/"

            # Extract raw DOM with absolutized URLs (KEEP SCRIPTS INTACT)
            stealer_js = """
            (async () => {
                const toAbs = (url) => { try { return new URL(url, document.baseURI).href; } catch(e) { return url; } };
                let allCSS = '';
                for (const sheet of Array.from(document.styleSheets)) {
                    try { for (const rule of Array.from(sheet.cssRules)) { allCSS += rule.cssText + '\\n'; } } catch(e) {}
                }
                document.querySelectorAll('[src]').forEach(el => el.src = toAbs(el.getAttribute('src')));
                document.querySelectorAll('[href]').forEach(el => el.href = toAbs(el.getAttribute('href')));
                
                return {
                    head: document.head.innerHTML,
                    body: document.body.innerHTML,
                    css: allCSS
                };
            })()
            """
            data = await self.page.evaluate(stealer_js)
            
            # The Brain Surgeon Proxy: Tricks React Router into thinking it's on the live site
            proxy_script = f"""
            <script>
                // GHOST BRAIN SURGEON PROXY
                try {{
                    window.history.replaceState({{}}, '', '{live_pathname}');
                    console.log("[Ghost] React Router Proxy Activated: " + '{live_pathname}');
                }} catch(e) {{}}
            </script>
            """
            
            html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <base href="{current_url}">
    {proxy_script}
    {data.get('head', '')}
    <style>{data.get('css', '')}</style>
    <style>/* Ghost Visibility Fix */ body {{ opacity: 1 !important; visibility: visible !important; display: block !important; }}</style>
</head>
<body>
    {data.get('body', '')}
</body>
</html>"""

            # Save the index.html inside the container
            index_path = os.path.join(container_dir, "index.html")
            with open(index_path, "w", encoding="utf-8") as f:
                f.write(html_content)
                
            # Create the Launcher Script (The Micro-Server)
            launcher_code = f"""import http.server
import socketserver
import threading
import time
import subprocess
import os
import sys

PORT = 8080
DIRECTORY = os.path.dirname(os.path.abspath(__file__))

class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)

httpd = socketserver.TCPServer(("", PORT), Handler)
thread = threading.Thread(target=httpd.serve_forever)
thread.daemon = True
thread.start()

print("👻 Ghost Container Booting on port", PORT)

# Launch Chrome in App Mode with Web Security Disabled (Bypasses CORS for WebGL/React)
chrome_paths = [
    r"C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",
    r"C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe"
]
chrome_exe = next((p for p in chrome_paths if os.path.exists(p)), None)

if chrome_exe:
    user_data = os.path.join(DIRECTORY, ".chrome_profile")
    cmd = [
        chrome_exe,
        f"--app=http://localhost:{{PORT}}",
        "--disable-web-security",
        f"--user-data-dir={{user_data}}",
        "--no-sandbox"
    ]
    subprocess.Popen(cmd)
    print("✨ Chrome App Launched. Press Ctrl+C to close server.")
else:
    print("⚠️ Chrome not found. Open http://localhost:8080 manually.")

try:
    while True: time.sleep(1)
except KeyboardInterrupt:
    print("Shutting down Ghost Container...")
    httpd.shutdown()
"""
            launcher_path = os.path.join(container_dir, "ghost_run.py")
            with open(launcher_path, "w", encoding="utf-8") as f:
                f.write(launcher_code)
                
            return f"✅ ULTIMATE GHOST CONTAINER CREATED:\nPath: {container_dir}\nTo launch: Run 'python ghost_run.py' inside the folder."
        except Exception as e:
            return f"❌ CONTAINER STEAL FAILED: {str(e)}"
