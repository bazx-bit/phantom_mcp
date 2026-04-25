import asyncio
import os
import sys
import json

# Ensure UTF-8 output on all systems
if sys.stdout.encoding != 'utf-8':
    try:
        import codecs
        sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
        sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')
    except Exception:
        pass

# Add engine/src to path so we can import ghost_browser
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "engine", "src"))
from ghost_browser import GhostBrowserManager


async def test_full_engine():
    """
    Comprehensive test of the Site-Ghost Playwright Engine.
    Tests: navigation, DOM mapping, interactions, scroll, viewport,
    JS injection, mutations, network log, performance, links, video.
    """
    manager = GhostBrowserManager()
    passed = 0
    failed = 0

    def check(name, condition, detail=""):
        nonlocal passed, failed
        if condition:
            passed += 1
            print(f"  ✅ {name}")
        else:
            failed += 1
            print(f"  ❌ {name} — {detail}")

    print("=" * 60)
    print("👻 SITE-GHOST ENGINE TEST SUITE")
    print("=" * 60)

    # ─── 1. INITIALIZE ────────────────────────────────
    print("\n[1/10] Initializing Playwright daemon...")
    await manager.initialize()
    check("Browser initialized", manager.browser is not None)
    check("Page created", manager.page is not None)

    # ─── 2. NAVIGATE ──────────────────────────────────
    print("\n[2/10] Navigation...")
    nav = await manager.navigate("https://example.com")
    check("Navigation success", "Navigated" in nav, nav)
    check("Page title extracted", "Example" in nav, nav)

    # ─── 3. DOM MAPPING ──────────────────────────────
    print("\n[3/10] Precision DOM Mapping...")
    dom = await manager.map_dom()
    check("DOM map status", dom["status"] == "success", dom.get("message", ""))
    check("Elements found", dom["element_count"] > 0, f"count={dom['element_count']}")
    check("Screenshot saved", os.path.exists(dom["screenshot_path"]), dom["screenshot_path"])
    check("Animated count returned", "animated_count" in dom)

    # ─── 4. INTERACTIONS ─────────────────────────────
    print("\n[4/10] Interactions (hover, click)...")
    elements = dom["data"]
    link_el = None
    for el in elements:
        if el["tagName"] == "A" and el.get("text"):
            link_el = el
            break
    if link_el:
        hover_res = await manager.perform_action(link_el["id"], "hover")
        check("Hover action", hover_res["status"] == "success", hover_res["message"])
        click_res = await manager.perform_action(link_el["id"], "click")
        check("Click action", click_res["status"] == "success", click_res["message"])
        # Navigate back
        await manager.navigate("https://example.com")
    else:
        check("Link element found", False, "No link found to test")

    # ─── 5. SCROLLING ────────────────────────────────
    print("\n[5/10] Scroll control...")
    scroll_res = await manager.scroll_page("down", 200)
    check("Scroll down", "Scrolled" in scroll_res, scroll_res)
    scroll_res = await manager.scroll_page("top")
    check("Scroll to top", "Scrolled" in scroll_res, scroll_res)

    # ─── 6. VIEWPORT ─────────────────────────────────
    print("\n[6/10] Viewport control...")
    vp_res = await manager.set_viewport(375, 812)
    check("Mobile viewport", "375x812" in vp_res, vp_res)
    vp_res = await manager.set_viewport(1280, 720)
    check("Desktop viewport", "1280x720" in vp_res, vp_res)

    # ─── 7. SCREENSHOT ───────────────────────────────
    print("\n[7/10] Named screenshot...")
    ss_path = await manager.take_screenshot("test_capture")
    check("Screenshot file created", os.path.exists(ss_path), ss_path)

    # ─── 8. JS INJECTION ─────────────────────────────
    print("\n[8/10] Live JavaScript injection...")
    js_res = await manager.execute_js("document.title")
    check("JS returns page title", "Example" in js_res, js_res)
    js_res2 = await manager.execute_js("document.querySelectorAll('*').length")
    check("JS returns DOM node count", js_res2.isdigit() or js_res2.strip().isdigit(), js_res2)

    # ─── 9. PERFORMANCE ──────────────────────────────
    print("\n[9/10] Performance metrics...")
    perf = await manager.get_performance_metrics()
    check("Performance extracted", perf["status"] == "success", perf.get("message", ""))
    if perf["status"] == "success":
        m = perf["metrics"]
        check("FCP available", m.get("firstContentfulPaint") is not None)
        check("Resource count available", m.get("resourceCount") is not None)

    # ─── 10. LINKS & NETWORK ─────────────────────────
    print("\n[10/10] Link extraction & Network log...")
    links = await manager.extract_links()
    check("Links extracted", len(links) > 0, f"count={len(links)}")
    net_log = await manager.get_network_log()
    check("Network log populated", len(net_log) > 0, f"count={len(net_log)}")

    # ─── VIDEO ────────────────────────────────────────
    video_path = await manager.get_video_path()
    check("Video recording active", os.path.exists(video_path), video_path)

    # ─── MUTATIONS ────────────────────────────────────
    await manager.map_dom()  # Re-inject observer
    mutations = await manager.drain_mutations()
    check("Mutation drain works", isinstance(mutations, list))

    # ─── SKILLS LOADED ────────────────────────────────
    skills_dir = os.path.join(os.path.dirname(__file__), "..", "engine", "src", "skills")
    skill_files = [f for f in os.listdir(skills_dir) if f.endswith(".md")]
    check(f"Skills loaded ({len(skill_files)} found)", len(skill_files) >= 7, str(skill_files))

    # ─── SHUTDOWN ─────────────────────────────────────
    print("\n[CLEANUP] Shutting down daemon...")
    await manager.close()
    check("Browser closed", manager.playwright is None)

    # ─── SUMMARY ──────────────────────────────────────
    total = passed + failed
    print("\n" + "=" * 60)
    print(f"👻 RESULTS: {passed}/{total} passed | {failed} failed")
    if failed == 0:
        print("🎉 ALL TESTS PASSED — ENGINE IS COMBAT-READY")
    else:
        print(f"⚠️  {failed} test(s) need attention")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(test_full_engine())
