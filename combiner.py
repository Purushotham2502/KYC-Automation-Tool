import re
from difflib import SequenceMatcher
from datetime import datetime
import spacy
from jsonpath_ng import parse as jp

nlp = spacy.load("en_core_web_sm")

FIELD_CATEGORIES = {
    'name': ['name','fullname','full_name','legalname','caption','personname','firstname','lastname'],
    'aliases': ['alias','aliases','othernames','other_names','alsoknownas','weakalias','aka','os_aliases','aliasesdetails','Also Known As'],
    'birth_date': ['birthdate','dateofbirth','dob','born','birth_date','datesofbirth'],
    'birth_place': ['birthplace','placeofbirth','place_of_birth','birthcity','placesofbirth'],
    'gender': ['gender','sex'],
    'nationality': ['nationality','nationalities','citizen','citizenship','citizenships','country'],
    'positions': ['position','positions','role','roles','title','titles','occupation','occupations','gov_military_roles','roles_details'],
    'email': ['email'],
    'phone': ['phone','phones','telephone','mobile','contact'],
    'address': ['address','addresses','location','residence','places'],
    'pep_status': ['pep','pepstatus','politically_exposed','pep_matches','numberofpepmatches'],
    'sanctions': ['sanction','sanctions','sanctioned','watchlist'],
    'topics': ['topic','topics','classification','category','categories'],
    'summary': ['summary','notes','description','bio','information'],
    'sources': ['source','sources','sourceurl','sourceUrls','dataset','datasets'],
    'identifiers': ['id','uid','identifier','wikidata','wikidataid'],
}

GOV_ROLES_KEYWORDS = {
    "prime minister","chief minister","member of the lok sabha",
    "minister","leader of the house","head, dept."
}

SOCIAL_CONTACT_FIELDS = {
    "Twitter":"twitter","Facebook":"facebook","Instagram":"instagram"
}

def is_valid_email(email):
    return isinstance(email, str) and '@' in email


def normalize_field_name(fn):
    n = fn.lower().strip()
    return re.sub(r'[_\-\s]+','',n)

def find_semantic_category(fn):
    norm = normalize_field_name(fn)
    best,score = None,0
    for cat,keys in FIELD_CATEGORIES.items():
        for k in keys:
            s = SequenceMatcher(None,norm,normalize_field_name(k)).ratio()
            if s > score and s > 0.7:
                best,score = cat,s
    return best

def extract_nested_data(d,cat):
    out=[]
    if isinstance(d,dict):
        for k,v in d.items():
            if find_semantic_category(k)==cat:
                out += v if isinstance(v,list) else [v]
            else:
                out += extract_nested_data(v,cat)
    elif isinstance(d,list):
        for e in d: out+=extract_nested_data(e,cat)
    return out

def extract_string_from_entry(e):
    if isinstance(e,dict): return str(e.get('name') or e.get('value') or '')
    return str(e)

def extract_person_array(arr):
    res={}
    if not isinstance(arr,list) or not arr: return res
    p=arr[0]
    res['names']=[p['name']] if 'name' in p else []
    # aliases
    a=[]
    for alt in p.get('otherNames',[]):
        a.append(alt['name'] if isinstance(alt,dict) else alt)
    res['aliases']=a
    # dates
    ds=[]
    for dob in p.get('datesOfBirth',[]):
        ds.append(dob.get('date') if isinstance(dob,dict) else dob)
    res['birth_dates']=ds
    # places
    bp=[]
    for plc in p.get('placesOfBirth',[]):
        if isinstance(plc,dict):
            loc,c=plc.get('location',''),plc.get('country','')
            bp.append(f"{loc}, {c}" if loc and c else loc or c)
    res['birth_places']=bp
    # roles
    pos=[]
    for r in p.get('roles',[]):
        pos.append(r.get('title') if isinstance(r,dict) else r)
    res['positions']=pos
    # contacts
    em,ph=[],[]
    for c in p.get('contacts',[]):
        if not isinstance(c,dict): continue
        t,v=c.get('type','').lower(),c.get('value','')
        if 'email'in t: em.append(v)
        if 'phone'in t or 'tel'in t: ph.append(v)
    res['emails'],res['phones']=em,ph
    res['gender'],res['citizenship'],res['nationality']=p.get('gender',''),p.get('citizenship',''),p.get('nationality','')
    res['category'],res['uid']=p.get('category',''),p.get('uid',None)
    return res

def detect_gov_roles(pos):
    out=[]
    for p in pos:
        if any(kw in p.lower() for kw in GOV_ROLES_KEYWORDS): out.append(p)
    return out or ['None']

def fetch_profile_image_url(ns,os):
    for key in ('profile_image_url','profile_image','images','image_urls'):
        v=ns.get(key) if key in ns else os.get('properties',{}).get(key)
        if v:
            return v[0] if isinstance(v,list) else v
    return None

def extract_social(ns,os):
    s={}
    # structured
    for k in ['Twitter','Facebook','Instagram']:
        v=ns.get('social_handles',{}).get(k)
        if v: s[k]=v
    # contacts fallback
    if not s:
        for label,kw in SOCIAL_CONTACT_FIELDS.items():
            for f,v in ns.get('contacts',{}).items():
                if kw in f.lower():
                    if not v.lower().startswith(('http://','https://')):
                        v=f"https://{kw}.com/{v}"
                    s[label]=v
    # website fallback
    for url in os.get('properties',{}).get('website',[]):
        if 'twitter.com' in url: s['Twitter']=url
        if 'facebook.com' in url: s['Facebook']=url
        if 'instagram.com' in url: s['Instagram']=url
    return s or {'None':'None'}

def extract_addresses(rec,limit=2):
    a=[]
    for fld in ('addresses','places'):
        for it in rec.get(fld,[]):
            f=it.get('location','')+(', '+it.get('country','') if it.get('country') else '') if isinstance(it,dict) else str(it)
            if f and f not in a: a.append(f)
            if len(a)>=limit: break
        if len(a)>=limit: break
    return a or ['None']

def smart_merge_records(ns,os_data):
    pns=extract_person_array(ns.get('persons',[]))
    ops=os_data.get('properties',{})
    u={}
    # name
    names=extract_nested_data(ns,'name')+extract_nested_data(os_data,'name')+pns.get('names',[])+ops.get('name',[])
    cleans=[extract_string_from_entry(n) for n in names if n]
    uni=list(dict.fromkeys(cleans))
    u['name']=uni[0] if uni else 'Unknown'; u['all_names']=uni
    # aliases
    al=extract_nested_data(ns,'aliases')+extract_nested_data(os_data,'aliases')+pns.get('aliases',[])+ops.get('alias',[])+ops.get('weakAlias',[])
    cl=[extract_string_from_entry(x) for x in al if x]; ua=list(dict.fromkeys(cl))
    u['aliases']=[x for x in ua if x!=u['name']]
    # birth_date/place
    bd=extract_nested_data(ns,'birth_date')+extract_nested_data(os_data,'birth_date')+pns.get('birth_dates',[])+ops.get('birthDate',[])
    u['birth_date']=bd[0] if bd else None
    bp=extract_nested_data(ns,'birth_place')+extract_nested_data(os_data,'birth_place')+pns.get('birth_places',[])+ops.get('birthPlace',[])
    u['birth_place']=bp[0] if bp else None
    # gender
    gopt=[pns.get('gender'),ops.get('gender',[None])[0] if isinstance(ops.get('gender'),list) else ops.get('gender')]
    u['gender']=next((x for x in gopt if x and x.lower()!='unknown'),'Unknown')
    # citizenship
    cit=extract_nested_data(ns,'nationality')+extract_nested_data(os_data,'nationality')
    if pns.get('citizenship'): cit.append(pns['citizenship'])
    if pns.get('nationality'): cit.append(pns['nationality'])
    cit+=ops.get('citizenship',[])+ops.get('nationality',[])+ops.get('country',[])
    u['citizenship']=list(dict.fromkeys([x for x in cit if x]))
    # positions
    pos=extract_nested_data(ns,'positions')+extract_nested_data(os_data,'positions')+pns.get('positions',[])+ops.get('position',[])
    cp=[extract_string_from_entry(x) for x in pos if x]; up=list(dict.fromkeys(cp))
    u['positions']=up
    # emails/phones
    em=extract_nested_data(ns,'email')+extract_nested_data(os_data,'email')+pns.get('emails',[])+ops.get('email',[])
    valid_emails = [e for e in em if is_valid_email(e)]
    ph=extract_nested_data(ns,'phone')+extract_nested_data(os_data,'phone')+pns.get('phones',[])
    u['emails'] = list(dict.fromkeys(valid_emails)); u['phones']=list(dict.fromkeys([extract_string_from_entry(x) for x in ph if x]))
    # pep
    pm=ns.get('pep_matches',ns.get('matches',0))
    cat=pns.get('category','').upper(); tps=ops.get('topics',[])
    is_pep=pm>0 or 'PEP' in cat or any('pep' in str(x).lower() for x in tps)
    u['pep_status']='Yes' if is_pep else 'No'; u['pep_matches']=pm
    # topics
    top=extract_nested_data(ns,'topics')+extract_nested_data(os_data,'topics')+tps+ops.get('classification',[])
    u['topics']=list(dict.fromkeys([x for x in top if x]))
    # summaries
    sm=extract_nested_data(ns,'summary')+extract_nested_data(os_data,'summary')+ops.get('notes',[])
    u['summaries']=[x for x in sm if x]
    # datasets/scan
    ds=os_data.get('datasets',[]); ds.append(ns.get('scanId','Namescan'))
    u['datasets']=list(dict.fromkeys(ds))
    u['scan_id']=ns.get('scanId'); u['match_rate']=ns.get('matchRate',ns.get('matchRate',0))
    u['last_updated']=os_data.get('last_change') or ns.get('scan_date')
    u['uid']=pns.get('uid'); u['wikidata_id']=ops.get('wikidataId',[None])[0]
    # enrich
    u['gov_military_roles']=detect_gov_roles(u['positions'])
    u['profile_image_url']=fetch_profile_image_url(ns,os_data)
    u['social_handles']=extract_social(ns,os_data)
    u['addresses']=extract_addresses({**(ns or {}),**(os_data or {})})
    return u

def analyze_risk_from_text(summaries,topics):
    txt=' '.join(summaries)+ ' ' + ' '.join(topics); txt=txt.lower()
    hr=[(r'\bterror(ist|ism)?\b',3),(r'\bsanction(s|ed)?\b',3),(r'\bfraud(ulent)?\b',3),(r'\bcriminal\b',3),(r'\bmoney\s*laundering\b',3),(r'\bcorruption\b',3),(r'\billegal\b',2)]
    mr=[(r'\binvestigat(ion|ed|ing)\b',2),(r'\balleged(ly)?\b',2),(r'\bsuspect(ed)?\b',2),(r'\blinked\s*to\b',1)]
    lr=[(r'\bformer\b',-1),(r'\bretired\b',-1)]
    score=0
    for p,w in hr+mr+lr:
        if re.search(p,txt): score+=w
    if score>=5: return "High"
    if score>=2: return "Medium"
    return "Low" if txt.strip() else "Unknown"

def extract_adverse_media(summaries):
    pats=[r'\b(criminal|fraud|sanction|investigation|convicted|arrested|illegal|corruption)\b',
          r'\b(indicted|prosecuted|charged|accused|sued)\b',
          r'\b(money\s*laundering|terrorist|terrorism|bribery)\b']
    out=[]
    for t in (summaries or []):
        s=str(t).lower()
        if any(re.search(p,s) for p in pats):
            out.append(t)
    return out
