import asyncio
import os
from engine.src.ghost_browser import GhostBrowserManager

async def clone_daofor():
    print("🚀 Initializing GhostBrowserManager...")
    manager = GhostBrowserManager()
    await manager.initialize()
    
    url = "https://www.daofor.design/"
    print(f"🌐 Navigating to: {url}")
    await manager.navigate(url)
    
    # Wait for the site to fully load its animations
    print("⏳ Waiting 12 seconds for WebGL and JS animations to settle...")
    await asyncio.sleep(12)
    
    # Scroll down to trigger any lazy loading
    print("📜 Scrolling down to trigger lazy loading...")
    await manager.page.evaluate('window.scrollTo(0, document.body.scrollHeight/2)')
    await asyncio.sleep(2)
    await manager.page.evaluate('window.scrollTo(0, document.body.scrollHeight)')
    await asyncio.sleep(2)
    await manager.page.evaluate('window.scrollTo(0, 0)')
    await asyncio.sleep(2)
    
    print("🔥 Executing extraction...")
    
    # 1. Capture Static HTML (CSS inlined, relative URLs absolutized)
    stealer_js = """
    (async () => {
        const toAbs = (url) => {
            try { return new URL(url, document.baseURI).href; }
            catch(e) { return url; }
        };
        let allCSS = '';
        for (const sheet of Array.from(document.styleSheets)) {
            try {
                for (const rule of Array.from(sheet.cssRules)) {
                    allCSS += rule.cssText + '\\n';
                }
            } catch(e) {}
        }
        document.querySelectorAll('[src]').forEach(el => el.src = toAbs(el.getAttribute('src')));
        document.querySelectorAll('[href]').forEach(el => el.href = toAbs(el.getAttribute('href')));
        
        return {
            title: document.title,
            head: document.head.innerHTML,
            body: document.body.innerHTML,
            css: allCSS
        };
    })()
    """
    data = await manager.page.evaluate(stealer_js)
    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    {data.get('head', '')}
    <style>{data.get('css', '')}</style>
    <style>/* Forced visibility for ripped clones */ body {{ opacity: 1 !important; visibility: visible !important; display: block !important; }}</style>
</head>
<body>
    {data.get('body', '')}
</body>
</html>"""

    html_path = os.path.join(manager.clones_dir, "daofor_perfect_clone.html")
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html_content)
    print(f"✅ STATIC HTML CLONE SAVED: {html_path} ({os.path.getsize(html_path) / 1024:.1f} KB)")

    # 2. Capture MHTML Web Archive (Fully Interactive)
    try:
        client = await manager.page.context.new_cdp_session(manager.page)
        snapshot = await client.send('Page.captureSnapshot', {'format': 'mhtml'})
        mhtml_path = os.path.join(manager.clones_dir, "daofor_perfect_archive.mhtml")
        with open(mhtml_path, "w", encoding="utf-8") as f:
            f.write(snapshot['data'])
        print(f"✅ INTERACTIVE MHTML ARCHIVE SAVED: {mhtml_path} ({os.path.getsize(mhtml_path) / 1024:.1f} KB)")
    except Exception as e:
        print(f"⚠️ MHTML Archive failed: {e}")

    await manager.close()

if __name__ == "__main__":
    asyncio.run(clone_daofor())
