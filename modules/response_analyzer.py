from modules import question_generator  # ✅ if you're running app.py from the root folder
import google.generativeai as genai

# Replace with your actual Gemini API key
genai.configure(api_key="AIzaSyCjxdgf-ioqlY04pJSkoZFSz66DHuGD6KU")

# Load the Gemini 1.5 Flash model
model = genai.GenerativeModel('models/gemini-1.5-flash')


def analyze_response(question, answer, jd_text=None):
    prompt = f"""
Evaluate the following interview answer:

Q: {question}
A: {answer}
"""

    if jd_text:
        prompt += f"\nJob Description: {jd_text.strip()}"

    prompt += """
Give:
- Accuracy (1-10)
- Clarity (1-10)
- Confidence (1-10)
- A 2-line feedback
"""

    response = model.generate_content(prompt)
    return response.text.strip()
