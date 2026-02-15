from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException
import asyncio

from utils.file import save_upload_tmp, remove_file_silent
from service.ai_service import (
    convert_to_wav,
    transcribe_file,
    analyze_text,
    analyze_voice_emotion
)
from core.database import get_db
from sqlalchemy.orm import Session
from models.question_result import QuestionResult
from models.question import Question
from utils.api_response import ApiResponse 
from utils.stt_converter import map_score_to_severity
import traceback


router = APIRouter(prefix="/api/transcribe", tags=["transcribe"])


@router.post("/")
async def handle_transcription(
    file: UploadFile = File(...),
    questionId: int = Form(...),
    db: Session = Depends(get_db)
):
    src_path = None
    wav_path = None
    loop = asyncio.get_running_loop()

    try:
        # 1️⃣ Save uploaded file
        src_path = save_upload_tmp(file)
        wav_path = src_path + ".wav"

        # 2️⃣ Convert to WAV
        convert_to_wav(src_path, wav_path)

        # 3️⃣ Transcribe audio
        transcript = await loop.run_in_executor(
            None, transcribe_file, wav_path
        )

        if not transcript or not transcript.strip():
            raise HTTPException(status_code=400, detail="Unable to transcribe audio.")

        # 4️⃣ Fetch question (SQLAlchemy 2.x style)
        question = db.get(Question, questionId)

        if not question:
            raise HTTPException(status_code=404, detail="Question not found")

        if not question.category:
            raise HTTPException(status_code=400, detail="Question category missing")

        category_name = question.category.name

        # 5️⃣ Analyze text & voice concurrently
        text_future = loop.run_in_executor(
            None, analyze_text, transcript, category_name
        )

        voice_future = loop.run_in_executor(
            None, analyze_voice_emotion, wav_path, category_name
        )

        text_result, voice_result = await asyncio.gather(
            text_future, voice_future
        )

        # 6️⃣ Weighted scoring
        final_score = round(
            (text_result["weightage"] * 0.6) +
            (voice_result["weightage"] * 0.4),
            2
        )

        final_severity = map_score_to_severity(final_score)

        # 7️⃣ Save to DB (store text only or path instead of blob)
        question_result = QuestionResult(
            question_id=question.id,
            user_answer_text=transcript,
            # user_answer_audio_path=wav_path   # Recommended instead of blob
        )

        db.add(question_result)
        db.commit()
        db.refresh(question_result)

        # 8️⃣ Response
        result = {
            "transcript": transcript,
            "text_emotion": text_result["emotion_breakdown"],
            "voice_emotion": voice_result["emotion_breakdown"],
            "final_score": final_score,
            "final_severity": final_severity
        }

        return ApiResponse(
            message="Transcription and emotion analysis completed successfully",
            status_code=200,
            data=result
        )

    except ValueError as ve:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(ve))

    except Exception as e:
        db.rollback()
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        remove_file_silent(src_path)
        remove_file_silent(wav_path)
