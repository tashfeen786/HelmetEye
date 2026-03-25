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
    """Calculate IoU between two boxes."""
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


def box_distance(box1, box2):
    """Calculate center-to-center distance between two boxes."""
    cx1 = (box1[0] + box1[2]) / 2
    cy1 = (box1[1] + box1[3]) / 2
    cx2 = (box2[0] + box2[2]) / 2
    cy2 = (box2[1] + box2[3]) / 2
    return ((cx1 - cx2)**2 + (cy1 - cy2)**2)**0.5


def expand_box(box, expand_factor=1.5):
    """Expand a bounding box by a factor to create search area."""
    x1, y1, x2, y2 = box
    w = x2 - x1
    h = y2 - y1
    cx = (x1 + x2) / 2
    cy = (y1 + y2) / 2
    new_w = w * expand_factor
    new_h = h * expand_factor
    return (
        int(cx - new_w/2),
        int(cy - new_h/2),
        int(cx + new_w/2),
        int(cy + new_h/2)
    )


def determine_helmet_status(plate_box, riders, with_helmets, without_helmets):
    """
    ✅ NEW LOGIC: Majority-based helmet detection
    - If ANY rider has helmet → TRUE (with_helmet)
    - Only if ALL riders are without helmet → FALSE (no_helmet)
    """
    # Expand search area around plate (bikes have riders above plates)
    search_box = expand_box(plate_box, expand_factor=2.5)
    
    # Find with_helmet and without_helmet detections in search area
    nearby_with_helmets = []
    nearby_without_helmets = []
    
    for helmet in with_helmets:
        overlap = box_overlap(search_box, helmet)
        distance = box_distance(plate_box, helmet)
        if overlap > 0.01 or distance < 300:  # Within range
            nearby_with_helmets.append((helmet, distance, overlap))
    
    for wh in without_helmets:
        overlap = box_overlap(search_box, wh)
        distance = box_distance(plate_box, wh)
        if overlap > 0.01 or distance < 300:
            nearby_without_helmets.append((wh, distance, overlap))
    
    # Sort by distance (closest first)
    nearby_with_helmets.sort(key=lambda x: x[1])
    nearby_without_helmets.sort(key=lambda x: x[1])
    
    print(f"[DEBUG] Search area for plate: with_helmets={len(nearby_with_helmets)}, without_helmets={len(nearby_without_helmets)}")
    
    # ✅ NEW DECISION LOGIC: "Any helmet present = Safe"
    if nearby_with_helmets:
        # If even 1 person has helmet, mark as SAFE
        print(f"[DEBUG] ✅ AT LEAST ONE HELMET DETECTED → MARKING AS SAFE")
        print(f"[DEBUG]    - With helmets: {len(nearby_with_helmets)}")
        print(f"[DEBUG]    - Without helmets: {len(nearby_without_helmets)}")
        return True
    elif nearby_without_helmets:
        # Only without_helmets found, no with_helmet → UNSAFE
        print(f"[DEBUG] ❌ ONLY WITHOUT HELMETS FOUND → MARKING AS UNSAFE")
        print(f"[DEBUG]    - Without helmets: {len(nearby_without_helmets)}")
        return False
    else:
        # No helmet detection at all
        nearby_riders = [r for r in riders if box_distance(plate_box, r) < 300]
        if nearby_riders:
            print(f"[DEBUG] ⚠️ Rider found but NO helmet detection → UNSAFE")
            return False
        else:
            print(f"[DEBUG] ⚠️ No rider/helmet detection → DEFAULT UNSAFE")
            return False


def boxes_are_duplicate(box1, box2):
    """Return True if two boxes are likely duplicates (same bike/person)."""
    iou = box_overlap(box1, box2)
    area1 = max(1, (box1[2] - box1[0])) * max(1, (box1[3] - box1[1]))
    area2 = max(1, (box2[2] - box2[0])) * max(1, (box2[3] - box2[1]))
    size_ratio = min(area1, area2) / max(area1, area2) if max(area1, area2) > 0 else 0
    return iou > 0.45 and size_ratio > 0.7


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
    """Helmet detection endpoint: inserts DB rows per number plate detected."""
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

        # ✅ FIXED: Updated class mapping to match actual model classes
        CLASS_MAP = {0: "rider", 1: "with_helmet", 2: "without_helmet", 3: "number_plate"}
        riders, with_helmets, without_helmets, plates = [], [], [], []

        # Parse detections
        for r in results:
            for box in r.boxes:
                cls_id = int(box.cls.cpu().numpy()[0])
                label = CLASS_MAP.get(cls_id, "unknown")
                x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())
                if label == "rider":
                    riders.append((x1, y1, x2, y2))
                elif label == "with_helmet":
                    with_helmets.append((x1, y1, x2, y2))
                elif label == "without_helmet":
                    without_helmets.append((x1, y1, x2, y2))
                elif label == "number_plate":
                    plates.append((x1, y1, x2, y2))

        print(f"[DEBUG] Total Detections -> Riders: {len(riders)}, WITH Helmets: {len(with_helmets)}, WITHOUT Helmets: {len(without_helmets)}, Plates: {len(plates)}")

        history = []

        # ✅ Process every detected plate
        for idx, plate_box in enumerate(plates):
            x1, y1, x2, y2 = plate_box
            crop = orig_img[y1:y2, x1:x2]
            plate_text = extract_plate_text(crop) if crop is not None and crop.size > 0 else "UNKNOWN"

            print(f"\n[DEBUG] === Processing Plate {idx}: {plate_text} ===")
            
            # ✅ Use corrected helmet detection
            has_helmet = determine_helmet_status(plate_box, riders, with_helmets, without_helmets)

            event_id = f"evt-{uuid.uuid4().hex[:8]}"
            event_data = {
                "id": event_id,
                "date": datetime.now().strftime("%Y-%m-%d"),
                "time": datetime.now().strftime("%H:%M"),
                "location": "UOK AJK",
                "number_plate": plate_text,
                "has_helmet": has_helmet,
                "image_url": f"/uploads/{detected_filename}",
            }

            print(f"[DEBUG] Final Decision -> Plate {idx} ({plate_text}): has_helmet={has_helmet}")
            print(f"[DEBUG] Inserting event -> {event_data}\n")

            try:
                insert_event(event_data)
                if verify_row_written(event_id):
                    print(f"✅ Event '{event_id}' inserted and verified!")
                else:
                    print(f"❌ Verification failed for {event_id}")
            except Exception as e:
                print(f"❌ DB insert failed for {event_id}: {e}")
                traceback.print_exc()
                continue

            history.append({
                "id": event_id,
                "numberPlate": plate_text,
                "hasHelmet": has_helmet,
                "imageUrl": f"/uploads/{detected_filename}",
            })

        return JSONResponse(content={
            "message": "Helmet detection completed (per number plate)",
            "data": {
                "totalPlates": len(plates),
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
# ✅ VIDEO DETECTION - FIXED
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

            CLASS_MAP = {0: "rider", 1: "with_helmet", 2: "without_helmet", 3: "number_plate"}
            riders, with_helmets, without_helmets, plates = [], [], [], []

            for r in results:
                for box in r.boxes:
                    cls_id = int(box.cls.cpu().numpy()[0])
                    label = CLASS_MAP.get(cls_id, "unknown")
                    x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())
                    if label == "rider":
                        riders.append((x1, y1, x2, y2))
                    elif label == "with_helmet":
                        with_helmets.append((x1, y1, x2, y2))
                    elif label == "without_helmet":
                        without_helmets.append((x1, y1, x2, y2))
                    elif label == "number_plate":
                        plates.append((x1, y1, x2, y2))

            # Process each plate
            for idx, plate_box in enumerate(plates):
                x1, y1, x2, y2 = plate_box
                crop = frame[y1:y2, x1:x2]
                plate_text = extract_plate_text(crop) if crop is not None and crop.size > 0 else "UNKNOWN"

                has_helmet = determine_helmet_status(plate_box, riders, with_helmets, without_helmets)

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

                try:
                    insert_event(event_data)
                    event_counter += 1
                except Exception as e:
                    print(f"❌ DB insert failed: {e}")
                    continue

            progress = (frame_count / total_frames) * 100
            if frame_count % 30 == 0:
                print(f"[VIDEO PROGRESS] {progress:.1f}% - Events: {event_counter}")

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
# ✅ LIVE STREAM - FIXED
# ============================================================
camera = None
is_streaming = False
log_threads = []
FRAME_INTERVAL = 5
stop_logging = False

def log_event_async(frame):
    global stop_logging
    if stop_logging:
        return
    try:
        results = model(frame)
        CLASS_MAP = {0: "rider", 1: "with_helmet", 2: "without_helmet", 3: "number_plate"}
        riders, with_helmets, without_helmets, plates = [], [], [], []

        for r in results:
            for box in r.boxes:
                cls_id = int(box.cls.cpu().numpy()[0])
                label = CLASS_MAP.get(cls_id, "unknown")
                x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())
                if label == "rider":
                    riders.append((x1, y1, x2, y2))
                elif label == "with_helmet":
                    with_helmets.append((x1, y1, x2, y2))
                elif label == "without_helmet":
                    without_helmets.append((x1, y1, x2, y2))
                elif label == "number_plate":
                    plates.append((x1, y1, x2, y2))

        for plate_box in plates:
            if stop_logging:
                break
            x1, y1, x2, y2 = plate_box
            crop = frame[y1:y2, x1:x2]
            plate_text = extract_plate_text(crop) if crop is not None and crop.size > 0 else "UNKNOWN"

            has_helmet = determine_helmet_status(plate_box, riders, with_helmets, without_helmets)

            snapshot_name = f"{uuid.uuid4().hex}_live.jpg"
            snapshot_path = os.path.join(UPLOAD_DIR, snapshot_name)
            cv2.imwrite(snapshot_path, frame)

            event_id = f"evt-{uuid.uuid4().hex[:8]}"
            event_data = {
                "id": event_id,
                "date": datetime.now().strftime("%Y-%m-%d"),
                "time": datetime.now().strftime("%H:%M"),
                "location": "MS Boys College Road, AJK",
                "number_plate": plate_text,
                "has_helmet": has_helmet,
                "image_url": f"/uploads/{snapshot_name}",
            }

            if stop_logging:
                break

            try:
                insert_event(event_data)
                print(f"✅ Live event inserted: {event_id}")
            except Exception as e:
                print(f"❌ DB insert failed: {e}")

    except Exception as e:
        print(f"⚠️ Live logging error: {e}")


def gen_frames():
    global camera, is_streaming, log_threads, stop_logging
    frame_count = 0
    stop_logging = False

    while is_streaming and camera is not None and camera.isOpened():
        success, frame = camera.read()
        if not success:
            break
        frame_count += 1

        results = model(frame)
        annotated = results[0].plot()

        if frame_count % FRAME_INTERVAL == 0 and not stop_logging:
            t = threading.Thread(target=log_event_async, args=(frame.copy(),))
            t.start()
            log_threads.append(t)

        _, buffer = cv2.imencode(".jpg", annotated)
        frame_bytes = buffer.tobytes()
        yield (b"--frame\r\n"
               b"Content-Type: image/jpeg\r\n\r\n" + frame_bytes + b"\r\n")

    print("🛑 Stream stopped, releasing camera.")
    if camera is not None:
        camera.release()
        camera = None
    is_streaming = False
    stop_logging = True

    for t in log_threads:
        t.join()
    log_threads.clear()


@app.get("/api/start_stream")
def start_stream():
    global camera, is_streaming
    if is_streaming:
        return {"status": "already streaming"}

    camera = cv2.VideoCapture(0)
    is_streaming = True
    return StreamingResponse(gen_frames(), media_type="multipart/x-mixed-replace; boundary=frame")


@app.get("/api/stop_stream")
def stop_stream():
    global is_streaming, stop_logging
    if not is_streaming:
        return {"status": "not streaming"}

    is_streaming = False
    stop_logging = True
    return {"status": "stopping stream"}