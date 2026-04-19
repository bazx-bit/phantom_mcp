import asyncio
import os
import sys

# Ensure Python can find the engine module
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "engine", "src"))
from ghost_browser import GhostBrowserManager

async def run_forensic_explanation_demo():
    print("🎬 Starting Phantom MCP 'Visual Forensic' Explanation Video...")
    
    manager = GhostBrowserManager()
    await manager.initialize()
    
    # Using Wikipedia - reliable and has many clear interactive elements
    url = "https://www.wikipedia.org"
    print(f"🌍 Navigating to {url}...")
    await manager.navigate(url)
    await asyncio.sleep(2)
    
    # Step 1: Trigger the DOM Mapper
    print("\n🧠 STEP 1: THE AI BRAIN INJECTION")
    print("AI is running 'ghost_map_dom'.")
    print("EXPLANATION: To 'see' like a human, the AI injects a script that highlights everything it can interact with.")
    
    dom = await manager.map_dom()
    print(f"✅ Mapped {dom.get('element_count')} elements.")
    print("💖 PINK BOXES = Interactive (Links, Buttons, Search bars).")
    print("🌀 CYAN BOXES = Animated (Elements with CSS transitions).")
    await asyncio.sleep(3)
    
    # Step 2: Interaction Demo
    print("\n🖱️ STEP 2: PRECISION MOUSE MOVEMENT")
    elements = dom.get("data", [])
    
    # Find the search input
    search_input = next((el for el in elements if el.get("tagName") == "INPUT" and "search" in el.get("attributes", {}).get("name", "").lower()), None)
    
    if search_input:
        print(f"🎯 Targeting Search Bar [{search_input['id']}].")
        print("Notice the Red AI Laser moving precisely into the Pink target box.")
        await manager.perform_action(search_input["id"], "hover")
        await asyncio.sleep(1.5)
        
        print("⌨️ AI is typing...")
        await manager.page.keyboard.type("Artificial Intelligence", delay=100)
        await asyncio.sleep(1)
        
    # Step 3: Viewport Forensics
    print("\n📱 STEP 3: RESPONSIVE AUDIT")
    print("AI is checking how the site adapts to different screens.")
    await manager.set_viewport(414, 896) # iPhone XR size
    await asyncio.sleep(2)
    
    print("Re-mapping mobile view...")
    await manager.map_dom()
    await asyncio.sleep(2)
    
    video_path = await manager.get_video_path()
    print("\n✅ DEMO COMPLETE!")
    print(f"🎥 FINAL VIDEO SAVED AT: {video_path}")
    
    await manager.close()

if __name__ == "__main__":
    asyncio.run(run_forensic_explanation_demo())
