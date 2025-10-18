import spacy
from rapidfuzz import fuzz

# Load the small English model (make sure to install with: python -m spacy download en_core_web_sm)
nlp = spacy.load("en_core_web_sm")

def nlp_name_scan(name, aliases):
    """
    Perform fuzzy matching between the main name and a list of aliases.
    Returns the best matching alias and its similarity score.
    """
    name_doc = nlp(name.lower())
    max_score = 0
    best_alias = None
    for alias in aliases:
        alias_doc = nlp(alias.lower())
        score = fuzz.ratio(name_doc.text, alias_doc.text)
        if score > max_score:
            max_score = score
            best_alias = alias
    return best_alias, max_score

def extract_entities(text):
    """
    Perform Named Entity Recognition (NER) on the input text.
    Returns a list of (entity_text, entity_label) tuples.
    """
    doc = nlp(text)
    return [(ent.text, ent.label_) for ent in doc.ents]
