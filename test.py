import os
import re
from pypdf import PdfReader

def extract_info_from_pdf(file_path):
    try:
        reader = PdfReader(file_path)
        text = ''
        for page in reader.pages:
            text += page.extract_text()

        # Regex to find the student number
        student_number_match = re.search(r'Student Number:  (\d+)', text)
        if student_number_match:
            student_number = student_number_match.group(1)
        else:
            student_number = "Not found"

        # Regex to find the extended time for exams
        extended_time_match = re.search(r'Extended time \((\d+\.?\d*)x\) for all exams', text)
        if extended_time_match:
            extended_time = extended_time_match.group(1)
        else:
            extended_time = "Not found"

        return {
            'Student Number': student_number,
            'Extended Time': extended_time
        }
    except Exception as e:
        print(f"Error processing file {file_path}: {e}")
        return None

def process_pdf_files(folder_path):

    for file_name in os.listdir(folder_path):
        if file_name.endswith('.pdf'):
            file_path = os.path.join(folder_path, file_name)
            info = extract_info_from_pdf(file_path)
            if info:
                print(f"File: {file_name}")
                print(f"Student Number: {info['Student Number']}, Extended Time: {info['Extended Time']}\n")

# Example usage
folder_path = 'extensions'
process_pdf_files(folder_path)
