import asyncio
import os
import sys

# Ensure Python can find the engine module
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "engine", "src"))
from ghost_browser import GhostBrowserManager

async def run_viral_demo():
    print("🎬 BOOTING VIRAL DEMO ENGINE...")
    
    manager = GhostBrowserManager()
    await manager.initialize()
    
    # Linear is the gold standard for web design - perfect for a visual demo
    url = "https://linear.app"
    print(f"🌍 Navigating to {url}...")
    await manager.navigate(url)
    await asyncio.sleep(3)
    
    # Step 1: Map DOM to reveal the 'AI Vision'
    print("👁️ TRIGGERING VISUAL FORENSICS...")
    dom = await manager.map_dom()
    await asyncio.sleep(2)
    
    # Step 2: Smooth Cinematic Scroll to show page structure
    print("📜 EXECUTING CINEMATIC SCROLL...")
    await manager.scroll_page("down", 800)
    await asyncio.sleep(1.5)
    await manager.scroll_page("down", 800)
    await asyncio.sleep(2)
    
    # Step 3: Precision Hover Dance
    # We'll hover over specific headlines and buttons to show the red laser
    elements = dom.get("data", [])
    
    # Find some high-impact targets
    # Looking for 'Get Started' or headlines
    targets = [el for el in elements if el.get("type") == "interactive" and len(el.get("text", "")) > 5]
    
    if len(targets) > 5:
        print("🎯 EXECUTING PRECISION HOVER DANCE...")
        for i in [2, 4, 1]: # Jump around to show the mouse travel
            target = targets[i]
            print(f"  -> Tracking: {target['text']}")
            await manager.perform_action(target["id"], "hover")
            await asyncio.sleep(1)
            
    # Step 4: The Reality Snap (Responsive Viewport)
    print("📱 EXECUTING RESPONSIVE STRESS TEST...")
    await manager.set_viewport(390, 844) # iPhone 13 Pro
    await asyncio.sleep(1.5)
    print("  -> Re-aligning vision for mobile...")
    await manager.map_dom()
    await asyncio.sleep(2)
    
    # Step 5: Final Click & Ripple
    print("💥 EXECUTING INTERACTION TRIGGER...")
    # Find a button on the mobile view
    dom_mobile = await manager.map_dom()
    mobile_elements = dom_mobile.get("data", [])
    btn = next((el for el in mobile_elements if el.get("tagName") == "BUTTON" or (el.get("tagName") == "A" and "button" in el.get("attributes", {}).get("class", "").lower())), None)
    
    if btn:
        print(f"  -> Final Target: {btn.get('text', 'CTA')}")
        await manager.perform_action(btn["id"], "click")
        await asyncio.sleep(1)
    
    # Step 6: Full Desktop Return
    await manager.set_viewport(1440, 900)
    await asyncio.sleep(1)

    video_path = await manager.get_video_path()
    print("\n✅ VIRAL DEMO COMPLETE!")
    print(f"🎥 FINAL EXPORT READY AT: {video_path}")
    
    await manager.close()

if __name__ == "__main__":
    asyncio.run(run_viral_demo())
