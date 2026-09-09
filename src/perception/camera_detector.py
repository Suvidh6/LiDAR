"""
src/perception/camera_detector.py
Modular 2D Camera Object Detector using YOLOv8.

Provides:
- CameraDetection structured class.
- CameraDetector class with integrated visual quality evaluation
  (Laplacian variance for sharpness/blur, mean luminance for illumination).
"""

import os
import cv2
import numpy as np
from ultralytics import YOLO

class CameraDetection:
    """Represents a single 2D camera detection."""
    def __init__(self, bbox_xyxy, confidence, class_id, class_name):
        self.bbox = [float(x) for x in bbox_xyxy]  # [x1, y1, x2, y2]
        self.confidence = float(confidence)
        self.class_id = int(class_id)
        self.class_name = str(class_name)
        self.area = (self.bbox[2] - self.bbox[0]) * (self.bbox[3] - self.bbox[1])
        self.centroid_2d = [
            (self.bbox[0] + self.bbox[2]) / 2.0,
            (self.bbox[1] + self.bbox[3]) / 2.0
        ]

    def to_dict(self):
        return {
            "bbox": self.bbox,
            "confidence": round(self.confidence, 4),
            "class_id": self.class_id,
            "class_name": self.class_name,
            "area": round(self.area, 1),
            "centroid_2d": [round(c, 1) for c in self.centroid_2d]
        }

class CameraDetector:
    """
    YOLOv8-based 2D detector that computes detection bounding boxes and
    evaluates visual image quality indicators (sharpness and illumination).
    """
    def __init__(self, model_path="yolov8n.pt", conf_thresh=0.25):
        self.conf_thresh = conf_thresh
        if not os.path.isabs(model_path) and not os.path.exists(model_path):
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            candidate = os.path.join(base_dir, model_path)
            if os.path.exists(candidate):
                model_path = candidate
        self.model = YOLO(model_path)

    @staticmethod
    def evaluate_image_quality(image_bgr):
        """
        Computes objective visual quality metrics:
        - Sharpness: Normalized Laplacian variance (detects motion blur/defocus).
        - Illumination: Deviation from nominal medium brightness (detects darkness/glare).
        """
        gray = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2GRAY)
        lap_var = float(cv2.Laplacian(gray, cv2.CV_64F).var())
        mean_brightness = float(np.mean(gray))

        sharpness_score = 1.0 / (1.0 + np.exp(-0.03 * (lap_var - 60.0)))
        illum_score = max(0.05, 1.0 - abs(mean_brightness - 128.0) / 128.0)

        return {
            "laplacian_var": round(lap_var, 2),
            "mean_brightness": round(mean_brightness, 2),
            "sharpness_score": float(np.clip(sharpness_score, 0.05, 1.0)),
            "illum_score": float(np.clip(illum_score, 0.05, 1.0))
        }

    def detect(self, image_input):
        """
        Runs object detection on image path or OpenCV BGR numpy array.
        Returns (detections, quality_metrics).
        """
        if isinstance(image_input, str):
            if not os.path.exists(image_input):
                raise FileNotFoundError(f"Image not found: {image_input}")
            img_bgr = cv2.imread(image_input)
        else:
            img_bgr = image_input

        if img_bgr is None:
            return [], {"sharpness_score": 0.05, "illum_score": 0.05, "laplacian_var": 0.0, "mean_brightness": 0.0}

        quality = self.evaluate_image_quality(img_bgr)
        results = self.model(img_bgr, conf=self.conf_thresh, verbose=False)

        detections = []
        if len(results) > 0 and results[0].boxes is not None:
            for box in results[0].boxes:
                cls_id = int(box.cls[0])
                conf = float(box.conf[0])
                cls_name = self.model.names[cls_id]
                xyxy = box.xyxy[0].cpu().numpy().tolist()
                detections.append(CameraDetection(xyxy, conf, cls_id, cls_name))

        return detections, quality
