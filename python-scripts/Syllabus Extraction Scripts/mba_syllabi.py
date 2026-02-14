import fitz  # PyMuPDF
import os
import re

def extract_specific_syllabi(pdf_path, output_folder, courses_to_extract):
    """
    Extracts specified syllabi from a PDF document.

    A syllabus is defined as the content starting from one course code
    until the beginning of the next course code.

    Args:
        pdf_path (str): The path to the input PDF file.
        output_folder (str): The folder where extracted PDFs will be saved.
        courses_to_extract (list): A list of course codes to extract.
    """
    # Create the output directory if it doesn't exist
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
        print(f"Created output directory: {output_folder}")

    try:
        source_doc = fitz.open(pdf_path)
    except Exception as e:
        print(f"Error: Could not open PDF file at '{pdf_path}'. Please ensure it's in the correct directory.")
        return

    # Regex to find course codes like 'MBAFM 211', 'MBASC-213', etc.
    # This pattern looks for "MBA" followed by letters, an optional space/hyphen, and numbers.
    course_code_pattern = re.compile(r"MBA[A-Z]{2,}\s?[-]?\s?\d{3}")

    # --- Step 1: Find all potential course code locations in the PDF ---
    all_course_starts = []
    print("Scanning document for all course syllabi...")
    for page_num, page in enumerate(source_doc):
        text = page.get_text("text")
        matches = course_code_pattern.finditer(text)
        for match in matches:
            # Normalize the code for easier comparison (e.g., "MBAFM-211" -> "MBAFM211")
            normalized_code = re.sub(r"[\s-]", "", match.group())
            # Find the exact coordinates of the matched text
            rects = page.search_for(match.group())
            if rects:
                all_course_starts.append({
                    "code_text": match.group(),
                    "normalized_code": normalized_code,
                    "page": page_num,
                    "y_start": rects[0].y0  # The top y-coordinate of the course code
                })

    # Sort all found course codes by their position in the document (page, then y-position)
    all_course_starts.sort(key=lambda x: (x["page"], x["y_start"]))

    # --- Step 2: Define the full boundary for each syllabus ---
    syllabus_blocks = []
    for i, start_event in enumerate(all_course_starts):
        # By default, the syllabus ends at the last page of the document
        end_page = len(source_doc) - 1
        y_end = source_doc[end_page].rect.height

        # If there's a next course, the current syllabus ends where the next one begins
        if i + 1 < len(all_course_starts):
            next_event = all_course_starts[i+1]
            end_page = next_event["page"]
            y_end = next_event["y_start"]

        syllabus_blocks.append({
            "code_text": start_event["code_text"],
            "normalized_code": start_event["normalized_code"],
            "start_page": start_event["page"],
            "y_start": start_event["y_start"],
            "end_page": end_page,
            "y_end": y_end
        })

    # --- Step 3: Extract and save only the syllabi the user requested ---
    print(f"\nFound {len(syllabus_blocks)} total syllabi. Now extracting the requested ones...")

    normalized_courses_to_extract = {re.sub(r"[\s-]", "", c) for c in courses_to_extract}
    extracted_count = 0

    for block in syllabus_blocks:
        if block["normalized_code"] in normalized_courses_to_extract:
            extracted_count += 1
            # Create a filename-safe version of the course code
            safe_filename = re.sub(r'[\s-]+', '_', block["code_text"])
            output_filename = os.path.join(output_folder, f"{safe_filename}.pdf")

            print(f"  -> Extracting '{block['code_text']}' to '{output_filename}'")

            # Create a new blank PDF document
            new_doc = fitz.open()
            # Copy the relevant page(s) from the source document
            new_doc.insert_pdf(source_doc, from_page=block["start_page"], to_page=block["end_page"])

            # Crop the first page of the new document
            if len(new_doc) > 0:
                first_page = new_doc[0]
                # If the syllabus is on a single page, the end-Y is y_end, otherwise it's the full page height
                end_y_on_first_page = block["y_end"] if block["start_page"] == block["end_page"] else first_page.rect.height
                crop_box = fitz.Rect(0, block["y_start"], first_page.rect.width, end_y_on_first_page)
                first_page.set_cropbox(crop_box)

            # If the syllabus spans multiple pages, crop the last page
            if len(new_doc) > 1 and block["start_page"] != block["end_page"]:
                last_page = new_doc[-1]
                crop_box = fitz.Rect(0, 0, last_page.rect.width, block["y_end"])
                last_page.set_cropbox(crop_box)

            # Save the newly created and cropped PDF
            new_doc.save(output_filename)
            new_doc.close()

    source_doc.close()

    if extracted_count == 0:
        print("\nWarning: No matching syllabi were found for the codes provided.")
    else:
        print(f"\n✅ Extraction complete. Check the '{output_folder}' directory.")


if __name__ == "__main__":
    # The name of your source PDF file
    PDF_FILE = "MBA.pdf"
    # The name of the folder where extracted PDFs will be saved
    OUTPUT_DIR = "Extracted_Syllabi2"

    # --- List the exact course codes you want to extract here ---
    # This list is now set up to get the ones you were missing.
    COURSES_TO_EXTRACT = [
        "MBA-107",
        "MBASC215",
        "MBA-105",
        "MBAMK213"
        # "MBASC213", # Already extracted
        # "MBAMK219"  # Already extracted
    ]

    if not os.path.exists(PDF_FILE):
        print(f"Error: The file '{PDF_FILE}' was not found. Please place it in the same directory as this script.")
    else:
        extract_specific_syllabi(PDF_FILE, OUTPUT_DIR, COURSES_TO_EXTRACT)