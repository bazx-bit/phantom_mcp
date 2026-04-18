import asyncio
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "engine", "src"))
from ghost_browser import GhostBrowserManager

async def test_virtual_mouse():
    manager = GhostBrowserManager()

    print("=" * 65)
    print("👻 PHANTOM MCP — VIRTUAL MOUSE & AI STREAMING TEST")
    print("=" * 65)

    await manager.initialize()

    print("\n[1] Navigating to ChainGPT...")
    await manager.navigate("https://labs.chaingpt.org/")

    print("\n[2] Mapping DOM to find physical buttons...")
    mapping = await manager.map_dom()
    
    # Let's find an interesting button. We know there's an "APPLY NOW" button
    target_id = None
    target_text = ""
    for el in mapping.get("data", []):
        if "interactive" in el["type"] and "APPLY" in el["text"].upper():
            target_id = el["id"]
            target_text = el["text"]
            break
            
    if not target_id:
         # fallback to any interactive element
         for el in mapping.get("data", []):
            if "interactive" in el["type"] and el["text"]:
                target_id = el["id"]
                target_text = el["text"]
                break

    if not target_id:
        print("❌ Could not find a button to click.")
        await manager.close()
        return

    print(f"    Target acquired: [{target_id}] '{target_text}'")

    print("\n[3] 🎥 Starting AI Vision Streaming (fps=4.0)...")
    await manager.start_vision(fps=4.0)
    
    print("\n[4] 🖱️ Executing phantom hover + click (watch the mouse move!)...")
    
    # ── This triggers the new visual cursor logic ──
    print("    -> Moving mouse and hovering...")
    res = await manager.perform_action(target_id, "hover")
    print(f"    {res['message']}")
    
    print("    -> Simulating physical click ripple...")
    res = await manager.perform_action(target_id, "click")
    print(f"    {res['message']}")
    
    # Wait for the page to react
    await asyncio.sleep(2)

    print("\n[5] 🛑 Stopping AI Vision Stream...")
    await manager.stop_vision()

    print("\n[6] 🎞️ Checking the Vision Timeline (What the AI 'saw' during the click)...")
    frames = await manager.get_vision_timeline(limit=10)
    print(f"    Fetched {len(frames)} frames from the interaction milliseconds.")
    
    # Save a copy of the video path before we close
    video = await manager.get_video_path()

    await manager.close()
    
    print("\n" + "=" * 65)
    print(f"🎉 TEST COMPLETE")
    print(f"🎥 FULL VIDEO (See the mouse move!): {video}")
    for f in frames:
        print(f"    Frame: {f}")
    print("=" * 65)

if __name__ == "__main__":
    asyncio.run(test_virtual_mouse())
