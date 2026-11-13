
import json
import re
from pathlib import Path

import fitz  # PyMuPDF


PROJECT_ROOT = Path(__file__).resolve().parents[1]

PDF_DIR = (
    PROJECT_ROOT
    / "app"
    / "question_banks"
    / "math"
    / "pdf"
)

JSON_DIR = (
    PROJECT_ROOT
    / "app"
    / "question_banks"
    / "math"
    / "json"
)


def extract_pdf_text(pdf_path: Path) -> str:
    """Extract selectable text from a PDF."""
    pages = []

    with fitz.open(pdf_path) as document:
        for page_number, page in enumerate(document, start=1):
            text = page.get_text("text")

            if not text.strip():
                print(
                    f"Review required: {pdf_path.name}, "
                    f"page {page_number} has no extractable text."
                )

            pages.append(text)

    return "\n".join(pages)


def split_questions(text: str) -> list[str]:
    """
    Split text using numbered question markers.

    This is a starting point, not a universal PDF parser.
    Check the results against the original worksheet.
    """
    pattern = re.compile(
        r"(?m)^\s*(\d{1,3})[.)]\s+"
    )

    matches = list(pattern.finditer(text))

    questions = []

    for index, match in enumerate(matches):
        start = match.start()

        if index + 1 < len(matches):
            end = matches[index + 1].start()
        else:
            end = len(text)

        question_text = text[start:end].strip()

        if question_text:
            questions.append(
                (match.group(1), question_text)
            )

    return questions


def convert_pdf(pdf_path: Path) -> dict:
    """Convert one PDF into a JSON-compatible dictionary."""
    text = extract_pdf_text(pdf_path)
    extracted_questions = split_questions(text)

    questions = []

    for number, question_text in extracted_questions:
        question_id = (
            f"{pdf_path.stem}-q{int(number):03d}"
        )

        questions.append(
            {
                "question_id": question_id,
                "question": question_text,
                "questiontopic": "Needs review",
                "answer": None,
                "explanation": None,
            }
        )

    return {
        "source_pdf": pdf_path.name,
        "questions": questions,
    }


def main() -> None:
    if not PDF_DIR.exists():
        raise FileNotFoundError(
            f"PDF input folder not found: {PDF_DIR}"
        )

    JSON_DIR.mkdir(parents=True, exist_ok=True)

    pdf_files = sorted(PDF_DIR.glob("*.pdf"))

    if not pdf_files:
        print(f"No PDF files found in {PDF_DIR}")
        return

    successful = 0
    failed = 0

    for pdf_path in pdf_files:
        output_path = JSON_DIR / f"{pdf_path.stem}.json"

        # Protect existing work.
        if output_path.exists():
            print(f"Skipped existing file: {output_path.name}")
            continue

        try:
            result = convert_pdf(pdf_path)

            with output_path.open(
                "w", encoding="utf-8"
            ) as output_file:
                json.dump(
                    result,
                    output_file,
                    ensure_ascii=False,
                    indent=2,
                )

            print(
                f"Converted {pdf_path.name}: "
                f"{len(result['questions'])} questions"
            )
            successful += 1

        except Exception as error:
            print(f"Failed {pdf_path.name}: {error}")
            failed += 1

    print("\nConversion summary")
    print(f"Successful: {successful}")
    print(f"Failed: {failed}")


if __name__ == "__main__":
    main()
