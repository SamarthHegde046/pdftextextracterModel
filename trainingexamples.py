import fitz
import re
import json

def extract_text_from_pdf(path):
    doc = fitz.open(path)
    text = " ".join([page.get_text("text") for page in doc])
    doc.close()
    return text

def clean_vtu_result_text(raw_text):
    # Keep only content from "Semester" onward
    sem_start = re.search(r"Semester\s*:\s*\d+", raw_text)
    if sem_start:
        raw_text = raw_text[sem_start.start():]
    
    # Stop after last line ending with 3-digit marks
    match_lines = re.findall(r".*?\d{1,3}\s+\d{1,3}\s+(\d{1,3})\s*", raw_text)
    if match_lines:
        last_match = list(re.finditer(r".*?\d{1,3}\s+\d{1,3}\s+(\d{1,3})\s*", raw_text))[-1]
        raw_text = raw_text[:last_match.end()]
    
    return raw_text.strip()

def auto_label_vtu_text(text):
    train_data = []

    text = re.sub(r"\n", " ", text)  # clean line breaks

    # Match subject code + marks line
    pattern = re.compile(
        r"([A-Z]{3,}[0-9]{3,}[A-Z0-9]*)\s+([A-Z&]+(?: [A-Z]+)*?)\s+(\d{1,3})\s+(\d{1,3})\s+(\d{1,3})"
    )

    for match in pattern.finditer(text):
        subcode = match.group(1)
        total = match.group(5)

        start_subcode = match.start(1)
        end_subcode = match.end(1)
        start_total = match.start(5)
        end_total = match.end(5)

        train_data.append((
            match.group(0),
            {
                "entities": [
                    (start_subcode - match.start(0), end_subcode - match.start(0), "SUBCODE"),
                    (start_total - match.start(0), end_total - match.start(0), "TMARK")
                ]
            }
        ))

    # Extract semester separately
    sem_pattern = re.compile(r"Semester\s*:\s*(\d+)")
    for sem_match in sem_pattern.finditer(text):
        sem = sem_match.group(1)
        line = sem_match.group(0)
        start_sem = line.find(sem)
        end_sem = start_sem + len(sem)
        train_data.append((
            line.strip(),
            {
                "entities": [(start_sem, end_sem, "SEM")]
            }
        ))

    return train_data

# PDF paths
pdf_paths = [
    "VTU Result 2024 (1) (1).pdf",
    "VTU Result 2024 (3).pdf",
    "VTU Result 2025 imp.pdf",
    "VTU Result 2025.pdf",
    "VTU Result 2024.pdf",
    "VTU Result 2025(5).pdf",
    "VTU Result 2025(6).pdf"
]

all_training_data = []

for path in pdf_paths:
    raw = extract_text_from_pdf(path)
    cleaned = clean_vtu_result_text(raw)
    labeled = auto_label_vtu_text(cleaned)
    all_training_data.extend(labeled)

# Save to training_data.py
with open("training_data.py", "w") as f:
    f.write("TRAIN_DATA = ")
    json.dump(all_training_data, f, indent=2)

print(f"✅ Generated {len(all_training_data)} examples saved to training_data.py")
