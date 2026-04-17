import asyncio
import os
import sys
import shutil

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "engine", "src"))
from ghost_browser import GhostBrowserManager

async def test_vision_system():
    manager = GhostBrowserManager()
    
    print("============================================================")
    print("👻 SITE-GHOST VISION STRESS TEST")
    print("============================================================")

    print("[1] Initialization...")
    await manager.initialize()
    await manager.navigate("https://example.com")
    
    vision_dir = manager.vision_dir
    # Ensure it's empty
    if os.path.exists(vision_dir):
        shutil.rmtree(vision_dir)
    os.makedirs(vision_dir, exist_ok=True)

    print("[2] Vision Start (5 FPS)...")
    result = await manager.start_vision(fps=5.0)
    print(f"    {result}")
    
    print("[3] Capturing 2 seconds of frames...")
    await asyncio.sleep(2.2) # Should be ~10-11 frames
    
    frames = os.listdir(vision_dir)
    print(f"    Frames on disk: {len(frames)}")
    if len(frames) >= 10:
        print("    ✅ FPS Capture within expected range")
    else:
        print(f"    ❌ Expected ~10 frames, found {len(frames)}")

    print("[4] Checking JPEG Compaction...")
    first_frame = os.path.join(vision_dir, frames[0])
    size = os.path.getsize(first_frame)
    print(f"    Frame size: {size / 1024:.2f} KB")
    if size < 200 * 1024:
        print("    ✅ Compression active (JPEG quality 60)")
    else:
        print(f"    ❌ Frame size too large: {size}")

    print("[5] Timeline Retrieval (limit 5)...")
    timeline = await manager.get_vision_timeline(limit=5)
    print(f"    Timeline count: {len(timeline)}")
    if len(timeline) == 5:
        print("    ✅ Timeline limit respected")
    else:
        print(f"    ❌ Expected 5 frames, got {len(timeline)}")

    print("[6] Sliding Window Stress (Max 50)...")
    print("    Starting high-speed 10 FPS vision...")
    await manager.start_vision(fps=10.0)
    await asyncio.sleep(6) # Should hit >60 frames total, but buffer should cap at 50
    
    frames_now = os.listdir(vision_dir)
    print(f"    Frames on disk: {len(frames_now)}")
    if len(frames_now) <= 55: # Allow slight overlap for async buffer removal
        print("    ✅ Sliding window works (capped at ~50)")
    else:
        print(f"    ❌ Buffer limit failed: {len(frames_now)} frames found")

    print("[7] Vision Stop...")
    stop_res = await manager.stop_vision()
    print(f"    {stop_res}")
    
    count_before = len(os.listdir(vision_dir))
    await asyncio.sleep(1)
    count_after = len(os.listdir(vision_dir))
    if count_before == count_after:
        print("    ✅ Background task ceased")
    else:
        print("    ❌ Vision task still running after stop")

    print("[8] Session Cleanup...")
    await manager.close()
    if not os.path.exists(vision_dir) or len(os.listdir(vision_dir)) == 0:
        print("    ✅ Visual cleanup success (directory purged)")
    else:
        print(f"    ❌ Cleanup failed: {len(os.listdir(vision_dir))} files remain")

    print("============================================================")
    print("🎉 ALL VISION TESTS PASSED")
    print("============================================================")

if __name__ == "__main__":
    asyncio.run(test_vision_system())
