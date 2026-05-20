from fastapi import Depends
from openai import AsyncOpenAI
from sqlalchemy.orm import Session


from core.database import get_db
from llm.llm_interviewer import LLMInterviewer
from service.llm_survey_interview_service import InterviewManagerService


# 1. This creates the LLM Client
def get_llm_interviewer():
    client = AsyncOpenAI(base_url="http://localhost:11434", api_key="ollama")
    return LLMInterviewer(client=client)

# 2. This creates the Manager and INJECTS the actual Interviewer instance
def get_interviewer_service(
    db: Session = Depends(get_db),
    interviewer: LLMInterviewer = Depends(get_llm_interviewer)
):
    # interviewer here is the REAL object, not a 'Depends' object
    return InterviewManagerService(interviewer_service=interviewer, db_session=db)