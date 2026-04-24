import asyncio
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')

from engine.src.ghost_browser import GhostBrowserManager

async def test_coffee():
    print("[RIPPER] Booting Phantom Engine for coffee-tech.com...")
    engine = GhostBrowserManager()
    await engine.initialize()
    
    url = "https://www.coffee-tech.com/"
    print(f"[NAV] Navigating to {url}...")
    result = await engine.navigate(url)
    print(f"[NAV] {result}")
    
    print("[WAIT] Waiting 15 seconds for 3D scene to load...")
    await asyncio.sleep(15)
    print(f"  Models found after initial load: {len(engine.ripped_models)}")
    
    # Deep scroll
    print("[SCROLL] Deep scrolling entire page...")
    page_height = await engine.page.evaluate("document.body.scrollHeight")
    print(f"  Page height: {page_height}px")
    
    scroll_pos = 0
    step = 400
    pass_num = 0
    while scroll_pos < page_height:
        scroll_pos += step
        await engine.page.evaluate(f"window.scrollTo(0, {scroll_pos})")
        await asyncio.sleep(1.5)
        pass_num += 1
        if pass_num % 5 == 0:
            print(f"  Scroll pass {pass_num} ({scroll_pos}px / {page_height}px) - Models: {len(engine.ripped_models)}")
    
    print("[WAIT] At bottom, waiting 8s for final assets...")
    await asyncio.sleep(8)
    
    # Scroll back to top
    await engine.page.evaluate("window.scrollTo(0, 0)")
    await asyncio.sleep(5)
    
    models = engine.ripped_models
    print("\n" + "=" * 50)
    print(f"  RESULT: Ripped {len(models)} assets!")
    print("=" * 50)
    for i, m in enumerate(models):
        size_kb = m['size'] / 1024
        atype = m.get('type', 'unknown')
        print(f"  [{i+1}] [{atype:>10}] {os.path.basename(m['file'])} ({size_kb:.1f} KB)")
        print(f"      Source: {m['url'][:150]}")
    
    # Scan for hidden assets
    print(f"\n[NETWORK] Scanning {len(engine.network_log)} requests for hidden 3D assets...")
    three_d_hints = [req for req in engine.network_log if any(
        kw in req['url'].lower() for kw in [
            'model', '3d', 'glb', 'gltf', 'spline', 'three', 'webgl',
            '.bin', 'scene', 'mesh', 'splat', 'draco', 'ktx', 'basis',
            'texture', 'environment', 'hdri', '.hdr', '.exr',
            'gaussian', 'ply', 'usdz', 'fbx', 'obj'
        ]
    )]
    if three_d_hints:
        print(f"  Found {len(three_d_hints)} 3D-related network requests:")
        for h in three_d_hints[:30]:
            print(f"    [{h['status']}] {h['type']:>10} | {h['url'][:120]}")
    
    print(f"\n[INFO] Models directory: {engine.models_dir}")
    
    await engine.close()
    print("[DONE] Engine shut down.")

if __name__ == "__main__":
    asyncio.run(test_coffee())
