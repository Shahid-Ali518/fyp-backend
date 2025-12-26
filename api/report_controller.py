from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from io import BytesIO

from core.database import get_db
from service.report_service import ReportService

router = APIRouter()

@router.get("/reports/{attempt_id}/pdf", tags=["Reports"])
def download_report(attempt_id: int, db: Session = Depends(get_db)):

    try:
        pdf_bytes = ReportService.generate_report_pdf(attempt_id, db)
        return StreamingResponse(
            BytesIO(pdf_bytes),
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename=assessment_report_{attempt_id}.pdf"
            }
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error generating report")
