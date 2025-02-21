import React, { useState, useEffect } from "react";
import axios from "axios";

export default function AdminPage() {
  const [users, setUsers] = useState([]);
  const [error, setError] = useState("");

  const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || "http://localhost:8007";

  useEffect(() => {
    const fetchUsers = async () => {
      try {
        const response = await axios.get(`${BACKEND_URL}/all-users`);
        setUsers(Object.entries(response.data.users)); // Convert object to array
      } catch (err) {
        setError("Failed to fetch users.");
      }
    };

    fetchUsers();
  }, []);

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
                <td>{data.password}</td> {/* Displays the password */}
              </tr>
            ))
          )}
        </tbody>
      </table>
    </div>
  );
}