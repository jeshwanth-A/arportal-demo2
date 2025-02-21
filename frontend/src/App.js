import React, { useState, useEffect } from "react";
import { BrowserRouter as Router, Routes, Route, Link, Navigate } from "react-router-dom";
import SignUpPage from "./SignUpPage";
import LoginPage from "./LoginPage";
import UploadPage from "./UploadPage";
import AdminPage from "./AdminPage";
import "./App.css"; // Import the styles

function App() {
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [isAdmin, setIsAdmin] = useState(false);

  useEffect(() => {
    const token = localStorage.getItem("authToken");
    const adminStatus = localStorage.getItem("isAdmin") === "true";

    setIsLoggedIn(!!token);
    setIsAdmin(adminStatus);
  }, []);

  const handleSuccessfulLogin = () => {
    setIsLoggedIn(true);
    setIsAdmin(localStorage.getItem("isAdmin") === "true");
  };

  const handleLogout = () => {
    localStorage.removeItem("authToken");
    localStorage.removeItem("isAdmin");
    setIsLoggedIn(false);
    setIsAdmin(false);
  };

  return (
    <Router>
      <div>
        <nav>
          {!isLoggedIn && <Link to="/signup">Sign Up</Link>}
          {!isLoggedIn && <Link to="/login">Login</Link>}
          {isLoggedIn && <Link to="/upload">Upload</Link>}
          {isAdmin && <Link to="/admin">Admin Panel</Link>}
          {isLoggedIn && <button onClick={handleLogout}>Logout</button>}
        </nav>

        <div className="container">
          <Routes>
            <Route path="/signup" element={<SignUpPage />} />
            <Route path="/login" element={<LoginPage onSuccessLogin={handleSuccessfulLogin} />} />
            <Route path="/upload" element={isLoggedIn ? <UploadPage /> : <Navigate to="/login" />} />
            <Route path="/admin" element={isAdmin ? <AdminPage /> : <Navigate to="/" />} />
            <Route path="/" element={<div>Welcome! Please sign up or log in.</div>} />
          </Routes>
        </div>
      </div>
    </Router>
  );
}

export default App;