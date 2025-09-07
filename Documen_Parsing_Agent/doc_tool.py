import PyPDF2
import json
from strands import tool,Agent
import re
import pdfplumber
import json
 
import os
 
 
# use this for complex
@tool
def extract_pdf_to_json(pdf_path, output_path):
    """
    Extracts structured content from a PDF file and saves it as a JSON file.

    This function uses `pdfplumber` to read the PDF and organizes the content into sections.
    Each section may contain:
    - Paragraphs (free text lines)
    - Key-value pairs (lines with a colon separator)
    - Tables (converted into lists of dictionaries)

    Section headers are detected based on formatting (e.g., "SECTION 1", all-uppercase lines).
    The extracted data is saved to the specified output path in JSON format.

    Args:
        pdf_path (str): Path to the input PDF file.
        output_path (str): Path where the output JSON file will be saved.

    Returns:
        dict: A dictionary representing the structured content extracted from the PDF.
    """
    result = {}
    current_section = "General"
    section_data = {"paragraphs": [], "key_values": {}, "tables": []}

    def is_section_header(line):
        return re.match(r"^(SECTION|Section)\s+\d+", line) or line.isupper()

    def is_key_value(line):
        return ':' in line and len(line.split(':', 1)[1].strip()) > 0

    with pdfplumber.open(pdf_path) as pdf:
        for page_num, page in enumerate(pdf.pages):
            lines = page.extract_text().split('\n') if page.extract_text() else []

            for line in lines:
                line = line.strip()
                if not line:
                    continue

                if is_section_header(line):
                    if section_data["paragraphs"] or section_data["key_values"] or section_data["tables"]:
                        result[current_section] = section_data
                    current_section = line
                    section_data = {"paragraphs": [], "key_values": {}, "tables": []}

                elif is_key_value(line):
                    key, value = line.split(':', 1)
                    section_data["key_values"][key.strip()] = value.strip()

                else:
                    section_data["paragraphs"].append(line)

            # Extract tables
            tables = page.extract_tables()
            for table in tables:
                headers = table[0]
                rows = [dict(zip(headers, row)) for row in table[1:] if len(row) == len(headers)]
                section_data["tables"].extend(rows)

        # Save last section
        if section_data["paragraphs"] or section_data["key_values"] or section_data["tables"]:
            result[current_section] = section_data

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    return result




agent = Agent(tools=[extract_pdf_to_json])


# # Define paths
# main_folder = os.path.dirname(os.path.abspath(__file__))
# print(f"Main folder: {main_folder}")
# pdf_filename = "star-enterprise-audit-form.pdf"
# pdf_path = os.path.join(main_folder, pdf_filename)
# output_folder = os.path.join(main_folder, "Audit_files")
# os.makedirs(output_folder, exist_ok=True)
# output_json_path = os.path.join(output_folder, "star-enterprise-audit-form.json")


# # Extract and save
# data = extract_pdf_to_json(pdf_path, output_json_path)
# with open(output_json_path, "w", encoding="utf-8") as f:
#     json.dump(data, f, ensure_ascii=False, indent=4)

# print(f"JSON saved to {output_json_path}")

