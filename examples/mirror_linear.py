import asyncio
import os
import sys
import json

# Ensure Python can find the engine module
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "engine", "src"))
from ghost_browser import GhostBrowserManager

async def run_linear_mirror():
    print("🎬 TRIGGERING PHANTOM MIRROR ORCHESTRATOR...")
    
    manager = GhostBrowserManager()
    await manager.initialize()
    
    target_url = "https://linear.app"
    print(f"🌍 Navigating to {target_url} to capture soul...")
    await manager.navigate(target_url)
    await asyncio.sleep(2)
    
    print("🧠 DECONSTRUCTING DESIGN SYSTEM (Obsidian Filter)...")
    decon_data = await manager.deconstruct_ui()
    
    # Extract specific linear colors
    bg_main = decon_data['palette']['background'][0] if decon_data['palette']['background'] else "#08090a"
    accent = "#5e6ad2" # Linear's signature purple
    text_main = decon_data['palette']['text'][0] if decon_data['palette']['text'] else "#f7f8f8"
    
    print("💎 RE-MATERIALIZING UI CLONE (Standalone HTML)...")
    
    # Define the Mirror Template (ForgeX Standard)
    clone_html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Phantom Mirror | Linear.app Clone</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap" rel="stylesheet">
    <style>
        :root {{
            --bg: {bg_main};
            --accent: {accent};
            --text: {text_main};
            --grid: rgba(255, 255, 255, 0.05);
        }}
        
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        
        body {{ 
            background: var(--bg); 
            color: var(--text); 
            font-family: 'Inter', sans-serif; 
            overflow-x: hidden;
            height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
        }}

        /* ── THE OBSIDIAN GRID ── */
        .grid-overlay {{
            position: fixed;
            top: 0; left: 0; width: 100%; height: 100%;
            background-image: 
                linear-gradient(var(--grid) 1px, transparent 1px),
                linear-gradient(90deg, var(--grid) 1px, transparent 1px);
            background-size: 40px 40px;
            z-index: -1;
            pointer-events: none;
        }}

        /* ── THE MOUSE GLOW ── */
        .glow {{
            position: fixed;
            width: 600px;
            height: 600px;
            background: radial-gradient(circle, rgba(94, 106, 210, 0.15) 0%, transparent 70%);
            border-radius: 50%;
            transform: translate(-50%, -50%);
            pointer-events: none;
            z-index: 0;
            filter: blur(40px);
            transition: opacity 0.3s;
        }}

        /* ── UI COMPONENTS ── */
        .hero {{
            text-align: center;
            z-index: 10;
            padding: 0 20px;
            max-width: 900px;
            animation: fadeInUp 1s ease-out;
        }}

        .badge {{
            display: inline-block;
            background: rgba(255, 255, 255, 0.05);
            border: 1px solid rgba(255, 255, 255, 0.1);
            padding: 6px 14px;
            border-radius: 100px;
            font-size: 13px;
            color: var(--text);
            margin-bottom: 30px;
            font-weight: 500;
            letter-spacing: 0.5px;
        }}

        h1 {{
            font-size: 80px;
            font-weight: 800;
            line-height: 1.1;
            letter-spacing: -3px;
            background: linear-gradient(180deg, #FFFFFF 0%, rgba(255,255,255,0.4) 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 24px;
        }}

        p {{
            font-size: 20px;
            color: #8a8f98;
            max-width: 600px;
            margin: 0 auto 40px;
            line-height: 1.5;
        }}

        .cta {{
            background: var(--accent);
            color: white;
            padding: 14px 28px;
            border-radius: 8px;
            font-weight: 600;
            text-decoration: none;
            display: inline-block;
            box-shadow: 0 10px 20px rgba(94, 106, 210, 0.3);
            transition: transform 0.2s, box-shadow 0.2s;
        }}
        .cta:hover {{
            transform: translateY(-2px);
            box-shadow: 0 15px 30px rgba(94, 106, 210, 0.5);
        }}

        @keyframes fadeInUp {{
            from {{ opacity: 0; transform: translateY(30px); }}
            to {{ opacity: 1; transform: translateY(0); }}
        }}
    </style>
</head>
<body>
    <div class="grid-overlay"></div>
    <div class="glow" id="mouse-glow"></div>

    <div class="hero">
        <div class="badge">Building for the next era of development</div>
        <h1>Linear is a better way<br>to build products</h1>
        <p>Meet the new standard for modern software development. Streamline issues, projects, and product roadmaps.</p>
        <a href="#" class="cta">Get started</a>
    </div>

    <script>
        const glow = document.getElementById('mouse-glow');
        window.addEventListener('mousemove', (e) => {{
            glow.style.left = e.clientX + 'px';
            glow.style.top = e.clientY + 'px';
        }});
    </script>
</body>
</html>
    """
    
    # Save the clone
    output_path = os.path.join(os.getcwd(), '.ghost', 'clones', 'linear_clone.html')
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(clone_html)
        
    print(f"\n✅ MIRROR CLONE COMPLETE!")
    print(f"📄 STANDALONE CLONE READY AT: {output_path}")
    
    await manager.close()

if __name__ == "__main__":
    asyncio.run(run_linear_mirror())
