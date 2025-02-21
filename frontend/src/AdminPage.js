import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import axios from "axios";

export default function AdminPage() {
  const [users, setUsers] = useState([]);
  const [error, setError] = useState("");
  const navigate = useNavigate();

  const BACKEND_URL = "https://arportaldemo2backend-686596926199.us-central1.run.app";

  // Check if user is admin
  const isAdmin = localStorage.getItem("isAdmin") === "true";

  useEffect(() => {
    if (!isAdmin) {
      navigate("/"); // Redirect non-admin users to home
      return;
    }

    const fetchUsers = async () => {
      try {
        const response = await axios.get(`${BACKEND_URL}/all-users`);
        setUsers(Object.entries(response.data.users));
      } catch (err) {
        console.error("❌ Fetch Users Error:", err.response || err.message);
        setError("Failed to fetch users.");
      }
    };

    fetchUsers();
  }, [isAdmin, navigate]);

  return (
    <div className="admin-container">
      <h2>All Registered Users</h2>
      {error && <p style={{ color: "red" }}>{error}</p>}
      
      <table border="1">
        <thead>
          <tr>
            <th>Username</th>
            <th>Password</th>
          </tr>
        </thead>
        <tbody>
          {users.length === 0 ? (
            <tr><td colSpan="2">No users found.</td></tr>
          ) : (
            users.map(([username, data], index) => (
              <tr key={index}>
                <td>{username}</td>
                <td>{data.password}</td>
              </tr>
            ))
          )}
        </tbody>
      </table>
    </div>
  );
}