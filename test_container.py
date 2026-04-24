import asyncio
from engine.src.ghost_browser import GhostBrowserManager

async def test_container():
    print("🚀 Booting GhostBrowserManager in Container Mode...")
    manager = GhostBrowserManager()
    await manager.initialize()
    
    url = "https://string-tune.fiddle.digital/"
    print(f"🌐 Navigating to: {url}")
    await manager.navigate(url)
    
    print("⏳ Waiting for animations to settle...")
    await asyncio.sleep(15)
    
    print("🔥 Building .ghost Container...")
    result = await manager.steal_container("fiddle")
    
    print("\n==================================================")
    print("RESULT:")
    print(result)
    print("==================================================\n")
    await manager.close()

if __name__ == "__main__":
    asyncio.run(test_container())
