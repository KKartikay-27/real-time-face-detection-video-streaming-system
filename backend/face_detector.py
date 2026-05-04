import io
import mediapipe as mp
from PIL import Image, ImageDraw
import numpy as np

# Initialize MediaPipe Face Detection
mp_face_detection = mp.solutions.face_detection
face_detection = mp_face_detection.FaceDetection(model_selection=0, min_detection_confidence=0.5)

def process_image(image_bytes: bytes):
    """
    Takes image bytes, detects face, draws ROI, and returns (processed_image_bytes, roi_data)
    """
    # Load image with Pillow
    image = Image.open(io.BytesIO(image_bytes)).convert('RGB')
    
    # Convert PIL image to numpy array for MediaPipe
    image_np = np.array(image)
    
    # Process the image with MediaPipe
    results = face_detection.process(image_np)
    
    roi_data = None
    if results.detections:
        # Get the first face detected (assuming only one face as per requirements)
        detection = results.detections[0]
        bboxC = detection.location_data.relative_bounding_box
        ih, iw, _ = image_np.shape
        x, y, w, h = int(bboxC.xmin * iw), int(bboxC.ymin * ih), \
                     int(bboxC.width * iw), int(bboxC.height * ih)
                     
        # Clip bounding box to image dimensions
        x, y = max(0, x), max(0, y)
        w, h = min(iw - x, w), min(ih - y, h)

        roi_data = {"x": float(x), "y": float(y), "width": float(w), "height": float(h)}
        
        # Draw ROI on the image using Pillow (without OpenCV)
        draw = ImageDraw.Draw(image)
        # Draw a red rectangle with line width 3
        draw.rectangle([x, y, x + w, y + h], outline="red", width=3)
    
    # Save the processed image to a byte buffer
    buf = io.BytesIO()
    # Save as JPEG for better transmission speed
    image.save(buf, format='JPEG')
    return buf.getvalue(), roi_data
