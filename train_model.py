import spacy
from spacy.training.example import Example
from training_data import TRAIN_DATA

# 1. Create blank English pipeline
nlp = spacy.blank("en")

# 2. Add NER to the pipeline
ner = nlp.add_pipe("ner")

# 3. Add your custom labels
ner.add_label("SUBCODE")
ner.add_label("TMARK")
ner.add_label("SEM")

# 4. Begin training
optimizer = nlp.begin_training()

for epoch in range(80): 
    print(f"🌀 Epoch {epoch+1}")
    losses = {}
    for text, annotations in TRAIN_DATA:
        doc = nlp.make_doc(text)
        example = Example.from_dict(doc, annotations)
        nlp.update([example], drop=0.3, sgd=optimizer, losses=losses)
    print("Loss:", losses)

# 5. Save the model
output_dir = "vtu_model"
nlp.to_disk(output_dir)
print(f"\n✅ Model trained and saved to '{output_dir}'")
