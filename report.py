# Report formatter - takes audit results and displays them
from config import SEVERITY

def print_report(ga4_results, gtm_results, datalayer_results):
    """Format and display the complete audit report"""
    
    print("\n")
    print("╔" + "═" * 58 + "╗")
    print("║        📊 ANALYTICS TRACKING AUDIT REPORT              ║")
    print("╚" + "═" * 58 + "╝")
    
    # Overall scores
    scores = {
        "GA4 Events": ga4_results.get("score", 0),
        "GTM Health": gtm_results.get("score", 0),
        "DataLayer": datalayer_results.get("score", 0)
    }
    overall = round(sum(scores.values()) / len(scores))
    
    print(f"\n🏆 OVERALL SCORE: {overall}/100")
    print("─" * 40)
    for name, score in scores.items():
        bar = "█" * (score // 5) + "░" * (20 - score // 5)
        print(f"   {name:<15} {bar} {score}/100")
    
    # Print each section
    sections = [
        ("🔵 GA4 EVENT COVERAGE", ga4_results),
        ("🟠 GTM CONTAINER HEALTH", gtm_results),
        ("🟣 DATALAYER QUALITY", datalayer_results)
    ]
    
    for title, results in sections:
        print(f"\n\n{'=' * 58}")
        print(f" {title}")
        print(f"{'=' * 58}")
        print(f"\n Summary: {results.get('summary', 'N/A')}\n")
        
        findings = results.get("findings", [])
        
        # Sort by severity
        severity_order = {"critical": 0, "high": 1, "medium": 2, "low": 3, "info": 4}
        findings.sort(key=lambda x: severity_order.get(x.get("severity", "info"), 5))
        
        for i, finding in enumerate(findings, 1):
            sev = finding.get("severity", "info")
            icon = SEVERITY.get(sev, "⚪")
            
            print(f" {icon} Finding #{i}: {finding['issue']}")
            print(f"    Severity:  {sev.upper()}")
            print(f"    Category:  {finding.get('category', 'N/A')}")
            print(f"    Details:   {finding.get('details', 'N/A')}")
            print(f"    Fix:       {finding.get('fix', 'N/A')}")
            print(f"    Impact:    {finding.get('business_impact', 'N/A')}")
            print()
    
    # Priority action items
    print(f"\n{'=' * 58}")
    print(" 🎯 PRIORITY ACTION ITEMS")
    print(f"{'=' * 58}\n")
    
    all_findings = (
        ga4_results.get("findings", []) + 
        gtm_results.get("findings", []) + 
        datalayer_results.get("findings", [])
    )
    
    critical_high = [f for f in all_findings if f.get("severity") in ("critical", "high")]
    critical_high.sort(key=lambda x: 0 if x.get("severity") == "critical" else 1)
    
    if critical_high:
        for i, item in enumerate(critical_high, 1):
            icon = SEVERITY.get(item["severity"], "⚪")
            print(f"  {i}. {icon} {item['issue']}")
            print(f"     → {item['fix']}")
            print()
    else:
        print("  ✅ No critical or high severity issues found!")
    
    print(f"{'=' * 58}")
    print(" Audit complete. Fix critical items first, then work down.")
    print(f"{'=' * 58}\n")