import fitz  # PyMuPDF
import os
import re
import argparse

# --- Predefined List of AE Syllabi and Their Start Pages ---
# This list is manually created for the AE.pdf file for maximum accuracy.
AE_SUBJECTS = [
    {'code': 'AE301', 'title': 'Manufacturing technology', 'page': 8},
    {'code': 'AE303', 'title': 'Design of Machine elements', 'page': 10},
    {'code': 'AE305', 'title': 'Measurements and Instrumentation', 'page': 12},
    {'code': 'HU301', 'title': 'Engineering Economics', 'page': 14},
    {'code': 'AE302', 'title': 'I C Engines', 'page': 16},
    {'code': 'AE304', 'title': 'Alternative fuels and energy systems', 'page': 18},
    {'code': 'MG302', 'title': 'Fundamentals of management', 'page': 20},
    {'code': 'AE307', 'title': 'Combustion Generated Pollution', 'page': 22},
    {'code': 'AE309', 'title': 'Operation Research', 'page': 24},
    {'code': 'AE311', 'title': 'Tyre Technology', 'page': 26},
    {'code': 'AE313', 'title': 'Thermal Engineering', 'page': 28},
    {'code': 'AE315', 'title': 'Turbo machinery and gas dynamics', 'page': 30},
    {'code': 'AE317', 'title': 'Power units and transmission', 'page': 32},
    {'code': 'AE319', 'title': 'Computer Simulation of I.C. Engine Process', 'page': 34},
    {'code': 'AE321', 'title': 'Advanced strength of material', 'page': 36},
    {'code': 'AE323', 'title': 'Finite Element Methods and Applications', 'page': 38},
    {'code': 'AE306', 'title': 'Automotive Aerodynamics & CFD', 'page': 40},
    {'code': 'AE308', 'title': 'Advanced Manufacturing Technology', 'page': 42},
    {'code': 'AE310', 'title': 'Quality Management & Six Sigma Applications', 'page': 44},
    {'code': 'AE312', 'title': 'Metrology', 'page': 46},
    {'code': 'AE314', 'title': 'Advances in Welding & Casting', 'page': 48},
    {'code': 'AE316', 'title': 'Materials for automobile components', 'page': 50},
    {'code': 'AE318', 'title': 'Tribology and lubrication', 'page': 52},
    {'code': 'AE320', 'title': 'Reliability & Maintenance Engineering', 'page': 54},
    {'code': 'AE322', 'title': 'Elastic & Plastic Behaviour of Materials', 'page': 56},
    {'code': 'AE324', 'title': 'Production Planning & Inventory Control', 'page': 58},
    {'code': 'AE326', 'title': 'Supply Chain Management', 'page': 60},
    {'code': 'AE328', 'title': 'Computer Integrated Manufacturing Systems', 'page': 62},
    {'code': 'AE405', 'title': 'Design of Automobile Components', 'page': 64},
    {'code': 'AE407', 'title': 'Production And Operations Management', 'page': 66},
    {'code': 'AE409', 'title': 'Computer Aided Vehicle Design and Safety', 'page': 68},
    {'code': 'AE411', 'title': 'Vehicle Maintenance & Tribology', 'page': 70},
    {'code': 'AE413', 'title': 'Vehicle Transport Management', 'page': 72},
    {'code': 'AE415', 'title': 'Power Plant Engineering', 'page': 74},
    {'code': 'AE417', 'title': 'Robotics & Automation', 'page': 76},
    {'code': 'AE419', 'title': 'Nuclear Energy', 'page': 78},
    {'code': 'AE421', 'title': 'Product design and development', 'page': 80},
    {'code': 'AE423', 'title': 'Financial Management', 'page': 82},
    {'code': 'AE425', 'title': 'Fracture mechanics', 'page': 84},
    {'code': 'AE404', 'title': 'Total Life Cycle Management', 'page': 86},
    {'code': 'AE406', 'title': 'Refrigeration & Automobile Air Conditioning', 'page': 88},
    {'code': 'AE408', 'title': 'Fuel Cells', 'page': 90},
    {'code': 'AE410', 'title': 'Modern Vehicle Technology', 'page': 92},
    {'code': 'AE412', 'title': 'Automobiles Vibration System Analysis', 'page': 94},
    {'code': 'AE414', 'title': 'Renewable Energy Sources', 'page': 96},
    {'code': 'AE416', 'title': 'Vehicle Safety Engineering', 'page': 98},
    {'code': 'AE418', 'title': 'Packaging Technology', 'page': 100},
    {'code': 'AE420', 'title': 'Mechatronics', 'page': 102},
    {'code': 'AE422', 'title': 'Tractors and Farm Equipment and Off-Road Vehicles', 'page': 104},
    {'code': 'AE424', 'title': 'Automobile process control', 'page': 106}
]

def extract_syllabi(doc: fitz.Document, syllabi_list: list, output_folder: str):
    """
    Extracts each syllabus based on the predefined start page.
    The end of one syllabus is defined by the start of the next one.
    """
    print("--- Using predefined page map for extraction ---")
    os.makedirs(output_folder, exist_ok=True)

    for i, syllabus in enumerate(syllabi_list):
        # Page numbers in the list are 1-based, convert to 0-based index for the library
        start_page = syllabus['page'] - 1

        # Define the end page
        if i + 1 < len(syllabi_list):
            # The end page is the page before the next syllabus starts
            end_page = syllabi_list[i+1]['page'] - 2
        else:
            # For the last syllabus, go to the end of the document
            end_page = len(doc) - 1
        
        # Ensure start_page is not greater than end_page
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
        description="Extracts syllabi from the AE.pdf using a predefined page map.",
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument('pdf_path', help='Path to the input AE.pdf file.')
    parser.add_argument('output_folder', help='Folder to save the extracted PDF files.')
    
    args = parser.parse_args()

    if not os.path.exists(args.pdf_path):
        print(f"Error: PDF file not found at '{args.pdf_path}'")
        return

    doc = fitz.open(args.pdf_path)
    
    # Use the predefined list of AE subjects and their pages
    extract_syllabi(doc, AE_SUBJECTS, args.output_folder)
    
    doc.close()

if __name__ == '__main__':
    main()