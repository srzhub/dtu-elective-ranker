import fitz  # PyMuPDF
import os
import re
import argparse
import json
from typing import List, Dict, Tuple, Optional

# Enhanced EP subjects list with better page detection
EP_SUBJECTS = [
    {'code': 'EP101', 'title': 'Physics', 'page': 10},
    {'code': 'EP102', 'title': 'Computational Methods', 'page': 13},
    {'code': 'EP104', 'title': 'Fundamentals of Electrodynamics', 'page': 15},
    {'code': 'EP207', 'title': 'Digital and Analog Electronics', 'page': 17},
    {'code': 'EP201', 'title': 'Classical Mechanics', 'page': 19},
    {'code': 'EP203', 'title': 'Mathematical Physics', 'page': 20},
    {'code': 'ESC-1', 'title': 'Introduction to Computing', 'page': 22},
    {'code': 'EP205', 'title': 'Quantum Mechanics', 'page': 24},
    {'code': 'EP204', 'title': 'Thermal Physics', 'page': 26},
    {'code': 'EP208', 'title': 'AI for Material Science', 'page': 29},
    {'code': 'EP206', 'title': 'Microprocessors Architecture and Programming', 'page': 32},
    {'code': 'ESC-2', 'title': 'Communication System', 'page': 34},
    {'code': 'EP202', 'title': 'Condensed Matter Physics', 'page': 37},
    {'code': 'EP301', 'title': 'Semiconductor Devices', 'page': 39},
    {'code': 'EP303', 'title': 'Electromagnetic Theory, antennas and Propagation', 'page': 40},
    {'code': 'HU301', 'title': 'Technical Communication', 'page': 42},
    {'code': 'EP302', 'title': 'Fiber Optics and Optical Communication', 'page': 43},
    {'code': 'EP304', 'title': 'Fabrication and Characterization of Nanostructures', 'page': 44},
    {'code': 'EP306', 'title': 'Microwave Engineering', 'page': 45},
    {'code': 'HU304', 'title': 'Professional Ethics and Human Values', 'page': 47},
    {'code': 'EP401', 'title': 'B.Tech Project-I', 'page': 48},
    {'code': 'EP403', 'title': 'Training Seminar', 'page': 48},
    {'code': 'EP405', 'title': 'VLSI and FPGA Design', 'page': 48},
    {'code': 'EP407', 'title': 'Mobile and Satellite Communication', 'page': 49},
    {'code': 'EP402', 'title': 'B.Tech project-II', 'page': 51},
    {'code': 'EP404', 'title': 'Alternative Energy Storage and Conversion Devices', 'page': 51},
    {'code': 'EP305', 'title': 'Atomic and Molecular Physics', 'page': 54},
    {'code': 'EP307', 'title': 'Biophysics', 'page': 55},
    {'code': 'EP309', 'title': 'Quantum Information and Computing', 'page': 56},
    {'code': 'EP311', 'title': 'Computer Networking', 'page': 57},
    {'code': 'EP308', 'title': 'Laser and Instrumentation', 'page': 59},
    {'code': 'EP310', 'title': 'MEDICAL PHYSICS AND PHYSIOLOGICAL MEASUREMENTS', 'page': 60},
    {'code': 'EP312', 'title': 'FOURIER OPTICS AND HOLOGRAPHY', 'page': 61},
    {'code': 'EP314', 'title': 'Instrumentation and Control', 'page': 62},
    {'code': 'EP316', 'title': 'Cosmology and Astrophysics', 'page': 63},
    {'code': 'EP409', 'title': 'Information Theory and Coding', 'page': 64},
    {'code': 'EP411', 'title': 'Advanced Simulation Techniques in Physics', 'page': 65},
    {'code': 'EP413', 'title': 'Continuum Mechanics', 'page': 66},
    {'code': 'EP415', 'title': 'Nanoscience & Technology', 'page': 67},
    {'code': 'EP417', 'title': 'Photonics', 'page': 68},
    {'code': 'EP419', 'title': 'Introduction to Automation and Motion Control', 'page': 70},
    {'code': 'EP421', 'title': 'Principles of Nuclear Engineering', 'page': 71},
    {'code': 'EP423', 'title': 'Space and Atmospheric Science-I', 'page': 72},
    {'code': 'EP425', 'title': 'Plasma Science and Technology-I', 'page': 73},
    {'code': 'EP406', 'title': 'INTRODUCTION TO SPINTRONICS', 'page': 75},
    {'code': 'EP408', 'title': 'Integrated Optics', 'page': 76},
    {'code': 'EP410', 'title': 'Robotic Engineering', 'page': 77},
    {'code': 'EP412', 'title': 'Nuclear Materials for Engineering Applications', 'page': 78},
    {'code': 'EP414', 'title': 'Space and Atmospheric Science-II', 'page': 79},
    {'code': 'EP416', 'title': 'Plasma Science and Technology-II', 'page': 80},
    {'code': 'EP418', 'title': 'Digital Signal Processing', 'page': 81},
    {'code': 'EP420', 'title': 'Fuzzy Logic and Neural Network', 'page': 83},
    {'code': 'EP422', 'title': 'Embedded Systems', 'page': 84}
]

def detect_syllabus_boundaries(doc: fitz.Document) -> List[Dict]:
    """
    Automatically detect syllabus boundaries by looking for subject codes and patterns.
    """
    detected_syllabi = []
    
    # Common patterns for subject codes
    subject_patterns = [
        r'Subject Code:\s*([A-Z]{2,3}[-\s]*\d{3})',
        r'Course Title:\s*(.+?)(?:\n|$)',
        r'^\s*(\d+\.)\s*Subject Code:\s*([A-Z]{2,3}[-\s]*\d{3})',
        r'DRAFT\s+([A-Z]{2,3}[-]*\d+)',
        r'^([A-Z]{2,3}[-\s]*\d{3})\s+Course Title:'
    ]
    
    for page_num in range(len(doc)):
        page = doc[page_num]
        text = page.get_text()
        
        # Look for subject code patterns
        for pattern in subject_patterns:
            matches = re.finditer(pattern, text, re.MULTILINE | re.IGNORECASE)
            for match in matches:
                if len(match.groups()) >= 1:
                    subject_code = match.group(1) if match.group(1) else match.group(2)
                    
                    # Try to extract course title from the same page
                    title_match = re.search(r'Course Title:\s*(.+?)(?:\n|$)', text, re.IGNORECASE)
                    title = title_match.group(1).strip() if title_match else "Unknown Title"
                    
                    detected_syllabi.append({
                        'code': subject_code.strip(),
                        'title': title,
                        'page': page_num + 1,
                        'detected': True
                    })
    
    return detected_syllabi

def merge_syllabus_lists(predefined: List[Dict], detected: List[Dict]) -> List[Dict]:
    """
    Merge predefined and detected syllabi, preferring detected boundaries where available.
    """
    merged = {}
    
    # Add predefined syllabi
    for syllabus in predefined:
        merged[syllabus['code']] = syllabus
    
    # Update with detected syllabi
    for syllabus in detected:
        code = syllabus['code']
        if code in merged:
            # Update page if detected page seems more accurate
            merged[code]['page'] = syllabus['page']
            merged[code]['detected'] = True
        else:
            merged[code] = syllabus
    
    # Convert back to list and sort by page number
    result = list(merged.values())
    result.sort(key=lambda x: x['page'])
    
    return result

def find_syllabus_end(doc: fitz.Document, start_page: int, next_start_page: int = None) -> int:
    """
    Intelligently find the end of a syllabus by looking for content patterns.
    """
    max_page = next_start_page - 1 if next_start_page else len(doc) - 1
    
    # Look for natural ending patterns
    end_indicators = [
        r'11\.\s*Suggested Books',
        r'Suggested Books\s*:',
        r'References\s*:',
        r'Bibliography\s*:',
        r'^\s*\d+\.\s*Subject Code:',
        r'DRAFT\s+[A-Z]{2,3}[-]*\d+'
    ]
    
    for page_num in range(start_page, min(start_page + 10, max_page + 1)):
        if page_num >= len(doc):
            break
            
        page = doc[page_num]
        text = page.get_text()
        
        # Check if this page contains the start of next syllabus
        if page_num > start_page:
            for pattern in end_indicators[3:]:  # Only check for next syllabus patterns
                if re.search(pattern, text, re.MULTILINE | re.IGNORECASE):
                    return page_num - 1
        
        # Check for natural ending patterns
        for pattern in end_indicators[:3]:
            if re.search(pattern, text, re.MULTILINE | re.IGNORECASE):
                # Look ahead a bit more to include references/books
                end_page = min(page_num + 2, max_page)
                return end_page
    
    return max_page

def validate_syllabus_content(doc: fitz.Document, start_page: int, end_page: int, subject_code: str) -> bool:
    """
    Validate that the extracted content actually contains a syllabus.
    """
    total_text = ""
    for page_num in range(start_page, end_page + 1):
        if page_num < len(doc):
            total_text += doc[page_num].get_text()
    
    # Check for key syllabus elements
    syllabus_indicators = [
        r'Contact Hours',
        r'Credits',
        r'Semester',
        r'Objective',
        r'Course Title',
        r'Subject Code',
        r'Details of Course',
        r'Suggested Books'
    ]
    
    found_indicators = 0
    for indicator in syllabus_indicators:
        if re.search(indicator, total_text, re.IGNORECASE):
            found_indicators += 1
    
    # Require at least 3 indicators for a valid syllabus
    return found_indicators >= 3

def extract_syllabi_improved(doc: fitz.Document, syllabi_list: List[Dict], output_folder: str, 
                           detect_boundaries: bool = True, validate_content: bool = True):
    """
    Enhanced syllabus extraction with better boundary detection and validation.
    """
    print("--- Enhanced Syllabus Extraction ---")
    os.makedirs(output_folder, exist_ok=True)
    
    # Optionally detect boundaries automatically
    if detect_boundaries:
        print("Detecting syllabus boundaries...")
        detected_syllabi = detect_syllabus_boundaries(doc)
        syllabi_list = merge_syllabus_lists(syllabi_list, detected_syllabi)
        print(f"Found {len(detected_syllabi)} additional/updated syllabi")
    
    extraction_log = []
    successful_extractions = 0
    
    for i, syllabus in enumerate(syllabi_list):
        start_page = syllabus['page'] - 1  # Convert to 0-based
        
        # Determine end page more intelligently
        if i + 1 < len(syllabi_list):
            next_start = syllabi_list[i + 1]['page'] - 1
            end_page = find_syllabus_end(doc, start_page, next_start)
        else:
            end_page = find_syllabus_end(doc, start_page)
        
        # Ensure we have at least the start page
        end_page = max(start_page, end_page)
        
        # Validate content if requested
        if validate_content:
            if not validate_syllabus_content(doc, start_page, end_page, syllabus['code']):
                print(f"⚠️  Warning: '{syllabus['code']}' may not contain valid syllabus content")
                # Try extending the range slightly
                end_page = min(end_page + 1, len(doc) - 1)
        
        # Sanitize filename
        clean_code = re.sub(r'[^\w\-_]', '_', syllabus['code'])
        clean_title = re.sub(r'[^\w\s\-_]', '', syllabus['title']).strip()
        out_fname = f"{clean_code}_{clean_title[:30]}.pdf"  # Limit title length
        out_path = os.path.join(output_folder, out_fname)
        
        print(f"Processing '{syllabus['code']}: {syllabus['title']}'...")
        print(f"  > Extracting pages {start_page + 1}-{end_page + 1} → '{out_fname}'")
        
        try:
            # Extract pages
            subdoc = fitz.open()
            subdoc.insert_pdf(doc, from_page=start_page, to_page=end_page)
            
            if len(subdoc) == 0:
                print(f"  → ERROR: No pages extracted for {syllabus['code']}")
                extraction_log.append({
                    'code': syllabus['code'],
                    'status': 'failed',
                    'reason': 'No pages extracted'
                })
                continue
            
            # Save with optimization
            subdoc.save(out_path, garbage=4, deflate=True, clean=True)
            subdoc.close()
            
            # Verify the saved file
            if os.path.exists(out_path) and os.path.getsize(out_path) > 1000:  # At least 1KB
                print(f"  → ✅ Successfully extracted ({os.path.getsize(out_path)} bytes)")
                successful_extractions += 1
                extraction_log.append({
                    'code': syllabus['code'],
                    'status': 'success',
                    'pages': f"{start_page + 1}-{end_page + 1}",
                    'file': out_fname,
                    'size': os.path.getsize(out_path)
                })
            else:
                print(f"  → ❌ File created but seems corrupted")
                extraction_log.append({
                    'code': syllabus['code'],
                    'status': 'failed',
                    'reason': 'Corrupted file'
                })
                
        except Exception as e:
            print(f"  → ERROR: {e}")
            extraction_log.append({
                'code': syllabus['code'],
                'status': 'failed',
                'reason': str(e)
            })
    
    # Save extraction log
    log_path = os.path.join(output_folder, 'extraction_log.json')
    with open(log_path, 'w') as f:
        json.dump(extraction_log, f, indent=2)
    
    print(f"\n✅ Extraction complete: {successful_extractions}/{len(syllabi_list)} successful")
    print(f"📋 Detailed log saved to: {log_path}")
    
    # Print summary of failed extractions
    failed = [log for log in extraction_log if log['status'] == 'failed']
    if failed:
        print(f"\n❌ Failed extractions ({len(failed)}):")
        for fail in failed:
            print(f"   - {fail['code']}: {fail.get('reason', 'Unknown error')}")

def analyze_pdf_structure(pdf_path: str, output_file: str = None):
    """
    Analyze PDF structure to help identify syllabus boundaries.
    """
    doc = fitz.open(pdf_path)
    analysis = []
    
    subject_pattern = r'Subject Code:\s*([A-Z]{2,3}[-\s]*\d{3})'
    title_pattern = r'Course Title:\s*(.+?)(?:\n|$)'
    
    for page_num in range(len(doc)):
        page = doc[page_num]
        text = page.get_text()
        
        # Look for subject codes
        subject_matches = re.findall(subject_pattern, text, re.IGNORECASE)
        title_matches = re.findall(title_pattern, text, re.IGNORECASE)
        
        if subject_matches or title_matches:
            analysis.append({
                'page': page_num + 1,
                'subject_codes': subject_matches,
                'titles': [title.strip() for title in title_matches],
                'text_preview': text[:200] + '...' if len(text) > 200 else text
            })
    
    doc.close()
    
    if output_file:
        with open(output_file, 'w') as f:
            json.dump(analysis, f, indent=2)
        print(f"PDF structure analysis saved to: {output_file}")
    
    return analysis

def main():
    parser = argparse.ArgumentParser(
        description="Enhanced syllabus extraction with automatic boundary detection",
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument('pdf_path', help='Path to the input EP.pdf file')
    parser.add_argument('output_folder', help='Folder to save extracted PDF files')
    parser.add_argument('--no-detect', action='store_true', 
                       help='Disable automatic boundary detection')
    parser.add_argument('--no-validate', action='store_true',
                       help='Disable content validation')
    parser.add_argument('--analyze', action='store_true',
                       help='Analyze PDF structure and save to JSON')
    
    args = parser.parse_args()
    
    if not os.path.exists(args.pdf_path):
        print(f"Error: PDF file not found at '{args.pdf_path}'")
        return
    
    doc = fitz.open(args.pdf_path)
    
    if args.analyze:
        analysis_file = os.path.join(args.output_folder, 'pdf_structure_analysis.json')
        os.makedirs(args.output_folder, exist_ok=True)
        analyze_pdf_structure(args.pdf_path, analysis_file)
    
    # Extract syllabi with enhanced features
    extract_syllabi_improved(
        doc, 
        EP_SUBJECTS, 
        args.output_folder,
        detect_boundaries=not args.no_detect,
        validate_content=not args.no_validate
    )
    
    doc.close()

if __name__ == '__main__':
    main()