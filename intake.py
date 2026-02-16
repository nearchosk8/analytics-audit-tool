# Intake module - gathers information about the user's setup

def run_intake():
    """Guided intake interview to understand the user's tracking setup"""
    
    print("\n📋 TRACKING AUDIT - INTAKE")
    print("=" * 50)
    print("I'll ask you a few questions about your setup,")
    print("then you can paste any config details you have.\n")
    
    setup = {}
    
    # --- Guided Questions ---
    
    # Industry
    print("1. What industry is your website in?")
    print("   a) E-commerce / Retail")
    print("   b) SaaS / Software")
    print("   c) Lead Generation / B2B")
    print("   d) Media / Publishing")
    print("   e) Travel / Hospitality")
    print("   f) Other")
    
    industry_map = {
        "a": "E-commerce / Retail",
        "b": "SaaS / Software", 
        "c": "Lead Generation / B2B",
        "d": "Media / Publishing",
        "e": "Travel / Hospitality"
    }
    choice = input("\n   Your choice: ").strip().lower()
    if choice == "f":
        setup["industry"] = input("   Please specify: ").strip()
    else:
        setup["industry"] = industry_map.get(choice, "Other")
    
    # Website type
    print(f"\n2. What type of website is it?")
    print("   a) Single product / landing page")
    print("   b) Multi-page website with forms")
    print("   c) E-commerce store")
    print("   d) Web application (SaaS)")
    print("   e) Content / blog site")
    
    type_map = {
        "a": "Single product / landing page",
        "b": "Multi-page website with forms",
        "c": "E-commerce store",
        "d": "Web application (SaaS)",
        "e": "Content / blog site"
    }
    choice = input("\n   Your choice: ").strip().lower()
    setup["website_type"] = type_map.get(choice, "Other")
    
    # Business goals
    print(f"\n3. What are your top analytics goals? (select all that apply)")
    print("   a) Track conversions / purchases")
    print("   b) Understand user journey / funnel")
    print("   c) Measure marketing campaign performance")
    print("   d) Track engagement / content performance")
    print("   e) Generate leads / form submissions")
    
    goals_map = {
        "a": "Track conversions / purchases",
        "b": "Understand user journey / funnel",
        "c": "Measure marketing campaign performance",
        "d": "Track engagement / content performance",
        "e": "Generate leads / form submissions"
    }
    choices = input("\n   Your choices (e.g. a,b,c): ").strip().lower().split(",")
    setup["goals"] = [goals_map.get(c.strip(), "") for c in choices if c.strip() in goals_map]
    
    # Platform
    print(f"\n4. What platform is your site built on?")
    platform = input("   (e.g. Shopify, WordPress, custom React, Next.js): ").strip()
    setup["platform"] = platform
    
    # --- Paste Config Details ---
    
    print("\n" + "=" * 50)
    print("📎 Now paste any config details you have.")
    print("   Press Enter twice (empty line) when done with each section.")
    print("   Type 'skip' to skip a section.\n")
    
    # GA4 Events
    print("5. Paste your GA4 events list (from GA4 > Admin > Events,")
    print("   or from your measurement plan):")
    setup["ga4_events"] = _multiline_input()
    
    # GTM Tags
    print("\n6. Paste your GTM tag list (from GTM > Tags overview,")
    print("   or describe your tags):")
    setup["gtm_tags"] = _multiline_input()
    
    # DataLayer
    print("\n7. Paste a sample of your dataLayer")
    print("   (copy from browser console: JSON.stringify(dataLayer, null, 2)):")
    setup["datalayer_sample"] = _multiline_input()
    
    # Summary
    print("\n" + "=" * 50)
    print("✅ INTAKE COMPLETE")
    print(f"   Industry:  {setup['industry']}")
    print(f"   Type:      {setup['website_type']}")
    print(f"   Platform:  {setup['platform']}")
    print(f"   Goals:     {', '.join(setup['goals'])}")
    print(f"   GA4 data:  {'Provided' if setup['ga4_events'] else 'Not provided'}")
    print(f"   GTM data:  {'Provided' if setup['gtm_tags'] else 'Not provided'}")
    print(f"   DataLayer: {'Provided' if setup['datalayer_sample'] else 'Not provided'}")
    
    return setup


def _multiline_input():
    """Collect multiline input until empty line or 'skip'"""
    lines = []
    while True:
        line = input()
        if line.lower().strip() == 'skip':
            return ""
        if line == "" and lines:
            break
        if line == "" and not lines:
            continue
        lines.append(line)
    return "\n".join(lines)