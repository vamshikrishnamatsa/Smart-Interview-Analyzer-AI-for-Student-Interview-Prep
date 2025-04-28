import re
from PyPDF2 import PdfReader
from modules import gemini_api  # Make sure this exists and has get_response()

def extract_resume_text(file):
    reader = PdfReader(file)
    text = ""
    for page in reader.pages:
        text += page.extract_text()
    return text

def extract_resume_keywords(text):
    keywords = re.findall(
        r'\b(Python|Java|C\+\+|ML|AI|SQL|TensorFlow|React|Leadership|Management|AWS|Docker|Kubernetes)\b',
        text,
        re.IGNORECASE
    )
    return list(set([kw.capitalize() for kw in keywords]))

def enhance_resume(text):
    prompt = f"""
I am sharing a resume below:

{text}

Please analyze and provide:
1. Resume Weaknesses (e.g., missing metrics, vague achievements, lack of impact-driven statements).
2. Suggestions for improvement (as bullet points).
3. Enhanced sample lines (rewrite 2-3 lines in a better way using strong impact verbs and quantifiable results).

Respond in a professional and friendly tone.
"""
    response = gemini_api.get_response(prompt)
    return response.strip()
