import { useState } from "react";
import { useNavigate } from "react-router";
import { api, setStoredUser, setToken } from "../api/client";

export default function Login() {
  const navigate = useNavigate();

  const [form, setForm] = useState({
    email: "patient@example.com",
    password: "Password123",
  });

  const [error, setError] = useState("");

  function updateField(e) {
    setForm({ ...form, [e.target.name]: e.target.value });
  }

  async function handleSubmit(e) {
    e.preventDefault();
    setError("");

    try {
      const tokenData = await api.login(form);
      setToken(tokenData.access_token);

      const user = await api.me();
      setStoredUser(user);

      if (user.role === "PATIENT") navigate("/patient");
      else if (user.role === "DOCTOR") navigate("/doctor");
      else if (user.role === "ADMIN") navigate("/admin");
      else navigate("/");
    } catch (err) {
      setError(err.message);
    }
  }

  return (
    <div className="page narrow">
      <h1>Login</h1>

      <form onSubmit={handleSubmit} className="card form">
        <label>Email</label>
        <input name="email" value={form.email} onChange={updateField} />

        <label>Password</label>
        <input name="password" type="password" value={form.password} onChange={updateField} />

        {error && <p className="error">{error}</p>}

        <button type="submit">Login</button>
      </form>

      <div className="hint">
        <p>Patient: patient@example.com / Password123</p>
        <p>Doctor: doctor@example.com / Password123</p>
        <p>Admin: admin@example.com / Password123</p>
      </div>
    </div>
  );
}