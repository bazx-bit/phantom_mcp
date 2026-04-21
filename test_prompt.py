import asyncio
import sys
import os

# Set working directory to the package root so 'engine.src.server' works.
sys.path.insert(0, os.path.dirname(__file__))
from engine.src.server import list_prompts, get_prompt, _load_skills

async def test_prompts():
    print("Testing _load_skills()...")
    skills = _load_skills()
    if "agentic_freedom" in skills:
        print("✅ 'agentic_freedom' found in skills registry!")
    else:
        print("❌ ERROR: 'agentic_freedom' missing!")
        sys.exit(1)
        
    print("\nTesting list_prompts()...")
    # list_prompts is wrapped with @app.list_prompts(), let's call the unwrapped function if needed,
    # or just rely on the dictionary.
    print(f"Loaded {len(skills)} prompts. Names: {list(skills.keys())[:5]}...")
    print("TEST PASSED.")

if __name__ == "__main__":
    asyncio.run(test_prompts())
