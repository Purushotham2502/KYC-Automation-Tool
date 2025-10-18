import requests
import spacy
from config import NAMESCAN_API_KEY

# Constants for API URLs and Key
PERSON_URL = "https://api.namescan.io/v2/person-scans/emerald"
ORG_URL = "https://api.namescan.io/v2/organisation-scans/emerald"
API_KEY = NAMESCAN_API_KEY

# Load spaCy English model once globally
nlp = spacy.load("en_core_web_sm")


def is_valid_name(name):
    """
    Use NLP to check if input name contains person entities.
    """
    doc = nlp(name)
    return any(ent.label_ == "PERSON" for ent in doc.ents)


def fetch_namescan_api(inputs):
    """
    Main function to fetch and extract Namescan data given input fields.
    Returns fully processed dictionary ready for use.
    """
    entity_type = inputs.get("entity_type", "person").lower()
    name = inputs.get("name", "")

    if entity_type == "person":
        if not is_valid_name(name):
            print(f"Warning: Input name '{name}' does not look like a valid person name.")
            # Optional: return None or continue based on your policy
    elif entity_type == "organization":
        # Skip person name validation for organizations
        pass
    else:
        print(f"Warning: Unknown entity_type '{entity_type}', assuming person for validation.")
        if not is_valid_name(name):
            print(f"Warning: Input name '{name}' does not look like a valid person name.")

    payload = build_payload(inputs, entity_type)
    raw_response = fetch_namescan(payload, entity_type)

    if not raw_response:
        return None

    extracted_data = extract_namescan_data(raw_response, entity_type)
    return extracted_data



def build_payload(inputs, entity_type):
    """
    Dynamically build request payload filtering out empty values.
    """
    date_key = "dateOfBirth" if entity_type == "person" else "dateEstablished"
    mapping = {
        "name": inputs.get("name"),
        date_key: inputs.get("date"),
        "country": inputs.get("country"),
        "passport": inputs.get("passport"),
        "email": inputs.get("email"),
        "phone": inputs.get("phone"),
        "occupation": inputs.get("occupation"),
        "nationality": inputs.get("nationality"),
        "address": inputs.get("address")
    }
    return {k: v for k, v in mapping.items() if v}


def fetch_namescan(payload, entity_type):
    """
    Perform HTTP POST to Namescan API with payload and return JSON response.
    """
    url = ORG_URL if entity_type == "organization" else PERSON_URL
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "api-key": API_KEY
    }

    try:
        #print("Sending payload:", payload)
        resp = requests.post(url, json=payload, headers=headers)
        #print("Response status:", resp.status_code)
        resp.raise_for_status()
        #print("Response data:", resp.text)
        return resp.json()
    except requests.exceptions.RequestException as e:
        print(f"API request failed: {e}")
        return None


def extract_namescan_data(raw, entity_type):
    """
    Extract relevant fields from raw API response with proper field mappings.
    Fixed to handle snake_case API response keys.
    """
    rec = {
        "scanId": raw.get("scan_id"),  # Fixed: was scanId, should be scan_id
        "scan_date": raw.get("date"),
        "matches": raw.get("number_of_matches", 0),  # Fixed: was numberOfMatches
        "pep_matches": raw.get("number_of_pep_matches", 0),  # Fixed: was numberOfPepMatches
        "sip_matches": raw.get("number_of_sip_matches", 0),  # Fixed: was numberOfSipMatches
        "positions": [],
        "pep_status": "Unknown",
        "gov_military_roles": [],
        "sanctions": [],
        "adverse_media": [],
        "risk_summary": raw.get("summary", ""),
        "os_aliases": [],
        "os_emails": [],
        "nationalities": [],
        "political_parties": [],
        "images": [],
        "links": [],
        "father": None,
        "mother": None,
        "spouse": None
    }

    key = "persons" if entity_type == "person" else "organisations"
    items = raw.get(key, [])
    if not items:
        return rec

    item = items[0]

    rec["name"] = item.get("name")
    rec["uid"] = item.get("uid")
    rec["matchRate"] = item.get("match_rate")  # Fixed: was matchRate
    rec["categories"] = item.get("categories", [])
    rec["category"] = item.get("category", "")
    rec["gender"] = item.get("gender")
    rec["first_name"] = item.get("first_name")
    rec["last_name"] = item.get("last_name")
    rec["original_script_name"] = item.get("original_script_name")

    contacts = item.get("contacts", [])
    rec["contacts"] = {c["type"]: c["value"] for c in contacts if "type" in c and "value" in c}
    rec["emails_ns"] = [c["value"] for c in contacts if c.get("type", "").lower() == "email"]
    rec["phones_ns"] = [c["value"] for c in contacts if c.get("type", "").lower() in ["phone", "phone number"]]

    if entity_type == "person":
        # Fixed: handle dates_of_birth array properly
        dates_of_birth = item.get("dates_of_birth", [])
        rec["dateOfBirth"] = dates_of_birth[0].get("date") if dates_of_birth else None
        
        # Fixed: handle places_of_birth
        places_of_birth = item.get("places_of_birth", [])
        rec["place_of_birth"] = places_of_birth[0] if places_of_birth else None
        
        rec["nationalities_ns"] = item.get("nationalities", [])
        rec["citizenship"] = item.get("citizenship", "")
        rec["occupations"] = item.get("occupations", [])
        rec["father"] = item.get("father")
        rec["mother"] = item.get("mother")
        rec["spouse"] = item.get("spouse")
    else:
        rec["dateEstablished"] = item.get("date_established")  # Fixed: snake_case
        rec["category"] = item.get("category", "")

    # Fixed: handle places/addresses properly
    rec["addresses"] = item.get("addresses", [])
    rec["places"] = item.get("places", [])
    
    rec["summary"] = item.get("summary", "")
    rec["associates"] = item.get("associates", [])

    # Extract positions from roles
    roles = item.get("roles", [])
    rec["positions"] = [role.get("title", "") for role in roles]
    rec["roles_details"] = roles  # Keep full role details with dates

    # Political parties
    rec["political_parties"] = item.get("political_parties", [])

    # Determine PEP status properly
    rec["pep_status"] = "Yes" if (rec.get("pep_matches", 0) > 0 
                                  or rec.get("category", "").upper() == "PEP"
                                  or item.get("category", "").upper() == "PEP") else "No"

    # NLP-enhanced government/military roles detection
    rec["gov_military_roles"] = nlp_detect_gov_military_roles(rec["positions"])

    # Extract sanctions - if available
    rec["sanctions"] = item.get("sanctions", [])

    # Extract adverse media alerts if present
    rec["adverse_media"] = item.get("adverse_media", [])
    rec["adverseMedia"] = item.get("adverseMedia", [])

    # Extract aliases from other_names
    other_names = item.get("other_names", [])
    rec["os_aliases"] = [alias.get("name") for alias in other_names if "name" in alias]
    rec["aliases_details"] = other_names  # Keep full alias details with types

    # Images and links
    rec["images"] = item.get("images", [])
    rec["links"] = item.get("links", [])
    
    # Identities (IDs from various sources)
    rec["identities"] = item.get("identities", [])

    # Extract reference type
    rec["reference_type"] = item.get("reference_type", "")

    return rec


def nlp_detect_gov_military_roles(positions):
    """
    Use NLP to detect government or military roles by keyword and entity recognition.
    """
    keywords = {"minister", "government", "military", "chief minister", "prime minister", 
                "president", "senator", "parliament", "congress", "secretary", "governor"}
    relevant_positions = []

    for pos in positions:
        doc = nlp(pos.lower())
        # Check if any entities or keywords indicating government/military role are present
        if any(ent.label_ in {"ORG", "GPE", "PERSON"} for ent in doc.ents):
            if any(kw in pos.lower() for kw in keywords):
                relevant_positions.append(pos)
        else:
            # Also include if just matches keywords without entities
            if any(kw in pos.lower() for kw in keywords):
                relevant_positions.append(pos)
    return relevant_positions


# Example usage




    