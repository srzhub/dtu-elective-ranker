import fitz  # PyMuPDF
import os
import re
import argparse

# --- Predefined List of BT Syllabi and Their Start Pages ---
# This list is manually created for the BT.pdf file for maximum accuracy.
BT_SUBJECTS = [
    # 1st Year
    {'code': 'BT103', 'title': 'Applied Aquaculture', 'page': 2},
    {'code': 'BT102', 'title': 'Biochemical Engineering Principles', 'page': 4},
    {'code': 'BT104', 'title': 'Introduction to Biotechnology', 'page': 5},
    {'code': 'BT106', 'title': 'Development of Scientific Instrumentations and its applications', 'page': 7},
    # 2nd Year
    {'code': 'BT201', 'title': 'Applied mathematics', 'page': 10},
    {'code': 'BT203', 'title': 'Cell Biology', 'page': 11},
    {'code': 'BT205', 'title': 'Genetics', 'page': 13},
    {'code': 'BT207', 'title': 'Fundamentals of computational biology', 'page': 15},
    {'code': 'BT209', 'title': 'Bioprocess Technology and Downstream Processing', 'page': 16},
    {'code': 'BT204', 'title': 'Data Structure and Algorithm', 'page': 19},
    {'code': 'BT202', 'title': 'Molecular Biology', 'page': 20},
    {'code': 'BT206', 'title': 'Microbiology', 'page': 22},
    {'code': 'BT208', 'title': 'Advances in computational biology', 'page': 24},
    {'code': 'BT210', 'title': 'Biochemistry', 'page': 25},
    # 3rd Year
    {'code': 'BT301', 'title': 'Immunology and Immunotechnology', 'page': 28},
    {'code': 'BT303', 'title': 'Genetic Engineering', 'page': 30},
    {'code': 'BT305', 'title': 'Environmental Biotechnology', 'page': 32},
    {'code': 'BT307', 'title': 'Engineering economics', 'page': 34},
    {'code': 'BT302', 'title': 'Plant Biotechnology', 'page': 36},
    {'code': 'BT304', 'title': 'Animal Biotechnology', 'page': 38},
    {'code': 'BT306', 'title': 'Fundamentals of Management', 'page': 40},
    # 4th Year / Electives
    {'code': 'BT309', 'title': 'Instrumentation in Biotechnology', 'page': 45},
    {'code': 'BT311', 'title': 'Food Biotechnology', 'page': 47},
    {'code': 'BT313', 'title': 'Object-oriented Programming', 'page': 48},
    {'code': 'BT315', 'title': 'Introduction to Biomedical Engineering', 'page': 50},
    {'code': 'BT317', 'title': 'Thermodynamics of Biological System', 'page': 52},
    {'code': 'BT319', 'title': 'Current topics in Biotechnology', 'page': 53},
    {'code': 'BT321', 'title': 'Cancer Biology', 'page': 54},
    {'code': 'BT323', 'title': 'Pharmacogenomics and Personalized Medicine', 'page': 55},
    {'code': 'BT325', 'title': 'Drug Design and Delivery', 'page': 57},
    {'code': 'BT308', 'title': 'Stem Cells and Regenerative Medicines', 'page': 58},
    {'code': 'BT310', 'title': 'Metabolic Engineering', 'page': 60},
    {'code': 'BT312', 'title': 'Ecology and Evolution', 'page': 61},
    {'code': 'BT314', 'title': 'Transgenic Technology', 'page': 62},
    {'code': 'BT316', 'title': 'Bioenergy and Biofuels', 'page': 64},
    {'code': 'BT318', 'title': 'Enzymology and Enzyme Technology', 'page': 65},
    {'code': 'BT320', 'title': 'Protein Engineering', 'page': 67},
    {'code': 'BT322', 'title': 'Technological applications in Food technology', 'page': 68},
    {'code': 'BT324', 'title': 'Medical Microbiology', 'page': 71},
    {'code': 'BT326', 'title': 'Industrial Biotechnology', 'page': 73},
    {'code': 'BT328', 'title': 'Concepts in Neurobiology', 'page': 74},
    {'code': 'BT330', 'title': 'Bioinformatic Approaches in Complex disorders', 'page': 76},
    {'code': 'BT332', 'title': 'Plant Bioinformatics', 'page': 78},
    {'code': 'BT334', 'title': 'Biomaterials', 'page': 80},
    {'code': 'BT336', 'title': 'Nanobiotechnology and Nanobiomedicine', 'page': 81},
    {'code': 'BT338', 'title': 'Biomaterials and clinical devices', 'page': 83},
    {'code': 'BT340', 'title': 'Basic Epidemiology', 'page': 84},
    {'code': 'BT342', 'title': 'Biodiversity and Bio-resource Planning', 'page': 86},
    {'code': 'BT344', 'title': 'PRINCIPLE OF IMAGING PROCESSING IN MEDICINE', 'page': 88},
    {'code': 'BT346', 'title': 'GENOMICS AND PROTEOMICS', 'page': 90},
    {'code': 'BT405', 'title': 'STRUCTURAL BIOLOGY', 'page': 91},
    {'code': 'BT407', 'title': 'PRINCIPLES AND PRACTICE IN PUBLIC HEALTH', 'page': 93},
    {'code': 'BT409', 'title': 'Rehabilitation Engineering', 'page': 94},
    {'code': 'BT411', 'title': 'SYSTEM BIOLOGY', 'page': 95},
    {'code': 'BT413', 'title': 'ADVANCED BIOANALYTICAL TECHNIQUES', 'page': 97},
    {'code': 'BT415', 'title': 'CLINICAL BIOTECHNOLOGY', 'page': 99},
    {'code': 'BT417', 'title': 'Plant Metabolic Engineering', 'page': 101},
    {'code': 'BT419', 'title': 'CROP PROTECTION AND PEST MANAGEMENT', 'page': 102},
    {'code': 'BT421', 'title': 'BIOSENSOR', 'page': 103},
    {'code': 'BT423', 'title': 'GREEN ENERGY TECHNOLOGY', 'page': 105},
    {'code': 'BT425', 'title': 'FOOD ENGINEERING & BIOTECHNOLOGY', 'page': 107},
    {'code': 'BT427', 'title': 'WASTE WATER TREATMENT', 'page': 108},
    {'code': 'BT429', 'title': 'BIOPROCESS PLANT DESIGNING', 'page': 110},
    {'code': 'BT431', 'title': 'BIOETHICS AND INTELLECTUAL PROPERTY RIGHTS', 'page': 112},
    {'code': 'BT433', 'title': 'BIOMEDICAL INSTRUMENTATION, BIOSENSOR AND TRANSDUCER', 'page': 113},
    {'code': 'BT435', 'title': 'BIOSTATISTICS', 'page': 115},
    {'code': 'BT404', 'title': 'BIOPROCESS PLANT DESIGN', 'page': 117},
    {'code': 'BT406', 'title': 'POPULATION GENETICS', 'page': 118},
    {'code': 'BT408', 'title': 'BIOPOLYMERS', 'page': 120},
    {'code': 'BT410', 'title': 'GENOMICS IN MEDICINE', 'page': 122},
    {'code': 'BT412', 'title': 'NANOBIOTECHNOLOGY', 'page': 123},
    {'code': 'BT414', 'title': 'MEDICAL PHYSICS', 'page': 124},
    {'code': 'BT416', 'title': 'PHARMACEUTICAL SCIENCES', 'page': 126},
    {'code': 'BT418', 'title': 'AGRICULTURE MICROBIOLOGY', 'page': 128},
    {'code': 'BT420', 'title': 'NUTRACEUTICALS', 'page': 129},
    {'code': 'BT422', 'title': 'TISSUE ENGINEERING AND ARTIFICIAL ORGANS', 'page': 131}
]

def extract_syllabi(doc: fitz.Document, syllabi_list: list, output_folder: str):
    """
    Extracts each syllabus based on the predefined start page. The end of one syllabus
    is defined by the start of the next one.
    """
    print("--- Using predefined page map for extraction ---")
    os.makedirs(output_folder, exist_ok=True)

    for i, syllabus in enumerate(syllabi_list):
        # Page numbers in the list are 1-based, convert to 0-based index
        start_page = syllabus['page'] - 1

        # Define the end page
        if i + 1 < len(syllabi_list):
            end_page = syllabi_list[i+1]['page'] - 2
        else:
            end_page = len(doc) - 1
        
        if start_page > end_page:
            end_page = start_page

        # Sanitize title for a valid filename
        clean_code = syllabus['code'].replace('/', '_')
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
        description="Extracts syllabi from the BT.pdf using a predefined page map.",
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument('pdf_path', help='Path to the input BT.pdf file.')
    parser.add_argument('output_folder', help='Folder to save the extracted PDF files.')
    
    args = parser.parse_args()

    if not os.path.exists(args.pdf_path):
        print(f"Error: PDF file not found at '{args.pdf_path}'")
        return

    doc = fitz.open(args.pdf_path)
    
    extract_syllabi(doc, BT_SUBJECTS, args.output_folder)
    
    doc.close()

if __name__ == '__main__':
    main()