import React, { useState } from "react";

function SignUpPage() {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [message, setMessage] = useState("");

  const handleSubmit = async (e) => {
    e.preventDefault();

    // Create form data for the backend
    const formData = new FormData();
    formData.append("username", username);
    formData.append("password", password);

    try {
      const response = await fetch("http://localhost:8080/register", {
        method: "POST",
        body: formData, // Send as form-data, not JSON
      });

      const data = await response.json();
      console.log("Response:", data); // Debug: check what comes back

      if (response.ok && data.message === "User registered successfully") {
        setMessage("Signup successful!");
        // Optionally redirect or clear form
        setUsername("");
        setPassword("");
      } else {
        setMessage("Signup failed. Try again.");
      }
    } catch (error) {
      console.error("Error:", error); // Debug: log any network errors
      setMessage("Signup failed. Try again.");
    }
  };

  return (
    <div>
      <h2>Sign Up</h2>
      <form onSubmit={handleSubmit}>
        <input
          type="text"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
          placeholder="Username"
          required
        />
        <input
          type="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          placeholder="Password"
          required
        />
        <button type="submit">Sign Up</button>
      </form>
      <p>{message}</p>
    </div>
  );
}

export default SignUpPage;