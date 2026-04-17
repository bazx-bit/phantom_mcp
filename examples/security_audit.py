"""
Security Audit Example — Site-Ghost
Demonstrates the security scanner workflow: finding exposed secrets,
checking cookie flags, and identifying mixed content.
"""
import asyncio
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "engine", "src"))
from ghost_browser import GhostBrowserManager

async def run_security_audit(url):
    manager = GhostBrowserManager()
    await manager.initialize()
    
    print(f"🕵️  Site-Ghost Security Audit: {url}")
    print("=" * 60)

    # 1. Navigation
    await manager.navigate(url)
    
    # 2. Tech Stack & Cookie Check
    cookies = await manager.get_cookies()
    print(f"[+] Cookies discovered: {len(cookies)}")
    insecure_cookies = [c for c in cookies if not c.get('secure')]
    if insecure_cookies:
        print(f"  ⚠️  WARNING: {len(insecure_cookies)} cookies are missing the 'Secure' flag.")

    # 3. Mixed Content Check
    net_log = await manager.get_network_log()
    mixed_content = [r for r in net_log if r['url'].startswith('http://')]
    if mixed_content:
        print(f"  🚨 CRITICAL: {len(mixed_content)} mixed content (HTTP) requests found.")
        for r in mixed_content[:5]:
            print(f"    - {r['url']}")
    else:
        print("  ✅ No mixed content (HTTP) detected.")

    # 4. Secret Exposure Check (Common .env or secret patterns in DOM)
    js_check = """
    (function() {
        const patterns = [/API_KEY/i, /SECRET/i, /PASSWORD/i, /sk-[a-zA-Z0-9]{20,}/];
        const bodyText = document.body.innerText;
        let found = [];
        patterns.forEach(p => {
            if (p.test(bodyText)) found.push(p.toString());
        });
        return found;
    })()
    """
    secrets = await manager.execute_js(js_check)
    if secrets:
        print(f"  🚨 SECURITY RISK: Possible secrets found in DOM: {secrets}")
    else:
        print("  ✅ No common secret patterns found in DOM.")

    # 5. CSP Check
    csp_check = "document.querySelector('meta[http-equiv=\"Content-Security-Policy\"]') ? true : false"
    has_csp = await manager.execute_js(csp_check)
    if has_csp:
        print("  ✅ Content Security Policy meta tag found.")
    else:
        print("  ⚠️  WARNING: No CSP meta tag detected.")

    await manager.take_screenshot("security_audit_report")
    await manager.close()
    print("=" * 60)
    print("Audit Complete. See .ghost/screenshots/security_audit_report.png")

if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else "https://example.com"
    asyncio.run(run_security_audit(target))
