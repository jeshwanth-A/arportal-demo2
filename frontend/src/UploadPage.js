import React, { useState, useEffect } from "react";
import axios from "axios";
import { useNavigate } from "react-router-dom";

export default function UploadPage() {
  const [file, setFile] = useState(null);
  const [taskId, setTaskId] = useState(null);
  const [loading, setLoading] = useState(false);
  const [progress, setProgress] = useState(0);
  const navigate = useNavigate();

  const BACKEND_URL = "https://arportaldemo2backend-686596926199.us-central1.run.app";

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

      const { task_id } = response.data;
      if (!task_id) {
        throw new Error("No task ID returned from server");
      }

      setTaskId(task_id);
      setProgress(20); // Upload complete, now processing
      pollTaskStatus(task_id, token);
    } catch (error) {
      console.error("❌ Upload failed:", error);
      alert("Upload failed. Check browser console for details.");
      setLoading(false);
    }
  };

  const pollTaskStatus = async (taskId, token) => {
    const checkStatus = async () => {
      try {
        const statusResponse = await axios.get(`${BACKEND_URL}/task-status/${taskId}`, {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        });

        const { status } = statusResponse.data;
        if (status === "SUCCEEDED") {
          setProgress(100);
          triggerDownload(taskId, token);
        } else if (status === "FAILED" || status === "CANCELED") {
          throw new Error(`Task ${status.toLowerCase()}`);
        } else {
          // Still pending, update progress and continue polling
          setProgress((prev) => Math.min(prev + 10, 90));
          setTimeout(checkStatus, 5000); // Poll every 5 seconds
        }
      } catch (error) {
        console.error("❌ Task status check failed:", error);
        alert(`Processing failed: ${error.message}. Check browser console for details.`);
        setLoading(false);
      }
    };

    checkStatus();
  };

  const triggerDownload = async (taskId, token) => {
    try {
      const downloadUrl = `${BACKEND_URL}/download/${taskId}`;
      const response = await fetch(downloadUrl, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      if (!response.ok) {
        throw new Error("Download failed");
      }

      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = url;
      link.download = `model_${taskId}.glb`; // Default filename
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);

      setLoading(false);
    } catch (error) {
      console.error("❌ Download failed:", error);
      alert("Download failed. Check browser console for details.");
      setLoading(false);
    }
  };

  return (
    <div className="upload-container">
      <h2>Upload an Image to Generate a 3D Model</h2>
      <input
        type="file"
        accept="image/*"
        onChange={(e) => setFile(e.target.files[0])}
        disabled={loading}
      />
      <button onClick={handleUpload} disabled={loading}>
        {loading ? `Processing... ${progress}%` : "Upload"}
      </button>
    </div>
  );
}