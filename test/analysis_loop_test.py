import asyncio
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "engine", "src"))
from ghost_browser import GhostBrowserManager

async def test_analysis_loop():
    manager = GhostBrowserManager()
    
    print("=" * 70)
    print("👻 PHANTOM MCP — FRAME-BY-FRAME ANALYSIS LOOP TEST")
    print("   Target: https://labs.chaingpt.org/")
    print("=" * 70)

    await manager.initialize()

    # ── Step 1: Navigate ──
    print("\n[1] Navigating...")
    result = await manager.navigate("https://labs.chaingpt.org/")
    print(f"    {result}")

    # ── Step 2: Cinematic Scroll with Context ──
    print("\n[2] 🎬 Cinematic Scan (with JSON context per frame)...")
    result = await manager.cinematic_scroll(step_px=400, pause_ms=600)
    
    if result["status"] == "error":
        print(f"    ❌ {result['message']}")
        await manager.close()
        return

    print(f"    ✅ {result['message']}")
    print(f"    Page Height: {result['page_height']}px")
    print(f"    Frames captured: {result['frame_count']}")

    # ── Step 3: Verify JSON Context Files ──
    print("\n[3] Verifying JSON context files...")
    for i, frame in enumerate(result["frames"][:3]):  # Check first 3
        json_path = frame["context"]
        if os.path.exists(json_path):
            with open(json_path, "r") as f:
                ctx = json.load(f)
            print(f"\n    --- Frame {i} ---")
            print(f"    Scroll: {ctx['scroll_y']}px ({ctx['scroll_percent']}%)")
            print(f"    Visible Elements: {ctx['visible_element_count']}")
            print(f"    Active Animations: {len(ctx.get('active_animations', []))}")
            print(f"    Console Errors: {ctx['console_error_count']}")
            # Show first 3 visible elements
            for el in ctx["visible_elements"][:3]:
                tag = el["tag"]
                txt = el.get("text", "")[:40]
                print(f"      [{tag}] \"{txt}\"")
        else:
            print(f"    ❌ Missing JSON for frame {i}")

    # ── Step 4: Show the AI Analysis Protocol ──
    print("\n[4] 📋 FRAME MANIFEST:")
    for frame in result["frames"]:
        s = frame["summary"]
        flag = "🔴" if s["errors"] > 0 else ("🌀" if s["animations"] > 0 else "✅")
        print(f"    {flag} Frame {s['frame']:>2d} | {s['scroll_percent']:>5.1f}% | {s['elements']:>2d} elems | {s['animations']} anims | {s['errors']} errors")

    # ── Step 5: Simulate AI Loop ──
    print("\n[5] 🧠 SIMULATING AI ANALYSIS LOOP:")
    print("    (In production, the AI calls ghost_frame_context(N) for each frame)")
    for i, frame in enumerate(result["frames"]):
        json_path = frame["context"]
        with open(json_path, "r") as f:
            ctx = json.load(f)
        headings = [el["text"][:50] for el in ctx["visible_elements"] if el["tag"] in ("H1", "H2", "H3") and el.get("text")]
        section = headings[0] if headings else "(no heading visible)"
        issues = []
        if ctx["console_error_count"] > 0:
            issues.append(f"{ctx['console_error_count']} JS errors")
        if len(ctx.get("active_animations", [])) > 5:
            issues.append("heavy animation load")
        status = " | ".join(issues) if issues else "clean"
        print(f"    Frame {i:>2d} → Section: \"{section}\" → [{status}]")

    await manager.close()

    print("\n" + "=" * 70)
    print("🎉 ANALYSIS LOOP TEST COMPLETE — ALL SYSTEMS GO")
    print("=" * 70)

if __name__ == "__main__":
    asyncio.run(test_analysis_loop())
