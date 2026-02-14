import fitz  # PyMuPDF
import os

# This is the course data you provided
COURSE_DATA = [
    {"code": "SE104", "title": "Basics of Software Engineering", "semester": 1},
    {"code": "SE102", "title": "Fundamentals of Computers", "semester": 1},
    {"code": "SE103", "title": "Computer Workshop 1", "semester": 1},
    {"code": "SE106", "title": "Computer Workshop 2", "semester": 2},
    {"code": "SE201", "title": "Digital Systems & Design", "semester": 3},
    {"code": "SE203", "title": "Data Structures", "semester": 3},
    {"code": "SE205", "title": "Object Oriented Programming", "semester": 3},
    {"code": "SE207", "title": "Operating System", "semester": 3},
    {"code": "SE209", "title": "Software Engineering Methodologies", "semester": 3},
    {"code": "SE204", "title": "Object Oriented Software Engineering", "semester": 4},
    {"code": "SE202", "title": "Computer System Architecture", "semester": 4},
    {"code": "SE206", "title": "Machine Learning", "semester": 4},
    {"code": "SE208", "title": "Database Management Systems", "semester": 4},
    {"code": "MSE210", "title": "Algorithm Design and Analysis", "semester": 4},
    {"code": "SE301", "title": "Software Testing", "semester": 5},
    {"code": "SE303", "title": "Software Quality and Metrics", "semester": 5},
    {"code": "SE305", "title": "Computer Networks", "semester": 5},
    {"code": "SE307", "title": "Software Requirement Engineering", "semester": 5},
    {"code": "SE309", "title": "Computer Graphics", "semester": 5},
    {"code": "SE311", "title": "Information Theory and Coding", "semester": 5},
    {"code": "SE313", "title": "Digital Signal Processing", "semester": 5},
    {"code": "SE315", "title": "Advanced Data Structures", "semester": 5},
    {"code": "SE317", "title": "Discrete Structures", "semester": 5},
    {"code": "SE319", "title": "Distributed Systems", "semester": 5},
    {"code": "SE321", "title": "Soft Computing", "semester": 5},
    {"code": "SE323", "title": "Artificial Intelligence", "semester": 5},
    {"code": "SE325", "title": "Theory of Computation", "semester": 5},
    {"code": "SE327", "title": "Web Technology", "semester": 5},
    {"code": "SE329", "title": "Methods for Data Analysis", "semester": 5},
    {"code": "SE331", "title": "Predictive Analytics", "semester": 5},
    {"code": "SE333", "title": "Artificial Intelligence for Sports", "semester": 5},
    {"code": "SE302", "title": "Empirical Software Engineering", "semester": 6},
    {"code": "SE304", "title": "Compiler Design", "semester": 6},
    {"code": "SE306", "title": "Software Reliability", "semester": 6},
    {"code": "SE308", "title": "Multimedia Systems", "semester": 6},
    {"code": "SE310", "title": "Parallel Computer Architecture", "semester": 6},
    {"code": "SE312", "title": "Introduction to Health Care Analytics", "semester": 6},
    {"code": "SE314", "title": "Natural Language Processing", "semester": 6},
    {"code": "SE316", "title": "Advanced Database Management Systems", "semester": 6},
    {"code": "SE318", "title": "Data Compression", "semester": 6},
    {"code": "SE320", "title": "Real Time Systems", "semester": 6},
    {"code": "SE322", "title": "Parallel Algorithms", "semester": 6},
    {"code": "SE324", "title": "Probability and Statistics", "semester": 6},
    {"code": "SE326", "title": "Artificial Intelligence for Sports Surfaces and Equipment", "semester": 6},
    {"code": "SE328", "title": "Sports Business Analytics", "semester": 6},
    {"code": "SE405", "title": "Software Maintenance", "semester": 7},
    {"code": "SE407", "title": "Deep Learning", "semester": 7},
    {"code": "SE409", "title": "Grid and Cluster Computing", "semester": 7},
    {"code": "SE411", "title": "Pattern Recognition", "semester": 7},
    {"code": "SE413", "title": "Agile Software Process", "semester": 7},
    {"code": "SE415", "title": "Cyber Forensics", "semester": 7},
    {"code": "SE417", "title": "Robotics", "semester": 7},
    {"code": "SE419", "title": "Wireless and Mobile Computing", "semester": 7},
    {"code": "SE421", "title": "Intellectual Property Rights and Cyber Laws", "semester": 7},
    {"code": "SE423", "title": "Software Project Management", "semester": 7},
    {"code": "SE425", "title": "Data Warehouse and Data Mining", "semester": 7},
    {"code": "SE427", "title": "Data Management and Ethics", "semester": 7},
    {"code": "SE429", "title": "GPU Computing", "semester": 7},
    {"code": "SE431", "title": "Data Security and Privacy", "semester": 7},
    {"code": "SE433", "title": "Quantum Computing", "semester": 7},
    {"code": "SE404", "title": "Advances in Software Engineering", "semester": 8},
    {"code": "SE406", "title": "Information and Network Security", "semester": 8},
    {"code": "SE408", "title": "Swarm and Evolutionary Computing", "semester": 8},
    {"code": "SE410", "title": "Semantic Web and Web Mining", "semester": 8},
    {"code": "SE412", "title": "Cloud Computing", "semester": 8},
    {"code": "SE414", "title": "Big Data Analytics", "semester": 8}
]

def find_syllabus_starts(doc, start_page_num):
    """
    Scans the PDF and finds the starting page for each syllabus.
    Uses a "first match wins" logic for each page.
    """
    syllabus_locations = []
    found_titles = set()

    print("Scanning document to locate syllabi...")
    # Iterate through each page to find the first matching syllabus title
    for page_num in range(start_page_num - 1, len(doc)):
        page = doc.load_page(page_num)
        # Iterate through our list of courses
        for course in COURSE_DATA:
            # If we haven't already found this course, search for its title on the current page
            if course["title"] not in found_titles:
                if page.search_for(course["title"]):
                    print(f"  Found '{course['title']}' on page {page_num + 1}")
                    syllabus_locations.append({
                        "code": course["code"],
                        "page": page_num
                    })
                    found_titles.add(course["title"])
                    # Once we find a match on this page, we "claim" it and move to the next page
                    break 

    return syllabus_locations

def extract_syllabi_from_se_pdf(pdf_path, output_folder, start_page=13):
    """
    Extracts syllabi from the SE.pdf file using improved logic.
    - Limits syllabus length to a maximum of 2 pages.
    - Prevents multiple syllabi from being detected on the same page.
    """
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
        print(f"Created directory: {output_folder}")

    try:
        source_doc = fitz.open(pdf_path)
    except Exception as e:
        print(f"Error: Could not open PDF file at '{pdf_path}'. Details: {e}")
        return

    # 1. Find the starting pages of all syllabi first
    found_syllabi = find_syllabus_starts(source_doc, start_page)

    if not found_syllabi:
        print("No syllabi could be located based on the provided course titles.")
        return

    print(f"\nFound {len(found_syllabi)} unique syllabi. Starting extraction...")

    # 2. Extract each syllabus based on the located start pages
    for i in range(len(found_syllabi)):
        current_syllabus = found_syllabi[i]
        start_page_num = current_syllabus["page"]
        course_code = current_syllabus["code"]

        # 3. Determine the end page with new logic
        end_page_num = 0
        if i + 1 < len(found_syllabi):
            # End page is the page before the next syllabus starts
            end_page_num = found_syllabi[i+1]["page"] - 1
        else:
            # This is the last syllabus, so it goes to the end of the doc
            end_page_num = len(source_doc) - 1

        # --- ENFORCE THE 2-PAGE LIMIT ---
        # If the calculated range is more than 2 pages, cap it.
        if end_page_num > start_page_num + 1:
            end_page_num = start_page_num + 1

        # Final check to ensure the end page is not before the start page
        if end_page_num < start_page_num:
            end_page_num = start_page_num
            
        # 4. Create and save the new PDF for the syllabus
        output_filename = os.path.join(output_folder, f"{course_code}.pdf")
        with fitz.open() as subject_doc:
            subject_doc.insert_pdf(source_doc, from_page=start_page_num, to_page=end_page_num)
            subject_doc.save(output_filename)
            print(f"  -> Saved '{output_filename}' (pages {start_page_num + 1} to {end_page_num + 1})")

    source_doc.close()
    print(f"\n✅ Extraction complete! Files are in the '{output_folder}' directory.")

if __name__ == "__main__":
    pdf_file_path = "SE.pdf"
    output_directory = "Extracted_SE_Syllabi_Improved" # Using a new folder name

    if os.path.exists(pdf_file_path):
        extract_syllabi_from_se_pdf(pdf_file_path, output_directory, start_page=13)
    else:
        print(f"Fatal Error: The file '{pdf_file_path}' was not found.")