from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException
# from concurrent.futures import ThreadPoolExecutor
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
from models.question import Question
from utils.api_response import ApiResponse 
from utils.stt_converter import map_score_to_severity

router = APIRouter(prefix="/api/transcribe", tags=["transcribe"])

# ThreadPoolExecutor for CPU-bound tasks (AI processing)
# executor = ThreadPoolExecutor(max_workers=4)


# def run_in_thread(func, *args):
#     """
#     Run CPU-bound functions in a thread pool (sync-safe).
#     """
#     loop = asyncio.new_event_loop()
#     asyncio.set_event_loop(loop)
#     return loop.run_in_executor(executor, lambda: func(*args))


@router.post("/")
def handle_transcription(
    file: UploadFile = File(...),
    questionId: int = Form(...),
    db: Session = Depends(get_db)
):
    print("Received transcription request with file:", file.filename, "for question ID:", questionId) 
    src_path = None
    wav_path = None

    try:
        # 1. Save uploaded file (SYNC)
        src_path = save_upload_tmp(file)
        wav_path = src_path + ".wav"
        file.file.seek(0)
        audio_bytes = file.file.read()
        # 2. Convert to WAV
        convert_to_wav(src_path, wav_path)
        print("Uploaded file:", file.filename, file.content_type)


        # 3. Transcribe using Whisper
        transcript =transcribe_file( wav_path)

        if not transcript.strip():
            raise HTTPException(status_code=400, detail="Unable to transcribe audio.")

        # 4. Load question from DB
        question = db.query(Question).get(questionId)

        if not question:
            raise HTTPException(status_code=404, detail="Question not found")

        if not question.category:
            raise HTTPException(status_code=400, detail="Question category missing")


        category_name = question.category.name  # depression / anxiety
        # survey_options = question.category.options
        print("Question category:", category_name)
        # options_data = [
        #     {
        #         "option_text": option.option_text,
        #         "weightage": option.weightage
        #     }
        #     for option in survey_options
        # ]

        text_result = analyze_text(transcript, category_name)
        print("TEXT RESULT:", text_result, type(text_result))

        voice_result = analyze_voice_emotion(wav_path, category_name)
        print("VOICE RESULT:", voice_result, type(voice_result))

        final_weightage = round(
            (text_result["weightage"] * 0.6) +
            (voice_result["weightage"] * 0.4),
            2
        )
        final_severity = map_score_to_severity(final_weightage)


        #  # # 5. Fetch severity weightage from SurveyOption
        # option_weight_map = {
        #     opt["option_text"].lower(): opt["weightage"]
        #     for opt in options_data
        # }

        # severity_weightage = option_weight_map.get(
        #     final_severity,
        #     min(option_weight_map.values())
        # )


        # selected_option = min(
        #     survey_options,
        #     key=lambda opt: abs(opt.weightage - final_weightage)
        # )
        # recognized_emotion = text_result["emotion_breakdown"]
        # confidence = text_result["model_confidence"]

        # 7. Build response
        result = {
            "transcript": transcript,

            "text_emotion": text_result["emotion_breakdown"],
            # "text_confidence": text_result["model_confidence"],
            
            "voice_emotion": voice_result["emotion_breakdown"],
            # "voice_confidence": voice_result["voice_emotion_confidence"],

            # "selected_option_id": selected_option.id,
            "final_weightage": final_severity
        }


        # 8. Save result to DB (SYNC)
       
        question_result = QuestionResult(
            question_id=question.id,
            # selected_option_id=selected_option.id,
            user_answer_audio=audio_bytes,
            user_answer_text=transcript,
            # recognized_emotion=recognized_emotion,
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
