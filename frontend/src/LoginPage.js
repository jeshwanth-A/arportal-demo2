import React, { useState } from "react";
import axios from "axios";

export default function LoginPage() {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");

  const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || "http://localhost:8007";

  const handleLogin = async () => {
    try {
      const response = await axios.post(`${BACKEND_URL}/login`, {
        username,
        password,
      });
      const token = response.data.token;
      if (token) {
        localStorage.setItem("authToken", token);
        alert("Login successful! Token stored in localStorage.");
        // Optionally redirect to upload page
      } else {
        setError("No token found in response.");
      }
    } catch (err) {
      setError(err.response?.data?.detail || "Login failed.");
    }
  };

  return (
    <div className="login-container">
      <h2>Login</h2>
      <div>
        <label>Username: </label>
        <input value={username} onChange={(e) => setUsername(e.target.value)} />
      </div>

      <div>
        <label>Password: </label>
        <input 
          type="password" 
          value={password} 
          onChange={(e) => setPassword(e.target.value)} 
        />
      </div>

      <button onClick={handleLogin}>Login</button>
      
      {error && <p style={{ color: "red" }}>{error}</p>}
    </div>
  );
}