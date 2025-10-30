import re
import spacy
from PyPDF2 import PdfReader

# Load spaCy's pre-trained English model
nlp = spacy.load("en_core_web_sm")

def scan_pdf(file_path):
    try:
        # Read the PDF file from the given file path
        with open(file_path, "rb") as f:
            reader = PdfReader(f)
            text = ''
            for page in reader.pages:
                text += page.extract_text()

        # Use spaCy to process the extracted text
        doc = nlp(text)

        # Initialize resume_data dictionary
        resume_data = {
            'name': None,
            'phone_number': None,
            'birthday': None,
            'working_exp': None,
            'education': [],
            'skills': [],
            'area': None,
            'resume_url': file_path
        }

        # Extract named entities using spaCy NER
        for ent in doc.ents:
            if ent.label_ == "PERSON" and not resume_data['name']:
                resume_data['name'] = ent.text
            elif ent.label_ == "DATE" and not resume_data['birthday']:
                resume_data['birthday'] = ent.text
            elif ent.label_ == "GPE" and not resume_data['area']:
                resume_data['area'] = ent.text

        # Extract phone number
        phone_pattern = r'(\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4})'
        phone_match = re.search(phone_pattern, text)
        if phone_match:
            resume_data['phone_number'] = phone_match.group(0)

        # Extract skills
        skills_keywords = ['python', 'java', 'c++', 'javascript', 'sql', 'react', 'angular', 'vue', 'node.js', 'django', 'flask']
        for keyword in skills_keywords:
            if re.search(r'\b' + keyword + r'\b', text, re.IGNORECASE):
                resume_data['skills'].append(keyword)

        # Extract education
        education_section = re.search(r'Education\n([\s\S]*?)(?=\n\n|\Z)', text, re.IGNORECASE)
        if education_section:
            education_text = education_section.group(1)
            # Simple split by newline, can be improved
            resume_data['education'] = [line.strip() for line in education_text.split('\n') if line.strip()]

        # Extract work experience
        experience_section = re.search(r'(Experience|Work History|Professional Experience)\n([\s\S]*?)(?=\n\n|Education|Skills|\Z)', text, re.IGNORECASE)
        if experience_section:
            resume_data['working_exp'] = experience_section.group(2).strip()

        return resume_data

    except Exception as e:
        return {'error': str(e)}
