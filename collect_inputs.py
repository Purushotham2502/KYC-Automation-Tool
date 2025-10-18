import os
import pandas as pd
import re



def format_date(val):
    import pandas as pd
    if pd.isna(val) or val == "":
        return ""
    if isinstance(val, str):
        # If already YYYY-MM-DD, just return
        if re.match(r"^\d{4}-\d{2}-\d{2}$", val.strip()):
            return val.strip()
        # If matches YYYY-MM-DD 00:00:00 or similar, extract date part
        m = re.match(r"^(\d{4}-\d{2}-\d{2}) [0-9:]+$", val.strip())
        if m:
            return m.group(1)
        return val.strip()
    else:
        # If it actually is a datetime object
        return val.strftime('%Y-%m-%d')



def safe_strip(val):
    if pd.isna(val):
        return ""
    return str(val).strip()


def collect_inputs():
    # Path to your single Excel file in the same folder as this script
    base_dir = os.path.dirname(os.path.abspath(__file__))
    data_file = os.path.join(base_dir, 'Client_Data.xlsx')

    if not os.path.exists(data_file):
        raise FileNotFoundError(f"No Excel file found at {data_file}")

    df = pd.read_excel(data_file, sheet_name=0, dtype=str)
    df = df.rename(columns=lambda c: c.strip())  # Clean column names
    


    inputs = []
    for _, row in df.iterrows():
        # Skip empty rows
        if row.isna().all():
            continue

        client = {
            "name": safe_strip(row.get("Name")),
            "entity_type": safe_strip(row.get("Entity Type")),
            "date": format_date(row.get("Date of Birth")),
            "country": safe_strip(row.get("Country")),
            "passport": safe_strip(row.get("Passport")),
            "email": safe_strip(row.get("Email")),
            "phone": safe_strip(row.get("Phone")),
            "occupation": safe_strip(row.get("Occupation")),
            "nationality": safe_strip(row.get("Nationality"))
}

        inputs.append(client)

    return inputs

