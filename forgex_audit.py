"""
Site-Ghost Forensics — forgexdev.online Audit
"""
import asyncio
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "engine", "src"))
from ghost_browser import GhostBrowserManager

async def audit_forgex():
    manager = GhostBrowserManager()
    
    print("=" * 60)
    print("👻 SITE-GHOST FORENSICS: forgexdev.online")
    print("=" * 60)

    await manager.initialize()
    
    # 1. Navigation
    print("[1] Primary Entry...")
    nav = await manager.navigate("https://forgexdev.online")
    print(f"    {nav}\n")

    # 2. Performance (Core Web Vitals)
    print("[2] Performance Profiling...")
    perf = await manager.get_performance_metrics()
    if perf["status"] == "success":
        m = perf["metrics"]
        print(f"    FCP: {m.get('firstContentfulPaint', '?')}ms")
        print(f"    Total Load: {m.get('fullLoad', '?')}ms")
        print(f"    DOM Nodes: {m.get('domInteractive', '?')}")
        print(f"    Network Requests: {m.get('resourceCount', '?')}\n")

    # 3. Precision DOM Mapping
    print("[3] Visual Hierarchy Audit...")
    dom = await manager.map_dom()
    print(f"    Mapped Elements: {dom['element_count']}")
    print(f"    Interactive Targets: {len([e for e in dom['data'] if e['type'] == 'interactive'])}")
    print(f"    Animation Layers Tracking: {dom['animated_count']}\n")

    # 4. Interaction Test (Hover over first major link/button)
    interactive = [e for e in dom["data"] if e["type"] == "interactive" and e["tagName"] in ("A", "BUTTON")]
    if interactive:
        target = interactive[0]
        print(f"[4] Interaction Stress: Hovering on '{target['text'][:30]}'...")
        await manager.perform_action(target["id"], "hover")
        mutations = await manager.drain_mutations()
        print(f"    Hover-triggered Mutations: {len(mutations)}")
    
    # 5. Mobile Stress Test
    print("\n[5] Mobile Viewport Stress (375x812)...")
    await manager.set_viewport(375, 812)
    await manager.navigate("https://forgexdev.online")
    ss_mobile = await manager.take_screenshot("forgex_mobile")
    print(f"    Mobile Screenshot: {ss_mobile}\n")

    # 6. Security Snapshot
    print("[6] Security Health Check...")
    cookies = await manager.get_cookies()
    insecure = [c for c in cookies if not c.get('secure')]
    print(f"    Active Cookies: {len(cookies)}")
    if insecure:
        print(f"    ⚠️  Found {len(insecure)} cookies without Secure flag")
    
    # 7. Final Report
    ss_final = await manager.take_screenshot("forgex_final_audit")
    print(f"\n[REPORT] Final Audit Capture: {ss_final}")
    
    video = await manager.get_video_path()
    print(f"[VIDEO] Session Recording: {video}\n")

    await manager.close()
    print("=" * 60)
    print("AUDIT COMPLETE.")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(audit_forgex())

