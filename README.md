# Analytics Tracking Audit Tool

An AI-powered auditing tool that analyzes GA4, GTM, and dataLayer implementations and generates a comprehensive tracking audit report with prioritized recommendations.

Built with the Anthropic Claude API.

## What It Does

1. **Guided Intake** — Asks about your industry, website type, platform, and goals
2. **Paste Your Config** — Accepts GA4 event lists, GTM tag exports, and dataLayer samples
3. **AI-Powered Audit** — Runs three specialized audits using Claude:
   - **GA4 Event Coverage** — Identifies missing events, wrong parameters, naming issues
   - **GTM Container Health** — Finds duplicates, unused tags, consent gaps, security risks
   - **DataLayer Quality** — Checks structure, naming conventions, PII exposure, data types
4. **Prioritized Report** — Generates a scored report with severity-ranked findings and action items

## Example Output
```
🏆 OVERALL SCORE: 25/100
────────────────────────────────
   GA4 Events      █░░░░░░░░░░░░░░░░░░░ 15/100
   GTM Health      █████████░░░░░░░░░░░ 45/100
   DataLayer       █░░░░░░░░░░░░░░░░░░░ 15/100

🔴 Finding #1: Missing core engagement events
   Severity:  CRITICAL
   Fix:       Implement page_view, scroll, file_download events
   Impact:    Cannot measure basic user engagement or user journey
```

## Architecture
```
analytics-audit-tool/
├── main.py              ← Entry point
├── config.py            ← API client, model settings
├── intake.py            ← Guided intake interview
├── prompts.py           ← All Claude prompts (centralized)
├── report.py            ← Report formatting and display
└── auditors/
    ├── ga4_auditor.py   ← GA4 event coverage analysis
    ├── gtm_auditor.py   ← GTM container health checks
    └── datalayer_auditor.py ← DataLayer quality analysis
```

## Key Concepts Used

- **Structured Outputs** — Claude returns JSON that Python parses and formats
- **Prompt Engineering** — Industry-specific, role-based prompts with strict output schemas
- **Modular Architecture** — Separated concerns: intake, audit logic, prompts, reporting
- **Defensive Parsing** — Handles markdown-wrapped JSON responses from the LLM

## Getting Started
```bash
# Clone the repo
git clone https://github.com/nearchosk8/analytics-audit-tool.git
cd analytics-audit-tool

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install anthropic

# Set your API key
export ANTHROPIC_API_KEY="your-key-here"

# Run the tool
python main.py
```

## Usage Tips

- For the best results, paste real data from your GA4 property, GTM container, and browser console
- Even without pasted data, the tool generates useful recommendations based on your industry and setup
- GA4 events can be copied from GA4 > Admin > Events
- DataLayer can be copied from browser console: `JSON.stringify(dataLayer, null, 2)`

## Roadmap

- [ ] Export report to PDF/HTML
- [ ] Save audit results as JSON for comparison over time
- [ ] Web interface (Streamlit)
- [ ] Real API integrations (GA4 Admin API, GTM API)
- [ ] Few-shot examples for more accurate audits

## Author

**Nearchos Katsanikakis** — Digital Analyst | AI Implementation

Part of my journey building AI-powered tools for digital analytics workflows using the Anthropic Claude API.
