import fitz  # PyMuPDF
import os
import re
import argparse

# --- Predefined List of ME Syllabi and Their Start Pages ---
# This list is manually created for the ME.pdf file for maximum accuracy.
ME_SUBJECTS = [
    {'code': 'ME301', 'title': 'Design of Machine Element - I', 'page': 11},
    {'code': 'ME303', 'title': 'Manufacturing Technology II', 'page': 13},
    {'code': 'ME305', 'title': 'Refrigeration and Air Conditioning', 'page': 15},
    {'code': 'MG301', 'title': 'Fundamentals of management', 'page': 17},
    {'code': 'ME302', 'title': 'Operations & Supply chain management', 'page': 19},
    {'code': 'ME304', 'title': 'Design of Machine Elements - II', 'page': 21},
    {'code': 'HU302', 'title': 'Engineering Economics', 'page': 23},
    {'code': 'ME351', 'title': 'Power Plant Engineering', 'page': 25},
    {'code': 'ME353', 'title': 'Clean Energy', 'page': 27},
    {'code': 'ME355', 'title': 'THERMAL SYSTEM', 'page': 29},
    {'code': 'ME357', 'title': 'Industrial Engineering', 'page': 31},
    {'code': 'ME359', 'title': 'Product Design & Simulation', 'page': 33},
    {'code': 'ME361', 'title': 'Computational Fluid Dynamics', 'page': 35},
    {'code': 'ME363', 'title': 'Finite Element Methods', 'page': 36},
    {'code': 'ME365', 'title': 'Total Life cycle Management', 'page': 38},
    {'code': 'ME367', 'title': 'Value Engineering', 'page': 40},
    {'code': 'ME308', 'title': 'Gas Dynamics and Jet Propulsion', 'page': 42},
    {'code': 'ME-310', 'title': 'Automation in Manufacturing', 'page': 44},
    {'code': 'ME312', 'title': 'Quality Management & Six Sigma Applications', 'page': 46},
    {'code': 'ME314', 'title': 'Mechanical Vibrations', 'page': 48},
    {'code': 'ME316', 'title': 'Power Plant Engineering', 'page': 50},
    {'code': 'ME318', 'title': 'Computer Aided Manufacturing', 'page': 52},
    {'code': 'ME320', 'title': 'Reliability and Maintenance Engineering', 'page': 54},
    {'code': 'ME322', 'title': 'Design of Mechanical Assemblies', 'page': 56},
    {'code': 'ME324', 'title': 'System Modelling, Simulation and Analysis', 'page': 58},
    {'code': 'ME326', 'title': 'Pressure Vessels and Piping Technology', 'page': 60},
    {'code': 'ME328', 'title': 'Composite Material Technology', 'page': 61},
    {'code': 'ME330', 'title': 'Production and Operations Management', 'page': 63},
    {'code': 'ME332', 'title': 'Finite Element Method', 'page': 65},
    {'code': 'ME-334', 'title': 'Industrial Economics & Management', 'page': 67},
    {'code': 'ME336', 'title': 'Creativity and Innovation Management', 'page': 69},
    {'code': 'ME407', 'title': 'Carbon Capture and Climate Change', 'page': 72},
    {'code': 'ME409', 'title': 'Mechatronics and Control', 'page': 74},
    {'code': 'ME411', 'title': 'I. C. Engines', 'page': 76},
    {'code': 'ME413', 'title': 'Metrology', 'page': 78},
    {'code': 'ME415', 'title': 'Project Management', 'page': 80},
    {'code': 'ME417', 'title': 'Robotics and Automation', 'page': 82},
    {'code': 'ME419', 'title': 'Computational Fluid Dynamics', 'page': 83},
    {'code': 'ME421', 'title': 'Advanced Manufacturing Processes', 'page': 85},
    {'code': 'ME423', 'title': 'Operations Research', 'page': 87},
    {'code': 'ME425', 'title': 'Industrial Tribology', 'page': 89},
    {'code': 'ME427', 'title': 'Non-Conventional Energy Sources', 'page': 91},
    {'code': 'ME429', 'title': 'Computer Integrated Manufacturing', 'page': 93},
    {'code': 'ME431', 'title': 'Optimization techniques', 'page': 95},
    {'code': 'ME404', 'title': 'Industrial Engineering', 'page': 97},
    {'code': 'ME406', 'title': 'Elastic and Plastic Behavior of Materials', 'page': 99},
    {'code': 'ME408', 'title': 'Combustion Generated Pollution', 'page': 101},
    {'code': 'ME410', 'title': 'Advances in Welding & Casting', 'page': 103},
    {'code': 'ME412', 'title': 'Supply Chain Management', 'page': 105},
    {'code': 'ME414', 'title': 'Fracture Mechanics', 'page': 107},
    {'code': 'ME416', 'title': 'Nuclear Energy', 'page': 109},
    {'code': 'ME418', 'title': 'Operations & Manufacturing Strategy', 'page': 111},
    {'code': 'ME420', 'title': 'Materials Management', 'page': 113},
    {'code': 'ME422', 'title': 'Fuel Cell', 'page': 115},
    {'code': 'ME424', 'title': 'Sustainable Energy Technologies', 'page': 117}
]


def extract_syllabi(doc: fitz.Document, syllabi_list: list, output_folder: str):
    """
    Extracts each syllabus based on the predefined start page.
    The end of one syllabus is defined by the start of the next one.
    """
    print("--- Using predefined page map for extraction ---")
    os.makedirs(output_folder, exist_ok=True)

    for i, syllabus in enumerate(syllabi_list):
        # Page numbers in the list are 1-based, convert to 0-based index
        start_page = syllabus['page'] - 1

        # Define the end page
        if i + 1 < len(syllabi_list):
            # The end page is the page before the next syllabus starts
            end_page = syllabi_list[i+1]['page'] - 2
        else:
            # For the last syllabus, go to the end of the document
            end_page = len(doc) - 1
        
        if start_page > end_page:
            end_page = start_page

        # Sanitize title for a valid filename
        clean_code = syllabus['code'].replace('-', '')
        clean_title = re.sub(r'[\n/\\:*?"<>|]', '', syllabus['title']).strip()
        out_fname = f"{clean_code}.pdf"
        out_path = os.path.join(output_folder, out_fname)
        
        print(f"Processing '{syllabus['code']}: {clean_title}'...")
        print(f"  > Extracting pages {start_page + 1} to {end_page + 1}. Saving to '{out_fname}'")

        subdoc = fitz.open()
        subdoc.insert_pdf(doc, from_page=start_page, to_page=end_page)

        if not subdoc:
            print(f"  -> ERROR: Failed to create sub-document for {syllabus['code']}.")
            continue
            
        try:
            subdoc.save(out_path, garbage=4, deflate=True)
        except Exception as e:
            print(f"  -> ERROR: Could not save file '{out_fname}'. Reason: {e}")
        finally:
            subdoc.close()

    print("\n✅ Extraction complete.")


def main():
    parser = argparse.ArgumentParser(
        description="Extracts syllabi from the ME.pdf using a predefined page map.",
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument('pdf_path', help='Path to the input ME.pdf file.')
    parser.add_argument('output_folder', help='Folder to save the extracted PDF files.')
    
    args = parser.parse_args()

    if not os.path.exists(args.pdf_path):
        print(f"Error: PDF file not found at '{args.pdf_path}'")
        return

    doc = fitz.open(args.pdf_path)
    
    extract_syllabi(doc, ME_SUBJECTS, args.output_folder)
    
    doc.close()

if __name__ == '__main__':
    main()