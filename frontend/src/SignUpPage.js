import React, { useState } from "react";
import axios from "axios";

export default function SignUpPage() {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");

  // Replace this with your actual Cloud Run backend URL
  const BACKEND_URL = "https://arportaldemo2backend-686596926199.us-central1.run.app";

  const handleSignUp = async () => {
    setError("");
    setMessage("");

    // Optional: Check if username/password are filled
    if (!username || !password) {
      setError("Username and password are required.");
      return;
    }

    // Debug log: shows in the browser console (F12 > Console)
    console.log("📤 Sending signup request to:", `${BACKEND_URL}/register`);

    try {
      // Use URLSearchParams for form-encoded data
      const formData = new URLSearchParams();
      formData.append("username", username);
      formData.append("password", password);

      // POST request to your FastAPI backend
      const response = await axios.post(`${BACKEND_URL}/register`, formData, {
        headers: { "Content-Type": "application/x-www-form-urlencoded" },
      });

      // Debug log: success response
      console.log("✅ Signup successful:", response.data);

      // Show success message from the backend
      setMessage(response.data.message);
    } catch (err) {
      // Debug log: error response
      console.error("❌ Signup Error:", err.response || err.message);

      // Show error detail from the backend or a default message
      setError(err.response?.data?.detail || "Signup failed. Try again.");
    }
  };

  return (
    <div className="signup-container">
      <h2>Sign Up</h2>
      
      <div style={{ marginBottom: "1rem" }}>
        <label>Username: </label>
        <input
          type="text"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
          placeholder="Enter username"
        />
      </div>
      
      <div style={{ marginBottom: "1rem" }}>
        <label>Password: </label>
        <input
          type="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          placeholder="Enter password"
        />
      </div>
      
      <button onClick={handleSignUp}>Sign Up</button>

      {message && <p style={{ color: "green", marginTop: "1rem" }}>{message}</p>}
      {error && <p style={{ color: "red", marginTop: "1rem" }}>{error}</p>}
    </div>
  );
}