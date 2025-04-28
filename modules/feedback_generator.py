from modules import gemini_api  # This should contain the Gemini model or get_response()

def generate_summary(history):
    qas = "\n".join([f"Q: {q['question']}\nA: {q['answer']}" for q in history])
    prompt = f"""
This is the complete mock interview:
{qas}

Now give:
- Final score (out of 10)
- Strengths
- Weaknesses
- Improvement Tips
"""
    response = gemini_api.get_response(prompt)
    return response.strip()

def generate_linkedin_summary(final_feedback):
    prompt = f"""
You are a professional career coach. Convert the following mock interview feedback into a LinkedIn post from the first-person point of view.

Feedback:
{final_feedback}

Tone: Professional, confident, and humble.
Audience: LinkedIn.
Length: Short (100-200 words)
"""
    response = gemini_api.get_response(prompt)
    return response.strip()

def generate_improvement_plan(final_feedback):
    prompt = f"""
You are a learning advisor. Based on the following feedback, generate a short improvement plan with 2-3 free online resources (e.g., YouTube, Coursera, edX, blogs) that help with each weakness.

Feedback:
{final_feedback}

Make it practical and beginner-friendly.
"""
    response = gemini_api.get_response(prompt)
    return response.strip()
