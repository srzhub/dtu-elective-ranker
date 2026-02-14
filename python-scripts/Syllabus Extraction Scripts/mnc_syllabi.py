import fitz  # PyMuPDF
import os
import re
import argparse

# Predefined dictionary of all 2nd year syllabi and their exact start pages
# This is the most reliable method and avoids search errors.
SECOND_YEAR_SUBJECTS = {
    'MC201': {'title': 'Data Structure', 'page': 15},
    'MC203': {'title': 'Real Analysis', 'page': 17},
    'MC205': {'title': 'Probability & Statistics', 'page': 19},
    'MC207': {'title': 'Modern Algebra', 'page': 21},
    'MC209': {'title': 'Database Management System', 'page': 23},
    'MC202': {'title': 'Operating System', 'page': 25},
    'MC204': {'title': 'Scientific Computing', 'page': 27},
    'MC206': {'title': 'Algorithm Design and Analysis', 'page': 29},
    'MC208': {'title': 'Linear Algebra', 'page': 31},
    'MC210': {'title': 'Differential Equations', 'page': 33}
}

def extract_syllabi_from_map(doc: fitz.Document, subjects_map: dict, output_folder: str):
    """
    Extracts a fixed number of pages (2) for each subject using the predefined map.
    """
    print("--- Extracting 2 pages for each syllabus based on predefined map ---")
    os.makedirs(output_folder, exist_ok=True)

    for code, details in subjects_map.items():
        title = details['title']
        # Page numbers in the map are 1-based, convert to 0-based index
        start_page = details['page'] - 1
        end_page = min(start_page + 1, len(doc) - 1)

        clean_title = re.sub(r'[\n/\\:*?"<>|]', '', title).strip()
        out_fname = f"{code}_{clean_title}.pdf"
        out_path = os.path.join(output_folder, out_fname)
        
        print(f"Processing '{code}: {clean_title}'...")
        print(f"  > Extracting pages {start_page + 1} to {end_page + 1}. Saving to '{out_fname}'")

        subdoc = fitz.open()
        subdoc.insert_pdf(doc, from_page=start_page, to_page=end_page)

        if not subdoc:
            print(f"  -> ERROR: Failed to create sub-document for {code}.")
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
        description="Extracts 2-page syllabi for 2nd year MNC courses from a PDF using a predefined page map.",
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument('pdf_path', help='Path to the input MNC.pdf file.')
    parser.add_argument('output_folder', help='Folder to save the extracted PDF files.')
    
    args = parser.parse_args()

    if not os.path.exists(args.pdf_path):
        print(f"Error: PDF file not found at '{args.pdf_path}'")
        return

    doc = fitz.open(args.pdf_path)
    
    extract_syllabi_from_map(doc, SECOND_YEAR_SUBJECTS, args.output_folder)
    
    doc.close()

if __name__ == '__main__':
    main()