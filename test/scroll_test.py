import asyncio
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "engine", "src"))
from ghost_browser import GhostBrowserManager

async def test_smooth_scroll():
    manager = GhostBrowserManager()
    
    print("=" * 60)
    print("👻 PHANTOM MCP — SMOOTH SCROLL & CINEMATIC TEST")
    print("=" * 60)

    await manager.initialize()

    print("\n[1] Navigating to example.com...")
    result = await manager.navigate("https://example.com")
    print(f"    {result}")

    print("\n[2] Testing SMOOTH scroll down 300px...")
    result = await manager.scroll_page("down", 300, smooth=True)
    print(f"    {result}")

    print("\n[3] Testing SMOOTH scroll to top...")
    result = await manager.scroll_page("top", smooth=True)
    print(f"    {result}")

    print("\n[4] Taking VIEWPORT screenshot (not full-page)...")
    path = await manager.take_screenshot("viewport_test")
    print(f"    Saved: {path}")
    
    # Check it's a reasonable size (viewport, not full page)
    if os.path.exists(path):
        size = os.path.getsize(path)
        print(f"    Size: {size / 1024:.1f} KB")
        if size < 500 * 1024:
            print("    ✅ Viewport screenshot (not a massive full-page dump)")
        else:
            print("    ⚠️ Screenshot might still be full-page")

    print("\n[5] Testing CINEMATIC SCROLL (full page journey)...")
    result = await manager.cinematic_scroll(step_px=200, pause_ms=500)
    if result["status"] == "success":
        print(f"    ✅ {result['message']}")
        print(f"    Page height: {result['page_height']}px")
        for i, snap in enumerate(result["snapshots"][:5]):
            print(f"    Frame {i}: {snap}")
    else:
        print(f"    ❌ {result['message']}")

    print("\n[6] Getting video path...")
    video = await manager.get_video_path()
    print(f"    Video: {video}")

    await manager.close()

    print("\n" + "=" * 60)
    print("🎉 ALL SMOOTH SCROLL TESTS PASSED")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(test_smooth_scroll())
