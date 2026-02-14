import fitz  # PyMuPDF
import os
import re
import argparse

# --- Master List of All Civil Engineering Subjects (Core & Electives) ---
CE_SUBJECTS = [
    # Core Subjects from ce_syllabi.pdf
    {'code': 'CE201', 'title': 'Introduction to Earth, Atmosphere, climate, and environmental sciences'},
    {'code': 'CE202', 'title': 'Smart city planning and intelligent transportation'},
    {'code': 'CE203', 'title': 'Design of Structures - I'},
    {'code': 'CE204', 'title': 'Analysis of Structures - II'},
    {'code': 'CE205', 'title': 'Fluid Mechanics'},
    {'code': 'CE206', 'title': 'Soil Mechanics'},
    {'code': 'CE207', 'title': 'Surveying and Geoinformatics'},
    {'code': 'CE208', 'title': 'Environmental Engineering -1'},
    {'code': 'CE209', 'title': 'Analysis of Structure - I'},
    {'code': 'CE210', 'title': 'Hydraulics & Hydraulic Machines'},
    {'code': 'CE301', 'title': 'Geotechnical Engineering'},
    {'code': 'CE302', 'title': 'Design of Steel Structures'},
    {'code': 'CE303', 'title': 'Environment Engineering-II'},
    {'code': 'CE304', 'title': 'Water Resources Engineering'},
    {'code': 'CE305', 'title': 'Transportation Engineering'},
    # Elective Subjects from ce_syllabi_electives.pdf
    {'code': 'CE307', 'title': 'Applications of Geo-informatics, Remote Sensing, and GIS in Engineering'},
    {'code': 'CE306', 'title': 'Infrastructure Resilience and Socio-Economic Dynamics'},
    {'code': 'CE405', 'title': 'Wind Effects on Structures and Wind Energy Systems'},
    {'code': 'CE404', 'title': 'Structural Health Monitoring and Sustainable Infrastructures'},
    {'code': 'CE308', 'title': 'Advanced Design of Structures'},
    {'code': 'CE309', 'title': 'Wind Loads on Structures'},
    {'code': 'CE310', 'title': 'Advanced Design of Steel Structures'},
    {'code': 'CE311', 'title': 'Disaster Management'},
    {'code': 'CE312', 'title': 'Analysis And Design of Underground Structure'},
    {'code': 'CE313', 'title': 'Rock Engineering'},
    {'code': 'CE314', 'title': 'Theory of Elasticity and Plasticity in Soil'},
    {'code': 'CE315', 'title': 'Advanced Mechanics of Soil'},
    {'code': 'CE316', 'title': 'Advanced Fluid Mechanics'},
    {'code': 'CE317', 'title': 'Water Power Engineering'},
    {'code': 'CE318', 'title': 'Environmental Aspects of Water Resources'},
    {'code': 'CE319', 'title': 'Water Resources Planning and System Engineering'},
    {'code': 'CE320', 'title': 'Transportation Safety and Environment'},
    {'code': 'CE321', 'title': 'Computational Fluid Dynamics'},
    {'code': 'CE322', 'title': 'Tunnel, Ports and Harbour Engineering'},
    {'code': 'CE323', 'title': 'Quantity Surveying and Estimation'},
    {'code': 'CE324', 'title': 'Earthquake Technology'},
    {'code': 'CE325', 'title': 'Geodesy and Navigation'},
    {'code': 'CE326', 'title': 'Cyclonic Risk and Management'},
    {'code': 'CE327', 'title': 'AI in Civil Engineering'},
    {'code': 'CE328', 'title': 'Fire Safety of Structures'},
    {'code': 'CE329', 'title': 'Concrete Technology'},
    {'code': 'CE330', 'title': 'Geotechnical Processes'},
    {'code': 'CE332', 'title': 'Transportation Geotechniques'},
    {'code': 'CE334', 'title': 'Design of Hydraulic Structures'},
    {'code': 'CE336', 'title': 'Groundwater Hydrology'},
    {'code': 'CE338', 'title': 'Advanced Transportation Engineering'},
    {'code': 'CE340', 'title': 'Solid Waste Management and Air Pollution'},
    {'code': 'CE342', 'title': 'Experimental Mechanics'},
    {'code': 'CE344', 'title': 'Building Materials, Masonry, Prestressing, and Construction Management'},
    {'code': 'CE406', 'title': 'Pre-stressed Concrete Structures'},
    {'code': 'CE407', 'title': 'Introduction to Building Information Modelling (BIM)'},
    {'code': 'CE408', 'title': 'Retrofitting of Structures'},
    {'code': 'CE409', 'title': 'Design of Bridges'},
    {'code': 'CE410', 'title': 'Advanced Geotechnical Engineering'},
    {'code': 'CE411', 'title': 'Forensic Engineering'},
    {'code': 'CE412', 'title': 'Climate Change and Sustainable Development'},
    {'code': 'CE413', 'title': 'Vulnerability and Risk Management'},
    {'code': 'CE414', 'title': 'Urban Planning and Flood Management'},
    {'code': 'CE415', 'title': 'Geotechnical Exploration and Excavation Methods'},
    {'code': 'CE416', 'title': 'Masonry, Timber, and Bamboo Structures'},
    {'code': 'CE417', 'title': 'Computer Methods in Geotechnical Engineering'},
    {'code': 'CE418', 'title': 'Water Resource Management'},
    {'code': 'CE419', 'title': 'Environmental Geo-Techniques'},
    {'code': 'CE421', 'title': 'Geosynthetics'},
    {'code': 'CE423', 'title': 'Advanced Open Channel Flow'},
    {'code': 'CE425', 'title': 'Flood and Drought Estimation and Management'},
    {'code': 'CE427', 'title': 'Advanced Hydrology'},
    {'code': 'CE429', 'title': 'Urban Water Resource Management'},
    {'code': 'CE431', 'title': 'Traffic Engineering'},
    {'code': 'CE433', 'title': 'Advanced Surveying and Geoinformatics'},
    {'code': 'CE435', 'title': 'Construction Project Management'},
    {'code': 'CE437', 'title': 'Construction and Design Aspects in Transportation Engineering'},
    {'code': 'CE439', 'title': 'Traffic and Transportation Planning'},
    {'code': 'CE441', 'title': 'Finite Element Method'},
    {'code': 'CE443', 'title': 'Sustainable Building Technologies'},
    {'code': 'CE445', 'title': 'Integrated Intelligent Transportation System'}
]

def find_all_syllabi(docs: dict, subjects_list: list) -> list:
    """
    Scans multiple documents to find the start of every syllabus section.
    """
    print("--- Step 1: Discovering all syllabus anchors across all provided PDFs ---")
    discovered = []
    
    for subject in subjects_list:
        search_term = subject['title']
        found_in_any_doc = False
        for doc_name, doc in docs.items():
            for page_num in range(doc.page_count):
                page = doc.load_page(page_num)
                rects = page.search_for(search_term)
                if rects:
                    syllabus_info = {
                        'code': subject['code'],
                        'title': subject['title'],
                        'doc_name': doc_name,
                        'page': page_num,
                    }
                    discovered.append(syllabus_info)
                    print(f"  > Found '{subject['code']}' in '{doc_name}' on page {page_num + 1}")
                    found_in_any_doc = True
                    break  # Stop searching pages in this doc
            if found_in_any_doc:
                break # Stop searching other docs for this subject
        if not found_in_any_doc:
            print(f"  > WARNING: Could not find syllabus for '{subject['code']}' in any PDF.")
            
    # Sort by the order they appear in the master list, which should reflect the PDF order
    discovered.sort(key=lambda x: CE_SUBJECTS.index(next(s for s in CE_SUBJECTS if s['code'] == x['code'])))
    print(f"\n--- Discovered and sorted {len(discovered)} syllabi. ---\n")
    return discovered

def extract_syllabi(docs: dict, syllabi_list: list, output_folder: str):
    """
    Extracts each syllabus. The end is defined by the start of the next one.
    """
    print("--- Step 2: Extracting syllabi based on the discovered map ---")
    os.makedirs(output_folder, exist_ok=True)

    for i, syllabus in enumerate(syllabi_list):
        start_doc_name = syllabus['doc_name']
        start_doc = docs[start_doc_name]
        start_page = syllabus['page']

        if i + 1 < len(syllabi_list):
            next_syllabus = syllabi_list[i+1]
            end_doc_name = next_syllabus['doc_name']
            # End page is the one right before the next syllabus starts
            end_page = next_syllabus['page'] - 1
            
            # If the next syllabus is in a different PDF, we extract to the end of the current PDF
            if start_doc_name != end_doc_name:
                end_page = len(start_doc) - 1
        else:
            # For the very last syllabus, extract to the end of its document
            end_page = len(start_doc) - 1

        if start_page > end_page:
            end_page = start_page

        clean_code = syllabus['code'].replace('/', '_')
        clean_title = re.sub(r'[\n/\\:*?"<>|]', '', syllabus['title']).strip()
        out_fname = f"{clean_code}.pdf"
        out_path = os.path.join(output_folder, out_fname)
        
        print(f"Processing '{syllabus['code']}: {clean_title}'...")
        print(f"  > Extracting from '{start_doc_name}' (pages {start_page + 1} to {end_page + 1}). Saving to '{out_fname}'")

        subdoc = fitz.open()
        subdoc.insert_pdf(start_doc, from_page=start_page, to_page=end_page)

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
        description="Extracts all Civil Engineering syllabi from core and elective PDFs.",
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument('core_pdf_path', help='Path to the main syllabus PDF (ce_syllabi.pdf).')
    parser.add_argument('elective_pdf_path', help='Path to the elective syllabus PDF (ce_syllabi_electives.pdf).')
    parser.add_argument('output_folder', help='Folder to save the extracted PDF files.')
    
    args = parser.parse_args()

    docs = {}
    try:
        docs[args.core_pdf_path] = fitz.open(args.core_pdf_path)
        docs[args.elective_pdf_path] = fitz.open(args.elective_pdf_path)
    except Exception as e:
        print(f"Error opening PDF files: {e}")
        return

    syllabi_list = find_all_syllabi(docs, CE_SUBJECTS)
    extract_syllabi(docs, syllabi_list, args.output_folder)
    
    for doc in docs.values():
        doc.close()

if __name__ == '__main__':
    main()