import streamlit as st
from resume_template import render_pdf
from parser import parse_docx, parse_txt
import json, yaml, os, io

st.set_page_config(page_title="Resume Builder", page_icon="🧰", layout="centered")

# ---- Theme Sidebar ----
st.sidebar.header("🎨 Theme")
import yaml, os
theme_file = "theme.yaml"
if os.path.exists(theme_file):
    with open(theme_file, "r") as f:
        theme = yaml.safe_load(f) or {}
else:
    theme = {}

with st.sidebar.expander("Page & Margins", expanded=False):
    ps = st.selectbox("Page Size", ["LETTER","A4"], index=(0 if (theme.get("page_size","LETTER")=="LETTER") else 1))
    ml = st.number_input("Left margin (in)", value=float(theme.get("margins_in",{}).get("left",0.6)), step=0.1)
    mr = st.number_input("Right margin (in)", value=float(theme.get("margins_in",{}).get("right",0.6)), step=0.1)
    mt = st.number_input("Top margin (in)", value=float(theme.get("margins_in",{}).get("top",0.6)), step=0.1)
    mb = st.number_input("Bottom margin (in)", value=float(theme.get("margins_in",{}).get("bottom",0.6)), step=0.1)

with st.sidebar.expander("Fonts", expanded=False):
    prefer_ttf = st.checkbox("Prefer custom TTF", value=bool(theme.get("fonts",{}).get("prefer_ttf", False)))
    base = st.text_input("Base font", value=theme.get("fonts",{}).get("base","Helvetica"))
    bold = st.text_input("Bold font", value=theme.get("fonts",{}).get("bold","Helvetica-Bold"))
    ttf_reg = st.text_input("TTF Regular (file name)", value=theme.get("fonts",{}).get("ttf_regular","Inter-Regular.ttf"))
    ttf_bold = st.text_input("TTF Bold (file name)", value=theme.get("fonts",{}).get("ttf_bold","Inter-Bold.ttf"))

with st.sidebar.expander("Colors", expanded=False):
    accent = st.color_picker("Accent", value=theme.get("colors",{}).get("accent_hex","#111111"))
    textc = st.color_picker("Text", value=theme.get("colors",{}).get("text_hex","#000000"))
    muted = st.color_picker("Muted", value=theme.get("colors",{}).get("muted_hex","#444444"))

with st.sidebar.expander("Sizes", expanded=False):
    h1 = st.number_input("H1 size", value=float(theme.get("sizes",{}).get("h1",16)))
    h2 = st.number_input("H2 size", value=float(theme.get("sizes",{}).get("h2",11.5)))
    body = st.number_input("Body size", value=float(theme.get("sizes",{}).get("body",10)))
    meta = st.number_input("Meta size", value=float(theme.get("sizes",{}).get("meta",9.5)))
    leading_adj = st.number_input("Leading adjust", value=float(theme.get("sizes",{}).get("leading_adjust",2)))

if st.sidebar.button("Save Theme"):
    theme["page_size"] = ps
    theme["margins_in"] = {"left":ml, "right":mr, "top":mt, "bottom":mb}
    theme.setdefault("fonts",{}).update({
        "prefer_ttf": prefer_ttf, "base": base, "bold": bold,
        "ttf_regular": ttf_reg, "ttf_bold": ttf_bold
    })
    theme["colors"] = {"accent_hex":accent, "text_hex":textc, "muted_hex":muted}
    theme["sizes"] = {"h1":h1,"h2":h2,"body":body,"meta":meta,"leading_adjust":leading_adj}
    with open(theme_file, "w") as f:
        yaml.safe_dump(theme, f, sort_keys=False)
    st.sidebar.success("Theme saved. Regenerate a PDF to see changes.")

st.title("🧰 Resume Builder & Transformer")

st.markdown("""
Create consistent, branded resumes **fast**:
- **Create from Form** — type details, export to PDF
- **Transform Existing** — upload DOCX/TXT, map & export to PDF
""")

mode = st.radio("Choose a mode:", ["Create from Form", "Transform Existing"], horizontal=True)

# Helper: download a generated PDF
def download_button(data_bytes: bytes, filename: str):
    st.download_button("⬇️ Download PDF", data=data_bytes, file_name=filename, mime="application/pdf")

# ---- Mode 1: Create from Form ----
if mode == "Create from Form":
    st.subheader("Enter details")
    col1, col2 = st.columns(2)
    with col1:
        name = st.text_input("Full Name", value="Jordan Avery")
        title = st.text_input("Title", value="Technical Integrations Specialist")
        email = st.text_input("Email", value="jordan.avery@email.com")
        phone = st.text_input("Phone", value="(555) 123-4567")
    with col2:
        location = st.text_input("Location", value="Dallas, TX")
        links = st.text_input("Links (comma-separated)", value="linkedin.com/in/jordanavery, github.com/jordanavery")

    summary = st.text_area("Summary", height=100, value="Integration-focused specialist with 8+ years delivering scalable, API-driven solutions. Known for fast onboarding, clear docs, and cost-to-serve reductions.")
    skills = st.text_input("Skills (comma-separated)", value="APIs, Webhooks, Python, SQL, Workato, Zapier, AWS, GCP, Jira, Postman, SLA Management, Client Onboarding")

    st.markdown("### Experience")
    exp = []
    for i in range(1, 3):
        with st.expander(f"Role {i}", expanded=(i==1)):
            role = st.text_input(f"Role {i} Title", key=f"role_{i}", value="Sr. Partner Integrations Specialist" if i==1 else "")
            company = st.text_input(f"Role {i} Company", key=f"company_{i}", value="DoorDash (Contract)" if i==1 else "")
            dates = st.text_input(f"Role {i} Dates", key=f"dates_{i}", value="Jul 2024 – Dec 2024" if i==1 else "")
            loc = st.text_input(f"Role {i} Location", key=f"loc_{i}", value="Remote" if i==1 else "")
            bullets = st.text_area(f"Role {i} Bullets (one per line)", key=f"bullets_{i}", value="Owned technical onboarding and certification for new partners across API-based products.\nBuilt repeatable playbooks and how-to guides to accelerate time-to-value.\nDiagnosed integration issues with Postman and browser dev tools; collaborated with engineering for fixes." if i==1 else "")
            if role or company or bullets.strip():
                exp.append({
                    "role": role, "company": company, "dates": dates, "location": loc,
                    "bullets": [b.strip() for b in bullets.splitlines() if b.strip()]
                })

    st.markdown("### Education")
    edu_degree = st.text_input("Degree", value="B.S. Information Systems")
    edu_school = st.text_input("School", value="State University")
    edu_location = st.text_input("School Location", value="Memphis, TN")
    edu_dates = st.text_input("Dates", value="2015 – 2019")

    certs = st.text_input("Certifications (comma-separated)", value="AWS Certified Cloud Practitioner")

    data = {
        "name": name,
        "title": title,
        "email": email,
        "phone": phone,
        "location": location,
        "links": [l.strip() for l in links.split(",") if l.strip()],
        "summary": summary,
        "skills": [s.strip() for s in skills.split(",") if s.strip()],
        "experience": exp,
        "education": [{"degree":edu_degree,"school":edu_school,"location":edu_location,"dates":edu_dates}] if edu_degree or edu_school else [],
        "certifications": [c.strip() for c in certs.split(",") if c.strip()]
    }

    if st.button("Generate PDF"):
        out_path = os.path.join("output", f"{name.replace(' ', '_')}_resume.pdf")
        os.makedirs("output", exist_ok=True)
        out_path = render_pdf(data, out_path=out_path)
        with open(out_path, "rb") as f:
            pdf_bytes = f.read()
        download_button(pdf_bytes, os.path.basename(out_path))
        st.success(f"Saved to {out_path}")

# ---- Mode 2: Transform Existing ----
else:
    st.subheader("Upload and transform an existing resume")
    file = st.file_uploader("Upload a DOCX or TXT", type=["docx","txt"])
    if file is not None:
        parsed = {}
        if file.name.lower().endswith(".docx"):
            parsed = parse_docx(file.read())
        else:
            parsed = parse_txt(file.read())

        st.markdown("### Parsed (edit before export)")
        name = st.text_input("Full Name", value=parsed.get("name",""))
        title = st.text_input("Title", value=parsed.get("title",""))
        email = st.text_input("Email", value=parsed.get("email",""))
        phone = st.text_input("Phone", value=parsed.get("phone",""))
        location = st.text_input("Location", value=parsed.get("location",""))
        links = st.text_input("Links (comma-separated)", value=", ".join(parsed.get("links", [])))
        summary = st.text_area("Summary", height=100, value=parsed.get("summary",""))
        skills = st.text_input("Skills (comma-separated)", value=", ".join(parsed.get("skills", [])))

        # Experience editor
        exp_out = []
        exp_src = parsed.get("experience", [])
        for idx, job in enumerate(exp_src or [{}], start=1):
            with st.expander(f"Experience {idx}", expanded=(idx==1)):
                role = st.text_input(f"Role {idx} Title", key=f"t_role_{idx}", value=job.get("role",""))
                company = st.text_input(f"Role {idx} Company", key=f"t_company_{idx}", value=job.get("company",""))
                dates = st.text_input(f"Role {idx} Dates", key=f"t_dates_{idx}", value=job.get("dates",""))
                loc = st.text_input(f"Role {idx} Location", key=f"t_loc_{idx}", value=job.get("location",""))
                bullets_src = job.get("bullets", [])
                bullets_txt = "\n".join(bullets_src) if bullets_src else ""
                bullets = st.text_area(f"Role {idx} Bullets (one per line)", key=f"t_bullets_{idx}", value=bullets_txt)
                exp_out.append({
                    "role": role, "company": company, "dates": dates, "location": loc,
                    "bullets": [b.strip() for b in bullets.splitlines() if b.strip()]
                })

        # Education & certs (manual for now)
        edu_degree = st.text_input("Degree", value="")
        edu_school = st.text_input("School", value="")
        edu_location = st.text_input("School Location", value="")
        edu_dates = st.text_input("Dates", value="")

        certs = st.text_input("Certifications (comma-separated)", value="")

        data = {
            "name": name,
            "title": title,
            "email": email,
            "phone": phone,
            "location": location,
            "links": [l.strip() for l in links.split(",") if l.strip()],
            "summary": summary,
            "skills": [s.strip() for s in skills.split(",") if s.strip()],
            "experience": exp_out,
            "education": [{"degree":edu_degree,"school":edu_school,"location":edu_location,"dates":edu_dates}] if (edu_degree or edu_school) else [],
            "certifications": [c.strip() for c in certs.split(",") if c.strip()]
        }

        if st.button("Generate PDF"):
            name_for_file = (data.get("name") or "resume").replace(" ", "_")
            out_path = os.path.join("output", f"{name_for_file}_resume.pdf")
            os.makedirs("output", exist_ok=True)
            out_path = render_pdf(data, out_path=out_path)
            with open(out_path, "rb") as f:
                pdf_bytes = f.read()
            download_button(pdf_bytes, os.path.basename(out_path))
            st.success(f"Saved to {out_path}")

st.caption("Tip: tweak fonts/margins/sections in resume_template.py to match your 10-year template.")
