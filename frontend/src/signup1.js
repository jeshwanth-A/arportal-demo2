import React, { useState } from "react";
import axios from "axios";
import "./App.css"; // Import the styles

export default function SignUpPage() {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");

  const BACKEND_URL = "https://arportaldemo2backend-686596926199.us-central1.run.app";

  const handleSignUp = async () => {
    setError("");
    setMessage("");

    if (!username || !password) {
      setError("Username and password are required.");
      return;
    }

    try {
      // Send signup request as JSON
      const response = await axios.post(`${BACKEND_URL}/register`, {
        username,
        password
      }, {
        headers: { "Content-Type": "application/json" },
      });

      console.log("Signup Response:", response.data); // Debugging

      if (response.data?.message) {
        setMessage(response.data.message);
      } else {
        setError("Unexpected response from server.");
      }
    } catch (err) {
      console.error("Signup Error:", err);
      setError(err.response?.data?.detail || "Signup failed. Try again.");
    }
  };

  return (
    <div className="container">
      <h2>Sign Up</h2>

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

      <button onClick={handleSignUp}>Sign Up</button>

      {message && <p className="success">{message}</p>}
      {error && <p className="error">{error}</p>}
    </div>
  );
}