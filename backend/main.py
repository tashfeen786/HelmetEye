from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import SQLModel, create_engine, Session
from pydantic import BaseModel
from sqlmodel import Field
from DB_Operations.get_data import get_data
import sqlite3
from fastapi.responses import StreamingResponse
import cv2


# Initialize FastAPI app
app = FastAPI()

# Enable CORS for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://192.168.1.7:9002", "http://localhost:9002"],  # React dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database setup
DATABASE_URL = "sqlite:///database.db"
engine = create_engine(DATABASE_URL)
SQLModel.metadata.create_all(engine)

# Example database model
class User(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    name: str
    email: str

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
    data =  get_data()
    print(data)
    return {"report": data}


@app.get("/api/detect_helmet")
def detect_helmit(request: Request):
    data = request.json()
    # Placeholder for helmit detection logic
    data = {
        "helmetedCount": 700,
        "unhelmetedCount": 20,
        "totalCount": 90,
        "history": [
            {
            "id": "evt-001",
            "date": "2024-07-28",
            "time": "14:32",
            "location": "Main St & 1st Ave",
            "numberPlate": "B-123-XYZ",
            "hasHelmet": True,
            "imageUrl": "https://placehold.co/150x100.png"
            }
        ]
    }
    return {
        "message": "Helmit detection logic not implemented", 
        "data": data
        }

camera = None

@app.get("/api/start_stream")
def start_stream():
    global camera
    if camera is None:
        camera = cv2.VideoCapture(0) # laptop/webcam
    if not camera.isOpened():
        return {"message": "Failed to access camera"}
    return {"message": "Live stream started"}


@app.get("/api/stop_stream")
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
