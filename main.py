#!/usr/bin/env python3
"""
Analytics Audit Tool
Powered by Claude API - Audits GA4, GTM, and DataLayer implementations
"""

import sys
import os

# Add project root to path so imports work
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from intake import run_intake
from auditors.ga4_auditor import audit_ga4
from auditors.gtm_auditor import audit_gtm
from auditors.datalayer_auditor import audit_datalayer
from report import print_report
from export_html import export_report


def main():
    print("\n")
    print("╔" + "═" * 58 + "╗")
    print("║     🔍 ANALYTICS TRACKING AUDIT TOOL                  ║")
    print("║     Powered by Claude AI                               ║")
    print("╚" + "═" * 58 + "╝")
    print()
    
    # Step 1: Gather information
    setup = run_intake()
    
    # Step 2: Run audits
    print("\n\n⏳ Running audits... This may take a minute.\n")
    
    print("  [1/3] Auditing GA4 event coverage...")
    ga4_results = audit_ga4(setup)
    print("  ✅ GA4 audit complete")
    
    print("  [2/3] Auditing GTM container health...")
    gtm_results = audit_gtm(setup)
    print("  ✅ GTM audit complete")
    
    print("  [3/3] Auditing dataLayer quality...")
    datalayer_results = audit_datalayer(setup)
    print("  ✅ DataLayer audit complete")
    
    # Step 3: Display terminal report
    print_report(ga4_results, gtm_results, datalayer_results)
    
    # Step 4: Offer HTML export
    print("\n")
    export_choice = input("📄 Export report as HTML file? (y/n): ").strip().lower()
    
    if export_choice == 'y':
        filepath = export_report(ga4_results, gtm_results, datalayer_results, setup)
        print(f"\n  ✅ Report saved to: {filepath}")
        print(f"  📂 Open it in your browser to see the formatted report.")
        
        # Try to open in browser automatically on Mac
        try:
            os.system(f'open "{filepath}"')
        except Exception:
            pass


if __name__ == "__main__":
    main()