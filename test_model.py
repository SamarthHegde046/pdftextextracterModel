import spacy

nlp = spacy.load("vtu_model")

text = "BCS401 DATABASE SYSTEMS 48 32 80\nSemester : 4  \n hai hello how are you \n BCS403 DATABASE MANAGEMENT 48 50 98"
doc = nlp(text)

for ent in doc.ents:
    print(ent.label_, ent.text)
