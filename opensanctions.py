import requests
from nlp_utils import nlp_name_scan, extract_entities
from config import OPENSANCTIONS_API_KEY

API_URL = "https://api.opensanctions.org/match/default"
API_KEY = OPENSANCTIONS_API_KEY

def fetch_opensanctions_api(inputs):
    # Extract required fields internally
    name = inputs.get("name")
    entity_type = inputs.get("entity_type")
    dob = inputs.get("date") if entity_type == "person" else None
    country = inputs.get("country")
    passport = inputs.get("passport")
    email = inputs.get("email")
    phone = inputs.get("phone")
    occupation = inputs.get("occupation")
    nationality = inputs.get("nationality")
    address=inputs.get("address")
    response = fetch_opensanctions(name, entity_type, dob, country, passport, email, phone, occupation, nationality,address)
    return response

def fetch_opensanctions(name, entity_type, dob, country, passport, email, phone, occupation, nationality,address):
    schema = "Organization" if entity_type.lower() != "person" else "Person"
    query = {
        "queries": {
            "match": {
                "schema": schema,
                "properties": {
                    "name": [name]
                }
            }
        }
    }
    for k, v in [("dob", dob), ("country", country), ("passport", passport),
                 ("email", email), ("phone", phone), ("occupation", occupation),
                 ("nationality", nationality),("address", address)]:
        if v:
            query["queries"]["match"]["properties"][k] = [v]
            
    headers = {"Authorization": f"ApiKey {API_KEY}", "Content-Type": "application/json"}
    url = API_URL + "?algorithm=logic-v2&cutoff=0.7&threshold=0.7"
    resp = requests.post(url, json=query, headers=headers)
    resp.raise_for_status()
    data = resp.json()
    results = data.get("responses", {}).get("match", {}).get("results", [])
    return results[0] if results else {}

def extract_opensanctions_data(raw, entity_type):
    rec = {}
    props = raw.get("properties", {})

    # Basic status and identity
    rec["os_status"] = "matched" if props else "no_match"
    rec["os_name"] = props.get("name", [""])[0] if props.get("name") else ""
    rec["os_aliases"] = props.get("alias", [])

    # Contact information
    rec["os_emails"] = props.get("email", [])
    rec["os_phones"] = props.get("phone", [])
    rec["os_addresses"] = props.get("address", [])
    rec["os_countries"] = props.get("country", [])

    # Topics and classification
    rec["os_topics"] = props.get("topics", [])
    rec["os_summary"] = props.get("notes", [])
    rec["os_classification"] = props.get("classification", [])

    # Citizenship and nationality
    rec["citizenships"] = props.get("citizenship", [])
    rec["nationalities"] = props.get("nationality", [])

    # Positions and roles (critical for PEP identification)
    rec["positions"] = props.get("position", [])

    # Source and metadata
    rec["source_urls"] = props.get("sourceUrl", [])
    rec["last_updated"] = props.get("modifiedAt", props.get("lastChange", ["N/A"]))[0] if isinstance(props.get("modifiedAt", props.get("lastChange", ["N/A"])), list) else props.get("modifiedAt", props.get("lastChange", "N/A"))
    rec["datasets"] = raw.get("datasets", [])

    # Person-specific fields
    if entity_type == "person":
        gender_list = props.get("gender", [])
        rec["gender"] = gender_list[0] if gender_list else "Unknown"

        birth_place_list = props.get("birthPlace", [])
        rec["birthPlace"] = birth_place_list[0] if birth_place_list else "Unknown"

        rec["os_date"] = props.get("birthDate", [props.get("createdAt", [""])[0]])[0]
    else:
        # Organization-specific fields
        rec["gender"] = None
        rec["birthPlace"] = None
        rec["os_date"] = props.get("createdAt", [""])[0]

    # PEP Status determination
    rec["pep_status"] = "Yes" if any("pep" in str(topic).lower() for topic in rec["os_topics"]) else "No"

    # Sanctions determination
    rec["sanctions"] = [topic for topic in rec["os_topics"] if "sanction" in str(topic).lower() or "crime" in str(topic).lower()]

    # Extract government/military roles from positions
    rec["gov_military_roles"] = [pos for pos in rec["positions"] if any(keyword in str(pos).lower() for keyword in ["minister", "government", "military", "parliament", "senator", "deputy"])]

    # Use NLP helper to fuzzy match best alias
    best_alias, score = nlp_name_scan(rec["os_name"], rec["os_aliases"])
    rec["best_alias_match"] = best_alias
    rec["match_score"] = score

    # Extract named entities from summary/notes using NLP
    summary_text = " ".join(rec["os_summary"]) if rec["os_summary"] else ""
    rec["nlp_entities"] = extract_entities(summary_text) if summary_text else []

    for field, default_value in {
        "positions": [],
        "pep_status": "Unknown",
        "gov_military_roles": [],
        "sanctions": [],
        "os_aliases": [],
        "os_emails": [],
    }.items():
        rec.setdefault(field, default_value)

    return rec
