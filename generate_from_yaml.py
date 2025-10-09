import argparse, yaml, os
from resume_template import render_pdf

def main():
    ap = argparse.ArgumentParser(description="Generate resume PDF from YAML data")
    ap.add_argument("yaml_path", help="Path to YAML file with resume fields")
    ap.add_argument("-o","--out", default=None, help="Output PDF path (default: ./output/<name>_resume.pdf)")
    args = ap.parse_args()

    with open(args.yaml_path, "r") as f:
        data = yaml.safe_load(f)

    name = (data.get("name") or "resume").replace(" ","_")
    out = args.out or os.path.join("output", f"{name}_resume.pdf")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    render_pdf(data, out_path=out)
    print(f"Wrote {out}")

if __name__ == "__main__":
    main()
