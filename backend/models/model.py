from ultralytics import YOLO
from pathlib import Path

# safer cross-platform path handling
model_path = Path(r"F:\FYP\HelmitUI\HelmetEye\backend\models\yolo11s.pt")
model = YOLO(str(model_path))
