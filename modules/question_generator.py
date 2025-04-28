import os
from dotenv import load_dotenv
from modules import gemini_api  # Uses Gemini 1.5 Flash
from modules.resume_parser import extract_resume_keywords

load_dotenv()

def generate_question(
    history,
    domain,
    level,
    resume_text=None,
    resume_keywords=None,
    jd_text=None,
    performance_feedback=None
):
    if not history:
        # First question
        prompt = f"You are an interviewer for a {domain} role at the {level} level.\n"

        if resume_keywords:
            prompt += f"The candidate's resume includes these skills: {', '.join(resume_keywords)}.\n"
        elif resume_text:
            # Fallback: extract keywords from resume_text
            keywords = extract_resume_keywords(resume_text)
            prompt += f"The candidate's resume includes these skills: {', '.join(keywords)}.\n"

        if jd_text:
            prompt += f"The job description mentions: {jd_text.strip()}\n"

        prompt += "Based on the resume and job description, ask a relevant technical or behavioral question to begin the interview."

        response = gemini_api.get_response(prompt)
        return response.strip()

    else:
        # Follow-up question
        last_question = history[-1]['question']
        last_answer = history[-1]['answer']

        prompt = f"""
        You are conducting an AI interview for a {domain} position at the {level} level.
        The last question was: "{last_question}"
        The candidate answered: "{last_answer}"
        """

        if jd_text:
            prompt += f"\nThe job description includes: {jd_text.strip()}"

        if performance_feedback:
            prompt += f"\nYour analysis of the response: {performance_feedback}"
            prompt += "\nAsk a follow-up question that addresses weaknesses or dives deeper based on the job description."
        else:
            prompt += "\nAsk a follow-up question based on the previous response and job description if provided."

        response = gemini_api.get_response(prompt)
        return response.strip()
