
from core.database import  get_db
from service.emotion_prediction_by_wavlm_service import EmotionPredictionByWavLmService
from schemas.api_response import ApiResponse
import os
import uuid
from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException
from sqlalchemy.orm import Session
from starlette.concurrency import run_in_threadpool

router = APIRouter(prefix="/api/emotions")

# route to detect emotion of a question
@router.post("/predict-emotion", response_model=ApiResponse)
async def predict_question(
        attempt_id: uuid.UUID = Form(...),
        question_id: uuid.UUID = Form(...),
        file: UploadFile = File(...),
        db: Session = Depends(get_db)
):

    print(attempt_id)
    print(question_id)
    print(file)
    # 1. Sanitize filename to prevent path traversal attacks
    ext = os.path.splitext(file.filename)[1]
    unique_filename = f"{attempt_id}_{question_id}_{uuid.uuid4()}{ext}"
    temp_dir = "temp_audio"
    os.makedirs(temp_dir, exist_ok=True)
    file_path = os.path.join(temp_dir, unique_filename)

    try:
        # 2. Async write to disk
        content = await file.read()
        with open(file_path, "wb") as buffer:
            buffer.write(content)

        # 3. Offload CPU-bound ML task to a separate thread
        # This prevents the API from freezing for other users
        service = EmotionPredictionByWavLmService(db)

        result = await run_in_threadpool(
            service.predict_question_emotion,
            attempt_id=attempt_id,
            question_id=question_id,
            audio_path=file_path
        )

        return result

    except Exception as e:
        print(f"Error occurred: {str(e)}")  # This will show in your terminal
        import traceback
        traceback.print_exc()  # This shows exactly which line failed
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        # 4. Ensure cleanup and close the upload stream
        await file.close()
        if os.path.exists(file_path):
            os.remove(file_path)