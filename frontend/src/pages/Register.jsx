import { useState } from "react";
import { api } from "../api/client";

export default function Register() {
  const [form, setForm] = useState({
    email: "",
    phone: "",
    password: "Password123",
    full_name: "",
    role: "PATIENT",
    specialization: "",
    experience_years: 0,
    consultation_fee: 500,
  });

  const [message, setMessage] = useState("");
  const [error, setError] = useState("");

  function updateField(e) {
    setForm({ ...form, [e.target.name]: e.target.value });
  }

  async function handleSubmit(e) {
    e.preventDefault();
    setMessage("");
    setError("");

    try {
      const payload = {
        email: form.email,
        phone: form.phone,
        password: form.password,
        full_name: form.full_name,
        role: form.role,
      };

      if (form.role === "DOCTOR") {
        payload.specialization = form.specialization;
        payload.experience_years = Number(form.experience_years);
        payload.consultation_fee = Number(form.consultation_fee);
      }

      await api.register(payload);
      setMessage("Registration successful. Now login.");
    } catch (err) {
      setError(err.message);
    }
  }

  return (
    <div className="page narrow">
      <h1>Register</h1>

      <form onSubmit={handleSubmit} className="card form">
        <label>Role</label>
        <select name="role" value={form.role} onChange={updateField}>
          <option value="PATIENT">Patient</option>
          <option value="DOCTOR">Doctor</option>
        </select>

        <label>Full Name</label>
        <input name="full_name" value={form.full_name} onChange={updateField} />

        <label>Email</label>
        <input name="email" value={form.email} onChange={updateField} />

        <label>Phone</label>
        <input name="phone" value={form.phone} onChange={updateField} />

        <label>Password</label>
        <input name="password" type="password" value={form.password} onChange={updateField} />

        {form.role === "DOCTOR" && (
          <>
            <label>Specialization</label>
            <input name="specialization" value={form.specialization} onChange={updateField} />

            <label>Experience Years</label>
            <input name="experience_years" type="number" value={form.experience_years} onChange={updateField} />

            <label>Consultation Fee</label>
            <input name="consultation_fee" type="number" value={form.consultation_fee} onChange={updateField} />
          </>
        )}

        {message && <p className="success">{message}</p>}
        {error && <p className="error">{error}</p>}

        <button type="submit">Register</button>
      </form>
    </div>
  );
}