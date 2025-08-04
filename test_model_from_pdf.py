import fitz
import re
import spacy 

nlp = spacy.load("vtu_model")
def extract_text_from_pdf(file_path):
    doc = fitz.open(file_path)
    text = "\n".join([page.get_text("text") for page in doc])
    doc.close()
    return text

def clean_vtu_result_text(text):
    # STEP 1: Start from "Semester :"
    sem_match = re.search(r"Semester\s*:\s*\d+", text)
    if not sem_match:
        return ""

    text = text[sem_match.start():]  # Cut everything before "Semester :"
    
    # STEP 2: Capture the entire "Semester : X" line separately
    sem_line = text.splitlines()[0].strip()

    # STEP 3: Collect subject lines from that point forward
    lines = text.splitlines()
    combined_lines = []
    current = ""
    
    subject_line_pattern = re.compile(r"([A-Z]{3,}[0-9]{3,}[A-Z0-9]*)\s+.*?\s+(\d{1,3})\s+(\d{1,3})\s+(\d{1,3})")

    for line in lines[1:]:  # Skip "Semester : X"
        line = line.strip()
        if not line:
            continue

        current += " " + line  # Build potential multiline subject entry

        # Try matching the combined line
        match = subject_line_pattern.search(current)
        if match:
            clean_line = match.group(0).strip()
            combined_lines.append(clean_line)
            current = ""  # Reset for next entry

    # Combine everything into final formatted string
    formatted_text = sem_line + "\n" + "\n".join(combined_lines)
    return formatted_text.strip()

def test_pdf_model(file_path):
    raw_text = extract_text_from_pdf(file_path)
    cleaned = clean_vtu_result_text(raw_text)

    doc = nlp(cleaned)

    result = {"SUBCODE": [], "TMARK": [], "SEM": []}
    for ent in doc.ents:
        if ent.label_ in result:
            if re.match(r"^[\w\d]+$", ent.text):  # Filter valid alphanumeric values
                result[ent.label_].append(ent.text)

    return result

# Path to your PDF
pdf_path = "VTU Result 2025 imp.pdf"

# Run model on cleaned PDF text
result = test_pdf_model(pdf_path)

print("✅ Model Output from PDF:")
print("\nSemester:", result["SEM"])
print("Subject Codes and Total Marks:\n")
for subcode, mark in zip(result["SUBCODE"], result["TMARK"]):
    print(f"{subcode} → {mark}")

