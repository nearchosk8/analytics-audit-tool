# HTML Report Exporter - generates a professional, shareable audit report
import os
from datetime import datetime
from config import SEVERITY

def export_report(ga4_results, gtm_results, datalayer_results, setup):
    """Generate a styled HTML report and save to file"""
    
    scores = {
        "GA4 Events": ga4_results.get("score", 0),
        "GTM Health": gtm_results.get("score", 0),
        "DataLayer": datalayer_results.get("score", 0)
    }
    overall = round(sum(scores.values()) / len(scores))
    
    # Determine score color
    if overall >= 70:
        score_color = "#22c55e"  # green
    elif overall >= 40:
        score_color = "#f59e0b"  # amber
    else:
        score_color = "#ef4444"  # red
    
    timestamp = datetime.now().strftime("%B %d, %Y at %H:%M")
    
    # Count findings by severity
    all_findings = (
        ga4_results.get("findings", []) + 
        gtm_results.get("findings", []) + 
        datalayer_results.get("findings", [])
    )
    severity_counts = {}
    for f in all_findings:
        sev = f.get("severity", "info")
        severity_counts[sev] = severity_counts.get(sev, 0) + 1
    
    # Build sections HTML
    sections_html = ""
    sections = [
        ("GA4 Event Coverage", "ga4", "#3b82f6", ga4_results),
        ("GTM Container Health", "gtm", "#f97316", gtm_results),
        ("DataLayer Quality", "datalayer", "#a855f7", datalayer_results)
    ]
    
    for title, section_id, color, results in sections:
        score = results.get("score", 0)
        summary = results.get("summary", "N/A")
        findings = results.get("findings", [])
        
        # Sort by severity
        severity_order = {"critical": 0, "high": 1, "medium": 2, "low": 3, "info": 4}
        findings.sort(key=lambda x: severity_order.get(x.get("severity", "info"), 5))
        
        findings_html = ""
        for i, finding in enumerate(findings, 1):
            sev = finding.get("severity", "info")
            sev_colors = {
                "critical": "#ef4444",
                "high": "#f97316", 
                "medium": "#f59e0b",
                "low": "#22c55e",
                "info": "#6b7280"
            }
            sev_color = sev_colors.get(sev, "#6b7280")
            
            findings_html += f"""
            <div class="finding">
                <div class="finding-header">
                    <span class="finding-number">#{i}</span>
                    <span class="finding-title">{finding.get('issue', 'N/A')}</span>
                    <span class="severity-badge" style="background: {sev_color}">{sev.upper()}</span>
                </div>
                <div class="finding-body">
                    <div class="finding-row">
                        <span class="finding-label">Category</span>
                        <span class="finding-value">{finding.get('category', 'N/A')}</span>
                    </div>
                    <div class="finding-row">
                        <span class="finding-label">Details</span>
                        <span class="finding-value">{finding.get('details', 'N/A')}</span>
                    </div>
                    <div class="finding-row">
                        <span class="finding-label">How to Fix</span>
                        <span class="finding-value fix">{finding.get('fix', 'N/A')}</span>
                    </div>
                    <div class="finding-row">
                        <span class="finding-label">Business Impact</span>
                        <span class="finding-value">{finding.get('business_impact', 'N/A')}</span>
                    </div>
                </div>
            </div>"""
        
        sections_html += f"""
        <div class="section" id="{section_id}">
            <div class="section-header" style="border-left: 4px solid {color}">
                <h2>{title}</h2>
                <div class="section-score" style="color: {color}">{score}/100</div>
            </div>
            <p class="section-summary">{summary}</p>
            <div class="score-bar-container">
                <div class="score-bar" style="width: {score}%; background: {color}"></div>
            </div>
            {findings_html}
        </div>"""
    
    # Priority action items
    critical_high = [f for f in all_findings if f.get("severity") in ("critical", "high")]
    critical_high.sort(key=lambda x: 0 if x.get("severity") == "critical" else 1)
    
    actions_html = ""
    for i, item in enumerate(critical_high, 1):
        sev = item.get("severity", "info")
        sev_colors = {"critical": "#ef4444", "high": "#f97316"}
        dot_color = sev_colors.get(sev, "#6b7280")
        actions_html += f"""
        <div class="action-item">
            <div class="action-number" style="background: {dot_color}">{i}</div>
            <div class="action-content">
                <div class="action-title">{item.get('issue', 'N/A')}</div>
                <div class="action-fix">{item.get('fix', 'N/A')}</div>
            </div>
        </div>"""
    
    if not actions_html:
        actions_html = '<p style="color: #22c55e; font-weight: 600;">✅ No critical or high severity issues found!</p>'
    
    # Setup summary
    setup_info = f"""
        <div class="setup-grid">
            <div class="setup-item"><span class="setup-label">Industry</span><span class="setup-value">{setup.get('industry', 'N/A')}</span></div>
            <div class="setup-item"><span class="setup-label">Website Type</span><span class="setup-value">{setup.get('website_type', 'N/A')}</span></div>
            <div class="setup-item"><span class="setup-label">Platform</span><span class="setup-value">{setup.get('platform', 'N/A')}</span></div>
            <div class="setup-item"><span class="setup-label">Goals</span><span class="setup-value">{', '.join(setup.get('goals', ['N/A']))}</span></div>
        </div>"""
    
    # Full HTML
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Analytics Tracking Audit Report</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #0f172a; 
            color: #e2e8f0;
            line-height: 1.6;
            padding: 2rem;
        }}
        .container {{ max-width: 900px; margin: 0 auto; }}
        
        /* Header */
        .header {{ 
            text-align: center; 
            padding: 2.5rem 2rem;
            background: linear-gradient(135deg, #1e293b, #334155);
            border-radius: 16px;
            margin-bottom: 2rem;
            border: 1px solid #475569;
        }}
        .header h1 {{ 
            font-size: 1.8rem; 
            font-weight: 700;
            margin-bottom: 0.5rem;
            color: #f8fafc;
        }}
        .header .subtitle {{ color: #94a3b8; font-size: 0.9rem; }}
        .header .timestamp {{ color: #64748b; font-size: 0.8rem; margin-top: 0.5rem; }}
        
        /* Overall Score */
        .overall-score {{
            text-align: center;
            padding: 2rem;
            background: #1e293b;
            border-radius: 16px;
            margin-bottom: 2rem;
            border: 1px solid #334155;
        }}
        .score-circle {{
            display: inline-flex;
            align-items: center;
            justify-content: center;
            width: 120px;
            height: 120px;
            border-radius: 50%;
            border: 6px solid {score_color};
            font-size: 2.5rem;
            font-weight: 800;
            color: {score_color};
            margin-bottom: 1rem;
        }}
        .score-label {{ color: #94a3b8; font-size: 0.9rem; }}
        
        /* Severity summary */
        .severity-summary {{
            display: flex;
            justify-content: center;
            gap: 1.5rem;
            margin-top: 1.5rem;
            flex-wrap: wrap;
        }}
        .severity-count {{
            display: flex;
            align-items: center;
            gap: 0.4rem;
            font-size: 0.85rem;
            color: #cbd5e1;
        }}
        .severity-dot {{
            width: 10px;
            height: 10px;
            border-radius: 50%;
        }}
        
        /* Score bars */
        .scores-grid {{
            display: grid;
            grid-template-columns: 1fr 1fr 1fr;
            gap: 1rem;
            margin-top: 1.5rem;
        }}
        .score-card {{
            background: #0f172a;
            border-radius: 8px;
            padding: 1rem;
            text-align: center;
        }}
        .score-card .label {{ font-size: 0.8rem; color: #94a3b8; }}
        .score-card .value {{ font-size: 1.5rem; font-weight: 700; }}
        
        /* Setup info */
        .setup-grid {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 0.75rem;
        }}
        .setup-item {{
            background: #0f172a;
            padding: 0.75rem 1rem;
            border-radius: 8px;
        }}
        .setup-label {{ font-size: 0.75rem; color: #64748b; display: block; }}
        .setup-value {{ font-size: 0.9rem; color: #e2e8f0; font-weight: 500; }}
        
        /* Sections */
        .section {{
            background: #1e293b;
            border-radius: 16px;
            padding: 2rem;
            margin-bottom: 1.5rem;
            border: 1px solid #334155;
        }}
        .section-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding-left: 1rem;
            margin-bottom: 1rem;
        }}
        .section-header h2 {{ font-size: 1.2rem; color: #f8fafc; }}
        .section-score {{ font-size: 1.5rem; font-weight: 800; }}
        .section-summary {{ 
            color: #94a3b8; 
            font-size: 0.9rem; 
            margin-bottom: 1.5rem;
            padding-bottom: 1rem;
            border-bottom: 1px solid #334155;
        }}
        .score-bar-container {{
            height: 6px;
            background: #334155;
            border-radius: 3px;
            margin-bottom: 1.5rem;
            overflow: hidden;
        }}
        .score-bar {{
            height: 100%;
            border-radius: 3px;
            transition: width 0.5s;
        }}
        
        /* Findings */
        .finding {{
            background: #0f172a;
            border-radius: 10px;
            margin-bottom: 0.75rem;
            overflow: hidden;
        }}
        .finding-header {{
            display: flex;
            align-items: center;
            gap: 0.75rem;
            padding: 0.85rem 1rem;
            cursor: pointer;
        }}
        .finding-number {{
            color: #64748b;
            font-size: 0.8rem;
            font-weight: 600;
        }}
        .finding-title {{
            flex: 1;
            font-weight: 600;
            font-size: 0.9rem;
            color: #f1f5f9;
        }}
        .severity-badge {{
            padding: 0.2rem 0.6rem;
            border-radius: 4px;
            font-size: 0.7rem;
            font-weight: 700;
            color: white;
        }}
        .finding-body {{
            padding: 0 1rem 1rem 1rem;
        }}
        .finding-row {{
            display: flex;
            gap: 1rem;
            padding: 0.4rem 0;
            font-size: 0.85rem;
            border-bottom: 1px solid #1e293b;
        }}
        .finding-row:last-child {{ border-bottom: none; }}
        .finding-label {{
            min-width: 110px;
            color: #64748b;
            font-weight: 500;
        }}
        .finding-value {{ color: #cbd5e1; }}
        .finding-value.fix {{ color: #60a5fa; }}
        
        /* Action Items */
        .actions {{
            background: #1e293b;
            border-radius: 16px;
            padding: 2rem;
            margin-bottom: 1.5rem;
            border: 1px solid #334155;
        }}
        .actions h2 {{ 
            font-size: 1.2rem; 
            margin-bottom: 1.5rem;
            color: #f8fafc;
        }}
        .action-item {{
            display: flex;
            align-items: flex-start;
            gap: 1rem;
            padding: 0.75rem 0;
            border-bottom: 1px solid #334155;
        }}
        .action-item:last-child {{ border-bottom: none; }}
        .action-number {{
            min-width: 28px;
            height: 28px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 0.75rem;
            font-weight: 700;
            color: white;
        }}
        .action-title {{ font-weight: 600; font-size: 0.9rem; color: #f1f5f9; }}
        .action-fix {{ font-size: 0.85rem; color: #60a5fa; margin-top: 0.25rem; }}
        
        /* Footer */
        .footer {{
            text-align: center;
            padding: 2rem;
            color: #475569;
            font-size: 0.8rem;
        }}
        .footer a {{ color: #60a5fa; text-decoration: none; }}
        
        @media print {{
            body {{ background: white; color: #1e293b; padding: 1rem; }}
            .container {{ max-width: 100%; }}
            .section, .overall-score, .header, .actions {{ 
                border: 1px solid #e2e8f0; 
                background: white;
            }}
            .finding {{ background: #f8fafc; }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Analytics Tracking Audit Report</h1>
            <div class="subtitle">Powered by Claude AI</div>
            <div class="timestamp">Generated on {timestamp}</div>
        </div>

        <div class="overall-score">
            <div class="score-circle">{overall}</div>
            <div class="score-label">Overall Score out of 100</div>
            
            <div class="severity-summary">
                <div class="severity-count"><span class="severity-dot" style="background:#ef4444"></span> {severity_counts.get('critical', 0)} Critical</div>
                <div class="severity-count"><span class="severity-dot" style="background:#f97316"></span> {severity_counts.get('high', 0)} High</div>
                <div class="severity-count"><span class="severity-dot" style="background:#f59e0b"></span> {severity_counts.get('medium', 0)} Medium</div>
                <div class="severity-count"><span class="severity-dot" style="background:#22c55e"></span> {severity_counts.get('low', 0)} Low</div>
            </div>
            
            <div class="scores-grid">
                <div class="score-card">
                    <div class="label">GA4 Events</div>
                    <div class="value" style="color: #3b82f6">{scores['GA4 Events']}</div>
                </div>
                <div class="score-card">
                    <div class="label">GTM Health</div>
                    <div class="value" style="color: #f97316">{scores['GTM Health']}</div>
                </div>
                <div class="score-card">
                    <div class="label">DataLayer</div>
                    <div class="value" style="color: #a855f7">{scores['DataLayer']}</div>
                </div>
            </div>
        </div>

        <div class="section" style="padding: 1.5rem 2rem;">
            <h3 style="font-size: 0.9rem; color: #94a3b8; margin-bottom: 1rem;">Setup Analyzed</h3>
            {setup_info}
        </div>

        {sections_html}

        <div class="actions">
            <h2>Priority Action Items</h2>
            {actions_html}
        </div>

        <div class="footer">
            <p>Generated by <strong>Analytics Audit Tool</strong> — Built with the Anthropic Claude API</p>
            <p style="margin-top: 0.5rem;">
                <a href="https://github.com/nearchosk8/analytics-audit-tool" target="_blank">View on GitHub</a>
            </p>
        </div>
    </div>
</body>
</html>"""
    
    # Save to file
    filename = f"audit-report-{datetime.now().strftime('%Y%m%d-%H%M%S')}.html"
    filepath = os.path.join(os.path.dirname(os.path.abspath(__file__)), filename)
    
    with open(filepath, 'w') as f:
        f.write(html)
    
    return filepath