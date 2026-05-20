import io
import asyncio
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends

from core.dependencies import get_interviewer_service
from utils.transcibe_audio import transcribe_audio
from utils.constants import INTERVIEW_QUESTIONS

router = APIRouter()


def safe_serialize(question):
    """Helper to prevent UUID JSON errors"""
    if not question: return None
    return {
        "id": str(question["id"]),
        "text": question["text"],
        "options": [{"id": str(o["id"]), "text": o["option_text"]} for o in question.get("options", [])]
    }


@router.websocket("/ws/interview")
async def interview_streaming(websocket: WebSocket, manager_service=Depends(get_interviewer_service)):
    await websocket.accept()
    current_idx = 0

    try:
        # Send initial greeting
        await websocket.send_json({
            "type": "TURN_COMPLETE",
            "data": {
                "feedback_text": "Hello, I am your clinical assistant.",
                "next_question": safe_serialize(INTERVIEW_QUESTIONS[current_idx])
            }
        })

        while True:
            # Receive raw audio bytes
            audio_bytes = await websocket.receive_bytes()

            # 1. Transcribe (Faster-Whisper GPU/CPU)
            user_text = await transcribe_audio(audio_bytes)
            if not user_text.strip(): continue

            # 2. Logic Turn
            turn_result = await manager_service.handle_turn(
                user_answer=user_text,
                current_q_id=INTERVIEW_QUESTIONS[current_idx]["id"],
                all_questions=INTERVIEW_QUESTIONS
            )

            # 3. Response
            await websocket.send_json({
                "type": "TURN_COMPLETE",
                "data": {
                    "feedback_text": turn_result.get("feedback_text"),
                    "next_question": safe_serialize(turn_result.get("next_question"))
                }
            })

            if not turn_result.get("next_question"): break
            current_idx += 1

    except WebSocketDisconnect:
        pass
    except Exception as e:
        print(f"Error: {e}")