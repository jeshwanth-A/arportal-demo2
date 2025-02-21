import React, { useState } from "react";
import axios from "axios";

export default function SignUpPage() {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");

  const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || "http://localhost:8007";

  const handleSignUp = async () => {
    setError("");
    setMessage("");

    try {
      const response = await axios.post(`${BACKEND_URL}/register`, {
        username,
        password,
      }, {
        headers: { "Content-Type": "application/x-www-form-urlencoded" },
      });

      setMessage(response.data.message);
    } catch (err) {
      setError(err.response?.data?.detail || "Signup failed. Try again.");
    }
  };

  return (
    <div className="signup-container">
      <h2>Sign Up</h2>
      <div>
        <label>Username: </label>
        <input
          value={username}
          onChange={(e) => setUsername(e.target.value)}
          placeholder="Enter username"
        />
      </div>

      <div>
        <label>Password: </label>
        <input
          type="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          placeholder="Enter password"
        />
      </div>

      <button onClick={handleSignUp}>Sign Up</button>

      {message && <p style={{ color: "green" }}>{message}</p>}
      {error && <p style={{ color: "red" }}>{error}</p>}
    </div>
  );
}