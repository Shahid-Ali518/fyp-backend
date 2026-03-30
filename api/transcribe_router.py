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
from models.test_category import TestCategory
from schemas.api_response import ApiResponse
from utils.stt_converter import map_final_score
import traceback
from service.llm_service import llm_service
from utils.tts_converter import text_to_audio_bytes

MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB limit for audio files

router = APIRouter(prefix="/api/transcribe", tags=["transcribe"])

@router.post("/start")
async def start_assessment(
    categoryId: int = Form(...),
    db: Session = Depends(get_db)
):
    category = db.get(TestCategory, categoryId)
    
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")

    first_question = await llm_service.get_next_question(category.name, [], [])
    audio_bytes = text_to_audio_bytes(first_question)
    
    return ApiResponse(
        message="Assessment started",
        status_code=200,
        data={
            "question": first_question,
            "audio": audio_bytes.hex() if audio_bytes else None # Hex for easy transfer
        }
    )

@router.post("/")
async def handle_transcription(
    file: UploadFile = File(...),
    categoryId: int = Form(...),
    previousQuestions: str = Form("[]"), # JSON string list
    previousAnswers: str = Form("[]"), # JSON string list
    db: Session = Depends(get_db)
):
    import json
    src_path = None
    wav_path = None
    loop = asyncio.get_running_loop()

    try:
        prev_q = json.loads(previousQuestions)
        prev_a = json.loads(previousAnswers)

        # 0️⃣ Validate file size
        file.file.seek(0, 2)
        file_size = file.file.tell()
        file.file.seek(0)
        
        if file_size > MAX_FILE_SIZE:
            raise HTTPException(status_code=400, detail=f"File exceeds maximum allowed size of {MAX_FILE_SIZE / (1024*1024)} MB.")

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

        # 4️⃣ Fetch Category
        category = db.get(TestCategory, categoryId)

        if not category:
            raise HTTPException(status_code=404, detail="Category not found")

        category_name = category.name

        # 5️⃣ Analyze text & voice concurrently
        print(f"DEBUG: Starting emotion analysis for {category_name}")
        text_future = loop.run_in_executor(
            None, analyze_text, transcript, category_name
        )

        voice_future = loop.run_in_executor(
            None, analyze_voice_emotion, wav_path, category_name
        )

        text_result, voice_result = await asyncio.gather(
            text_future, voice_future
        )
        print(f"DEBUG: Text Score: {text_result['weightage']}, Voice Score: {voice_result['weightage']}")

        # 6️⃣ Weighted scoring
        score = round(
            (text_result["weightage"] * 0.6) +
            (voice_result["weightage"] * 0.4),
            2
        )
        print("score",score)
        final_score = map_final_score(score)
        print("final_score",final_score)
        # 7️⃣ Get Next LLM Question
        prev_a.append(transcript)
        
        print(f"--- Assessment Progress: {len(prev_a)}/5 questions answered ---")

        next_question = None
        next_audio = None
        if len(prev_a) < 5:
            next_question = await llm_service.get_next_question(category_name, prev_q, prev_a)
            next_audio = text_to_audio_bytes(next_question)

        # 8️⃣ Response
        result = {
            "transcript": transcript,
            "text_emotion": text_result["emotion_breakdown"],
            "voice_emotion": voice_result["emotion_breakdown"],
            "score": final_score,
            "next_question": next_question,
            "next_audio": next_audio.hex() if next_audio else None
        }    

        return ApiResponse(
            message="Analysis successful",
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
