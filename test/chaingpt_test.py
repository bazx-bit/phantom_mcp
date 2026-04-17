import asyncio
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "engine", "src"))
from ghost_browser import GhostBrowserManager

async def test_chaingpt():
    manager = GhostBrowserManager()
    
    print("=" * 60)
    print("👻 PHANTOM MCP — REAL SITE TEST: labs.chaingpt.org")
    print("=" * 60)

    await manager.initialize()

    # ── Step 1: Navigate ──
    print("\n[1] Navigating to https://labs.chaingpt.org/ ...")
    result = await manager.navigate("https://labs.chaingpt.org/")
    print(f"    {result}")

    # ── Step 2: Viewport screenshot of hero section ──
    print("\n[2] Taking VIEWPORT screenshot of the hero (what user sees)...")
    path = await manager.take_screenshot("chaingpt_hero_viewport")
    size = os.path.getsize(path) if os.path.exists(path) else 0
    print(f"    Saved: {path}  ({size/1024:.1f} KB)")

    # ── Step 3: Smooth scroll down 500px ──
    print("\n[3] Smooth scrolling DOWN 500px...")
    result = await manager.scroll_page("down", 500, smooth=True)
    print(f"    {result}")
    path = await manager.take_screenshot("chaingpt_after_scroll_500")
    print(f"    Screenshot: {path}")

    # ── Step 4: Smooth scroll down another 500px ──
    print("\n[4] Smooth scrolling DOWN another 500px...")
    result = await manager.scroll_page("down", 500, smooth=True)
    print(f"    {result}")
    path = await manager.take_screenshot("chaingpt_after_scroll_1000")
    print(f"    Screenshot: {path}")

    # ── Step 5: Smooth scroll back to top ──
    print("\n[5] Smooth scrolling back to TOP...")
    result = await manager.scroll_page("top", smooth=True)
    print(f"    {result}")

    # ── Step 6: CINEMATIC SCROLL (the main event) ──
    print("\n[6] 🎬 CINEMATIC SCROLL — Full page journey...")
    print("    (This will take a moment — scrolling the entire page slowly)")
    result = await manager.cinematic_scroll(step_px=350, pause_ms=700)
    if result["status"] == "success":
        print(f"    ✅ {result['message']}")
        print(f"    Page Height: {result['page_height']}px")
        print(f"    Snapshots captured: {result['frames']}")
        for i, snap in enumerate(result["snapshots"][:5]):
            print(f"      [{i}] {os.path.basename(snap)}")
        if result["frames"] > 5:
            print(f"      ... and {result['frames'] - 5} more")
    else:
        print(f"    ❌ {result['message']}")

    # ── Step 7: Video path ──
    print("\n[7] 🎥 Video recording path...")
    video = await manager.get_video_path()
    print(f"    {video}")

    await manager.close()

    # ── Show disk summary ──
    screenshots_dir = os.path.join(os.getcwd(), '.ghost', 'screenshots')
    files = [f for f in os.listdir(screenshots_dir) if f.startswith("cinematic_") or f.startswith("chaingpt_")]
    print(f"\n📁 Total screenshots saved: {len(files)}")
    for f in sorted(files):
        fpath = os.path.join(screenshots_dir, f)
        print(f"    {f}  ({os.path.getsize(fpath)/1024:.1f} KB)")

    print("\n" + "=" * 60)
    print("🎉 CHAINGPT REAL-SITE TEST COMPLETE")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(test_chaingpt())
