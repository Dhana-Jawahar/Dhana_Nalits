
---
name: pdf-to-question-json
description: Convert 11+ maths worksheet PDFs into structured JSON question banks, preserving question text and extracting answers and explanations only when supported by the source.
---

# PDF to Question JSON Converter

## Objective

Convert all PDF worksheets in:

app/question_banks/math/pdf/

into JSON files saved in:

app/question_banks/math/json/

Use Python for PDF extraction, question parsing, validation and JSON writing.

## Required JSON structure

Each output file must contain:

- source_pdf
- questions

Each question must contain exactly these fields:

- question_id
- question
- questiontopic
- answer
- explanation

Use null for an answer or explanation that cannot be
reliably extracted or verified.

## Question IDs

Generate a unique, stable ID using the source PDF
filename and question number.

Example: mat-3-q001

Do not create duplicate IDs within a question bank.

## Extraction rules

1. Process every PDF in the input folder.
2. Preserve the original question wording.
3. Preserve answer options, mathematical notation and
   references to diagrams where possible.
4. Identify question boundaries using numbering and
   document structure.
5. Assign a topic only when it can be identified
   reliably. Otherwise use "Needs review".
6. Extract answers and explanations only when supported
   by the PDF or a verified answer key.
7. Never invent missing answers or explanations.
8. Flag scanned pages, missing text, ambiguous
   question boundaries and diagram-dependent questions
   for review.
9. Do not modify or delete source PDFs.
10. Do not overwrite existing JSON files without
    an explicit user-approved option.

## Implementation requirements

- Use Python and PyMuPDF for PDF text extraction.
- Use pathlib for file paths.
- Use json for JSON output.
- Validate the output against the required schema.
- Handle errors for individual PDFs without stopping
  the entire batch.
- Print a summary of successful files, failed files
  and questions requiring review.
- Write UTF-8 JSON with readable indentation.

## Testing

Test at least one PDF before processing the entire
folder.

Verify:
- Every JSON file is valid.
- Every question has the five required fields.
- Question IDs are unique.
- Missing values are null or explicitly flagged.
- Source PDFs remain unchanged.

Do not claim perfect extraction when the PDF contains
scanned pages, diagrams or ambiguous formatting.
