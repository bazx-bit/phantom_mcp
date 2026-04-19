import asyncio
import os
import sys

# Ensure Python can find the engine module
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "engine", "src"))
from ghost_browser import GhostBrowserManager

async def run_linkedin_demo():
    print("🎬 Starting Phantom MCP Cinematic Recording for LinkedIn...")
    
    # Initialize the engine
    manager = GhostBrowserManager()
    await manager.initialize()
    
    # 1. Navigate to a highly interactive demo site
    print("🌍 Navigating to Demo App...")
    await manager.navigate("https://demo.playwright.dev/todomvc/")
    await asyncio.sleep(1.5)
    
    # 2. Map the DOM so we can interact
    print("🗺️ Mapping the DOM (Injecting visual overlays)...")
    dom = await manager.map_dom()
    await asyncio.sleep(1)
    
    # We need to find the input box to type something
    elements = dom.get("data", [])
    
    # Find the main input field
    input_box = next((el for el in elements if el.get("tagName") == "INPUT" and el.get("attributes", {}).get("placeholder") == "What needs to be done?"), None)
    
    if input_box:
        # Hover over the input box to show the mouse moving
        print(f"🖱️ Moving physical mouse to Input Box [{input_box['id']}]...")
        await manager.perform_action(input_box["id"], "hover")
        await asyncio.sleep(1)
        
        # Click the input box
        print("💥 Clicking Input Box...")
        await manager.perform_action(input_box["id"], "click")
        await asyncio.sleep(0.5)
        
        # Type a command via script execution then hit Enter
        # For typing, perform_action currently takes value in kwargs if we modify the API or we can just run JS
        # Wait, perform_action for 'type' needs 'value' kwarg. But let's use page.keyboard.type for cinematic typing.
        print("⌨️ Typing out a task...")
        await manager.page.keyboard.type("Automate lead generation", delay=100)
        await manager.page.keyboard.press("Enter")
        await asyncio.sleep(1)
        
        await manager.page.keyboard.type("Launch Phantom MCP", delay=100)
        await manager.page.keyboard.press("Enter")
        await asyncio.sleep(1)
        
        # Re-map the DOM to find the new checkboxes
        dom = await manager.map_dom()
        elements = dom.get("data", [])
        
        # Find the checkbox for the first task
        checkbox = next((el for el in elements if el.get("tagName") == "INPUT" and el.get("attributes", {}).get("type") == "checkbox"), None)
        
        if checkbox:
            print(f"🖱️ Tracking mouse to Checkbox [{checkbox['id']}]...")
            await manager.perform_action(checkbox["id"], "hover")
            await asyncio.sleep(0.5)
            
            print("💥 Clicking Checkbox to complete task...")
            await manager.perform_action(checkbox["id"], "click")
            await asyncio.sleep(1.5)
            
    # Get the final video path before closing
    video_path = await manager.get_video_path()
    
    print("\n✅ Demo Complete!")
    print(f"🎥 YOUR LINKEDIN VIDEO IS READY AT:\n{video_path}")
    print("\n💡 NOTE: To view the video, open this .webm file in Chrome or double-click it in your file explorer!")
    
    await manager.close()

if __name__ == "__main__":
    asyncio.run(run_linkedin_demo())
