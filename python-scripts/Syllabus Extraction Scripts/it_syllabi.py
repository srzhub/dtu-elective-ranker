import fitz  # PyMuPDF
import os
import re
import argparse

# --- Configuration: The full list of subjects ---
SUBJECTS = [
    # SEMESTER 1
    {'course_code': 'IT101', 'subject_name': 'Mathematics-I'},
    {'course_code': 'IT103', 'subject_name': 'Physics/Programming Fundamentals'},
    {'course_code': 'IT105', 'subject_name': 'Basic Electrical Engineering'},
    {'course_code': 'IT107', 'subject_name': 'Basic of Electronics & Communication'},
    {'course_code': 'IT109', 'subject_name': 'Fundamentals of Web Design'},
    # Note: Ability Enhancement Course-I (IT111) is in the PDF but not the JSON.

    # SEMESTER 2
    {'course_code': 'IT102', 'subject_name': 'Mathematics-II'},
    {'course_code': 'IT104', 'subject_name': 'Programming Fundamentals/Physics'},
    {'course_code': 'IT106', 'subject_name': 'Discrete Structures'},
    {'course_code': 'IT108', 'subject_name': 'Object Oriented Programming'},
    {'course_code': 'IT110', 'subject_name': 'Open Source Programming'},
    # Note: Ability Enhancement Course-II (IT112) is in the PDF but not the JSON.

    # SEMESTER 3
    {'course_code': 'IT201', 'subject_name': 'Digital Systems and Microcontrollers'},
    {'course_code': 'IT203', 'subject_name': 'Data Structures'},
    {'course_code': 'IT205', 'subject_name': 'Data Science and Visualization'},
    {'course_code': 'IT207', 'subject_name': 'Data Communications'},
    {'course_code': 'IT209', 'subject_name': 'Theory of Computation'},

    # SEMESTER 4
    {'course_code': 'IT202', 'subject_name': 'Software Engineering'},
    {'course_code': 'IT204', 'subject_name': 'Algorithm Design and Analysis'},
    {'course_code': 'IT206', 'subject_name': 'Operating Systems'},
    {'course_code': 'IT208', 'subject_name': 'Database Management Systems'},
    {'course_code': 'IT210', 'subject_name': 'Machine Learning'},

    # SEMESTER 5
    {'course_code': 'IT301', 'subject_name': 'Compiler Design'},
    {'course_code': 'IT303', 'subject_name': 'Computer Networks'},
    {'course_code': 'IT305', 'subject_name': 'Computer Organization and Architecture'},
    {'course_code': 'SECXX', 'subject_name': 'Engg. Economics/Fundamentals of Mgmt.'},
    {'course_code': 'IT309', 'subject_name': 'Deep Learning'},
    {'course_code': 'IT311', 'subject_name': 'Cyber Laws'},
    {'course_code': 'IT313', 'subject_name': 'Malware Analysis'},
    {'course_code': 'IT315', 'subject_name': 'Internet of Things'},
    {'course_code': 'IT317', 'subject_name': 'Computer Graphics'},
    {'course_code': 'IT319', 'subject_name': 'Software Project Management'},
    {'course_code': 'IT351', 'subject_name': 'Data Structures and Algorithms'},
    {'course_code': 'IT353', 'subject_name': 'Information and Network Security'},
    {'course_code': 'IT355', 'subject_name': 'Introduction to Computer Networks'},
    {'course_code': 'IT357', 'subject_name': 'Computer Architecture'},
    {'course_code': 'IT359', 'subject_name': 'Introduction to Database Systems'},
    {'course_code': 'IT361', 'subject_name': 'Computer Vision and Applications'},

    # SEMESTER 6
    {'course_code': 'IT302', 'subject_name': 'Data Engineering and Analytics'},
    {'course_code': 'IT304', 'subject_name': 'Cyber Security'},
    {'course_code': 'SECXX', 'subject_name': 'Fundamentals of Mgmt./Engg. Economics'},
    {'course_code': 'IT308', 'subject_name': 'Distributed and Cloud Computing'},
    {'course_code': 'IT310', 'subject_name': 'Pattern Recognition'},
    {'course_code': 'IT312', 'subject_name': 'Secure Coding'},
    {'course_code': 'IT314', 'subject_name': 'Wireless Ad hoc Mobile Networks'},
    {'course_code': 'IT316', 'subject_name': 'Blockchain Technology'},
    {'course_code': 'IT318', 'subject_name': 'Digital Image Processing'},
    {'course_code': 'IT320', 'subject_name': 'Natural Language Processing'},
    {'course_code': 'IT322', 'subject_name': 'Cyber and Digital Forensics'},
    {'course_code': 'IT324', 'subject_name': 'Computer Vision'},
    {'course_code': 'IT326', 'subject_name': 'Artificial Intelligence'},
    {'course_code': 'IT328', 'subject_name': 'Software Testing'},
    {'course_code': 'IT330', 'subject_name': 'Competitive Programming'},
    {'course_code': 'IT352', 'subject_name': 'Deep Learning Applications'},
    {'course_code': 'IT354', 'subject_name': 'Introduction to JAVA programming'},
    {'course_code': 'IT356', 'subject_name': 'Operating System Principles'},
    {'course_code': 'IT358', 'subject_name': 'Data Analysis using R'},
    {'course_code': 'IT360', 'subject_name': 'Dependable Machine Learning'},
    {'course_code': 'IT362', 'subject_name': 'Embedded Systems'},

    # SEMESTER 7
    {'course_code': 'IT401', 'subject_name': 'B.Tech Project-I'},
    {'course_code': 'IT403', 'subject_name': 'Internship'},
    {'course_code': 'IT425', 'subject_name': 'Social Networks'},
    {'course_code': 'IT427', 'subject_name': 'Intrusion Detection and Info. Warfare'},
    {'course_code': 'IT405', 'subject_name': 'High Performance Computing'},
    {'course_code': 'IT407', 'subject_name': 'High Speed Networks'},
    {'course_code': 'IT409', 'subject_name': 'Information Security and Audit'},
    {'course_code': 'IT411', 'subject_name': 'Multimedia System Design'},
    {'course_code': 'IT413', 'subject_name': 'Multimodal Data Processing'},
    {'course_code': 'IT415', 'subject_name': 'Big Data Analysis'},
    {'course_code': 'IT417', 'subject_name': 'Mobile and Digital Forensics'},
    {'course_code': 'IT419', 'subject_name': 'Soft Computing'},
    {'course_code': 'IT421', 'subject_name': 'Augmented Reality & Virtual Reality'},
    {'course_code': 'IT423', 'subject_name': 'Enterprise JAVA'},
    {'course_code': 'IT451', 'subject_name': 'Intro. to Cyber and Physical Systems'},
    {'course_code': 'IT453', 'subject_name': 'Data Warehousing and Data Mining'},
    {'course_code': 'IT455', 'subject_name': 'Game Theory'},
    {'course_code': 'IT457', 'subject_name': 'Information Theory and Coding'},
    {'course_code': 'IT459', 'subject_name': 'Pattern Recognition and Applications'},
    {'course_code': 'IT461', 'subject_name': 'Grid and Cluster Computing'},
    {'course_code': 'VACXX', 'subject_name': 'Indian Knowledge Systems'},

    # SEMESTER 8
    {'course_code': 'IT402', 'subject_name': 'B.Tech Project-II'},
    {'course_code': 'IT414', 'subject_name': 'Speech & Natural Lang. Understanding'},
    {'course_code': 'IT404', 'subject_name': 'Ethical Hacking'},
    {'course_code': 'IT406', 'subject_name': 'Quantum Computing'},
    {'course_code': 'IT408', 'subject_name': 'GPU Computing'},
    {'course_code': 'IT410', 'subject_name': 'Autonomous Systems and Robotics'},
    {'course_code': 'IT412', 'subject_name': 'Semantic Web and Web Mining'},
    {'course_code': 'IT452', 'subject_name': 'Mobile Application Development'},
    {'course_code': 'IT454', 'subject_name': 'Edge and Fog Computing'},
    {'course_code': 'IT456', 'subject_name': 'Cognitive Computing'},
    {'course_code': 'IT458', 'subject_name': 'Neuromorphic Computing'},
    {'course_code': 'IT460', 'subject_name': 'Optimization Techniques'},
    {'course_code': 'IT462', 'subject_name': 'Pervasive and Ubiquitous Computing'},
]

def find_validated_start(doc, subject, search_page, last_y):
    """
    Finds the start of a subject by searching for its name and validating it.
    Validation means 'Course Objective' or 'Course Outcomes' is found shortly after.
    """
    name_term = subject['subject_name'].replace('\n', ' ')
    
    for p_num in range(search_page, len(doc)):
        page = doc.load_page(p_num)
        rects = page.search_for(name_term)
        
        for r in rects:
            # Ensure we are looking forward in the document
            if p_num == search_page and r.y0 <= last_y:
                continue
            
            # --- VALIDATION STEP ---
            clip_area = fitz.Rect(0, r.y1, page.rect.width, r.y1 + 150)
            has_objective = page.search_for("Course Objective:", clip=clip_area)
            has_outcomes = page.search_for("Course Outcomes (CO)", clip=clip_area)
            # Adding another common keyword for robustness
            has_outcomes_alt = page.search_for("Course Outcomes (CO)", clip=clip_area)


            if has_objective or has_outcomes or has_outcomes_alt:
                return (p_num, r.y0)
                
    return None


def extract_syllabi(pdf_path, output_folder, subjects, start_page=0):
    """
    Extracts syllabi using a corrected version of the original, sequential logic.
    """
    os.makedirs(output_folder, exist_ok=True)
    doc = fitz.open(pdf_path)
    print(f"Opened '{pdf_path}' ({len(doc)} pages). Starting extraction...")

    last_end_page = start_page
    last_end_y = -1 # Start at -1 to ensure the first item on the page is found

    for i, info in enumerate(subjects):
        code = info['course_code']
        name = info['subject_name'].replace('\n', ' ')
        print(f"\nProcessing '{code}': {name}")

        # --- Step 1: Find a RELIABLE Start Event ---
        start_evt = find_validated_start(doc, info, last_end_page, last_end_y)

        if not start_evt:
            print(f"  -> WARNING: Could not find a validated start for '{name}'. Skipping.")
            continue
            
        start_page_num, start_y = start_evt
        print(f"  > Found validated start on page {start_page_num + 1}")

        # --- Step 2: Find a RELIABLE End Event ---
        end_evt = None
        
        if i + 1 < len(subjects):
            next_subject = subjects[i+1]
            end_evt = find_validated_start(doc, next_subject, start_page_num, start_y)
            if end_evt:
                print(f"  > Found end-point using start of next subject ('{next_subject['subject_name'].replace(chr(10),' ')}') on page {end_evt[0] + 1}")

        if not end_evt:
            for p_num in range(start_page_num, len(doc)):
                page = doc.load_page(p_num)
                # Use a more generic end-of-section marker
                rects = page.search_for("REFERENCES")
                if rects:
                    for r in rects:
                        if p_num > start_page_num or r.y0 > start_y:
                            # Try to get the bounding box of the entire references table/block
                            try:
                                blocks = page.get_text("blocks", clip=fitz.Rect(0, r.y0, page.rect.width, page.rect.height))
                                end_y_coord = blocks[-1][3] + 5 if blocks else r.y1 + 10
                                end_evt = (p_num, end_y_coord)
                                print(f"  > Using 'REFERENCES' as end-point on page {p_num + 1}")
                            except:
                                end_evt = (p_num, r.y1 + 10)
                            break
                if end_evt:
                    break
        
        if not end_evt:
             end_evt = (start_page_num, doc.load_page(start_page_num).rect.height)
             print("  > WARNING: No definitive end-point found. Ending at page bottom.")

        end_page_num, end_y = end_evt
        
        last_end_page = start_page_num # Start next search from the same page
        last_end_y = start_y # Update the y-coordinate to search below

        # --- Step 3: Extract and Save ---
        clean_name = re.sub(r'[\n/\\:*?"<>|]', ' ', name).strip()
        out_fname = f"{code}.pdf"
        out_path = os.path.join(output_folder, out_fname)

        subdoc = fitz.open()
        subdoc.insert_pdf(doc, from_page=start_page_num, to_page=end_page_num)

        if not subdoc:
            print(f"  -> ERROR: Could not create PDF for '{code}'.")
            continue

        # --- CROP LOGIC FIX ---
        # The 'rect' attribute belongs to a Page, not a Document.
        
        page_for_dims = doc.load_page(start_page_num) # Get original page for dimensions
        page_width = page_for_dims.rect.width
        page_height = page_for_dims.rect.height

        if start_page_num == end_page_num:
            # Crop a single page
            subdoc[0].set_cropbox(fitz.Rect(0, start_y, page_width, end_y))
        else:
            # Crop the first page of a multi-page section
            subdoc[0].set_cropbox(fitz.Rect(0, start_y, page_width, page_height))
            # Crop the last page of a multi-page section
            if len(subdoc) > 1:
                last_page_dims = doc.load_page(end_page_num).rect
                subdoc[-1].set_cropbox(fitz.Rect(0, 0, last_page_dims.width, end_y))

        subdoc.save(out_path, garbage=4, deflate=True)
        subdoc.close()
        print(f"  > Saved to '{out_fname}'")

    doc.close()
    print("\n✅ Extraction complete.")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Extract and crop syllabi sections using validated anchors.')
    parser.add_argument('pdf', help='Input PDF file path')
    parser.add_argument('outdir', help='Output directory')
    parser.add_argument('--start', type=int, default=1, help='Page number to start search (1-based)')
    args = parser.parse_args()
    
    extract_syllabi(args.pdf, args.outdir, SUBJECTS, start_page=args.start-1)