# Resume Builder & Transformer (Python + Streamlit + ReportLab)

This app helps you rapidly create consistent, branded resumes for friends in two ways:

1. **Create from Form** — Fill out a simple form and instantly generate a PDF resume using your template.
2. **Transform Existing** — Upload an existing resume (DOCX or TXT), map sections, tweak details, and export to PDF in your template.

## Quick Start

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

The app writes finished PDFs to `./output`.

## Why ReportLab?
ReportLab is a pure-Python PDF engine (no system dependencies like `wkhtmltopdf` or WeasyPrint libs). It lets us enforce consistent layout and brand quickly.

## Customizing Your Template
- Edit `resume_template.py` for fonts, spacing, and section order.
- You can also modify colors/margins and add a logo or monogram in the header.

## Supported Inputs (Transform Existing)
- **DOCX** (best results) or **TXT**.
- PDFs are *not* parsed here (PDFs are hard to parse reliably). Convert PDFs to DOCX/TXT first for best results.

## Notes
- This is a starter template—clean and pragmatic. Tweak the layout/typography to match your long-used resume style.
- Consider adding your own brand colors, icon bullets, or watermark.
