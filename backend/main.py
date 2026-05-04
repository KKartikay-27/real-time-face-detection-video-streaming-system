import asyncio
from fastapi import FastAPI, Depends, File, UploadFile, Request
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import io
from database import engine, Base, get_db
import models
from face_detector import process_image

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Real-Time Face Detection API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global variables to store the latest frame and ROI
latest_frame = None
latest_roi = None

@app.post("/api/video_frame")
async def receive_video_frame(file: UploadFile = File(...), db: Session = Depends(get_db)):
    """
    Endpoint 1: Receive the video feed.
    Expects an image file uploaded as form data.
    """
    global latest_frame, latest_roi
    
    image_bytes = await file.read()
    
    # Process image
    processed_bytes, roi_data = process_image(image_bytes)
    
    # Update global state for the stream
    latest_frame = processed_bytes
    latest_roi = roi_data
    
    # If face is detected, store ROI in DB
    if roi_data:
        roi_record = models.ROI(
            x=roi_data["x"],
            y=roi_data["y"],
            width=roi_data["width"],
            height=roi_data["height"]
        )
        db.add(roi_record)
        db.commit()
        
    return {"status": "success", "roi": roi_data}

async def generate_frames():
    """Generator for MJPEG streaming"""
    global latest_frame
    while True:
        if latest_frame is not None:
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + latest_frame + b'\r\n')
        await asyncio.sleep(0.033) # roughly 30fps

@app.get("/api/video_feed")
async def serve_video_feed():
    """
    Endpoint 2: Serve the video feed.
    Returns an MJPEG stream of the processed frames.
    """
    return StreamingResponse(generate_frames(), media_type="multipart/x-mixed-replace; boundary=frame")

@app.get("/api/roi")
def get_roi_history(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    Endpoint 3: Serve ROI data.
    """
    rois = db.query(models.ROI).order_by(models.ROI.timestamp.desc()).offset(skip).limit(limit).all()
    return rois
