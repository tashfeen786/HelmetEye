from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi import Response
import os, shutil, uuid, traceback, re
from datetime import datetime
import cv2
from PIL import Image
import pytesseract
from models.model import model  # YOLO model import
from DB_Operations.get_data import get_data
from DB_Operations.insert_data import insert_event

# Optional EasyOCR
try:
    import easyocr
    EASYOCR_AVAILABLE = True
except Exception:
    EASYOCR_AVAILABLE = False

# ---------- Tesseract Setup ----------
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# ---------- Helper Functions ----------
def extract_plate_text(bgr_crop):
    try:
        gray = cv2.cvtColor(bgr_crop, cv2.COLOR_BGR2GRAY)
        gray = cv2.bilateralFilter(gray, 11, 17, 17)

        text = ""
        if EASYOCR_AVAILABLE:
            reader = easyocr.Reader(["en"], gpu=False)
            results = reader.readtext(gray)
            if results:
                text = " ".join(r[1] for r in results)

        if not text.strip():
            text = pytesseract.image_to_string(Image.fromarray(gray))

        text = re.sub(r"[^A-Z0-9]", "", text.upper())
        return text if len(text) >= 4 else "UNKNOWN"
    except Exception:
        return "UNKNOWN"

def box_overlap(box1, box2):
    """Calculate IoU (Intersection over Union) between two boxes."""
    x1, y1, x2, y2 = box1
    x1b, y1b, x2b, y2b = box2
    inter_x1 = max(x1, x1b)
    inter_y1 = max(y1, y1b)
    inter_x2 = min(x2, x2b)
    inter_y2 = min(y2, y2b)
    inter_area = max(0, inter_x2 - inter_x1) * max(0, inter_y2 - inter_y1)
    area1 = (x2 - x1) * (y2 - y1)
    area2 = (x2b - x1b) * (y2b - y1b)
    union_area = area1 + area2 - inter_area
    return inter_area / union_area if union_area > 0 else 0

def find_closest_plate(rider_box, plates):
    """Find the plate with the highest overlap or closest to the rider."""
    best_plate = None
    best_iou = 0
    for plate in plates:
        iou = box_overlap(rider_box, plate)
        if iou > best_iou:
            best_iou = iou
            best_plate = plate
    return best_plate

print("DB_PATH used by FastAPI:", os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "events.db")))
print("Current working directory:", os.getcwd())
#FastAPI Setup ----------
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:9002", "http://192.168.1.7:9002"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------- Static Files ----------
UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "uploads")  # absolute path
os.makedirs(UPLOAD_DIR, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")


# ---------- Routes ----------
@app.get("/")
def read_root():
    return {"message": "Backend is running!"}

@app.get("/api/report")
def get_report():
    data = get_data()
    response = JSONResponse(content={"report": data})
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response

# ---------- Image Detection ----------
@app.post("/api/detect_helmet")
async def detect_helmet(file: UploadFile = File(...)):
    try:
        if not file:
            return JSONResponse(status_code=400, content={"message": "No file uploaded"})

        # Save uploaded image
        unique_filename = f"{uuid.uuid4().hex}_{file.filename}"
        file_path = os.path.join(UPLOAD_DIR, unique_filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Run YOLO model
        orig_img = cv2.imread(file_path)
        results = model(file_path)
        annotated_frame = results[0].plot()

        # Save annotated image
        detected_filename = f"detected_{unique_filename}"
        detected_path = os.path.join(UPLOAD_DIR, detected_filename)
        cv2.imwrite(detected_path, annotated_frame)

        # Parse detections
        CLASS_MAP = {0: "rider", 1: "helmet", 2: "without_helmet", 3: "number_plate"}
        riders, helmets, plates, without_helmets = [], [], [], []
        # print('Results:', results)
        
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

        for rider_box in riders:
            # Check if rider overlaps with any helmet
            hasHelmet = any(box_overlap(rider_box, helmet_box) > 0.1 for helmet_box in helmets)
            # If no helmet overlap, check for without_helmet
            if not hasHelmet:
                hasHelmet = not any(box_overlap(rider_box, wh_box) > 0.1 for wh_box in without_helmets)

            # Find closest plate
            plate_text = "UNKNOWN"
            closest_plate = find_closest_plate(rider_box, plates)
            if closest_plate:
                x1, y1, x2, y2 = closest_plate
                crop = orig_img[y1:y2, x1:x2]
                if crop.size > 0:
                    plate_text = extract_plate_text(crop)

            event_id = f"evt-{uuid.uuid4().hex[:8]}"
            event_data = {
                "id": event_id,
                "date": datetime.now().strftime("%Y-%m-%d"),
                "time": datetime.now().strftime("%H:%M"),
                "location": "kotli shaheed chock",
                "number_plate": plate_text,
                "has_helmet": hasHelmet,
                "image_url": f"/uploads/{detected_filename}"
            }

            insert_event(event_data)

            history.append({
                "id": event_id,
                "numberPlate": plate_text,
                "hasHelmet": hasHelmet,
                "imageUrl": f"/uploads/{detected_filename}"
            })

        return JSONResponse(content={
            "message": "Helmet detection completed",
            "data": {
                "totalRiders": len(riders),
                "helmeted": sum(1 for r in history if r["hasHelmet"]),
                "unhelmeted": sum(1 for r in history if not r["hasHelmet"]),
                "history": history,
                "processedImageUrl": f"/uploads/{detected_filename}"
            }
        })

    except Exception as e:
        traceback.print_exc()
        return JSONResponse(status_code=500, content={"message": str(e)})

#Video Detection 
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
        width, height = int(cap.get(3)), int(cap.get(4))
        out = cv2.VideoWriter(out_path, fourcc, fps, (width, height))

        frame_count, MAX_FRAMES = 0, int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

        while True:
            ret, frame = cap.read()
            if not ret or frame_count >= MAX_FRAMES:
                break

            results = model(frame, verbose=False)
            annotated_frame = results[0].plot()
            out.write(annotated_frame)
            frame_count += 1

            CLASS_MAP = {0: "rider", 1: "helmet", 2: "without_helmet", 3: "number_plate"}
            riders, helmets, plates, without_helmets = [], [], [], []

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

            # Save frame as image for events
            frame_filename = f"frame_{frame_count}_{unique_filename}.jpg"
            frame_path = os.path.join(UPLOAD_DIR, frame_filename)
            cv2.imwrite(frame_path, annotated_frame)

            for rider_box in riders:
                # Check if rider overlaps with any helmet
                hasHelmet = any(box_overlap(rider_box, helmet_box) > 0.1 for helmet_box in helmets)
                # If no helmet overlap, check for without_helmet
                if not hasHelmet:
                    hasHelmet = not any(box_overlap(rider_box, wh_box) > 0.1 for wh_box in without_helmets)

                # Find closest plate
                plate_text = "UNKNOWN"
                closest_plate = find_closest_plate(rider_box, plates)
                if closest_plate:
                    x1, y1, x2, y2 = closest_plate
                    crop = frame[y1:y2, x1:x2]
                    if crop.size > 0:
                        plate_text = extract_plate_text(crop)

                event_id = f"evt-{uuid.uuid4().hex[:8]}"
                event_data = {
                    "id": event_id,
                    "date": datetime.now().strftime("%Y-%m-%d"),
                    "time": datetime.now().strftime("%H:%M"),
                    "location": "kotli shaheed chock",
                    "number_plate": plate_text,
                    "has_helmet": hasHelmet,
                    "image_url": f"/uploads/{frame_filename}"
                }
                insert_event(event_data)

        cap.release()
        out.release()

        return JSONResponse(content={
            "message": "Video processed successfully",
            "processedVideoUrl": f"/uploads/detected_{unique_filename}"
        })

    except Exception as e:
        traceback.print_exc()
        return JSONResponse(status_code=500, content={"message": str(e)})

#Camera Stream 
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
