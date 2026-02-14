import fitz  # PyMuPDF
import os
import re
import argparse

# --- Predefined List of EC Syllabi and Their Start Pages ---
# This list is manually created for the EC.pdf file for maximum accuracy.
EC_SUBJECTS = [
    # 2nd Year
    {'code': 'EC201', 'title': 'Probability and Random Processes', 'page': 9},
    {'code': 'EC203', 'title': 'Digital Design-1', 'page': 11},
    {'code': 'EC205', 'title': 'Signals and Systems', 'page': 13},
    {'code': 'EC207', 'title': 'Analog Electronics-I', 'page': 15},
    {'code': 'EC209', 'title': 'Communication Systems', 'page': 17},
    {'code': 'EC202', 'title': 'Electromagnetic Field Theory', 'page': 19},
    {'code': 'EC204', 'title': 'Digital Design - II', 'page': 21},
    {'code': 'EC206', 'title': 'Digital Communication', 'page': 23},
    {'code': 'EC208', 'title': 'Computer Architecture', 'page': 25},
    {'code': 'EC210', 'title': 'Analog Electronics - II', 'page': 27},
    # 3rd Year
    {'code': 'EC301', 'title': 'Digital Signal Processing', 'page': 29},
    {'code': 'EC303', 'title': 'Linear Integrated Circuit', 'page': 31},
    {'code': 'EC305', 'title': 'Microwave & RF Communication', 'page': 34},
    {'code': 'EC307', 'title': 'Semiconductor Device Electronics', 'page': 36},
    {'code': 'EC309', 'title': 'Bio-Medical Electronics & Instrumentation', 'page': 38},
    {'code': 'EC311', 'title': 'Algorithms Design and Analysis', 'page': 40},
    {'code': 'EC313', 'title': 'Microprocessor and Interfacing', 'page': 43},
    {'code': 'EC315', 'title': 'IC Technology', 'page': 45},
    {'code': 'EC317', 'title': 'Control Systems', 'page': 47},
    {'code': 'EC302', 'title': 'VLSI Design', 'page': 49},
    {'code': 'EC304', 'title': 'Embedded Systems', 'page': 51},
    {'code': 'EC306', 'title': 'Flexible Electronics', 'page': 53},
    {'code': 'EC308', 'title': 'Analog Filter Design', 'page': 55},
    {'code': 'EC310', 'title': 'Testing and Diagnosis of Digital System Design', 'page': 57},
    {'code': 'EC312', 'title': 'Software Defined Radio', 'page': 59},
    {'code': 'EC314', 'title': 'Machine Learning', 'page': 61},
    {'code': 'EC316', 'title': 'Wireless Sensor Networks', 'page': 63},
    {'code': 'EC318', 'title': 'RF MEMS Design and Technology', 'page': 65},
    {'code': 'EC320', 'title': 'Soft Computing', 'page': 67},
    {'code': 'EC322', 'title': 'Operating Systems', 'page': 69},
    {'code': 'EC324', 'title': 'Speech Processing', 'page': 71},
    {'code': 'EC326', 'title': 'Digital Image Processing', 'page': 73},
    {'code': 'EC328', 'title': 'Information Theory and Coding', 'page': 75},
    # 4th Year
    {'code': 'EC401', 'title': 'Radar Signal Processing', 'page': 77},
    {'code': 'EC403', 'title': 'Statistical Signal Processing', 'page': 79},
    {'code': 'EC405', 'title': 'System on Chip Design', 'page': 81},
    {'code': 'EC407', 'title': 'Optical Communication', 'page': 83},
    {'code': 'EC409', 'title': 'Computer Vision', 'page': 85},
    {'code': 'EC411', 'title': 'Bio-Medical Signal Processing', 'page': 87},
    {'code': 'EC413', 'title': 'MEMS and Sensor Design', 'page': 89},
    {'code': 'EC415', 'title': 'Nanophotonic Devices for Communications', 'page': 91},
    {'code': 'EC417', 'title': 'Spread Spectrum Communication', 'page': 92},
    {'code': 'EC419', 'title': 'Adaptive Signal Processing', 'page': 95},
    {'code': 'EC421', 'title': 'Data Analytics', 'page': 97},
    {'code': 'EC423', 'title': 'Multi-rate Signal Processing', 'page': 99},
    {'code': 'EC402', 'title': 'Smart Antennas', 'page': 101},
    {'code': 'EC404', 'title': 'Wireless Communications', 'page': 103},
    {'code': 'EC406', 'title': 'Deep Learning', 'page': 105},
    {'code': 'EC408', 'title': 'Low-Power VLSI Design', 'page': 107},
    {'code': 'EC410', 'title': 'Estimation and Detection Theory', 'page': 109},
    {'code': 'EC412', 'title': 'Fundamentals of MIMO', 'page': 111}
]

def extract_syllabi(doc: fitz.Document, syllabi_list: list, output_folder: str):
    """
    Extracts each syllabus based on the predefined start page.
    The end of one syllabus is defined by the start of the next one.
    """
    print("--- Step 1: Using predefined page map for extraction ---")
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
        clean_code = syllabus['code'].replace('/', '_')
        clean_title = re.sub(r'[\n/\\:*?"<>|]', '', syllabus['title']).strip()
        out_fname = f"{clean_code}.pdf"
        out_path = os.path.join(output_folder, out_fname)
        
        print(f"Processing '{syllabus['code']}: {clean_title}'...")
        print(f"  > Extracting from page {start_page + 1} to {end_page + 1}. Saving to '{out_fname}'")

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
        description="Extracts syllabi from the EC.pdf using a predefined page map.",
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument('pdf_path', help='Path to the input EC.pdf file.')
    parser.add_argument('output_folder', help='Folder to save the extracted PDF files.')
    
    args = parser.parse_args()

    if not os.path.exists(args.pdf_path):
        print(f"Error: PDF file not found at '{args.pdf_path}'")
        return

    doc = fitz.open(args.pdf_path)
    
    # Use the predefined list of EC subjects
    extract_syllabi(doc, EC_SUBJECTS, args.output_folder)
    
    doc.close()

if __name__ == '__main__':
    main()