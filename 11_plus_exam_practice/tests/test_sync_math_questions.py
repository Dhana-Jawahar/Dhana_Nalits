import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path


def run_converter(repo_root: Path, cwd=None, env=None, args=None):
    args = args or []
    cmd = [sys.executable, str(repo_root / "scripts" / "sync_math_questions.py")] + args
    res = subprocess.run(cmd, cwd=str(cwd or repo_root), env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return res.returncode, res.stdout.decode("utf-8"), res.stderr.decode("utf-8")


def test_new_pdfs_produce_expected_questions(tmp_path):
    repo = tmp_path / "repo"
    repo.mkdir()
    # copy script
    import shutil
    shutil.copytree(Path(__file__).parent.parent / "scripts", repo / "scripts")
    (repo / "app" / "question_banks" / "math" / "pdf").mkdir(parents=True)
    (repo / "tests").mkdir(parents=True)
    # create a synthetic PDF with text using fitz
    import fitz
    pdf_path = repo / "app" / "question_banks" / "math" / "pdf" / "test1.pdf"
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((50, 50), "1. What is 2+2?\n\n2. Solve for x: x+1=3\n")
    doc.save(str(pdf_path))
    doc.close()
    rc, out, err = run_converter(repo)
    assert rc == 0, err
    mat = json.loads((repo / "app" / "question_banks" / "math" / "mat.json").read_text())
    assert isinstance(mat, list)
    assert len(mat) == 2
    for q in mat:
        assert set(q.keys()) == {"question_id", "question", "questiontopic", "answer", "explanation"}
        assert isinstance(q["question_id"], str) and q["question_id"].startswith("math-")
        assert isinstance(q["question"], str) and q["question"].strip()
        assert isinstance(q["answer"], str)
        assert isinstance(q["explanation"], str)


def test_rerun_unchanged_pdf_no_duplicates(tmp_path):
    repo = tmp_path / "repo"
    import shutil
    shutil.copytree(Path(__file__).parent.parent / "scripts", repo / "scripts")
    (repo / "app" / "question_banks" / "math" / "pdf").mkdir(parents=True)
    import fitz
    pdf_path = repo / "app" / "question_banks" / "math" / "pdf" / "test1.pdf"
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((50, 50), "1. What is 3+3?\n")
    doc.save(str(pdf_path))
    doc.close()
    rc, out, err = run_converter(repo)
    assert rc == 0
    mat1 = json.loads((repo / "app" / "question_banks" / "math" / "mat.json").read_text())
    rc2, out2, err2 = run_converter(repo)
    assert rc2 == 0
    mat2 = json.loads((repo / "app" / "question_banks" / "math" / "mat.json").read_text())
    assert len(mat2) == len(mat1) == 1


def test_changed_pdf_detected_existing_preserved(tmp_path):
    repo = tmp_path / "repo"
    import shutil
    shutil.copytree(Path(__file__).parent.parent / "scripts", repo / "scripts")
    (repo / "app" / "question_banks" / "math" / "pdf").mkdir(parents=True)
    import fitz
    pdf_path = repo / "app" / "question_banks" / "math" / "pdf" / "test1.pdf"
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((50, 50), "1. First question?\n")
    doc.save(str(pdf_path))
    doc.close()
    rc, out, err = run_converter(repo)
    assert rc == 0
    mat1 = json.loads((repo / "app" / "question_banks" / "math" / "mat.json").read_text())
    old_id = mat1[0]["question_id"]
    # change PDF
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((50, 50), "1. First question?\n\n2. Second question?\n")
    doc.save(str(pdf_path))
    doc.close()
    rc2, out2, err2 = run_converter(repo)
    assert rc2 == 0
    mat2 = json.loads((repo / "app" / "question_banks" / "math" / "mat.json").read_text())
    assert len(mat2) == 2
    assert mat2[0]["question_id"] == old_id
    assert mat2[0]["question"] == mat1[0]["question"]


def test_duplicate_normalized_skipped(tmp_path):
    repo = tmp_path / "repo"
    import shutil
    shutil.copytree(Path(__file__).parent.parent / "scripts", repo / "scripts")
    (repo / "app" / "question_banks" / "math" / "pdf").mkdir(parents=True)
    import fitz
    # first PDF
    pdf1 = repo / "app" / "question_banks" / "math" / "pdf" / "a.pdf"
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((50, 50), "1. What is 5+5?\n")
    doc.save(str(pdf1))
    doc.close()
    rc, out, err = run_converter(repo)
    assert rc == 0
    # second PDF with same question different spacing/case
    pdf2 = repo / "app" / "question_banks" / "math" / "pdf" / "b.pdf"
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((50, 50), "1.   WHAT   IS   5+5?   \n")
    doc.save(str(pdf2))
    doc.close()
    rc2, out2, err2 = run_converter(repo)
    assert rc2 == 0
    mat = json.loads((repo / "app" / "question_banks" / "math" / "mat.json").read_text())
    assert len(mat) == 1


def test_stable_ids_deterministic(tmp_path):
    repo = tmp_path / "repo"
    import shutil
    shutil.copytree(Path(__file__).parent.parent / "scripts", repo / "scripts")
    (repo / "app" / "question_banks" / "math" / "pdf").mkdir(parents=True)
    import fitz
    pdf_path = repo / "app" / "question_banks" / "math" / "pdf" / "test1.pdf"
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((50, 50), "1. Test question\n")
    doc.save(str(pdf_path))
    doc.close()
    rc, out, err = run_converter(repo)
    assert rc == 0
    mat1 = json.loads((repo / "app" / "question_banks" / "math" / "mat.json").read_text())
    id1 = mat1[0]["question_id"]
    rc2, out2, err2 = run_converter(repo)
    assert rc2 == 0
    mat2 = json.loads((repo / "app" / "question_banks" / "math" / "mat.json").read_text())
    id2 = mat2[0]["question_id"]
    assert id1 == id2


def test_missing_answers_flagged(tmp_path):
    repo = tmp_path / "repo"
    import shutil
    shutil.copytree(Path(__file__).parent.parent / "scripts", repo / "scripts")
    (repo / "app" / "question_banks" / "math" / "pdf").mkdir(parents=True)
    import fitz
    pdf_path = repo / "app" / "question_banks" / "math" / "pdf" / "test1.pdf"
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((50, 50), "1. Question without answer\n")
    doc.save(str(pdf_path))
    doc.close()
    rc, out, err = run_converter(repo)
    assert rc == 0
    mat = json.loads((repo / "app" / "question_banks" / "math" / "mat.json").read_text())
    assert mat[0]["answer"] == ""
    assert mat[0]["explanation"] == ""
    review = (repo / "app" / "question_banks" / "math" / "review_report.md").read_text()
    assert "review" in review.lower() or "missing" in review.lower() or "unclassified" in review.lower()


def test_scanned_empty_pages_flagged(tmp_path):
    repo = tmp_path / "repo"
    import shutil
    shutil.copytree(Path(__file__).parent.parent / "scripts", repo / "scripts")
    (repo / "app" / "question_banks" / "math" / "pdf").mkdir(parents=True)
    import fitz
    pdf_path = repo / "app" / "question_banks" / "math" / "pdf" / "test1.pdf"
    doc = fitz.open()
    page = doc.new_page()
    # insert image-like low text? easier: page with no text
    doc.save(str(pdf_path))
    doc.close()
    rc, out, err = run_converter(repo)
    assert rc == 0
    review = (repo / "app" / "question_banks" / "math" / "review_report.md").read_text()
    assert "scanned" in review.lower() or "image" in review.lower()


def test_invalid_json_causes_no_write(tmp_path):
    repo = tmp_path / "repo"
    import shutil
    shutil.copytree(Path(__file__).parent.parent / "scripts", repo / "scripts")
    (repo / "app" / "question_banks" / "math" / "pdf").mkdir(parents=True)
    (repo / "app" / "question_banks" / "math").mkdir(parents=True, exist_ok=True)
    (repo / "app" / "question_banks" / "math" / "mat.json").write_text("{not json")
    import fitz
    pdf_path = repo / "app" / "question_banks" / "math" / "pdf" / "test1.pdf"
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((50, 50), "1. Q\n")
    doc.save(str(pdf_path))
    doc.close()
    rc, out, err = run_converter(repo)
    assert rc != 0
    # should still be invalid
    content = (repo / "app" / "question_banks" / "math" / "mat.json").read_text()
    assert content.startswith("{not")


def test_backup_created_before_update(tmp_path):
    repo = tmp_path / "repo"
    import shutil
    shutil.copytree(Path(__file__).parent.parent / "scripts", repo / "scripts")
    (repo / "app" / "question_banks" / "math" / "pdf").mkdir(parents=True)
    (repo / "app" / "question_banks" / "math").mkdir(parents=True, exist_ok=True)
    (repo / "app" / "question_banks" / "math" / "mat.json").write_text("[]")
    import fitz
    pdf_path = repo / "app" / "question_banks" / "math" / "pdf" / "test1.pdf"
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((50, 50), "1. New Q\n")
    doc.save(str(pdf_path))
    doc.close()
    rc, out, err = run_converter(repo)
    assert rc == 0
    backups = list((repo / "app" / "question_banks" / "math" / "backups").glob("mat.json.*.bak"))
    assert len(backups) >= 1


def test_only_mat_json_created_no_per_pdf_json(tmp_path):
    repo = tmp_path / "repo"
    import shutil
    shutil.copytree(Path(__file__).parent.parent / "scripts", repo / "scripts")
    (repo / "app" / "question_banks" / "math" / "pdf").mkdir(parents=True)
    import fitz
    pdf_path = repo / "app" / "question_banks" / "math" / "pdf" / "test1.pdf"
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((50, 50), "1. Q\n")
    doc.save(str(pdf_path))
    doc.close()
    rc, out, err = run_converter(repo)
    assert rc == 0
    # check no other json question banks
    for p in repo.rglob("*.json"):
        if p.name == "mat.json":
            continue
        # allow package files? no, but in tmp repo only our files
        assert False, f"Unexpected json: {p}"
