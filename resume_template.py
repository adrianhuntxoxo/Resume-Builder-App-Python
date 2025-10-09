from reportlab.lib.pagesizes import LETTER, A4
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, ListFlowable, ListItem, Table, TableStyle
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import os, yaml

# ---------- THEME ----------
def load_theme(path="theme.yaml"):
    if os.path.exists(path):
        with open(path, "r") as f:
            return yaml.safe_load(f) or {}
    return {}
THEME = load_theme()

def register_fonts():
    prefer_ttf = THEME.get("fonts", {}).get("prefer_ttf", False)
    reg_path   = THEME.get("fonts", {}).get("ttf_regular", "Inter-Regular.ttf")
    bold_path  = THEME.get("fonts", {}).get("ttf_bold", "Inter-Bold.ttf")
    base = THEME.get("fonts", {}).get("base", "Helvetica")
    bold = THEME.get("fonts", {}).get("bold", "Helvetica-Bold")
    if prefer_ttf and os.path.exists(reg_path) and os.path.exists(bold_path):
        try:
            pdfmetrics.registerFont(TTFont("Tpl-Regular", reg_path))
            pdfmetrics.registerFont(TTFont("Tpl-Bold", bold_path))
            base, bold = "Tpl-Regular", "Tpl-Bold"
        except Exception:
            pass
    return base, bold

BASE_FONT, BOLD_FONT = register_fonts()

def page_and_margins():
    ps = (THEME.get("page_size") or "LETTER").upper()
    page = LETTER if ps == "LETTER" else A4
    m = THEME.get("margins_in", {"left":0.7, "right":0.7, "top":0.7, "bottom":0.7})
    return page, (m["left"]*inch, m["right"]*inch, m["top"]*inch, m["bottom"]*inch)

# ---------- STYLES ----------
sizes  = THEME.get("sizes", {})
accent = colors.HexColor(THEME.get("colors", {}).get("accent_hex", "#000000"))
muted  = colors.HexColor(THEME.get("colors", {}).get("muted_hex", "#444444"))
textc  = colors.HexColor(THEME.get("colors", {}).get("text_hex", "#000000"))

def _sz(k, d): return sizes.get(k, d)
H1     = ParagraphStyle("H1",     fontName=BOLD_FONT, fontSize=_sz("h1",18),   leading=_sz("h1",18)+_sz("leading_adjust",2), textColor=accent, spaceAfter=6)
H2     = ParagraphStyle("H2",     fontName=BOLD_FONT, fontSize=_sz("h2",12),   leading=_sz("h2",12)+_sz("leading_adjust",2), textColor=accent, spaceBefore=10, spaceAfter=4)
BODY   = ParagraphStyle("BODY",   fontName=BASE_FONT, fontSize=_sz("body",10.5),leading=_sz("body",10.5)+_sz("leading_adjust",2), textColor=textc)
META   = ParagraphStyle("META",   fontName=BASE_FONT, fontSize=_sz("meta",9.5),leading=_sz("meta",9.5)+_sz("leading_adjust",2), textColor=muted)
BULLET = ParagraphStyle("BULLET", fontName=BASE_FONT, fontSize=_sz("body",10.5),leading=_sz("body",10.5)+_sz("leading_adjust",2), leftIndent=12, textColor=textc)

LABELS = THEME.get("labels", {})
def label(key, default): return LABELS.get(key, default)

# ---------- RENDER HELPERS ----------
def bullet_list(items):
    return ListFlowable([ListItem(Paragraph(i, BULLET)) for i in items], bulletType="bullet")

def draw_header(story, data):
    name     = data.get("name","")
    email    = data.get("email","")
    phone    = data.get("phone","")
    location = data.get("location","")
    links    = data.get("links",[])
    story.append(Paragraph(name, H1))
    bits = [b for b in [location, email, phone] if b]
    if links: bits.extend(links)
    if bits: story.append(Paragraph(" &#8226; ".join(bits), META))
    story.append(Spacer(1,6))

def draw_summary(story, data):
    s = data.get("summary","")
    if s:
        story.append(Paragraph(label("summary","SUMMARY"), H2))
        story.append(Paragraph(s, BODY))

def draw_skills(story, data):
    skills = data.get("skills",[])
    if skills:
        story.append(Paragraph(label("skills","SKILLS AND SOFTWARE PROFICIENCIES"), H2))
        story.append(Paragraph(" &#8226; ".join(skills), BODY))

def draw_experience(story, data):
    jobs = data.get("experience",[])
    if not jobs: return
    story.append(Paragraph(label("experience","RELEVANT EXPERIENCES"), H2))
    for j in jobs:
        org  = j.get("company","") or j.get("organization","")
        role = j.get("role","")
        dates= j.get("dates","")
        loc  = j.get("location","")
        if org:  story.append(Paragraph(org, BODY))
        if role: story.append(Paragraph(role, BODY))
        if dates:story.append(Paragraph(dates, META))
        if loc:  story.append(Paragraph(loc, META))
        bullets = j.get("bullets",[])
        if bullets: story.append(bullet_list(bullets))

def draw_education(story, data):
    edus = data.get("education",[])
    if not edus: return
    story.append(Paragraph(label("education","EDUCATION"), H2))
    for e in edus:
        school   = e.get("school","")
        grad     = e.get("grad","") or e.get("dates","")
        location = e.get("location","")
        degree   = e.get("degree","")
        left = school + (f", {grad}" if grad else "")
        tbl = Table([[Paragraph(left, BODY), Paragraph(location, META)]], colWidths=[4.6*inch, 2.4*inch])
        tbl.setStyle(TableStyle([
            ("VALIGN",(0,0),(-1,-1),"TOP"),
            ("ALIGN",(1,0),(1,0),"RIGHT"),
            ("LEFTPADDING",(0,0),(-1,-1),0), ("RIGHTPADDING",(0,0),(-1,-1),0),
            ("TOPPADDING",(0,0),(-1,-1),0),  ("BOTTOMPADDING",(0,0),(-1,-1),0),
        ]))
        story.append(tbl)
        if degree: story.append(Paragraph(degree, BODY))
        story.append(Spacer(1,4))

def draw_certifications(story, data):
    certs = data.get("certifications",[])
    if certs:
        story.append(Paragraph(label("certifications","CERTIFICATIONS"), H2))
        story.append(Paragraph(", ".join(certs), BODY))

SECTION_ORDER = THEME.get("section_order", ["header","summary","education","skills","experience","certifications"])

def render_pdf(data, out_path="output/resume.pdf", page_size=None, margins=None):
    """PUBLIC API used by app.py"""
    page_size, margins = page_and_margins()
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    doc = SimpleDocTemplate(out_path, pagesize=page_size,
                            leftMargin=margins[0], rightMargin=margins[1],
                            topMargin=margins[2],  bottomMargin=margins[3],
                            title=data.get("name","Resume"))
    story = []
    draw_header(story, data)
    draw_summary(story, data)
    draw_education(story, data)
    draw_skills(story, data)
    draw_experience(story, data)
    draw_certifications(story, data)
    doc.build(story)
    return out_path
