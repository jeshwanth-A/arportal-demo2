import React, { useState } from "react";
import axios from "axios";
import { useNavigate } from "react-router-dom";
import "./App.css"; // Import the styles

export default function LoginPage({ onSuccessLogin }) {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");

  const navigate = useNavigate();
  const BACKEND_URL = "https://arportaldemo2backend-686596926199.us-central1.run.app";

  const handleLogin = async () => {
    setError("");

    if (!username || !password) {
      setError("Username and password are required.");
      return;
    }

    try {
      // Send login request as JSON
      const response = await axios.post(`${BACKEND_URL}/login`, {
        username,
        password
      }, {
        headers: { "Content-Type": "application/json" },
      });

      console.log("Response Data:", response.data); // Debugging

      if (response.data?.token) {
        localStorage.setItem("authToken", response.data.token);
        localStorage.setItem("isAdmin", response.data.is_admin ? "true" : "false");

        onSuccessLogin();
        setTimeout(() => navigate("/upload"), 500); // Small delay before navigating
      } else {
        setError("Invalid response from server.");
      }
    } catch (err) {
      console.error("Login Error:", err);
      setError(err.response?.data?.detail || "Login failed. Try again.");
    }
  };

  return (
    <div className="container">
      <h2>Login</h2>

      <input 
        type="text" 
        value={username} 
        onChange={(e) => setUsername(e.target.value)} 
        placeholder="Enter username" 
      />

      <input 
        type="password" 
        value={password} 
        onChange={(e) => setPassword(e.target.value)} 
        placeholder="Enter password" 
      />

      <button onClick={handleLogin}>Login</button>

      {error && <p className="error">{error}</p>}
    </div>
  );
}