from collect_inputs import collect_inputs
from scanname import fetch_namescan_api
from opensanctions import fetch_opensanctions_api
from combiner import smart_merge_records
from extract_customer_identity import extract_customer_identity
from kyc_dashboard import dashboard
from report import report, write_summary_to_excel

def main():
    all_inputs = collect_inputs()  # List of client dicts

    for inputs in all_inputs:
        
        ns_data = fetch_namescan_api(inputs)
        os_data = fetch_opensanctions_api(inputs)
        unified = smart_merge_records(ns_data, os_data)
        identity_info = extract_customer_identity(unified)
        
        '''
        print(f"inputs={inputs}")
        print("\n")
        '''
        
        if identity_info.get("Full Legal Name") == "Unknown":
            dashboard(None, inputs.get("name"))
        else:
            dashboard(identity_info)
        
        report(identity_info, inputs.get("name"))
    write_summary_to_excel("kyc_summary.xlsx")

if __name__ == "__main__":
    main()
