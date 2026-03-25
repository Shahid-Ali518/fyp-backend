
from fpdf import FPDF
from models import TestAttempt, QuestionResult, User, TestCategory
from sqlalchemy.orm import Session

class ReportService:

    @staticmethod
    def generate_report_pdf(attempt_id: int, db: Session) -> bytes:
        # Fetch attempt with relations
        attempt = db.query(TestAttempt).filter(TestAttempt.id == attempt_id).first()
        if not attempt:
            raise ValueError("Test attempt not found")

        user = attempt.user
        category = attempt.category
        question_results = attempt.question_results or []

        pdf = FPDF()
        pdf.add_page()
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.set_font("Arial", 'B', 16)
        pdf.cell(0, 10, "Assessment Report", ln=True, align="C")
        pdf.ln(10)

        # User Info
        pdf.set_font("Arial", '', 12)
        pdf.cell(0, 8, f"Name: {user.name}", ln=True)
        pdf.cell(0, 8, f"Name: {user.phone_number}", ln=True)
        pdf.cell(0, 8, f"Email: {user.email}", ln=True)
        pdf.cell(0, 8, f"Category: {category.name}", ln=True)
        pdf.cell(0, 8, f"Mental Health Score: {attempt.mental_health_score}", ln=True)
        pdf.cell(0, 8, f"Mental Health State: {attempt.mental_health_state}", ln=True)
        pdf.ln(10)

        # Question Results
        if question_results:
            pdf.set_font("Arial", 'B', 14)
            pdf.cell(0, 8, "Question Results:", ln=True)
            pdf.set_font("Arial", '', 12)
            for idx, qr in enumerate(question_results, start=1):
                pdf.cell(0, 6, f"{idx}. Question ID: {qr.question_id}", ln=True)
                pdf.cell(0, 6, f"   Selected Option: {qr.selected_option.option_text}", ln=True)
                pdf.cell(0, 6, f"   Score: {qr.selected_option.weightage}", ln=True)
                if hasattr(qr, "emotions") and qr.emotions:
                    emotions_str = ", ".join([f"{k}: {v:.1f}%" for k, v in qr.emotions.items()])
                    pdf.cell(0, 6, f"   Emotions: {emotions_str}", ln=True)
                pdf.ln(2)

        # Recommendations (example)
        pdf.set_font("Arial", 'B', 14)
        pdf.cell(0, 8, "Recommendations:", ln=True)
        pdf.set_font("Arial", '', 12)
        # Placeholder example, replace with actual logic
        recommendations = [
            "Practice more on weak areas",
            "Review topics with low confidence",
            "Focus on time management"
        ]
        for idx, rec in enumerate(recommendations, start=1):
            pdf.cell(0, 6, f"{idx}. {rec}", ln=True)

        return pdf.output(dest='S').encode('latin1')  # return as bytes
