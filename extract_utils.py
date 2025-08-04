# extract_utils.py
import fitz  # PyMuPDF
import re
import spacy

# Load the custom NER model
nlp = spacy.load("vtu_model")

def extract_text_from_pdf(pdf_file):
    # ✅ Support uploaded file from Flask request.files['pdf']
    doc = fitz.open(stream=pdf_file.read(), filetype="pdf")
    text = "\n".join([page.get_text("text") for page in doc])
    doc.close()
    return text


def clean_vtu_result_text(text):
    # Step 1: Find where "Semester :" starts
    sem_match = re.search(r"Semester\s*:\s*\d+", text)
    if not sem_match:
        return ""

    # Trim everything before "Semester :"
    text = text[sem_match.start():]

    # Get the "Semester : X" line
    sem_line = text.splitlines()[0].strip()

    lines = text.splitlines()
    combined_lines = []
    current = ""

    # Pattern: subject code + some name + 3 marks (ends with total)
    subject_line_pattern = re.compile(
        r"([A-Z]{3,}[0-9]{3,}[A-Z0-9]*)\s+.*?\s+(\d{1,3})\s+(\d{1,3})\s+(\d{1,3})"
    )

    for line in lines[1:]:  # skip semester line
        line = line.strip()
        if not line:
            continue

        current += " " + line  # append to current line (to support multiline subjects)

        match = subject_line_pattern.search(current)
        if match:
            clean_line = match.group(0).strip()
            combined_lines.append(clean_line)
            current = ""

    # Final formatted text
    formatted_text = sem_line + "\n" + "\n".join(combined_lines)
    return formatted_text.strip()

def test_pdf_model(file_path):
    raw_text = extract_text_from_pdf(file_path)
    cleaned = clean_vtu_result_text(raw_text)

    doc = nlp(cleaned)

    result = {"SUBCODE": [], "TMARK": [], "SEM": []}
    for ent in doc.ents:
        if ent.label_ in result:
            if re.match(r"^[\w\d]+$", ent.text):
                result[ent.label_].append(ent.text)

    return result
