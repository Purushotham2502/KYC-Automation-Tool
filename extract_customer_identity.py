import requests
from io import BytesIO
from PIL import Image
from combiner import analyze_risk_from_text, extract_adverse_media
import spacy

nlp = spacy.load("en_core_web_sm")

SOCIAL_CONTACT_FIELDS = {
    "Twitter": "twitter",
    "Facebook": "facebook",
    "Instagram": "instagram"
}

def detect_gov_roles(positions):
    gov_roles = []
    for pos in positions:
        text = pos.lower()
        for keyword in ["prime minister", "chief minister", "member of the lok sabha", "minister", "leader of the house", "head, dept.,CM office", "governor", "cabinet secretary", "judge", "justice", "ambassador", "senator", "representative", "congressman", "congresswoman", "mp ", "m.p.", "m.p", "member of parliament", "secretary of state", "secretary", "attorney general", "chancellor", "mayor", "councilor", "councillor", "director general", "director", "commissioner", "inspector", "admiral", "general ", "colonel", "lieutenant", "sergeant", "captain", "officer","president", "prime minister", "vice president", "head of state"]:
            if keyword in text:
                gov_roles.append(pos)
                break
    return gov_roles or ['None']

def fetch_profile_image_url(data):
    # Returns URL string or None
    for key in ('profile_image_url', 'profile_image', 'images', 'image_urls'):
        val = data.get(key)
        if val:
            if isinstance(val, list):
                if val:
                    return val[0]
            elif isinstance(val, str):
                return val
    return None

def download_image(url):
    if not url:
        return None
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    try:
        resp = requests.get(url, headers=headers, timeout=8)
        resp.raise_for_status()
        if 'image' not in resp.headers.get('Content-Type', ''):
            return None  # Not an image response
        return Image.open(BytesIO(resp.content))
    except Exception as e:
        print(f"Error downloading image from {url}: {e}")
        return None

def extract_social_handles(data):
    socials = {}

    # Prefer explicit 'social_handles'
    social_direct = data.get('social_handles', {})
    for k in ['Twitter', 'Facebook', 'Instagram']:
        if social_direct.get(k):
            socials[k] = social_direct[k]

    if not socials:
        contacts = data.get('contacts', {})
        for label, keyword in SOCIAL_CONTACT_FIELDS.items():
            for field, value in contacts.items():
                if keyword in field.lower():
                    if not value.lower().startswith(('http://', 'https://')):
                        if label == 'Twitter':
                            value = f"https://twitter.com/{value}"
                        elif label == 'Facebook':
                            value = f"https://facebook.com/{value}"
                        elif label == 'Instagram':
                            value = f"https://instagram.com/{value}"
                    socials[label] = value
    return socials if socials else {'None': 'None'}

def extract_customer_identity(merged_record):
    info = {}
    info['Full Legal Name'] = merged_record.get('name', 'Unknown')
    info['Aliases'] = merged_record.get('aliases', [])

    info['Date of Birth'] = merged_record.get('birth_date', 'Unknown')
    gender = merged_record.get('gender', 'Unknown').lower()
    if gender in ['', 'unknown', 'none', 'n/a']:
        gender = 'Unknown'
    info['Gender'] = gender

    bp = merged_record.get('birth_place')
    if isinstance(bp, dict):
        location = bp.get('location', '')
        country = bp.get('country', '')
        birthplace = f"{location} ({country})" if location and country else location or country or 'Unknown'
    else:
        birthplace = bp or 'Unknown'
    info['Place of Birth'] = birthplace

    contact_info = merged_record.get('Contact Information', {})
    info['Contact Information'] = {
        'Emails': contact_info.get('Emails', merged_record.get('emails', ['Unknown'])),
        'Phones': contact_info.get('Phones', merged_record.get('phones', ['Unknown'])),
        'Addresses': contact_info.get('Addresses', merged_record.get('addresses', ['Unknown'])),
        'Country of Residence': contact_info.get('Country of Residence', ', '.join(merged_record.get('citizenship', ['Unknown'])))
    }

    info['Social Media'] = extract_social_handles(merged_record)

    img_url = fetch_profile_image_url(merged_record)
    info['Profile Image URL'] = img_url
    info['Profile Image'] = download_image(img_url)

    info['Government IDs'] = {
        'UID': merged_record.get('uid', 'Unknown'),
        'Wikidata ID': merged_record.get('wikidata_id', 'Unknown')
    }

    citizenships = merged_record.get('citizenship', ['Unknown'])
    info['Citizenship(s)'] = citizenships
    info['Nationality'] = ', '.join(citizenships) if citizenships else 'Unknown'

    pep_status = merged_record.get('pep_status', 'Unknown')
    positions = merged_record.get('positions', []) or ['None']
    info['PEP Status'] = pep_status
    info['Positions Held'] = positions
    info['Government/Military Roles'] = detect_gov_roles(positions)
    directors = [p for p in positions if 'director' in p.lower()]
    info['Corporate Directorships'] = directors or ['None']

    info['Sanctions List'] = merged_record.get('sanctions', []) or ['None']
    info['Watchlist Categories'] = merged_record.get('topics', []) or ['None']

    summaries = merged_record.get('summaries', [])
    topics = merged_record.get('topics', [])
    info['Risk Classification'] = analyze_risk_from_text(summaries, topics)
    adverse = extract_adverse_media(summaries)
    info['Fraud/Legal Alerts'] = adverse
    info['Negative Media'] = adverse

    info['Summary Notes'] = summaries[:3] if summaries else ['None']

    info['Data Sources'] = merged_record.get('datasets', [])
    info['Scan ID'] = merged_record.get('scan_id', 'Unknown')
    rate = merged_record.get('match_rate', 0)
    info['Match Rate'] = f"{rate}%" if isinstance(rate, int) else rate
    info['Number of Matches'] = merged_record.get('number_of_matches', rate)

    return info
