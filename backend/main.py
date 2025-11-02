import os
import re
import cv2
import uuid
import shutil
import traceback
import sqlite3
from datetime import datetime
from fastapi import FastAPI, UploadFile, File, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from PIL import Image
import pytesseract
import threading

# === Import model and DB helpers ===
from models.model import model
from DB_Operations.get_data import get_data
from DB_Operations.insert_data import insert_event
from DB_Operations.db_config import DB_PATH  # ✅ absolute path from db_config.py

# Optional EasyOCR
try:
    import easyocr
    EASYOCR_AVAILABLE = True
except ImportError:
    EASYOCR_AVAILABLE = False

# Tesseract path (adjust if different on your machine)
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# FastAPI app
app = FastAPI(title="Helmet Detection Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:9002",
        "http://127.0.0.1:9002",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://192.168.1.7:9002",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Upload directory (absolute)
UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")

def extract_plate_text(bgr_crop):
    """
    Extracts clean license plate text from a cropped plate image.
    Improves OCR accuracy with preprocessing and cleanup.
    """
    try:
        if bgr_crop is None or bgr_crop.size == 0:
            return "UNKNOWN"

        # Convert to grayscale
        gray = cv2.cvtColor(bgr_crop, cv2.COLOR_BGR2GRAY)

        # Denoise and enhance contrast
        gray = cv2.bilateralFilter(gray, 11, 17, 17)
        gray = cv2.equalizeHist(gray)

        # Adaptive thresholding for cleaner text edges
        thresh = cv2.adaptiveThreshold(
            gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY, 15, 5
        )

        text = ""

        # --- EasyOCR path ---
        if EASYOCR_AVAILABLE:
            reader = easyocr.Reader(["en"], gpu=False)
            results = reader.readtext(thresh)
            if results:
                # pick the text with the highest confidence
                results = sorted(results, key=lambda r: r[2], reverse=True)
                text = results[0][1]

        # --- Fallback to Tesseract ---
        if not text.strip():
            config = "--psm 7 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
            text = pytesseract.image_to_string(Image.fromarray(thresh), config=config)

        # --- Clean up the text ---
        text = re.sub(r"[^A-Z0-9]", "", text.upper())

        # Return only if plausible plate
        return text if len(text) >= 4 else "UNKNOWN"

    except Exception as e:
        print(f"OCR error: {e}")
        return "UNKNOWN"



def box_overlap(box1, box2):
    x1, y1, x2, y2 = box1
    x1b, y1b, x2b, y2b = box2
    inter_x1 = max(x1, x1b)
    inter_y1 = max(y1, y1b)
    inter_x2 = min(x2, x2b)
    inter_y2 = min(y2, y2b)
    inter_area = max(0, inter_x2 - inter_x1) * max(0, inter_y2 - inter_y1)
    area1 = max(0, (x2 - x1)) * max(0, (y2 - y1))
    area2 = max(0, (x2b - x1b)) * max(0, (y2b - y1b))
    union_area = area1 + area2 - inter_area
    return inter_area / union_area if union_area > 0 else 0


def find_closest_plate(rider_box, plates):
    best_plate, best_iou = None, 0
    for plate in plates:
        iou = box_overlap(rider_box, plate)
        if iou > best_iou:
            best_iou, best_plate = iou, plate
    return best_plate


def verify_row_written(event_id):
    """Check DB for an event with event_id. Returns True if found."""
    try:
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute("SELECT id FROM events WHERE id = ?", (event_id,))
        found = cur.fetchone() is not None
        conn.close()
        return found
    except Exception as e:
        print(f"[DB VERIFY ERROR] {e}")
        return False

# ---------- ROUTES ----------
@app.get("/")
def read_root():
    return {"message": "Backend is running!"}


@app.get("/api/report")
def get_report():
    try:
        data = get_data()
        return JSONResponse(
            content={"report": data},
            headers={
                "Cache-Control": "no-cache, no-store, must-revalidate",
                "Pragma": "no-cache",
                "Expires": "0",
            },
        )
    except Exception as e:
        traceback.print_exc()
        return JSONResponse(status_code=500, content={"message": str(e)})

@app.post("/api/detect_helmet")
async def detect_helmet(file: UploadFile = File(...)):
    """Handle single image helmet detection and store all detected events."""
    try:
        if not file:
            return JSONResponse(status_code=400, content={"message": "No file uploaded"})

        # Save uploaded image
        unique_filename = f"{uuid.uuid4().hex}_{file.filename}"
        file_path = os.path.join(UPLOAD_DIR, unique_filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Run detection
        orig_img = cv2.imread(file_path)
        results = model(file_path)
        annotated_frame = results[0].plot()

        # Save annotated image
        detected_filename = f"detected_{unique_filename}"
        detected_path = os.path.join(UPLOAD_DIR, detected_filename)
        cv2.imwrite(detected_path, annotated_frame)

        CLASS_MAP = {0: "rider", 1: "helmet", 2: "without_helmet", 3: "number_plate"}
        riders, helmets, plates, without_helmets = [], [], [], []

        # Parse detections
        for r in results:
            for box in r.boxes:
                cls_id = int(box.cls.cpu().numpy()[0])
                label = CLASS_MAP.get(cls_id, "unknown")
                x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())

                if label == "rider":
                    riders.append((x1, y1, x2, y2))
                elif label == "helmet":
                    helmets.append((x1, y1, x2, y2))
                elif label == "without_helmet":
                    without_helmets.append((x1, y1, x2, y2))
                elif label == "number_plate":
                    plates.append((x1, y1, x2, y2))

        history = []
        processed_riders = []

        for rider_box in riders:
            # Skip duplicate riders (overlap > 0.6)
            if any(box_overlap(rider_box, prev) > 0.6 for prev in processed_riders):
                continue
            processed_riders.append(rider_box)

            # Determine if rider has a helmet
            has_helmet = any(box_overlap(rider_box, h) > 0.05 for h in helmets)
            if not has_helmet:
                has_helmet = not any(box_overlap(rider_box, wh) > 0.05 for wh in without_helmets)

            # Find nearest number plate
            plate_text = "UNKNOWN"
            closest_plate = find_closest_plate(rider_box, plates)
            if closest_plate:
                x1, y1, x2, y2 = closest_plate
                crop = orig_img[y1:y2, x1:x2]
                if crop is not None and crop.size > 0:
                    plate_text = extract_plate_text(crop)

            event_id = f"evt-{uuid.uuid4().hex[:8]}"
            event_data = {
                "id": event_id,
                "date": datetime.now().strftime("%Y-%m-%d"),
                "time": datetime.now().strftime("%H:%M"),
                "location": "MS Boys College Road, AJK",
                "number_plate": plate_text,
                "has_helmet": has_helmet,
                "image_url": f"/uploads/{detected_filename}",
            }

            try:
                insert_event(event_data)
                if verify_row_written(event_id):
                    print(f"✅ Event '{event_id}' verified in database!")
                else:
                    print(f"❌ Verification failed for {event_id}")
            except Exception as ins_err:
                print(f"❌ insert_event raised an exception for {event_id}: {ins_err}")
                traceback.print_exc()
                continue

            history.append({
                "id": event_id,
                "numberPlate": plate_text,
                "hasHelmet": has_helmet,
                "imageUrl": f"/uploads/{detected_filename}",
            })

        return JSONResponse(content={
            "message": "Helmet detection completed",
            "data": {
                "totalRiders": len(processed_riders),
                "helmeted": sum(1 for r in history if r["hasHelmet"]),
                "unhelmeted": sum(1 for r in history if not r["hasHelmet"]),
                "history": history,
                "processedImageUrl": f"/uploads/{detected_filename}",
            },
        })

    except Exception as e:
        traceback.print_exc()
        return JSONResponse(status_code=500, content={"message": str(e)})


# ============================================================
# ✅ VIDEO DETECTION
# ============================================================
@app.post("/api/detect_video")
async def detect_video(file: UploadFile = File(...)):
    try:
        video_filename = f"{uuid.uuid4().hex}_{file.filename}"
        video_path = os.path.join(UPLOAD_DIR, video_filename)
        with open(video_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            return JSONResponse(status_code=400, content={"message": "Cannot open video"})

        frame_rate = int(cap.get(cv2.CAP_PROP_FPS))
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

        out_filename = f"processed_{video_filename}"
        out_path = os.path.join(UPLOAD_DIR, out_filename)
        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        out = cv2.VideoWriter(out_path, fourcc, frame_rate, (width, height))

        frame_count = 0
        event_counter = 0

        while True:
            ret, frame = cap.read()
            if not ret:
                break
            frame_count += 1

            if frame_count % 10 != 0:
                out.write(frame)
                continue

            results = model(frame)
            annotated_frame = results[0].plot()
            out.write(annotated_frame)

            CLASS_MAP = {0: "rider", 1: "helmet", 2: "without_helmet", 3: "number_plate"}
            helmets, without_helmets, plates = [], [], []

            for r in results:
                for box in r.boxes:
                    cls_id = int(box.cls.cpu().numpy()[0])
                    label = CLASS_MAP.get(cls_id, "unknown")
                    x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())
                    if label == "helmet":
                        helmets.append((x1, y1, x2, y2))
                    elif label == "without_helmet":
                        without_helmets.append((x1, y1, x2, y2))
                    elif label == "number_plate":
                        plates.append((x1, y1, x2, y2))

            riders = helmets + without_helmets
            for rider_box in riders:
                has_helmet = rider_box in helmets
                plate_text = "UNKNOWN"
                closest_plate = find_closest_plate(rider_box, plates)
                if closest_plate:
                    x1, y1, x2, y2 = closest_plate
                    crop = frame[y1:y2, x1:x2]
                    if crop is not None and crop.size > 0:
                        plate_text = extract_plate_text(crop)

                event_id = f"evt-{uuid.uuid4().hex[:8]}"
                event_data = {
                    "id": event_id,
                    "date": datetime.now().strftime("%Y-%m-%d"),
                    "time": datetime.now().strftime("%H:%M"),
                    "location": "MS Boys College Road, AJK",
                    "number_plate": plate_text,
                    "has_helmet": has_helmet,
                    "image_url": f"/uploads/{out_filename}",
                }
                insert_event(event_data)
                event_counter += 1

            progress = (frame_count / total_frames) * 100
            print(f"[VIDEO PROGRESS] {progress:.1f}%")

        cap.release()
        out.release()

        return JSONResponse(content={
            "message": f"Video processed successfully ({event_counter} events saved)",
            "processedVideoUrl": f"/uploads/{out_filename}"
        })

    except Exception as e:
        traceback.print_exc()
        return JSONResponse(status_code=500, content={"message": str(e)})

# ============================================================
# ✅ LIVE CAMERA STREAM WITH SAFE STOP
# ============================================================
import threading
import cv2
from fastapi import FastAPI
from fastapi.responses import StreamingResponse


camera = None
is_streaming = False
log_threads = []

# Dummy DB logging function (replace with your actual DB code)
def log_event_async(frame, results):
    print("Logging event to DB...")
    import time
    time.sleep(0.1)

# Frame generator for live feed
def gen_frames():
    global camera, is_streaming, log_threads

    while is_streaming and camera is not None and camera.isOpened():
        success, frame = camera.read()
        if not success:
            break

        # Replace with your actual model inference
        # results = model(frame)
        # annotated = results[0].plot()
        annotated = frame  # For now just show raw frame

        # Start DB logging in a separate thread
        if is_streaming:
            t = threading.Thread(target=log_event_async, args=(frame.copy(), None))
            t.start()
            log_threads.append(t)

        # Encode frame to JPEG
        _, buffer = cv2.imencode(".jpg", annotated)
        frame_bytes = buffer.tobytes()
        yield (b"--frame\r\n"
               b"Content-Type: image/jpeg\r\n\r\n" + frame_bytes + b"\r\n")

    # Cleanup after stopping
    print("🛑 Stream stopped, releasing camera.")
    if camera is not None:
        camera.release()
        camera = None
    is_streaming = False

    # Wait for all DB logging threads to finish
    for t in log_threads:
        t.join()
    log_threads.clear()

@app.get("/api/start_stream")
def start_stream():
    global camera, is_streaming
    if is_streaming:
        return {"status": "already streaming"}

    camera = cv2.VideoCapture(0)  # Or your video source
    is_streaming = True
    # Use StreamingResponse to stream the generator to the frontend
    return StreamingResponse(gen_frames(), media_type="multipart/x-mixed-replace; boundary=frame")

@app.get("/api/stop_stream")
def stop_stream():
    global is_streaming
    if not is_streaming:
        return {"status": "not streaming"}
    
    # Setting the flag will stop the streaming generator
    is_streaming = False
    return {"status": "stopping stream"}

