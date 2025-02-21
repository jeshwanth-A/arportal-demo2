import React, { useState } from "react";
import axios from "axios";
import { useNavigate } from "react-router-dom";

export default function LoginPage({ onSuccessLogin }) {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");

  const navigate = useNavigate();
  const BACKEND_URL = "https://arportaldemo2backend-686596926199.us-central1.run.app"; // Update if needed

  const handleLogin = async () => {
    setError("");

    if (!username || !password) {
      setError("Username and password are required.");
      return;
    }

    console.log("📤 Sending login request to:", `${BACKEND_URL}/login`);

    try {
      const formData = new URLSearchParams();
      formData.append("username", username);
      formData.append("password", password);

      const response = await axios.post(`${BACKEND_URL}/login`, formData, {
        headers: { "Content-Type": "application/x-www-form-urlencoded" },
      });

      console.log("✅ Login successful:", response.data);

      // Save token to local storage
      localStorage.setItem("authToken", response.data.token);

      // Notify App.js that login is successful
      onSuccessLogin();

      // Redirect to Upload Page
      navigate("/upload");
    } catch (err) {
      console.error("❌ Login Error:", err.response || err.message);
      setError(err.response?.data?.detail || "Login failed. Try again.");
    }
  };

  return (
    <div className="login-container">
      <h2>Login</h2>
      
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
      
      <button onClick={handleLogin}>Login</button>

      {error && <p style={{ color: "red", marginTop: "1rem" }}>{error}</p>}
    </div>
  );
}