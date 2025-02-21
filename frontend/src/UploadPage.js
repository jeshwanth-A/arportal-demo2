import React, { useState } from "react";
import axios from "axios";

export default function UploadPage() {
  const [file, setFile] = useState(null);
  const [modelUrl, setModelUrl] = useState("");
  const [loading, setLoading] = useState(false);
  const [progress, setProgress] = useState(0);

  const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || "http://localhost:8007";

  const handleUpload = async () => {
    if (!file) {
      alert("Please select an image");
      return;
    }

    const formData = new FormData();
    formData.append("file", file);

    try {
      setLoading(true);
      setProgress(10);

      console.log(`📤 Uploading file to: ${BACKEND_URL}/upload`);

      const response = await axios.post(`${BACKEND_URL}/upload`, formData, {
        headers: { "Content-Type": "multipart/form-data" },
        onUploadProgress: (progressEvent) => {
          const percent = Math.round((progressEvent.loaded * 100) / progressEvent.total);
          setProgress(percent);
        },
      });

      console.log("✅ Upload response:", response.data);

      if (response.data.download_url) {
        setModelUrl(response.data.download_url);
        setProgress(100);
        setLoading(false);
        console.log("🎉 3D Model Ready:", response.data.download_url);
      } else {
        alert("Upload successful, but no model file found in response.");
        setLoading(false);
      }
    } catch (error) {
      console.error("❌ Upload failed:", error);
      alert("Upload failed. Check browser console for details.");
      setLoading(false);
    }
  };

  return (
    <div className="upload-container">
      <h2>Upload an Image to Generate a 3D Model</h2>
      <input type="file" accept="image/*" onChange={(e) => setFile(e.target.files[0])} />
      <button onClick={handleUpload} disabled={loading}>{loading ? "Processing..." : "Upload"}</button>

      {loading && <p>Generating 3D Model...</p>}
      {modelUrl && <p>✅ <a href={modelUrl} target="_blank" rel="noopener noreferrer">Download Here</a></p>}
    </div>
  );
}