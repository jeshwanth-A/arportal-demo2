import React, { useState, useEffect } from "react";
import { BrowserRouter as Router, Routes, Route, Link, Navigate } from "react-router-dom";
import SignUpPage from "./SignUpPage";
import LoginPage from "./LoginPage";
import UploadPage from "./UploadPage";
import AdminPage from "./AdminPage";

function App() {
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [isAdmin, setIsAdmin] = useState(false);

  useEffect(() => {
    // Get login state from localStorage
    const token = localStorage.getItem("authToken");
    const adminStatus = localStorage.getItem("isAdmin") === "true";

    setIsLoggedIn(!!token); // If token exists, user is logged in
    setIsAdmin(adminStatus); // If isAdmin = true, user is admin
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
        <h1>3D Model Upload Portal</h1>

        <nav>
          {!isLoggedIn && <Link to="/signup">Sign Up</Link>}
          {!isLoggedIn && <Link to="/login">Login</Link>}
          {isLoggedIn && <Link to="/upload">Upload</Link>}
          {isAdmin && <Link to="/admin">Admin Panel</Link>} {/* Only admin sees this */}
          {isLoggedIn && <button onClick={handleLogout}>Logout</button>}
        </nav>

        <Routes>
          <Route path="/signup" element={<SignUpPage />} />
          <Route path="/login" element={<LoginPage onSuccessLogin={handleSuccessfulLogin} />} />
          <Route path="/upload" element={isLoggedIn ? <UploadPage /> : <Navigate to="/login" />} />
          <Route path="/admin" element={isAdmin ? <AdminPage /> : <Navigate to="/" />} />
          <Route path="/" element={<div>Welcome! Please sign up or log in.</div>} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;