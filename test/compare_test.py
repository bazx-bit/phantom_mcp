import asyncio
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "engine", "src"))
from ghost_browser import GhostBrowserManager

async def test_comparison():
    manager = GhostBrowserManager()
    
    print("=" * 65)
    print("👻 PHANTOM MCP — MULTI-TAB COMPARISON TEST")
    print("   Site A: https://labs.chaingpt.org/")
    print("   Site B: https://stripe.com/")
    print("=" * 65)

    await manager.initialize()

    # ── Run the comparison ──
    print("\n[1] Running side-by-side comparison...")
    result = await manager.compare_sites(
        "https://labs.chaingpt.org/",
        "https://stripe.com/"
    )

    if result["status"] == "error":
        print(f"    ❌ {result['message']}")
        await manager.close()
        return

    print(f"    ✅ {result['message']}")
    
    a = result["comparisons"]["site_a"]
    b = result["comparisons"]["site_b"]

    # ── Print Report ──
    print("\n" + "═" * 65)
    print("🔍 COMPARISON REPORT")
    print("═" * 65)

    # Site Info
    print(f"\n  SITE A: {a['url']}")
    print(f"  Title:  {a['title']}")
    print(f"  Tech:   {', '.join(a['tech']['frameworks']) or 'None'}")
    print(f"  ©:      {a['tech'].get('copyright_year', '?')}")
    
    print(f"\n  SITE B: {b['url']}")
    print(f"  Title:  {b['title']}")
    print(f"  Tech:   {', '.join(b['tech']['frameworks']) or 'None'}")
    print(f"  ©:      {b['tech'].get('copyright_year', '?')}")

    # Performance
    print("\n" + "─" * 65)
    print("⚡ PERFORMANCE:")
    perf_keys = ["domContentLoaded", "fullLoad", "firstContentfulPaint"]
    for key in perf_keys:
        va = a["performance"].get(key, "?")
        vb = b["performance"].get(key, "?")
        print(f"  {key:<25} A={va}ms  |  B={vb}ms")

    # Content
    print("\n" + "─" * 65)
    print("📊 CONTENT:")
    print(f"  Page Height:   A={a['structure'].get('page_height', '?')}px  |  B={b['structure'].get('page_height', '?')}px")
    print(f"  Links:         A={a['structure'].get('links', '?')}  |  B={b['structure'].get('links', '?')}")
    print(f"  Images:        A={a['structure'].get('images', '?')}  |  B={b['structure'].get('images', '?')}")
    print(f"  Buttons:       A={a['structure'].get('buttons', '?')}  |  B={b['structure'].get('buttons', '?')}")
    print(f"  Scripts:       A={a['structure'].get('scripts', '?')}  |  B={b['structure'].get('scripts', '?')}")

    # SEO
    print("\n" + "─" * 65)
    print("🛡️ SEO & HEALTH:")
    print(f"  Meta Desc:   A={'✅' if a['structure'].get('has_meta_description') else '❌'}  |  B={'✅' if b['structure'].get('has_meta_description') else '❌'}")
    print(f"  OG Image:    A={'✅' if a['structure'].get('has_og_image') else '❌'}  |  B={'✅' if b['structure'].get('has_og_image') else '❌'}")
    print(f"  JS Errors:   A={a['console_errors']}  |  B={b['console_errors']}")
    print(f"  Net Failed:  A={a['failed_requests']}  |  B={b['failed_requests']}")
    print(f"  Net Total:   A={a['network_requests']}  |  B={b['network_requests']}")

    # Hero screenshots
    print("\n" + "─" * 65)
    print("📸 SCREENSHOTS:")
    print(f"  A: {a['hero_screenshot']}")
    print(f"  B: {b['hero_screenshot']}")

    # Diff
    print("\n" + "─" * 65)
    print("📋 DIFF TABLE:")
    for d in result["diff"]:
        m = d["metric"]
        va = d.get("site_a", "?")
        vb = d.get("site_b", "?")
        w = d.get("winner", "")
        print(f"  {m:<25} A={str(va):<10}  B={str(vb):<10}  {w}")

    await manager.close()

    print("\n" + "═" * 65)
    print("🎉 COMPARISON TEST COMPLETE")
    print("═" * 65)

if __name__ == "__main__":
    asyncio.run(test_comparison())
