import asyncio
import os
import sys
import json

# Ensure Python can find the engine module
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "engine", "src"))
from ghost_browser import GhostBrowserManager

async def run_ui_deconstruction():
    print("🎬 BOOTING PHANTOM UI/UX DECONSTRUCTOR...")
    
    manager = GhostBrowserManager()
    await manager.initialize()
    
    # Target: Linear.app (Excellent UI example)
    url = "https://linear.app"
    print(f"🌍 Navigating to {url}...")
    await manager.navigate(url)
    await asyncio.sleep(2)
    
    print("🧠 TRIGGERING DESIGN FORENSIC DECONSTRUCTION...")
    # This deconstructs the design system and layout
    decon_data = await manager.deconstruct_ui()
    
    print("\n═" * 60)
    print("🏛️ FOUNDATION ANALYSIS")
    print(f"  Design Style:    {decon_data['analysis']['design_intent']}")
    print(f"  Main Font:        {decon_data['analysis']['primary_font']}")
    print(f"  Primary Focus:    {decon_data['analysis']['ux_focus']}")
    
    print("\n🎨 BRAND PALETTE")
    print(f"  Backgrounds:      {', '.join(decon_data['palette']['background'])}")
    print(f"  Text Colors:      {', '.join(decon_data['palette']['text'])}")
    
    print("\n📐 ARCHITECTURAL PATTERNS")
    print(f"  Layout Mode:      {decon_data['analysis']['layout_complexity']}")
    print(f"  UI Components:    {', '.join(decon_data['discovered_components'])}")
    print("═" * 60)
    
    print("\n💡 AI INSIGHT:")
    print(f"  {decon_data['analysis']['architecture_summary']}")
    
    # Save the full deconstruction log for the user to see the 'Code Breakdown'
    log_path = os.path.join(os.getcwd(), '.ghost', 'reports', 'ui_deconstruction.json')
    os.makedirs(os.path.dirname(log_path), exist_ok=True)
    with open(log_path, "w") as f:
        json.dump(decon_data, f, indent=2)
        
    print(f"\n📂 FULL DECONSTRUCTION DATA SAVED: {log_path}")
    
    await manager.close()

if __name__ == "__main__":
    asyncio.run(run_ui_deconstruction())
