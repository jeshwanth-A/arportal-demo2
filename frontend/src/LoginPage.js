// LoginPage.js
import React, { useState } from "react";
import axios from "axios";

function LoginPage({ onSuccessLogin }) {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");

  const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || "http://localhost:8007";

  const handleLogin = async () => {
    setError(""); // Clear any previous error
    try {
      const response = await axios.post(`${BACKEND_URL}/login`, {
        username,
        password,
      });
      // Store the token in localStorage
      localStorage.setItem("authToken", response.data.token);
      
      // Notify the parent (App.js) that login was successful
      onSuccessLogin();
    } catch (err) {
      // Display error from server or default
      setError(err.response?.data?.detail || "Login failed, please try again.");
    }
  };

  return (
    <div style={{ maxWidth: "400px", margin: "0 auto" }}>
      <h2>Login</h2>
      <div style={{ marginBottom: "1rem" }}>
        <label>Username: </label>
        <input
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

      {error && <p style={{ color: "red" }}>{error}</p>}
    </div>
  );
}

export default LoginPage;