from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
import sqlite3, os, shutil, uuid, traceback, re
from datetime import datetime
import cv2
from PIL import Image
import pytesseract
from models.model import model  # YOLO model import
from DB_Operations.get_data import get_data

# Optional EasyOCR
try:
    import easyocr
    EASYOCR_AVAILABLE = True
except Exception:
    EASYOCR_AVAILABLE = False

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# ---------- Helper: OCR ----------
def extract_plate_text(bgr_crop):
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

# ---------- FastAPI Setup ----------
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:9002", "http://192.168.1.7:9002"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------- Static Files Setup ----------
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")

# ---------- Routes ----------
@app.get("/")
def read_root():
    return {"message": "Backend is running!"}

@app.get("/api/report")
def get_report():
    data = get_data()
    return {"report": data}

# ---------- Helmet Detection for Image ----------
@app.post("/api/detect_helmet")
async def detect_helmet(file: UploadFile = File(...)):
    try:
        if not file:
            return JSONResponse(status_code=400, content={"message": "No file uploaded"})

        # Save uploaded file
        unique_filename = f"{uuid.uuid4().hex}_{file.filename}"
        file_path = os.path.join(UPLOAD_DIR, unique_filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        orig_img = cv2.imread(file_path)

        # Run YOLO detection
        results = model(file_path)

        helmeted = 0
        unhelmeted = 0
        history = []

        # Annotated image
        annotated_frame = results[0].plot()
        detected_filename = f"detected_{unique_filename}"
        detected_path = os.path.join(UPLOAD_DIR, detected_filename)
        cv2.imwrite(detected_path, annotated_frame)

        # Save events in DB
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
                if cls_id == 3:  # number plate
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
                    "imageUrl": f"/uploads/{detected_filename}"
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
                    f"/uploads/{detected_filename}"
                ))

        conn.commit()
        conn.close()

        return JSONResponse(content={
            "message": "Helmet detection completed",
            "data": {
                "helmetedCount": helmeted,
                "unhelmetedCount": unhelmeted,
                "totalCount": helmeted + unhelmeted,
                "history": history,
                "processedImageUrl": f"/uploads/{detected_filename}"
            }
        })

    except Exception as e:
        traceback.print_exc()
        return JSONResponse(status_code=500, content={"message": str(e)})

## ---------- Helmet Detection for Video ----------
@app.post("/api/detect_video")
async def detect_video(file: UploadFile = File(...)):
    try:
        if not file:
            return JSONResponse(status_code=400, content={"message": "No file uploaded"})

        unique_filename = f"{uuid.uuid4().hex}_{file.filename}"
        file_path = os.path.join(UPLOAD_DIR, unique_filename)
        with open(file_path, "wb") as f:
            shutil.copyfileobj(file.file, f)

        cap = cv2.VideoCapture(file_path)
        if not cap.isOpened():
            return JSONResponse(status_code=400, content={"message": "Cannot open video"})

        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out_path = os.path.join(UPLOAD_DIR, f"detected_{unique_filename}")
        fps = cap.get(cv2.CAP_PROP_FPS) or 25
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        out = cv2.VideoWriter(out_path, fourcc, fps, (width, height))

        frame_count = 0
        MAX_FRAMES = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))  # process all frames

        while True:
            ret, frame = cap.read()
            if not ret or frame_count >= MAX_FRAMES:
                break

            # YOLO detection with logging off
            results = model(frame, verbose=False)
            annotated_frame = results[0].plot()
            out.write(annotated_frame)
            frame_count += 1

        cap.release()
        out.release()

        return JSONResponse(content={
            "message": "Video processed",
            "processedVideoUrl": f"/uploads/detected_{unique_filename}"
        })

    except Exception as e:
        traceback.print_exc()
        return JSONResponse(status_code=500, content={"message": str(e)})

# ---------- Camera Streaming ----------
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
    while camera is not None:
        success, frame = camera.read()
        if not success:
            break
        # YOLO detection optional: verbose=False to avoid logs
        results = model(frame, verbose=False)
        annotated_frame = results[0].plot()
        _, buffer = cv2.imencode('.jpg', annotated_frame)
        yield (b"--frame\r\n"
               b"Content-Type: image/jpeg\r\n\r\n" + buffer.tobytes() + b"\r\n")
