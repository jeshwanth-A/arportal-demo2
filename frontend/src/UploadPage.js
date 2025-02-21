import React, { useState } from "react";
import axios from "axios";

export default function UploadPage() {
  const [file, setFile] = useState(null);
  const [username, setUsername] = useState("guest");
  const [modelUrl, setModelUrl] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState("");

  // Get backend URL from environment variables
  const backendUrl = process.env.REACT_APP_API_URL || "http://localhost:8003";

  const handleUpload = async (e) => {
    e.preventDefault();
    setError("");
    setModelUrl("");
    
    if (!file) {
      setError("Please select an image file");
      return;
    }

    setIsLoading(true);
    
    try {
      const formData = new FormData();
      formData.append("file", file);
      formData.append("username", username);

      const response = await axios.post(`${backendUrl}/upload`, formData, {
        headers: {
          "Content-Type": "multipart/form-data",
        },
      });

      if (response.data.error) {
        setError(response.data.error);
      } else {
        setModelUrl(response.data.model_file);
      }
    } catch (error) {
      console.error("Upload failed:", error);
      setError(error.response?.data?.details || "Failed to upload file");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="upload-container">
      <h2>Generate 3D Model from Image..</h2>
      <form onSubmit={handleUpload}>
        <div className="form-group">
          <label htmlFor="username">Username:</label>
          <input
            type="text"
            id="username"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            placeholder="Enter your username"
          />
        </div>

        <div className="form-group">
          <label htmlFor="file-upload">Select Image:</label>
          <input
            id="file-upload"
            type="file"
            accept="image/*"
            onChange={(e) => setFile(e.target.files[0])}
          />
        </div>

        <button 
          type="submit" 
          disabled={isLoading}
          className={isLoading ? "loading" : ""}
        >
          {isLoading ? "Processing..." : "Generate 3D Model"}
        </button>
      </form>

      {error && <div className="error-message">{error}</div>}

      {modelUrl && (
        <div className="result-container">
          <h3>3D Model Generated Successfully!</h3>
          <div className="download-section">
            <p>Your model is ready for download:</p>
            <a
              href={modelUrl}
              download
              className="download-link"
              target="_blank"
              rel="noopener noreferrer"
            >
              Download GLB File
            </a>
          </div>
        </div>
      )}
    </div>
  );
}