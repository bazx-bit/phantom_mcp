import asyncio
import os
import sys

# Ensure Python can find the engine module
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "engine", "src"))
from ghost_browser import GhostBrowserManager

async def run_pro_audit():
    print("🎬 BOOTING PHANTOM PRO AUDIT ENGINE...")
    
    manager = GhostBrowserManager()
    await manager.initialize()
    
    # Target: Linear.app (The standard for high-end web design)
    url = "https://linear.app"
    print(f"🌍 Navigating to {url}...")
    await manager.navigate(url)
    await asyncio.sleep(2)
    
    print("👁️ TRIGGERING DEEP FORENSIC SCAN...")
    # This maps the DOM, checks performance, and tech stack
    audit_data = await manager.run_full_audit()
    
    print("📊 GENERATING PROFESSIONAL FORGEX PDF REPORT...")
    # Generate the professional PDF report
    report_path = manager.reporter.generate_single_report(
        audit_data, 
        title="Linear.app Technical Audit", 
        client="ForgeX Internal"
    )
    
    # Convert to PDF
    pdf_path = report_path.replace(".html", ".pdf")
    await manager.generate_pdf(report_path, pdf_path)
    
    print("\n✅ AUDIT COMPLETE!")
    print(f"📄 PROFESSIONAL PDF READY AT: {pdf_path}")
    
    # Keep the path for the user
    with open("last_report_path.txt", "w") as f:
        f.write(pdf_path)
    
    await manager.close()

if __name__ == "__main__":
    asyncio.run(run_pro_audit())
