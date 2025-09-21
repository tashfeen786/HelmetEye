from fastapi import FastAPI, Request, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import SQLModel, create_engine
from pydantic import BaseModel
from DB_Operations.get_data import get_data
import sqlite3
from fastapi.responses import StreamingResponse, JSONResponse
import cv2
from models.model import model
from datetime import datetime
import os
import shutil
from fastapi.staticfiles import StaticFiles
import pytesseract
from PIL import Image
import numpy as np
import uuid
import traceback
import re
from fastapi.staticfiles import StaticFiles

# --- optional EasyOCR (used if installed) ---
try:
    import easyocr
    EASYOCR_AVAILABLE = True
except Exception:
    EASYOCR_AVAILABLE = False

# --- Tesseract executable path ---
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"  # change if needed

# ---------- helper for number-plate OCR ----------
def extract_plate_text(bgr_crop):
    """Try EasyOCR first, fall back to Tesseract, return cleaned text."""
    text = ""
    if EASYOCR_AVAILABLE:
        reader = easyocr.Reader(["en"], gpu=False)
        results = reader.readtext(bgr_crop)
        if results:
            text = " ".join(r[1] for r in results)
    if not text.strip():
        text = pytesseract.image_to_string(Image.fromarray(cv2.cvtColor(bgr_crop, cv2.COLOR_BGR2RGB)))
    text = re.sub(r"[^A-Z0-9]", "", text.upper())
    return text or "UNKNOWN"

# ---------- FastAPI setup ----------
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:9002",
        "http://192.168.1.7:9002"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

DATABASE_URL = "sqlite:///database.db"
engine = create_engine(DATABASE_URL)
SQLModel.metadata.create_all(engine)

class UserCreate(BaseModel):
    name: str
    email: str

@app.get("/")
def read_root():
    return {"message": "Welcome to the FastAPI backend!"}

@app.get("/api/report")
def get_report():
    data = get_data()
    return {"report": data}

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# ---------- main detection endpoint ----------
@app.post("/api/detect_helmet")
async def detect_helmet(file: UploadFile = File(...)):
    try:
        if not file:
            return JSONResponse(status_code=400,
                                content={"message": "No file uploaded. Please upload an image OR video."})

        # save uploaded file and read original image
        file_path = os.path.join(UPLOAD_DIR, file.filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        orig_img = cv2.imread(file_path)

        # YOLO detection
        results = model(file_path)

        helmeted = 0
        unhelmeted = 0
        history = []

        # annotate frame
        annotated_frame = results[0].plot()
        detected_path = os.path.join(UPLOAD_DIR, f"detected_{file.filename}")
        cv2.imwrite(detected_path, annotated_frame)

        conn = sqlite3.connect("DB_Operations/events.db")
        cursor = conn.cursor()

        for r in results:
            for box in r.boxes:
                cls_id = int(box.cls.cpu().numpy()[0])
                hasHelmet = cls_id == 0
                if hasHelmet:
                    helmeted += 1
                else:
                    unhelmeted += 1

                number_plate_text = "UNKNOWN"
                # run OCR if this box is a number plate (class id 3)
                if cls_id == 3:
                    x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())
                    plate_crop = orig_img[y1:y2, x1:x2]
                    if plate_crop.size > 0:
                        number_plate_text = extract_plate_text(plate_crop)

                event_id = f"evt-{uuid.uuid4().hex[:8]}"
                history.append({
                    "id": event_id,
                    "date": datetime.now().strftime("%Y-%m-%d"),
                    "time": datetime.now().strftime("%H:%M"),
                    "location": "Main St & 1st Ave",
                    "numberPlate": number_plate_text,
                    "hasHelmet": hasHelmet,
                    "imageUrl": f"/uploads/detected_{file.filename}"
                })

                cursor.execute("""
                    INSERT INTO events (id, date, time, location, number_plate, has_helmet, image_url)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    event_id,
                    datetime.now().strftime("%Y-%m-%d"),
                    datetime.now().strftime("%H:%M"),
                    "Main St & 1st Ave",
                    number_plate_text,
                    int(hasHelmet),
                    f"/uploads/detected_{file.filename}"
                ))

        conn.commit()
        conn.close()

        data = {
            "helmetedCount": helmeted,
            "unhelmetedCount": unhelmeted,
            "totalCount": helmeted + unhelmeted,
            "history": history
        }
        return JSONResponse(content={"message": "Helmet detection completed", "data": data})

    except Exception as e:
        traceback.print_exc()
        return JSONResponse(status_code=500, content={"message": str(e)})

# ---------- camera streaming ----------
camera = None

@app.get("/api/start_stream")
def start_stream():
    global camera
    if camera is None:
        camera = cv2.VideoCapture(0)
    if not camera.isOpened():
        return {"message": "Failed to access camera"}
    return {"message": "Live stream started"}

@app.post("/api/stop_stream")
def stop_stream():
    global camera
    if camera is not None:
        camera.release()
        camera = None
    return {"message": "Live stream stopped"}

def generate_frames():
    global camera
    while True:
        if camera is None:
            break
        success, frame = camera.read()
        if not success:
            break
        _, buffer = cv2.imencode('.jpg', frame)
        yield (b"--frame\r\n"
               b"Content-Type: image/jpeg\r\n\r\n" + buffer.tobytes() + b"\r\n")

@app.get("/api/live_feed")
def live_feed():
    if camera is None:
        return {"message": "Stream not started"}
    return StreamingResponse(generate_frames(),
                             media_type="multipart/x-mixed-replace; boundary=frame")
