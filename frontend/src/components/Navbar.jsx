import { Link, useNavigate } from "react-router";
import { clearToken, getStoredUser } from "../api/client";

export default function Navbar() {
  const navigate = useNavigate();
  const user = getStoredUser();

  function logout() {
    clearToken();
    navigate("/login");
  }

  return (
    <nav className="navbar">
      <Link to="/" className="brand">Amrutam Telemedicine</Link>

      <div className="nav-right">
        {user && <span>{user.email} ({user.role})</span>}
        {user ? (
          <button onClick={logout}>Logout</button>
        ) : (
          <>
            <Link to="/login">Login</Link>
            <Link to="/register">Register</Link>
          </>
        )}
      </div>
    </nav>
  );
}