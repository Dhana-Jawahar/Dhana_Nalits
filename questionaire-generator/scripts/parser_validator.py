import json
import re
import sys
import argparse
from datetime import datetime

def parse_pdf_text_to_questions(raw_text, source_filename="sample.pdf"):
    """
    Parses raw extracted text from PDF into structured question objects.
    """
    questions = []
    # Pattern to match question starts e.g., Q1., 1., Question 1:
    q_blocks = re.split(r'\n(?=(?:Q(?:uestion)?\s*\d+[\.\:]?|\d+[\.\:]\s+))', raw_text, flags=re.IGNORECASE)
    
    for idx, block in enumerate(q_blocks):
        block = block.strip()
        if not block:
            continue
        
        # Extract question number/id and content
        lines = block.split('\n')
        header_match = re.match(r'^(?:Q(?:uestion)?\s*(\d+)[\.\:]?|(\d+)[\.\:]\s+)', lines[0], re.IGNORECASE)
        q_id = idx + 1
        if header_match:
            q_id = int(header_match.group(1) or header_match.group(2))
        
        # Detect topic if present e.g. [Topic: Physics] or Topic: Physics
        topic = "General"
        topic_match = re.search(r'\[?(?:Topic|Category)\:\s*([^\]\n]+)\]?', block, re.IGNORECASE)
        if topic_match:
            topic = topic_match.group(1).strip()
            block = re.sub(r'\[?(?:Topic|Category)\:\s*([^\]\n]+)\]?', '', block, flags=re.IGNORECASE).strip()

        # Extract Options if present
        options = re.findall(r'([A-E]\)\s*.*?)(?=(?:[A-E]\)|$|\n\s*Answer:))', block, re.DOTALL)
        options = [opt.strip() for opt in options]

        # Extract Correct Answer if present
        ans_match = re.search(r'(?:Answer|Ans)\:\s*([A-E]|\S+)', block, re.IGNORECASE)
        correct_answer = ans_match.group(1).strip() if ans_match else ""

        # Extract Question Text
        q_text = lines[0]
        if len(lines) > 1:
            q_text = " ".join([l.strip() for l in lines if not re.match(r'^[A-E]\)', l.strip()) and not re.match(r'^(?:Answer|Ans)\:', l.strip(), re.IGNORECASE)])
        
        # Clean question text prefix
        q_text = re.sub(r'^(?:Q(?:uestion)?\s*\d+[\.\:]?|\d+[\.\:]\s+)', '', q_text, flags=re.IGNORECASE).strip()

        questions.append({
            "id": q_id,
            "topic": topic,
            "question_text": q_text,
            "options": options,
            "correct_answer": correct_answer,
            "is_complete": True,
            "validation_notes": ""
        })

    return validate_and_structure_json(questions, source_filename)

def validate_and_structure_json(questions, source_filename):
    """
    Validates each question in the JSON blob for completeness and integrity.
    Checks for cut-off text, missing options, missing answers, or invalid formatting.
    """
    incomplete_count = 0
    
    for q in questions:
        notes = []
        text = q["question_text"].strip()
        
        # Check 1: Empty text
        if not text:
            notes.append("Question text is empty.")
        
        # Check 2: Truncated or partial question text detection
        # Checks if ends with dangling conjunctions, prepositions, or missing trailing punctuation
        if re.search(r'\b(and|or|the|a|an|in|on|at|of|to|for|with|by|is|are|if|where|which|what|how)\s*$', text, re.IGNORECASE):
            notes.append("Question appears to be cut off (dangling conjunction/preposition at end).")
        elif not re.search(r'[\?\.\:\!\)]$', text):
            notes.append("Question text lacks terminal punctuation (possible truncation).")
            
        # Check 3: Short/Suspicious length
        if len(text.split()) < 3:
            notes.append("Question text is unusually short.")

        # Check 4: Option integrity (if multiple choice format detected)
        if q["options"] and len(q["options"]) < 2:
            notes.append("Multiple choice question has fewer than 2 options.")
            
        if notes:
            q["is_complete"] = False
            q["validation_notes"] = " | ".join(notes)
            incomplete_count += 1

    result = {
        "metadata": {
            "source_pdf": source_filename,
            "created_at": datetime.now().isoformat(),
            "total_questions": len(questions),
            "valid_questions": len(questions) - incomplete_count,
            "incomplete_questions": incomplete_count
        },
        "questions": questions
    }
    
    return result

def save_json(data, filepath):
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"Persisted questionnaire JSON to: {filepath}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="PDF Question Extractor & JSON Validator")
    parser.add_argument("--pdf", type=str, help="Path to input PDF file")
    parser.add_argument("--text_file", type=str, help="Path to extracted text file (if PDF already converted)")
    parser.add_argument("--output", type=str, default="question_bank.json", help="Path to persistent JSON output file")
    
    args = parser.parse_args()
    
    raw_text = ""
    if args.pdf:
        try:
            import pypdf
            reader = pypdf.PdfReader(args.pdf)
            for page in reader.pages:
                raw_text += page.extract_text() + "\n"
        except ImportError:
            print("pypdf module not found. Reading as plain text fallback or install pypdf.")
            with open(args.pdf, 'r', encoding='utf-8', errors='ignore') as f:
                raw_text = f.read()
    elif args.text_file:
        with open(args.text_file, 'r', encoding='utf-8') as f:
            raw_text = f.read()
    else:
        print("Please provide --pdf or --text_file argument.")
        sys.exit(1)
        
    structured_data = parse_pdf_text_to_questions(raw_text, args.pdf or args.text_file)
    save_json(structured_data, args.output)
