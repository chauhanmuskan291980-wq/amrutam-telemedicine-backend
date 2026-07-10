import { Link } from "react-router";
import { getStoredUser } from "../api/client";

export default function Home() {
  const user = getStoredUser();

  return (
    <div className="page hero">
      <h1>Amrutam Telemedicine System</h1>
      <p>Frontend preview connected with FastAPI backend.</p>

      {!user && (
        <div className="row center">
          <Link className="button-link" to="/login">Login</Link>
          <Link className="button-link secondary" to="/register">Register</Link>
        </div>
      )}

      {user?.role === "PATIENT" && <Link className="button-link" to="/patient">Go to Patient Dashboard</Link>}
      {user?.role === "DOCTOR" && <Link className="button-link" to="/doctor">Go to Doctor Dashboard</Link>}
      {user?.role === "ADMIN" && <Link className="button-link" to="/admin">Go to Admin Dashboard</Link>}
    </div>
  );
}