import uuid
from typing import List, Dict, Any

from llm.llm_interviewer import LLMInterviewer
from schemas.question_schema import QuestionDTO


class InterviewManagerService:
    def __init__(self, interviewer_service: LLMInterviewer, db_session):
        self.interviewer_service = interviewer_service
        self.db = db_session

    async def handle_turn(
            self,
            user_answer: str,
            current_q_id: uuid.UUID,
            all_questions: List[Dict[str, Any]]
    ) -> Dict[str, Any]:

        # 1. Find the current question from the constants list
        current_question = next(q for q in all_questions if q["id"] == current_q_id)

        # 2. Get AI Evaluation (Mapping + Feedback)
        # Assuming ai_service returns {"selected_id": "...", "feedback": "..."}
        evaluation = await self.interviewer_service.evaluate_answer(
            user_answer,
            current_question["options"]
        )

        # 3. Logic to find the next question
        next_q = None
        for i, q in enumerate(all_questions):
            if q["id"] == current_q_id and i + 1 < len(all_questions):
                next_q = all_questions[i + 1]
                break

        # 4. Return as a plain Dictionary
        return {
            "selected_option_id": evaluation.get('selected_id'),
            "feedback_text": evaluation.get('feedback'),
            "next_question": next_q
        }