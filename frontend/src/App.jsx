import { useEffect, useRef, useState } from 'react'
import './App.css'

function App() {
  const videoRef = useRef(null)
  const canvasRef = useRef(null)
  const [rois, setRois] = useState([])
  const [isStreaming, setIsStreaming] = useState(false)

  // Start webcam and frame capturing
  const startWebcam = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ video: true })
      if (videoRef.current) {
        videoRef.current.srcObject = stream
        videoRef.current.play()
        setIsStreaming(true)
      }
    } catch (err) {
      console.error("Error accessing webcam: ", err)
    }
  }

  // Capture frame and send to backend
  useEffect(() => {
    if (!isStreaming) return

    const interval = setInterval(() => {
      if (videoRef.current && canvasRef.current) {
        const video = videoRef.current
        const canvas = canvasRef.current
        const context = canvas.getContext('2d')
        
        // Set canvas dimensions to match video
        if (canvas.width !== video.videoWidth) {
          canvas.width = video.videoWidth
          canvas.height = video.videoHeight
        }
        
        // Draw video frame to canvas
        context.drawImage(video, 0, 0, canvas.width, canvas.height)
        
        // Convert to blob and send
        canvas.toBlob(blob => {
          if (blob) {
            const formData = new FormData()
            formData.append('file', blob, 'frame.jpg')
            
            fetch('http://localhost:8000/api/video_frame', {
              method: 'POST',
              body: formData
            }).catch(err => console.error("Error sending frame:", err))
          }
        }, 'image/jpeg', 0.7)
      }
    }, 100) // 10 fps to avoid overloading the backend

    return () => clearInterval(interval)
  }, [isStreaming])

  // Fetch ROI history periodically
  useEffect(() => {
    const fetchROI = () => {
      fetch('http://localhost:8000/api/roi?limit=10')
        .then(res => res.json())
        .then(data => setRois(data))
        .catch(err => console.error("Error fetching ROI:", err))
    }

    const interval = setInterval(fetchROI, 1000)
    return () => clearInterval(interval)
  }, [])

  return (
    <div className="App">
      <h1>Real-Time Face Detection</h1>
      
      {!isStreaming && (
        <button onClick={startWebcam} className="start-btn">Start Webcam</button>
      )}

      <div className="video-container">
        <div className="video-box">
          <h3>Your Webcam</h3>
          {/* Hidden video element used to capture frames */}
          <video ref={videoRef} style={{ display: isStreaming ? 'block' : 'none' }} muted />
          {/* Hidden canvas to extract image blobs */}
          <canvas ref={canvasRef} style={{ display: 'none' }} />
        </div>
        
        <div className="video-box">
          <h3>Processed Stream</h3>
          {/* MJPEG Stream from the backend */}
          {isStreaming ? (
            <img 
              src="http://localhost:8000/api/video_feed" 
              alt="Processed video feed" 
              className="processed-stream"
            />
          ) : (
            <div className="placeholder">Start webcam to see stream</div>
          )}
        </div>
      </div>

      <div className="roi-panel">
        <h3>Recent Regions of Interest (ROI)</h3>
        <table>
          <thead>
            <tr>
              <th>Time</th>
              <th>X</th>
              <th>Y</th>
              <th>Width</th>
              <th>Height</th>
            </tr>
          </thead>
          <tbody>
            {rois.map((roi, index) => (
              <tr key={index}>
                <td>{new Date(roi.timestamp).toLocaleTimeString()}</td>
                <td>{roi.x.toFixed(2)}</td>
                <td>{roi.y.toFixed(2)}</td>
                <td>{roi.width.toFixed(2)}</td>
                <td>{roi.height.toFixed(2)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}

export default App
