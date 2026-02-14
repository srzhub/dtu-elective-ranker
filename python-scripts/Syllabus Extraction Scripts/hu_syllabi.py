import os
import re
import pandas as pd
from pypdf import PdfReader, PdfWriter

def split_syllabus_to_pdfs(input_pdf_path):
    reader = PdfReader(input_pdf_path)
    output_folder = "syllabi"
    
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # Subject data storage for Excel
    mapping_data = []
    
    # Track which subject belongs to which page range
    # Subject Code pattern: HU followed by space and 3 digits
    code_pattern = r"(HU\s\d{3})"
    # Subject Name pattern: The text following the code and a colon
    name_pattern = r"HU\s\d{3}:\s?([\w\s,&-]+)"

    current_subject_code = None
    current_subject_name = None
    subject_pages = {}

    # Step 1: Analyze pages to find which pages belong to which subject
    for i, page in enumerate(reader.pages):
        text = page.extract_text()
        
        # Look for new subject headers on the page
        code_match = re.search(code_pattern, text)
        name_match = re.search(name_pattern, text)
        
        if code_match:
            new_code = code_match.group(1).replace(" ", "")
            new_name = name_match.group(1).strip() if name_match else "Unknown Subject"
            
            current_subject_code = new_code
            current_subject_name = new_name
            
            if current_subject_code not in subject_pages:
                subject_pages[current_subject_code] = []
                mapping_data.append({
                    "Subject Code": current_subject_code,
                    "Subject Name": current_subject_name
                })
        
        if current_subject_code:
            subject_pages[current_subject_code].append(i)

    # Step 2: Create individual PDFs based on the identified pages
    for code, pages in subject_pages.items():
        writer = PdfWriter()
        for page_num in pages:
            writer.add_page(reader.pages[page_num])
        
        output_filename = os.path.join(output_folder, f"{code}.pdf")
        with open(output_filename, "wb") as output_pdf:
            writer.write(output_pdf)

    # Step 3: Save mapping to Excel
    df = pd.DataFrame(mapping_data)
    df.to_excel("subject_mapping.xlsx", index=False)
    
    print(f"Successfully created {len(mapping_data)} individual PDFs in the '{output_folder}' folder.")
    print("Created 'subject_mapping.xlsx' for code-to-name mapping.")

# Run the process
split_syllabus_to_pdfs("HU_syllabus.pdf")