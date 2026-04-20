import os
import base64
import json
from datetime import datetime
from typing import Dict, Any, List

class GhostReporter:
    """
    Phantom Forensic Reporter: Generates standalone, high-end HTML and PDF audit reports 
    based on Site-Ghost visual forensics and performance data.
    """
    
    def __init__(self, reports_dir: str):
        self.reports_dir = reports_dir
        os.makedirs(self.reports_dir, exist_ok=True)
        
    def _to_base64(self, file_path: str) -> str:
        """Converts an image file to a base64 string for embedding."""
        if not file_path or not os.path.exists(file_path):
            return ""
        try:
            with open(file_path, "rb") as image_file:
                encoded_string = base64.b64encode(image_file.read()).decode("utf-8")
                ext = file_path.split(".")[-1]
                return f"data:image/{ext};base64,{encoded_string}"
        except Exception:
            return ""

    def generate_single_report(self, data: Dict[str, Any], title: str = "Site Audit", client: str = "Internal") -> str:
        """Generates a professional, multi-page audit report for a single website."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        file_name = f"audit_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
        file_path = os.path.join(self.reports_dir, file_name)
        
        # Prepare visuals
        hero_b64 = self._to_base64(data.get("hero_screenshot"))
        
        # Semantic Score calculation
        sem = data['structure'].get('semantic_tags', {})
        sem_score = min(100, (sum(sem.values()) * 15))
        
        # AI Readiness Score
        ai = data.get('ai_readiness', {})
        ai_score = (40 if ai.get('llms_txt') else 0) + (len(ai.get('robots_ai_rules', [])) * 20)
        ai_score = min(100, ai_score)

        # Mixed Content logic
        mixed = data['structure'].get('mixed_content', [])
        security_status = "CRITICAL" if mixed else "SECURE"
        security_color = "var(--primary)" if mixed else "var(--secondary)"

        html_template = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ForgeX Forensic Audit | {title}</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;800&family=JetBrains+Mono&display=swap" rel="stylesheet">
    <style>
        :root {{
            --bg: #050505;
            --surface: #111111;
            --primary: #FF0055;
            --secondary: #00FFCC;
            --text-main: #FFFFFF;
            --text-dim: #BBBBBB;
            --border: #222222;
        }}
        
        @page {{ size: A4; margin: 0; }}
        * {{ margin: 0; padding: 0; box-sizing: border-box; -webkit-print-color-adjust: exact; }}
        
        body {{ 
            background: var(--bg); 
            color: var(--text-main); 
            font-family: 'Inter', sans-serif; 
            line-height: 1.6;
        }}
        
        /* ── COVER PAGE ── */
        .page-cover {{
            height: 100vh;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            text-align: center;
            background: radial-gradient(circle at center, #1a000a 0%, #050505 100%);
            position: relative;
            page-break-after: always;
        }}
        
        .cover-logo {{ font-size: 80px; font-weight: 800; letter-spacing: -3px; margin-bottom: 10px; }}
        .cover-logo span {{ color: var(--primary); }}
        .cover-subtitle {{ font-size: 14px; letter-spacing: 12px; color: var(--text-dim); text-transform: uppercase; margin-bottom: 80px; }}
        
        .cover-details {{ border-top: 1px solid var(--border); padding-top: 40px; text-align: left; width: 400px; }}
        .cover-details p {{ font-size: 13px; margin-bottom: 8px; color: var(--text-dim); }}
        .cover-details b {{ color: var(--text-main); text-transform: uppercase; width: 120px; display: inline-block; }}

        /* ── CONTENT PAGES ── */
        .page {{ 
            min-height: 100vh; 
            padding: 60px 50px; 
            position: relative;
            page-break-after: always;
        }}
        
        header {{
            display: flex;
            justify-content: space-between;
            align-items: flex-end;
            border-bottom: 2px solid var(--primary);
            padding-bottom: 20px;
            margin-bottom: 40px;
        }}
        
        .logo-small {{ font-size: 24px; font-weight: 800; }}
        .logo-small span {{ color: var(--primary); }}
        
        .section-title {{ font-size: 12px; letter-spacing: 3px; color: var(--primary); font-weight: 800; text-transform: uppercase; margin-bottom: 20px; }}
        
        .hero {{ 
            background: var(--surface);
            border: 1px solid var(--border);
            border-radius: 12px;
            overflow: hidden;
            margin-bottom: 30px;
        }}
        .hero img {{ width: 100%; display: block; }}
        
        .grid {{ display: grid; grid-template-columns: repeat(2, 1fr); gap: 20px; margin-bottom: 40px; }}
        .card {{ 
            background: var(--surface); 
            border: 1px solid var(--border); 
            border-radius: 8px; 
            padding: 24px;
        }}
        .card h3 {{ font-size: 12px; text-transform: uppercase; letter-spacing: 1px; color: var(--text-dim); margin-bottom: 15px; }}
        
        .metric {{ font-size: 28px; font-weight: 600; color: var(--secondary); }}
        .metric-label {{ font-size: 11px; color: var(--text-dim); text-transform: uppercase; }}
        
        .score-bar {{ height: 4px; background: #222; border-radius: 2px; margin-top: 10px; position: relative; }}
        .score-fill {{ height: 100%; background: var(--secondary); border-radius: 2px; transition: width 1s; }}
        
        .tech-tag {{ 
            display: inline-block; background: #222; padding: 4px 10px; 
            border-radius: 4px; font-size: 11px; font-family: 'JetBrains Mono', monospace;
            margin-right: 5px; margin-bottom: 5px; color: var(--secondary);
        }}
        
        .hierarchy-list {{ list-style: none; font-family: 'JetBrains Mono', monospace; font-size: 11px; }}
        .hierarchy-item {{ padding: 6px 0; border-bottom: 1px solid #1a1a1a; display: flex; }}
        .h-tag {{ color: var(--primary); width: 40px; font-weight: bold; flex-shrink: 0; }}
        
        .security-flag {{ color: {security_color}; font-weight: bold; font-family: 'JetBrains Mono'; }}
        
        footer {{
            position: absolute; bottom: 30px; left: 50px; right: 50px;
            border-top: 1px solid var(--border); padding-top: 15px;
            display: flex; justify-content: space-between; font-size: 10px; color: var(--text-dim);
            letter-spacing: 1px;
        }}
        footer b {{ color: var(--primary); }}
    </style>
</head>
<body>

    <!-- PAGE 1: COVER -->
    <div class="page-cover">
        <div class="cover-logo">PHANTOM<span>.</span></div>
        <div class="cover-subtitle">Visual Forensic Engine</div>
        
        <div class="cover-details">
            <p><b>Project</b> {title}</p>
            <p><b>Client</b> {client}</p>
            <p><b>URL</b> {data.get('url')}</p>
            <p><b>Date</b> {timestamp}</p>
            <p><b>Status</b> Audit Finalized</p>
            <p><b>Agency</b> ForgeX Solutions</p>
        </div>
    </div>

    <!-- PAGE 2: EXECUTIVE SUMMARY -->
    <div class="page">
        <header>
            <div class="logo-small">PHANTOM<span>.</span></div>
            <div style="text-align: right; font-size: 12px; color: var(--text-dim);">EXEC SUMMARY // PAGE 02</div>
        </header>
        
        <div class="section-title">Visual Context // Hero Frame</div>
        <div class="hero">
            <img src="{hero_b64}" alt="Hero Screenshot">
        </div>
        
        <div class="grid">
            <div class="card">
                <h3>Vitals & Latency</h3>
                <div style="display: flex; gap: 40px; margin-bottom: 20px;">
                    <div><p class="metric">{data['performance'].get('domContentLoaded', 0)}ms</p><p class="metric-label">DOM Ready</p></div>
                    <div><p class="metric">{data['performance'].get('fullLoad', 0)}ms</p><p class="metric-label">Full Load</p></div>
                </div>
                <div>
                     <p class="metric" style="color: {(data['performance'].get('firstContentfulPaint', 0) or 0) > 2000 and 'var(--primary)' or 'var(--secondary)'}">
                        {data['performance'].get('firstContentfulPaint', 0)}ms
                     </p>
                     <p class="metric-label">FCP (Visual Snap)</p>
                </div>
            </div>
            
            <div class="card">
                <h3>Technical IQ</h3>
                <div style="margin-bottom: 20px;">
                    {" ".join([f'<span class="tech-tag">{t}</span>' for t in data['tech'].get('frameworks', [])])}
                </div>
                <div style="margin-bottom: 12px;">
                    <p class="metric-label">Semantic Integrity: {sem_score}%</p>
                    <div class="score-bar"><div class="score-fill" style="width: {sem_score}%"></div></div>
                </div>
                <div>
                    <p class="metric-label">AI Agent Readiness: {ai_score}%</p>
                    <div class="score-bar"><div class="score-fill" style="width: {ai_score}%"></div></div>
                </div>
            </div>
        </div>
        
        <div class="card">
            <h3>Audit Overview</h3>
            <p style="font-size: 14px; color: var(--text-dim);">
                Technical audit complete for <b>{data.get('url')}</b>. The machine scanner identified <b>{data.get('element_count', 0)}</b> physical interaction points. 
                Security posture is currently marked as <span class="security-flag">{security_status}</span>.
            </p>
        </div>

        <footer>
            <div>© 2026 FORGEX // PHANTOM FORENSIC SYSTEM</div>
            <div>STRICTLY CONFIDENTIAL</div>
        </footer>
    </div>

    <!-- PAGE 3: TECHNICAL DEEP DIVE -->
    <div class="page" style="page-break-after: auto;">
        <header>
            <div class="logo-small">PHANTOM<span>.</span></div>
            <div style="text-align: right; font-size: 12px; color: var(--text-dim);">TECHNICAL FORENSICS // PAGE 03</div>
        </header>

        <div class="grid">
            <div class="card">
                <h3>AI AGENT GOVERNANCE</h3>
                <p class="hierarchy-item"><span class="h-tag">READ</span> llms.txt: {data['ai_readiness'].get('llms_txt') and 'PRESENT' or 'MISSING'}</p>
                <p class="hierarchy-item"><span class="h-tag">BOTS</span> Allowed: {", ".join(data['ai_readiness'].get('robots_ai_rules', [])) or 'None'}</p>
                <p style="font-size: 11px; margin-top: 10px; color: var(--text-dim);">Scanning for machine-readable directives and generative-AI crawler permissions.</p>
            </div>
            <div class="card">
                <h3>SECURITY & HEALTH</h3>
                <p class="hierarchy-item"><span class="h-tag">ERR</span> Console Warnings: {data['console_errors']}</p>
                <p class="hierarchy-item"><span class="h-tag">NET</span> Failed Requests: {data['failed_requests']}</p>
                <div style="margin-top: 10px;">
                    <p class="metric-label" style="margin-bottom: 5px;">Mixed Content Detected:</p>
                    { "".join([f'<p style="font-family: monospace; font-size: 10px; color: var(--primary);">{m}</p>' for m in mixed]) or '<p style="font-size: 10px; color: var(--secondary);">NONE - ALL ASSETS SECURE</p>' }
                </div>
            </div>
        </div>

        <div class="card">
            <h3>Semantic Hierarchy Map</h3>
            <ul class="hierarchy-list">
                {"".join([f'<li class="hierarchy-item"><span class="h-tag">H{h["level"]}</span> {h["text"]}</li>' for h in data['structure'].get('headings', [])[:15]])}
            </ul>
        </div>
        
        <div style="margin-top: 20px; display: flex; gap: 20px;">
            <div class="card" style="flex: 1;">
                <h3>Semantic Tags</h3>
                <div style="font-size: 11px;">
                    { "".join([f'<span class="tech-tag" style="color: var(--text-dim)">{tag.upper()}: {count}</span>' for tag, count in data['structure'].get('semantic_tags', {}).items() if count > 0]) }
                </div>
            </div>
        </div>

        <footer>
            <div>GENERATED BY PHANTOM // FOUNDER @ FORGEX</div>
            <div>VERIFIED ARCHITECTURE</div>
        </footer>
    </div>

</body>
</html>
        """
        
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(html_template)
            
        return file_path

    def generate_compare_report(self, data: Dict[str, Any], title: str = "Competitor Audit", client: str = "Internal") -> str:
        """Generates a side-by-side comparison report for two websites (Standard Single Page for now)."""
        # I'll keep the comparison report as a high-end single page for better visual 'Diff' tracking
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        file_name = f"compare_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
        file_path = os.path.join(self.reports_dir, file_name)
        
        a = data["comparisons"]["site_a"]
        b = data["comparisons"]["site_b"]
        
        hero_a = self._to_base64(a.get("hero_screenshot"))
        hero_b = self._to_base64(b.get("hero_screenshot"))
        
        diff_rows = ""
        for d in data.get("diff", []):
            winner_a = "winner" if d.get("winner") == "A" else ""
            winner_b = "winner" if d.get("winner") == "B" else ""
            diff_rows += f"""
                <tr>
                    <td>{d['metric']}</td>
                    <td class="{winner_a}">{d['site_a']}</td>
                    <td class="{winner_b}">{d['site_b']}</td>
                </tr>
            """

        html_template = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ForgeX | {title}</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;800&family=JetBrains+Mono&display=swap" rel="stylesheet">
    <style>
        :root {{
            --bg: #050505;
            --surface: #111111;
            --primary: #FF0055;
            --secondary: #00FFCC;
            --text-main: #FFFFFF;
            --text-dim: #BBBBBB;
            --border: #222222;
        }}
        @page {{ size: A4 landscape; margin: 0; }}
        * {{ margin: 0; padding: 0; box-sizing: border-box; -webkit-print-color-adjust: exact; }}
        body {{ background: var(--bg); color: var(--text-main); font-family: 'Inter', sans-serif; padding: 40px; }}
        
        header {{ display: flex; justify-content: space-between; align-items: flex-end; border-bottom: 2px solid var(--primary); padding-bottom: 20px; margin-bottom: 40px; }}
        .logo-area h1 {{ font-size: 32px; font-weight: 800; }}
        .logo-area span {{ color: var(--primary); }}
        
        .comparison-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 40px; margin-bottom: 40px; }}
        .site-card {{ background: var(--surface); border: 1px solid var(--border); border-radius: 12px; overflow: hidden; }}
        .site-card img {{ width: 100%; height: 280px; object-fit: cover; border-bottom: 1px solid var(--border); }}
        .site-info {{ padding: 20px; }}
        .site-info h2 {{ font-size: 18px; margin-bottom: 5px; color: var(--secondary); }}
        
        table {{ width: 100%; border-collapse: collapse; background: var(--surface); border-radius: 8px; overflow: hidden; }}
        th, td {{ padding: 12px 15px; text-align: left; border-bottom: 1px solid var(--border); font-size: 13px; }}
        th {{ background: #1a1a1a; text-transform: uppercase; font-size: 10px; letter-spacing: 1px; color: var(--text-dim); }}
        td {{ font-family: 'JetBrains Mono', monospace; }}
        
        .winner {{ color: var(--secondary); font-weight: bold; background: rgba(0, 255, 204, 0.05); }}
        
        footer {{ margin-top: 40px; border-top: 1px solid var(--border); padding-top: 15px; text-align: center; font-size: 10px; color: var(--text-dim); }}
        footer b {{ color: var(--primary); }}
    </style>
</head>
<body>

    <header>
        <div class="logo-area">
            <h1>PHANTOM<span>.</span></h1>
            <p>COMPETITIVE FORENSIC DIFF</p>
        </div>
        <div class="meta-area" style="text-align: right; font-size: 12px;">
            <p><b>CLIENT:</b> {client}</p>
            <p><b>DATE:</b> {timestamp}</p>
        </div>
    </header>

    <div class="comparison-grid">
        <div class="site-card">
            <img src="{hero_a}" alt="Site A">
            <div class="site-info">
                <h2>SITE A: {a['url']}</h2>
            </div>
        </div>
        <div class="site-card">
            <img src="{hero_b}" alt="Site B">
            <div class="site-info">
                <h2>SITE B: {b['url']}</h2>
            </div>
        </div>
    </div>

    <table>
        <thead>
            <tr>
                <th>Metric</th>
                <th>Site A Result</th>
                <th>Site B Result</th>
            </tr>
        </thead>
        <tbody>
            {diff_rows}
        </tbody>
    </table>

    <footer>
        Generated by <b>Phantom MCP</b> | Powered by <b>ForgeX</b> | <a href="https://forgexdev.online" style="color: var(--text-dim); text-decoration: none;">forgexdev.online</a>
    </footer>

</body>
</html>
        """
        
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(html_template)
            
        return file_path
