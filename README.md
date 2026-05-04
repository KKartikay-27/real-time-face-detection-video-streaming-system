# Real-Time Face Detection Streaming System

A containerized application that captures a video feed, detects faces in real-time, draws an axis-aligned bounding box (ROI) without using OpenCV, and stores the ROI data in a PostgreSQL database. 

## Features
- **Frontend (React)**: Captures user webcam, sends frames to backend, and streams the processed video back. Also displays recent ROI history.
- **Backend (FastAPI)**: Processes frames using `MediaPipe` for face detection and `Pillow` (PIL) for drawing the ROI. Exposes a Multipart HTTP stream (MJPEG) for real-time video serving.
- **Database (PostgreSQL)**: Stores every face detection event (`timestamp`, `x`, `y`, `width`, `height`).

## Requirements
- Docker
- Docker Compose

## Quick Start (Run in 5 minutes)

1. **Clone/Navigate** to the project directory:
   ```bash
   cd Face-Detection
   ```

2. **Run Docker Compose**:
   ```bash
   docker compose up --build
   ```

3. **Access the Application**:
   - Open your browser and navigate to `http://localhost:8080`
   - Allow webcam permissions.
   - Click "Start Webcam".
   - You will see the original webcam feed on the left, and the processed feed with a red bounding box (ROI) on the right.
   - The ROI panel at the bottom will automatically update with data points from the PostgreSQL database.

## Architecture & API Design
- **`POST /api/video_frame`**: Endpoint to receive the raw video frames from the frontend.
- **`GET /api/video_feed`**: Endpoint to serve the processed video feed using MJPEG streaming.
- **`GET /api/roi`**: Endpoint to serve historical ROI data from the database.

## Technologies Used
- React.js (Vite)
- FastAPI (Python)
- MediaPipe (Face Detection)
- Pillow (Image manipulation without OpenCV)
- PostgreSQL & SQLAlchemy
