#!/usr/bin/env python3
import argparse
import ast
import hashlib
import json
import math
import operator as op
import os
import re
import shutil
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

try:
    import fitz  # PyMuPDF
except Exception as e:
    print(f"ERROR: PyMuPDF (fitz) required: {e}", file=sys.stderr)
    sys.exit(2)

try:
    import pytesseract
    from PIL import Image
    OCR_AVAILABLE = True
    import os
    local_tess = '/tmp/tess/usr/bin/tesseract'
    if os.path.exists(local_tess):
        pytesseract.pytesseract.tesseract_cmd = local_tess
    os.environ['TESSDATA_PREFIX'] = '/tmp/tess/usr/share/tesseract-ocr/5/tessdata'
    os.environ['LD_LIBRARY_PATH'] = '/tmp/tess/usr/lib/x86_64-linux-gnu:' + os.environ.get('LD_LIBRARY_PATH', '')
    os.environ['PATH'] = '/tmp/tess/usr/bin:' + os.environ.get('PATH', '')
except Exception:
    pytesseract = None
    Image = None
    OCR_AVAILABLE = False


REPO_ROOT = Path(__file__).resolve().parent.parent
MATH_DIR = REPO_ROOT / "app" / "question_banks" / "math"
PDF_DIR = MATH_DIR / "pdf"
MAT_JSON = MATH_DIR / "mat.json"
MANIFEST = MATH_DIR / "pdf_manifest.sha256"
REVIEW_REPORT = MATH_DIR / "review_report.md"
BACKUP_DIR = MATH_DIR / "backups"

REQUIRED_FIELDS = ["question_id", "question", "questiontopic", "answer", "explanation"]
DIAGRAM_CUES = re.compile(r"\b(diagram|figure|fig\.|shown below|picture|image|shape|graph|chart|drawing)\b", re.I)
ANSWER_LABELS = re.compile(r"^\s*(answers?|answer\s*key|mark\s*scheme|solutions?)\b", re.I)
NUM_PATTERNS = [
    re.compile(r"^\s*(?:Q|Question)\s*(\d+)[\.\:\)]\s+", re.I | re.M),
    re.compile(r"^\s*(\d+)[\.\)\:]\s+", re.I | re.M),
]

# Safe eval for simple arithmetic
_OPERATORS = {ast.Add: op.add, ast.Sub: op.sub, ast.Mult: op.mul,
              ast.Div: op.truediv, ast.Pow: op.pow, ast.USub: op.neg, ast.Mod: op.mod}

def safe_eval(expr):
    try:
        expr = expr.strip()
        # replace unicode
        expr = expr.replace('×', '*').replace('÷', '/').replace('—', '-').replace('–', '-')
        if not re.match(r'^[0-9+\-*/().\[\]\s%]+$', expr):
            return None
        # convert brackets to parens
        expr2 = expr
        expr2 = expr2.replace('[', '(')
        expr2 = expr2.replace(']', ')')
        node = ast.parse(expr2, mode='eval')
        def _eval(n):
            if isinstance(n, ast.Constant):
                if isinstance(n.value, (int, float)):
                    return n.value
                return None
            elif hasattr(ast, 'Num') and isinstance(n, ast.Num):
                return n.n
            elif isinstance(n, ast.BinOp):
                left = _eval(n.left)
                right = _eval(n.right)
                if left is None or right is None:
                    return None
                op_func = _OPERATORS.get(type(n.op))
                if not op_func:
                    return None
                try:
                    return op_func(left, right)
                except Exception:
                    return None
            elif isinstance(n, ast.UnaryOp):
                operand = _eval(n.operand)
                if operand is None:
                    return None
                op_func = _OPERATORS.get(type(n.op))
                if not op_func:
                    return None
                try:
                    return op_func(operand)
                except Exception:
                    return None
            else:
                return None
        res = _eval(node.body)
        return res
    except Exception:
        return None


def utc_ts():
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def normalize_text(s: str) -> str:
    if not isinstance(s, str):
        s = "" if s is None else str(s)
    s2 = s.casefold()
    s2 = re.sub(r"\s+", " ", s2)
    s2 = re.sub(r"[^\w\s\+\-\=\*\/\^\.\,\:\;\(\)\[\]\{\}\%]", " ", s2)
    s2 = re.sub(r"\s+", " ", s2).strip()
    return s2


def stable_id(pdf_name: str, page_num: int, qtext: str) -> str:
    base = f"{pdf_name}|{page_num}|{normalize_text(qtext)}"
    h = hashlib.sha256(base.encode("utf-8")).hexdigest()[:16]
    return f"math-{h}"


def read_manifest() -> dict:
    if not MANIFEST.exists():
        return {}
    out = {}
    for line in MANIFEST.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        parts = re.split(r"\s+", line, maxsplit=1)
        if len(parts) == 2:
            sha, fname = parts[0].strip(), parts[1].strip().lstrip("*")
            out[fname] = sha
    return out


def write_manifest(manifest: dict):
    MANIFEST.parent.mkdir(parents=True, exist_ok=True)
    lines = []
    for fname in sorted(manifest.keys()):
        lines.append(f"{manifest[fname]}  {fname}")
    MANIFEST.write_text("\n".join(lines) + ("\n" if lines else ""), encoding="utf-8")


def load_mat_json() -> list:
    if not MAT_JSON.exists():
        return []
    try:
        data = json.loads(MAT_JSON.read_text(encoding="utf-8"))
    except Exception as e:
        raise ValueError(f"Invalid existing JSON at {MAT_JSON}: {e}")
    if not isinstance(data, list):
        raise ValueError(f"mat.json must be a top-level array")
    return data


def validate_questions(questions: list) -> None:
    seen_ids = set()
    seen_norm = set()
    for i, q in enumerate(questions):
        if not isinstance(q, dict):
            raise ValueError(f"Question at index {i} is not an object")
        if set(q.keys()) != set(REQUIRED_FIELDS):
            raise ValueError(f"Question at index {i} must have exactly fields {REQUIRED_FIELDS}, got {sorted(q.keys())}")
        for f in REQUIRED_FIELDS:
            if not isinstance(q[f], str):
                raise ValueError(f"Question at index {i} field '{f}' must be a string")
        if not q["question_id"]:
            raise ValueError(f"Question at index {i} has empty question_id")
        if q["question_id"] in seen_ids:
            raise ValueError(f"Duplicate question_id: {q['question_id']}")
        seen_ids.add(q["question_id"])
        if not q["question"].strip():
            raise ValueError(f"Question at index {i} has empty question text")
        n = normalize_text(q["question"])
        if n in seen_norm:
            raise ValueError(f"Duplicate normalized question text at index {i}")
        seen_norm.add(n)


def backup_mat_json():
    if not MAT_JSON.exists():
        return None
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    bak = BACKUP_DIR / f"mat.json.{utc_ts()}.bak"
    shutil.copy2(MAT_JSON, bak)
    return bak


def atomic_write_json(path: Path, data: list):
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=str(path.parent))
    os.close(fd)
    try:
        tmp_path = Path(tmp)
        tmp_path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        os.replace(tmp_path, path)
    finally:
        try:
            if Path(tmp).exists():
                Path(tmp).unlink()
        except Exception:
            pass


def append_review(entries: list):
    if not entries:
        return
    REVIEW_REPORT.parent.mkdir(parents=True, exist_ok=True)
    lines = []
    if REVIEW_REPORT.exists():
        content = REVIEW_REPORT.read_text(encoding="utf-8")
        lines.append(content)
        if content and not content.endswith("\n"):
            lines.append("\n")
    lines.append(f"\n# Review run {utc_ts()}\n\n")
    for e in entries:
        lines.append(f"- PDF: {e.get('pdf')} | Page: {e.get('page')} | Reason: {e.get('reason')}\n")
        if e.get('excerpt'):
            ex = str(e['excerpt']).replace("\n", " ")
            if len(ex) > 200:
                ex = ex[:197] + "..."
            lines.append(f"  Excerpt: {ex}\n")
        if e.get('note'):
            lines.append(f"  Note: {e['note']}\n")
    REVIEW_REPORT.write_text("".join(lines), encoding="utf-8")


def split_questions_from_text(text: str):
    if not text:
        return []
    matches = []
    for pat in NUM_PATTERNS:
        for m in pat.finditer(text):
            matches.append((m.start(), m.group(0)))
    if not matches:
        parts = re.split(r"\n\s*\n+", text)
        out = []
        for p in parts:
            p2 = p.strip()
            if len(p2) > 5:
                out.append(p2)
        return out
    matches_sorted = sorted(set((s, g) for s, g in matches), key=lambda x: x[0])
    out = []
    for i, (start, _) in enumerate(matches_sorted):
        end = matches_sorted[i + 1][0] if i + 1 < len(matches_sorted) else len(text)
        chunk = text[start:end].strip()
        if chunk:
            out.append(chunk)
    return out


def generate_answer_explanation(qtext: str):
    """Try to solve arithmetic questions and provide child-friendly explanation."""
    qt = qtext
    if DIAGRAM_CUES.search(qt):
        return "", "", True
    # Try equations
    m = re.search(r'([A-Za-z])\s*([+\-*/=])\s*([0-9]+)\s*=\s*([0-9]+)', qt)
    if m:
        var = m.group(1)
        op1 = m.group(2)
        num1 = int(m.group(3))
        res = int(m.group(4))
        if op1 == '+':
            ans = res - num1
            expl = f"1) We have {var} + {num1} = {res}.\n2) To find {var}, subtract {num1} from both sides: {var} = {res} - {num1} = {ans}.\n3) Check: {ans} + {num1} = {res}. Correct!"
            if safe_eval(f"{ans}+{num1}") == res:
                return str(ans), expl, False
        elif op1 == '-':
            ans = res + num1
            expl = f"1) We have {var} - {num1} = {res}.\n2) Add {num1} to both sides: {var} = {res} + {num1} = {ans}.\n3) Check: {ans} - {num1} = {res}. Correct!"
            if safe_eval(f"{ans}-{num1}") == res:
                return str(ans), expl, False
    # Try to find full expressions in parentheses/brackets and evaluate
    # Look for patterns like (7+5)-(16-9)=
    exprs = re.findall(r'[\(\[][^\(\)\[\]]*[\+\-\*\/][^\(\)\[\]]*[\)\]]', qt)
    # Also look for standalone expressions ending with =
    if '=' in qt and not re.match(r'^\s*\d+\.', qt.strip()) or re.match(r'^\s*\d+\.\s*.*=', qt):
        # try to extract expression before =
        m2 = re.search(r'[\d\(\)\[\]\+\-\*\/\s]+=', qt)
        if m2:
            expr = m2.group(0).rstrip('=').strip()
            # clean up OCR issues
            expr_clean = expr.replace('x', '*').replace('X', '*').replace('÷', '/').replace('—', '-').replace('–', '-')
            # verify brackets balance roughly
            if expr_clean.count('(') == expr_clean.count(')') and expr_clean.count('[') == expr_clean.count(']'):
                v = safe_eval(expr_clean)
                if v is not None:
                    if isinstance(v, float):
                        if abs(v - int(v)) < 1e-9:
                            ans_str = str(int(v))
                        else:
                            ans_str = str(v)
                    else:
                        ans_str = str(v)
                    expl = f"1) Look at the calculation: {expr_clean}.\n2) Work it out step by step, doing brackets first.\n3) The answer is {ans_str}.\n4) Let's quickly check with Python: {expr_clean} = {ans_str}. Correct!"
                    return ans_str, expl, False
    # Try simple two-number
    for expr in re.findall(r'([0-9]+(?:\.[0-9]+)?)\s*([+\-*/%xX])\s*([0-9]+(?:\.[0-9]+)?)', qt):
        a, opstr, b = expr
        opstr_clean = '*' if opstr.lower() == 'x' else opstr
        try:
            fa, fb = float(a), float(b)
            if opstr_clean == '+': res = fa + fb
            elif opstr_clean == '-': res = fa - fb
            elif opstr_clean == '*': res = fa * fb
            elif opstr_clean == '/':
                if fb == 0: continue
                res = fa / fb
            elif opstr_clean == '%': res = fa % fb
            else: continue
            v = safe_eval(f"{a}{opstr_clean}{b}")
            if v is not None and abs(float(v) - float(res)) < 1e-9:
                if res == int(res): ans_str = str(int(res))
                else: ans_str = str(res)
                expl = f"1) Look at the numbers: {a} {opstr_clean} {b}.\n2) Work it out step by step: {a} {opstr_clean} {b} = {ans_str}.\n3) Let's quickly check: {ans_str} is correct."
                return ans_str, expl, False
        except Exception:
            continue
    if re.search(r'\d', qt):
        return "", "", True
    return "", "", True


def ocr_page_text(page):
    if not OCR_AVAILABLE:
        return ""
    try:
        # render from extracted image if available, else page
        images = []
        try:
            images = page.get_images(full=True)
        except Exception:
            images = []
        if images:
            try:
                xref = images[0][0]
                base_image = page.parent.extract_image(xref)
                img_data = base_image['image']
                from io import BytesIO
                img = Image.open(BytesIO(img_data))
            except Exception:
                pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))
                img_data = pix.tobytes("png")
                from io import BytesIO
                img = Image.open(BytesIO(img_data))
        else:
            pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))
            img_data = pix.tobytes("png")
            from io import BytesIO
            img = Image.open(BytesIO(img_data))
        try:
            text = pytesseract.image_to_string(img, lang='eng')
        except Exception:
            return ""
        return text or ""
    except Exception:
        return ""


def extract_from_pdf(pdf_path: Path):
    questions = []
    review = []
    doc = fitz.open(str(pdf_path))
    try:
        for page_num in range(len(doc)):
            page = doc[page_num]
            try:
                text = page.get_text("text") or ""
            except Exception:
                text = ""
            images = []
            try:
                images = page.get_images(full=True)
            except Exception:
                images = []
            if len(text.strip()) < 20:
                if OCR_AVAILABLE:
                    ocr_text = ocr_page_text(page)
                    if ocr_text and len(ocr_text.strip()) > 20:
                        text = ocr_text
                    elif len(images) > 0:
                        review.append({
                            "pdf": pdf_path.name, "page": page_num + 1,
                            "reason": "scanned/image-only page",
                            "excerpt": text[:120], "note": "Low text yield with images present; OCR attempted"
                        })
                        continue
                else:
                    if len(images) > 0:
                        review.append({
                            "pdf": pdf_path.name, "page": page_num + 1,
                            "reason": "scanned/image-only page",
                            "excerpt": text[:120], "note": "Low text yield with images present"
                        })
                        continue
            if len(text.strip()) < 10:
                review.append({
                    "pdf": pdf_path.name, "page": page_num + 1,
                    "reason": "scanned/image-only page",
                    "excerpt": "", "note": "Very low or empty text"
                })
                continue
            has_diagram_cue = bool(DIAGRAM_CUES.search(text))
            if has_diagram_cue and len(images) > 0:
                review.append({
                    "pdf": pdf_path.name, "page": page_num + 1,
                    "reason": "diagram-dependent question",
                    "excerpt": text[:150], "note": "Diagram cues and images present"
                })
            qchunks = split_questions_from_text(text)
            if not qchunks:
                review.append({
                    "pdf": pdf_path.name, "page": page_num + 1,
                    "reason": "low-confidence extraction",
                    "excerpt": text[:150], "note": "Could not split into numbered questions"
                })
                continue
            for qc in qchunks:
                qid = stable_id(pdf_path.name, page_num + 1, qc)
                topic = "Unclassified"
                if has_diagram_cue:
                    review.append({
                        "pdf": pdf_path.name, "page": page_num + 1,
                        "reason": "diagram-dependent question",
                        "excerpt": qc[:150], "note": "Question references diagram/image"
                    })
                questions.append({
                    "question_id": qid,
                    "question": qc,
                    "questiontopic": topic,
                    "answer": "",
                    "explanation": "",
                    "_src_pdf": pdf_path.name,
                    "_src_page": page_num + 1,
                    "_has_diagram": bool(has_diagram_cue and len(images) > 0),
                })
    finally:
        doc.close()
    return questions, review


def main(argv=None):
    parser = argparse.ArgumentParser(description="Sync maths PDFs to single mat.json")
    parser.add_argument("--dry-run", action="store_true", help="Do not write mat.json or manifest")
    parser.add_argument("--pdf", action="append", help="Process only specific PDF filename(s)")
    args = parser.parse_args(argv)

    MATH_DIR.mkdir(parents=True, exist_ok=True)
    PDF_DIR.mkdir(parents=True, exist_ok=True)
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)

    all_pdfs = sorted([p for p in PDF_DIR.glob("*.pdf")])
    if args.pdf:
        wanted = set(args.pdf)
        all_pdfs = [p for p in all_pdfs if p.name in wanted]
    if not all_pdfs:
        print("No PDFs found in app/question_banks/math/pdf/")
        return 0

    manifest = read_manifest()
    to_process = []
    for p in all_pdfs:
        sha = sha256_file(p)
        old = manifest.get(p.name)
        if old is None or old != sha:
            to_process.append((p, sha))
    print(f"PDFs checked: {len(all_pdfs)}, new/changed: {len(to_process)}")

    try:
        existing = load_mat_json()
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 1
    validate_questions(existing)

    existing_by_id = {q["question_id"]: q for q in existing}
    existing_norm = {normalize_text(q["question"]): q["question_id"] for q in existing}

    new_questions_all = []
    review_all = []
    for p, sha in to_process:
        qs, rev = extract_from_pdf(p)
        review_all.extend(rev)
        for q in qs:
            new_questions_all.append(q)

    added = 0
    skipped_dup = 0
    merged = list(existing)
    seen_norm_merged = set(existing_norm.keys())
    seen_id_merged = set(existing_by_id.keys())

    for q in new_questions_all:
        qid = q["question_id"]
        qnorm = normalize_text(q["question"])
        if qid in seen_id_merged or qnorm in seen_norm_merged:
            skipped_dup += 1
            continue
        ans = ""
        expl = ""
        # Try to generate if no source answer
        g_ans, g_expl, needs_review = generate_answer_explanation(q["question"])
        if q.get("_has_diagram"):
            needs_review = True
        if not ans and not expl and g_ans and g_expl:
            ans = g_ans
            expl = g_expl
            review_all.append({
                "pdf": q.get("_src_pdf", ""),
                "page": q.get("_src_page", ""),
                "reason": "generated answer needs verification",
                "excerpt": q["question"][:150],
                "note": "Generated answer and step-by-step explanation; verify calculations"
            })
        elif needs_review or (not ans and not expl):
            # flag
            reason = "ambiguous question" if q.get("_has_diagram") or DIAGRAM_CUES.search(q["question"]) else "missing answer"
            if q.get("_has_diagram"):
                reason = "unreadable diagram"
            review_all.append({
                "pdf": q.get("_src_pdf", ""),
                "page": q.get("_src_page", ""),
                "reason": reason,
                "excerpt": q["question"][:150],
                "note": "No confident answer/explanation generated; left empty for review"
            })
        clean = {
            "question_id": qid,
            "question": q["question"],
            "questiontopic": q.get("questiontopic") or "Unclassified",
            "answer": ans,
            "explanation": expl,
        }
        merged.append(clean)
        seen_id_merged.add(qid)
        seen_norm_merged.add(qnorm)
        added += 1
        if clean["questiontopic"] == "Unclassified":
            review_all.append({
                "pdf": q.get("_src_pdf", ""),
                "page": q.get("_src_page", ""),
                "reason": "low-confidence extraction",
                "excerpt": clean["question"][:150],
                "note": "Topic unclassified"
            })

    try:
        validate_questions(merged)
    except Exception as e:
        print(f"ERROR: validation failed: {e}", file=sys.stderr)
        return 1

    print(f"Questions added: {added}, duplicates skipped: {skipped_dup}, review items: {len(review_all)}")

    if args.dry_run:
        append_review(review_all)
        print("DRY RUN: no files written")
        return 0

    if MAT_JSON.exists():
        bak = backup_mat_json()
        if bak:
            print(f"Backed up to {bak}")

    atomic_write_json(MAT_JSON, merged)
    for p, sha in to_process:
        manifest[p.name] = sha
    write_manifest(manifest)
    append_review(review_all)
    print(f"Wrote {MAT_JSON} ({len(merged)} questions total)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
