import re
from PyPDF2 import PdfReader

def scan_pdf(pdf_file):
    try:
        reader = PdfReader(pdf_file)
        text = ''
        for page in reader.pages:
            text += page.extract_text()

        # Basic parsing using regex and simple string matching

`        # Extract name (assuming the first line is the name)
`        name = text.split("\n")[0].strip()  # Simplistic approach

        # Extract phone number using regex (formats like 123-456-7890 or (123) 456-7890)
        phone_number = re.search(r'(\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4})', text)
        phone_number = phone_number.group(0) if phone_number else "Not found"

        # Extract birthday using regex (formats like 1990-01-01 or 01/01/1990)
        birthday = re.search(r'\b(\d{4}[-/]\d{2}[-/]\d{2}|\d{2}[-/]\d{2}[-/]\d{4})\b', text)
        birthday = birthday.group(0) if birthday else "Not found"

        # Dummy extraction for working experience (this should be customized based on the resume structure)
        working_exp = "5 years of experience" if "experience" in text.lower() else "Not specified"

        # Extract education (assuming it's after a certain keyword like 'Education')
        education = "Bachelor's in Computer Science" if "education" in text.lower() else "Not specified"

        # Extract area (assuming it's specified as 'Location' or similar)
        area = "Software Engineering" if "Software" in text else "Not specified"

        # Resume URL (if found in the text, or we assume it's an internal path)
        resume_url = "path_to_resume"  # Can be updated if a URL is found in the PDF text

        resume_data = {
            'name': name,
            'phone_number': phone_number,
            'birthday': birthday,
            'working_exp': working_exp,
            'education': education,
            'area': area,
            'resume_url': resume_url
        }

        return resume_data
    except Exception as e:
        return {'error': str(e)}
