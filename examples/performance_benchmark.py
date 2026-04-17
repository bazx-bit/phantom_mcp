"""
Performance Benchmark Example — Site-Ghost
Runs a speed comparison across multiple URLs and outputs a CSV-like summary.
"""
import asyncio
import os
import sys
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "engine", "src"))
from ghost_browser import GhostBrowserManager

async def benchmark_site(manager, url):
    print(f"  ⚡ Benchmarking {url}...")
    await manager.navigate(url)
    res = await manager.get_performance_metrics()
    if res["status"] == "success":
        return res["metrics"]
    return None

async def run_benchmark(urls):
    manager = GhostBrowserManager()
    await manager.initialize()
    
    print(f"📊 Site-Ghost Performance Benchmark: {len(urls)} sites")
    print("=" * 70)
    print(f"{'URL':<30} | {'FCP':<8} | {'Load':<8} | {'Resources':<8} | {'Size':<8}")
    print("-" * 70)

    results = []
    for url in urls:
        m = await benchmark_site(manager, url)
        if m:
            fcp = f"{m.get('firstContentfulPaint', 0)}ms"
            load = f"{m.get('fullLoad', 0)}ms"
            count = m.get('resourceCount', 0)
            size = f"{round(m.get('totalTransferSize', 0)/1024, 1)}KB"
            print(f"{url[:28]:<30} | {fcp:<8} | {load:<8} | {count:<8} | {size:<8}")
            results.append({"url": url, **m})
        else:
            print(f"{url[:28]:<30} | ERROR    | ERROR    | ERROR    | ERROR")

    await manager.close()
    print("=" * 70)
    print("Benchmark Complete.")

if __name__ == "__main__":
    targets = [
        "https://example.com",
        "https://google.com",
        "https://stripe.com",
        "https://github.com",
        "https://vercel.com"
    ]
    asyncio.run(run_benchmark(targets))
