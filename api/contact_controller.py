import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr
import os
from dotenv import load_dotenv

load_dotenv()

router = APIRouter(prefix="/contact", tags=["contact"])

class ContactRequest(BaseModel):
    firstName: str
    lastName: str
    email: EmailStr
    message: str

@router.post("")
async def send_contact_email(request: ContactRequest):
    smtp_host = os.getenv("SMTP_HOST")
    smtp_port = int(os.getenv("SMTP_PORT", 465))
    smtp_user = os.getenv("SMTP_USER")
    smtp_password = os.getenv("SMTP_PASSWORD")
    contact_email = os.getenv("CONTACT_EMAIL")

    if not all([smtp_host, smtp_port, smtp_user, smtp_password, contact_email]):
        raise HTTPException(status_code=500, detail="SMTP configuration missing")

    try:
        # Create message
        msg = MIMEMultipart()
        msg['From'] = smtp_user
        msg['To'] = contact_email
        msg['Subject'] = f"New Contact Form Submission from {request.firstName} {request.lastName}"

        body = f"""
        New message received from EmotiCare Contact Form:
        
        Name: {request.firstName} {request.lastName}
        Email: {request.email}
        
        Message:
        {request.message}
        """
        msg.attach(MIMEText(body, 'plain'))

        # Send email using SMTP_SSL for port 465
        with smtplib.SMTP_SSL(smtp_host, smtp_port) as server:
            server.login(smtp_user, smtp_password)
            server.send_message(msg)

        return {"message": "Email sent successfully", "statusCode": 200}
    except Exception as e:
        print(f"Error sending email: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to send email: {str(e)}")
