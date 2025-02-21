import React from "react";
import { BrowserRouter as Router, Routes, Route, Link } from "react-router-dom";
import SignUpPage from "./SignUpPage";
import LoginPage from "./LoginPage";
import UploadPage from "./UploadPage";
import AdminPage from "./AdminPage"; // Import Admin Page

function App() {
  return (
    <Router>
      <div>
        <h1>3D Model Upload Portal</h1>

        {/* Navigation Links */}
        <nav>
          <Link to="/signup">Sign Up</Link>
          <Link to="/login">Login</Link>
          <Link to="/upload">Upload</Link>
          <Link to="/admin">Admin Panel</Link> {/* New Admin Link */}
        </nav>

        {/* Define Routes */}
        <Routes>
          <Route path="/signup" element={<SignUpPage />} />
          <Route path="/login" element={<LoginPage />} />
          <Route path="/upload" element={<UploadPage />} />
          <Route path="/admin" element={<AdminPage />} /> {/* Admin Route */}
          <Route path="/" element={<div>Welcome! Please sign up or log in.</div>} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;