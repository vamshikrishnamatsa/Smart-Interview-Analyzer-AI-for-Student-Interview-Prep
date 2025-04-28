from fpdf import FPDF
import os

class PDF(FPDF):
    def header(self):
        self.set_font("Arial", "B", 14)
        self.cell(0, 10, "AI Interview Report", ln=True, align="C")
        self.ln(10)

    def chapter_title(self, title):
        self.set_font("Arial", "B", 12)
        self.set_text_color(30, 30, 120)
        self.cell(0, 10, title, ln=True)
        self.ln(2)

    def chapter_body(self, body):
        self.set_font("Arial", "", 11)
        self.set_text_color(0)
        self.multi_cell(0, 8, body)
        self.ln()

def generate_pdf(history, final_feedback):
    pdf = PDF()
    pdf.add_page()

    # Final Feedback
    pdf.chapter_title("Final Interview Summary")
    pdf.chapter_body(final_feedback)

    # Question-wise Feedback
    pdf.chapter_title("Question-wise Feedback")
    for i, q in enumerate(history, 1):
        pdf.chapter_body(f"Q{i}: {q['question']}")
        pdf.chapter_body(f"Your Answer: {q['answer']}")
        pdf.chapter_body(f"Feedback: {q.get('feedback', 'N/A')}")
        pdf.ln(3)

    # Save the PDF
    output_path = os.path.join("generated", "interview_report.pdf")
    os.makedirs("generated", exist_ok=True)
    pdf.output(output_path)
    return output_path
