from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException
from concurrent.futures import ThreadPoolExecutor
import asyncio

from utils.file import save_upload_tmp, remove_file_silent
from service.ai_service import (
    convert_to_wav,
    transcribe_file,
    analyze_text,
    analyze_voice_emotion
)
from core.database import get_db
from api.question_controller import get_question
from sqlalchemy.orm import Session
from models.question_result import QuestionResult
from utils.api_response import ApiResponse 
from utils.stt_converter import map_score_to_severity

router = APIRouter(prefix="/api/transcribe", tags=["transcribe"])

# ThreadPoolExecutor for CPU-bound tasks (AI processing)
executor = ThreadPoolExecutor(max_workers=4)


def run_in_thread(func, *args):
    """
    Run CPU-bound functions in a thread pool (sync-safe).
    """
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    return loop.run_in_executor(executor, lambda: func(*args))


@router.post("/")
def handle_transcription(
    file: UploadFile = File(...),
    questionId: int = Form(...),
    db: Session = Depends(get_db)
):
    src_path = None
    wav_path = None

    try:
        # 1. Save uploaded file (SYNC)
        src_path = save_upload_tmp(file)
        wav_path = src_path + ".wav"
        file.file.seek(0)
        audio_bytes = file.file.read()
        # 2. Convert to WAV
        asyncio.run(run_in_thread(convert_to_wav, src_path, wav_path))

        # 3. Transcribe using Whisper
        transcript = asyncio.run(run_in_thread(transcribe_file, wav_path))

        if not transcript.strip():
            raise HTTPException(status_code=400, detail="Unable to transcribe audio.")

        # 4. Load question from DB
        question = get_question(db, questionId)

        category_name = question.category.name  # depression / anxiety
        survey_options = question.category.options

        options_data = [
            {
                "option_text": option.option_text,
                "weightage": option.weightage
            }
            for option in survey_options
        ]

        text_result = asyncio.run(
            run_in_thread(
                analyze_text,
                transcript,
                category_name,
                options_data
            )
        )


        # 6. Voice emotion analysis
        voice_result = asyncio.run(
            run_in_thread(
                analyze_voice_emotion,
                wav_path,
                category_name,
                options_data
            )
        )


        final_weightage = round(
            (text_result["weightage"] * 0.4) +
            (voice_result["weightage"] * 0.6),
            2
        )
        final_severity = map_score_to_severity(final_weightage)
        selected_option = min(
            survey_options,
            key=lambda opt: abs(opt.weightage - final_weightage)
        )
        recognized_emotion = voice_result["voice_emotion"]
        # confidence = voice_result["voice_confidence"]

        # 7. Build response
        result = {
            "transcript": transcript,

            "text_emotion": text_result["emotion"],
            # "text_confidence": text_result["emotion_confidence"],
            
            "voice_emotion": voice_result["voice_emotion"],
            # "voice_confidence": voice_result["voice_emotion_confidence"],

            "selected_option_id": selected_option.id,
            "final_weightage": final_weightage
        }


        # 8. Save result to DB (SYNC)
       
        question_result = QuestionResult(
            question_id=question.id,
            selected_option_id=selected_option.id,
            user_answer_audio=audio_bytes,
            user_answer_text=transcript,
            recognized_emotion=recognized_emotion,
            # confidence=confidence
        )

        db.add(question_result)
        db.commit()
        db.refresh(question_result)




        return ApiResponse(
            message="Transcription and emotion analysis completed successfully",
            status_code=200,
            data=result
        )

    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Processing failed: {str(e)}")

    finally:
        # Cleanup temporary files
        remove_file_silent(src_path)
        remove_file_silent(wav_path)
