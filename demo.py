"""
Site-Ghost Live Demo — Runs against stripe.com to demonstrate
scrolling, DOM mapping, interactions, performance, and screenshots.
"""
import asyncio
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "engine", "src"))
from ghost_browser import GhostBrowserManager


async def live_demo():
    manager = GhostBrowserManager()
    
    print("=" * 60)
    print("SITE-GHOST LIVE DEMO — stripe.com")
    print("=" * 60)

    await manager.initialize()
    print("[+] Chromium daemon started with video recording.\n")

    # ─── 1. NAVIGATE ──────────────────────────────────────
    print("[1] Navigating to stripe.com...")
    nav = await manager.navigate("https://stripe.com")
    print(f"    {nav}\n")

    # ─── 2. PERFORMANCE ──────────────────────────────────
    print("[2] Extracting Core Web Vitals...")
    perf = await manager.get_performance_metrics()
    if perf["status"] == "success":
        m = perf["metrics"]
        print(f"    FCP:          {m.get('firstContentfulPaint', '?')}ms")
        print(f"    Full Load:    {m.get('fullLoad', '?')}ms")
        print(f"    DOM Ready:    {m.get('domInteractive', '?')}ms")
        print(f"    Resources:    {m.get('resourceCount', '?')}")
        print(f"    Transfer:     {round(m.get('totalTransferSize', 0) / 1024, 1)}KB")
    print()

    # ─── 3. DOM MAP (top of page) ─────────────────────────
    print("[3] Injecting Precision DOM Mapper (top of page)...")
    dom = await manager.map_dom()
    print(f"    Elements mapped: {dom['element_count']}")
    print(f"    Animated elements: {dom['animated_count']}")
    print(f"    Console errors: {len(dom['console_errors'])}")
    print(f"    Screenshot: {dom['screenshot_path']}")
    
    # Show first 10 interactive elements
    interactive = [e for e in dom["data"] if e["type"] == "interactive"]
    print(f"    Interactive elements: {len(interactive)}")
    for el in interactive[:8]:
        print(f"      [{el['id']}] {el['tagName']} '{el['text'][:40]}' @ ({el['x']},{el['y']})")
    print()

    # ─── 4. SCROLL DOWN ──────────────────────────────────
    print("[4] Scrolling down 500px...")
    scroll_res = await manager.scroll_page("down", 500)
    print(f"    {scroll_res}")
    ss1 = await manager.take_screenshot("demo_scroll_1")
    print(f"    Screenshot after scroll: {ss1}\n")

    # ─── 5. SCROLL MORE ──────────────────────────────────
    print("[5] Scrolling down 500px more...")
    scroll_res = await manager.scroll_page("down", 500)
    print(f"    {scroll_res}")
    
    # Check for mutations (scroll-triggered animations)
    mutations = await manager.drain_mutations()
    print(f"    DOM mutations from scroll: {len(mutations)}")
    ss2 = await manager.take_screenshot("demo_scroll_2")
    print(f"    Screenshot: {ss2}\n")

    # ─── 6. SCROLL TO BOTTOM ─────────────────────────────
    print("[6] Scrolling to bottom of page...")
    scroll_res = await manager.scroll_page("bottom")
    print(f"    {scroll_res}")
    ss3 = await manager.take_screenshot("demo_bottom")
    print(f"    Screenshot: {ss3}\n")

    # ─── 7. BACK TO TOP + HOVER TEST ─────────────────────
    print("[7] Back to top, re-mapping DOM for hover test...")
    await manager.scroll_page("top")
    dom2 = await manager.map_dom()
    
    # Find a link or button to hover
    hover_target = None
    for el in dom2["data"]:
        if el["type"] == "interactive" and el["tagName"] in ("A", "BUTTON") and el["text"]:
            hover_target = el
            break
    
    if hover_target:
        print(f"    Hovering over [{hover_target['id']}] '{hover_target['text'][:30]}'...")
        hover_res = await manager.perform_action(hover_target["id"], "hover")
        print(f"    {hover_res['message']}")
        mutations = await manager.drain_mutations()
        print(f"    Mutations from hover: {len(mutations)}")
        ss4 = await manager.take_screenshot("demo_hover")
        print(f"    Screenshot: {ss4}")
    print()

    # ─── 8. MOBILE VIEWPORT ──────────────────────────────
    print("[8] Switching to mobile viewport (375x812)...")
    vp = await manager.set_viewport(375, 812)
    print(f"    {vp}")
    await manager.navigate("https://stripe.com")
    dom3 = await manager.map_dom()
    ss5 = await manager.take_screenshot("demo_mobile")
    print(f"    Mobile elements: {dom3['element_count']}")
    print(f"    Mobile screenshot: {ss5}\n")

    # ─── 9. JS INJECTION ─────────────────────────────────
    print("[9] Injecting live JavaScript...")
    js_res = await manager.execute_js("document.title")
    print(f"    Page title: {js_res}")
    js_res2 = await manager.execute_js("document.querySelectorAll('*').length")
    print(f"    Total DOM nodes: {js_res2}")
    js_res3 = await manager.execute_js("navigator.userAgent")
    print(f"    User Agent: {js_res3[:60]}...\n")

    # ─── 10. NETWORK LOG ─────────────────────────────────
    print("[10] Network request summary...")
    net = await manager.get_network_log()
    types_count = {}
    for r in net:
        t = r.get("type", "unknown")
        types_count[t] = types_count.get(t, 0) + 1
    print(f"    Total requests: {len(net)}")
    for t, c in sorted(types_count.items(), key=lambda x: -x[1]):
        print(f"      {t}: {c}")
    print()

    # ─── 11. EXTRACT LINKS ────────────────────────────────
    print("[11] Extracting page links...")
    links = await manager.extract_links()
    print(f"    Total links: {len(links)}")
    for l in links[:5]:
        print(f"      [{l['text'][:30]}] -> {l['href'][:60]}")
    print()

    # ─── VIDEO PATH ───────────────────────────────────────
    video = await manager.get_video_path()
    print(f"[VIDEO] Full session recording: {video}\n")

    # ─── SHUTDOWN ─────────────────────────────────────────
    await manager.close()
    print("=" * 60)
    print("DEMO COMPLETE. Check .ghost/screenshots/ for all captures.")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(live_demo())
