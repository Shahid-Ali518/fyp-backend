import uuid

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from io import BytesIO

from core.database import get_db
from service.report_service import ReportService

router = APIRouter(prefix="/api/reports")


@router.get("/{attempt_id}/pdf", tags=["Reports"])
def download_report(attempt_id: uuid.UUID, db: Session = Depends(get_db)):
    try:
        pdf_bytes = ReportService.generate_report_pdf(str(attempt_id), db)

        # Create the buffer
        buffer = BytesIO(pdf_bytes)
        buffer.seek(0)  # <--- CRITICAL: Move cursor to the beginning of the buffer

        return StreamingResponse(
            buffer,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename=assessment_report_{attempt_id}.pdf",
                "Content-Length": str(len(pdf_bytes))  # Optional: helps browser show progress
            }
        )
    except Exception as e:
        print(f"Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))