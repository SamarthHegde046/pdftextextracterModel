from flask import Flask, request, jsonify
from flask_cors import CORS
import spacy
from extract_utils import extract_text_from_pdf, clean_vtu_result_text

app = Flask(__name__)

# ✅ Allow requests from any origin including file://
CORS(app, resources={r"/*": {"origins": "*"}})

nlp = spacy.load("vtu_model")

@app.route("/")
def home():
    return jsonify({"message": "VTU Extractor API is running."})

@app.route("/extract", methods=["POST"])
def extract_info():
    if 'pdf' not in request.files:
        return jsonify({'error': 'No PDF uploaded'}), 400

    pdf_file = request.files['pdf']
    raw_text = extract_text_from_pdf(pdf_file)
    cleaned_text = clean_vtu_result_text(raw_text)

    doc = nlp(cleaned_text)

    result = {"SEM": [], "SUBCODE": [], "TMARK": []}
    for ent in doc.ents:
        label = ent.label_
        value = ent.text.strip()

        if label in result and value not in result[label]:
            result[label].append(value)

    return jsonify(result)

if __name__ == "__main__":
    app.run(debug=True)
