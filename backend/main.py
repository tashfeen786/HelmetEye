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


# --- Add this line after importing pytesseract ---
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"  # Update this path if necessary


# Initialize FastAPI app
app = FastAPI()

# Enable CORS for frontend integration
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:9002",
        "http://192.168.1.7:9002"  # replace with your actual dev machine IP if needed
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Serve static files (for uploaded images)
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# Database setup
DATABASE_URL = "sqlite:///database.db"
engine = create_engine(DATABASE_URL)
SQLModel.metadata.create_all(engine)

# Pydantic model for request validation
class UserCreate(BaseModel):
    name: str
    email: str

# API Endpoints
@app.get("/")
def read_root():
    return {"message": "Welcome to the FastAPI backend!"}

@app.get("/api/report")
def get_report():
    print("Fetching report data...")
    data = get_data()
    print(data)
    return {"report": data}


UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@app.post("/api/detect_helmet")
async def detect_helmet(file: UploadFile = File(...)):
    try:
        if not file:
            return JSONResponse(
                status_code=400,
                content={"message": "No file uploaded. Please upload an image OR video."}
            )

        # Save uploaded file
        file_path = os.path.join(UPLOAD_DIR, file.filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Run YOLO detection
        results = model(file_path)

        helmeted = 0
        unhelmeted = 0
        history = []

        # Annotate and save detected image
        annotated_frame = results[0].plot()
        detected_path = os.path.join(UPLOAD_DIR, f"detected_{file.filename}")
        cv2.imwrite(detected_path, annotated_frame)

        # Open DB connection once per request
        conn = sqlite3.connect("DB_Operations/events.db")
        cursor = conn.cursor()

        for r in results:
            for i, box in enumerate(r.boxes):
                cls_id = int(box.cls.cpu().numpy()[0])
                hasHelmet = cls_id == 0
                if hasHelmet:
                    helmeted += 1
                else:
                    unhelmeted += 1

                number_plate_text = "UNKNOWN"
                # OCR for number plate
                if cls_id == 2:
                    x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())
                    plate_crop = annotated_frame[y1:y2, x1:x2]
                    plate_crop = cv2.cvtColor(plate_crop, cv2.COLOR_BGR2RGB)
                    plate_text = pytesseract.image_to_string(Image.fromarray(plate_crop))
                    number_plate_text = plate_text.strip()

                # Unique event ID
                event_id = f"evt-{uuid.uuid4().hex[:8]}"

                # Append to history
                history.append({
                    "id": event_id,
                    "date": datetime.now().strftime("%Y-%m-%d"),
                    "time": datetime.now().strftime("%H:%M"),
                    "location": "Main St & 1st Ave",
                    "numberPlate": number_plate_text,
                    "hasHelmet": hasHelmet,
                    "imageUrl": f"/uploads/detected_{file.filename}"
                })

                # Insert into DB
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

        return JSONResponse(content={
            "message": "Helmet detection completed",
            "data": data
        })

    except Exception as e:
        traceback.print_exc()  # prints full error in console
        return JSONResponse(status_code=500, content={"message": str(e)})
camera = None

@app.get("/api/start_stream")
def start_stream():
    global camera
    if camera is None:
        camera = cv2.VideoCapture(0)  # laptop/webcam
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
        # Encode frame as JPEG
        _, buffer = cv2.imencode('.jpg', frame)
        frame_bytes = buffer.tobytes()
        yield (
            b"--frame\r\n"
            b"Content-Type: image/jpeg\r\n\r\n" + frame_bytes + b"\r\n"
        )


@app.get("/api/live_feed")
def live_feed():
    if camera is None:
        return {"message": "Stream not started"}
    return StreamingResponse(generate_frames(), media_type="multipart/x-mixed-replace; boundary=frame")
