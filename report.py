import pandas as pd

# Internal storage for summary rows
_summary_rows = []

def report(identity_info, original_name=None):
    """
    Summarize identity_info into one row: Name, Risk Level, Category.
    If identity_info is None or missing, mark for manual check.
    """
    if identity_info is None or identity_info.get("Full Legal Name") == "Unknown":
        name = original_name or "Unknown"
        risk = "Unknown"
        category = "Manual Check"
    else:
        name = identity_info.get("Full Legal Name", "Unknown")
        risk = identity_info.get("Risk Classification", "Unknown")
        cats = identity_info.get("Watchlist Categories", [])
        if any("pep" in c.lower() for c in cats):
            category = "PEP"
        elif any("terror" in c.lower() for c in cats):
            category = "Terrorism"
        elif any("government" in c.lower() for c in cats):
            category = "Government"
        else:
            category = "None"

    _summary_rows.append({
        "Name": name,
        "Risk Level": risk,
        "Category": category
    })

def write_summary_to_excel(output_path="kyc_summary.xlsx"):
    """
    Write summary rows to a styled Excel file with professional formatting.
    """
    df = pd.DataFrame(_summary_rows, columns=["Name", "Risk Level", "Category"])

    # Use XlsxWriter for styling
    with pd.ExcelWriter(output_path, engine="xlsxwriter") as writer:
        df.to_excel(writer, index=False, sheet_name="KYC Summary")
        workbook  = writer.book
        worksheet = writer.sheets["KYC Summary"]

        # Define header format
        header_format = workbook.add_format({
            "bold": True,
            "text_wrap": True,
            "valign": "middle",
            "fg_color": "#4F81BD",
            "font_color": "white",
            "border": 1
        })

        # Define conditional formats for Risk Level
        risk_formats = {
            "High":   workbook.add_format({"bg_color": "#FFC7CE", "font_color": "#9C0006"}),
            "Medium": workbook.add_format({"bg_color": "#FFEB9C", "font_color": "#9C6500"}),
            "Low":    workbook.add_format({"bg_color": "#C6EFCE", "font_color": "#006100"}),
            "Unknown":workbook.add_format({"bg_color": "#D9D9D9", "font_color": "#404040"})
        }

        # Format for Category cells (border and wrap text)
        category_format = workbook.add_format({"text_wrap": True, "valign": "top", "border": 1})

        # Apply header formatting and set column widths
        for col_num, value in enumerate(df.columns.values):
            worksheet.write(0, col_num, value, header_format)
            if value == "Name":
                worksheet.set_column(col_num, col_num, 30)
            else:
                worksheet.set_column(col_num, col_num, 15)

        # Apply conditional formatting for Risk Level column
        risk_col = df.columns.get_loc("Risk Level")
        for level, fmt in risk_formats.items():
            worksheet.conditional_format(1, risk_col, len(df), risk_col, {
                "type":     "cell",
                "criteria": "==",
                "value":    f'"{level}"',
                "format":   fmt
            })

        # Apply border and wrapping to Category column
        cat_col = df.columns.get_loc("Category")
        worksheet.set_column(cat_col, cat_col, 20, category_format)

    #print(f"Styled summary written to {output_path}")
