from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_get_roi_history():
    response = client.get("/api/roi")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_video_feed_endpoint():
    # Because it's a streaming response, we can just check if the endpoint exists and returns 200 OK
    with client.stream("GET", "/api/video_feed") as response:
        assert response.status_code == 200
        assert response.headers["content-type"] == "multipart/x-mixed-replace; boundary=frame"

def test_video_frame_no_file():
    # Posting without a file should return 422 Unprocessable Entity
    response = client.post("/api/video_frame")
    assert response.status_code == 422
