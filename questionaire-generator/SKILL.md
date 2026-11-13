---
name: questionaire-generator
description: Parses question paper PDFs into structured JSON, validates JSON integrity for missing or partial questions, persists the question bank, and generates custom sample test papers based on specific topics or random mixes.
---

# Questionnaire Generator

A comprehensive skill and Python toolkit to extract, parse, validate, persist, and generate question papers from PDF sources.

## Overview

This skill provides a complete Python-driven workflow for:
1. **PDF Parsing & Structuring**: Extracts text and questions from PDFs into a standardized JSON schema.
2. **Validation & Integrity Check**: Detects incomplete, truncated, or malformed questions, missing options, missing answers, or invalid JSON structures.
3. **JSON Persistence**: Stores structured question banks persistently in JSON format.
4. **Sample Paper Generation**: Generates custom question papers based on topic filtering or random selection (topic-wise or mixed), along with answer keys.

---

## Directory & File Structure

The skill includes robust Python scripts for executing these operations programmatically:

- `scripts/parser_validator.py`: Handles PDF parsing, JSON schema validation, partial question detection, and file persistence.
- `scripts/paper_generator.py`: Handles loading persistent JSON question banks, filtering questions by topics or generating random test papers, and saving output test papers and answer keys.

---

## JSON Data Schema

All extracted question banks follow this standard JSON format:

```json
{
  "metadata": {
    "source_pdf": "exam_paper.pdf",
    "created_at": "2026-10-27T11:00:00Z",
    "total_questions": 10
  },
  "questions": [
    {
      "id": 1,
      "topic": "Mathematics",
      "question_text": "What is the derivative of sin(x)?",
      "options": ["A) cos(x)", "B) -cos(x)", "C) tan(x)", "D) sec(x)"],
      "correct_answer": "A) cos(x)",
      "is_complete": true,
      "validation_notes": ""
    }
  ]
}
```

---

## Step-by-Step Workflow

### Step 1: Extract PDF to JSON & Validate

Run `parser_validator.py` to process an input PDF file, validate all extracted items, and save the persistent JSON.

```bash
python scripts/parser_validator.py --pdf pdf/input_paper.pdf --output question_bank.json
```

**Validation Checks performed by `parser_validator.py`:**
- Checks if `question_text` is cut off (e.g., ends abruptly with trailing prepositions/conjunctions or missing punctuation).
- Checks if options are missing or incomplete for multiple-choice questions.
- Flag any questions with `is_complete: false` and list issues under `validation_notes`.

### Step 2: Generate Sample Test Paper

Run `paper_generator.py` to create custom test papers from the saved JSON bank.

**Options:**
- **Random Mix (Default)**: Select $N$ questions randomly across all available topics.
- **Topic Specific**: Select questions filtered by one or more specific topics.

```bash
# Generate 10 random questions across all topics
python scripts/paper_generator.py --json jsonquestionbank/question_bank.json --num 10 --mode random --output sample_paper.json

# Generate 5 questions specific to "Physics" and "Chemistry"
python scripts/paper_generator.py --json jsonquestionbank/question_bank.json --num 5 --mode topic --topics "Physics" "Chemistry" --output sample_paper.json
```

---

## Script Implementation Details

Refer to `scripts/parser_validator.py` and `scripts/paper_generator.py` inside the skill directory for full Python source code.
