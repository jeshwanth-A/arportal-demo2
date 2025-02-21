import React, { useState, useEffect } from "react";
import axios from "axios";
import { useNavigate } from "react-router-dom";

export default function UploadPage() {
  const [file, setFile] = useState(null);
  const [modelUrl, setModelUrl] = useState("");
  const [loading, setLoading] = useState(false);
  const [progress, setProgress] = useState(0);
  const navigate = useNavigate();

  const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || "http://localhost:8007";

  useEffect(() => {
    // Redirect to login if no token is found
    if (!localStorage.getItem("authToken")) {
      navigate("/login");
    }
  }, [navigate]);

  const handleUpload = async () => {
    if (!file) {
      alert("Please select an image");
      return;
    }

    const token = localStorage.getItem("authToken");
    if (!token) {
      alert("You must be logged in to upload.");
      navigate("/login");
      return;
    }

    const formData = new FormData();
    formData.append("file", file);

    try {
      setLoading(true);
      setProgress(10);

      const response = await axios.post(`${BACKEND_URL}/upload`, formData, {
        headers: {
          "Content-Type": "multipart/form-data",
          Authorization: `Bearer ${token}`,
        },
        onUploadProgress: (progressEvent) => {
          const percent = Math.round((progressEvent.loaded * 100) / progressEvent.total);
          setProgress(percent);
        },
      });

      if (response.data.model_file) {
        setModelUrl(response.data.model_file);
        setProgress(100);
      } else {
        alert("Upload successful, but no model file found in response.");
      }
    } catch (error) {
      console.error("❌ Upload failed:", error);
      alert("Upload failed. Check browser console for details.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="upload-container">
      <h2>Upload an Image to Generate a 3D Model</h2>
      <input type="file" accept="image/*" onChange={(e) => setFile(e.target.files[0])} />
      <button onClick={handleUpload} disabled={loading}>
        {loading ? `Processing... ${progress}%` : "Upload"}
      </button>

      {modelUrl && (
        <p>✅ 
          <a href={modelUrl} target="_blank" rel="noopener noreferrer">
            Download Here
          </a>
        </p>
      )}
    </div>
  );
}