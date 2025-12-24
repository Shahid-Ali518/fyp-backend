import os
import tempfile
from fastapi import UploadFile

ALLOWED_EXT = {".wav", ".mp3", ".ogg", ".m4a", ".webm"}

def save_upload_tmp(upload_file: UploadFile) -> str:
    ext = os.path.splitext(upload_file.filename)[1].lower()
    if not ext:
        ext = ".webm"  # MediaRecorder default
    if ext not in ALLOWED_EXT:
        raise ValueError(f"Unsupported audio format: {ext}")

    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=ext)
    temp_path = tmp.name

    with tmp:
        while True:
            chunk = upload_file.file.read(1024 * 1024)
            if not chunk:
                break
            tmp.write(chunk)

    return temp_path



def remove_file_silent(path: str):
    try:
        if path and os.path.exists(path):
            os.remove(path)
    except:
        pass
