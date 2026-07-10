import { useEffect, useState } from "react";
import { api } from "../api/client";

export default function PatientDashboard() {
  const [specialization, setSpecialization] = useState("Ayurveda");
  const [doctors, setDoctors] = useState([]);
  const [slots, setSlots] = useState([]);
  const [consultations, setConsultations] = useState([]);
  const [selectedDoctor, setSelectedDoctor] = useState(null);
  const [prescription, setPrescription] = useState(null);
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");

  async function loadDoctors() {
    setError("");
    try {
      const data = await api.searchDoctors(specialization);
      setDoctors(data);
    } catch (err) {
      setError(err.message);
    }
  }

  async function loadSlots(doctorId) {
    setSelectedDoctor(doctorId);
    setPrescription(null);
    setError("");

    try {
      const data = await api.getDoctorSlots(doctorId);
      setSlots(data);
    } catch (err) {
      setError(err.message);
    }
  }

  async function bookSlot(slotId) {
    setMessage("");
    setError("");

    try {
      await api.bookConsultation({
        slot_id: slotId,
        reason: "General consultation from frontend",
      });

      setMessage("Consultation booked successfully");
      await loadSlots(selectedDoctor);
      await loadConsultations();
    } catch (err) {
      setError(err.message);
    }
  }

  async function loadConsultations() {
    try {
      const data = await api.listConsultations();
      setConsultations(data);
    } catch (err) {
      setError(err.message);
    }
  }

  async function viewPrescription(consultationId) {
    setPrescription(null);
    setError("");

    try {
      const data = await api.getPrescription(consultationId);
      setPrescription(data);
    } catch (err) {
      setError(err.message);
    }
  }

  useEffect(() => {
    loadDoctors();
    loadConsultations();
  }, []);

  return (
    <div className="page">
      <h1>Patient Dashboard</h1>

      {message && <p className="success">{message}</p>}
      {error && <p className="error">{error}</p>}

      <section className="card">
        <h2>Find Doctors</h2>

        <div className="row">
          <input
            value={specialization}
            onChange={(e) => setSpecialization(e.target.value)}
            placeholder="Specialization"
          />
          <button onClick={loadDoctors}>Search</button>
        </div>

        <div className="grid">
          {doctors.map((doctor) => (
            <div key={doctor.id} className="mini-card">
              <h3>Doctor #{doctor.id}</h3>
              <p>Specialization: {doctor.specialization}</p>
              <p>Experience: {doctor.experience_years} years</p>
              <p>Fee: ₹{doctor.consultation_fee}</p>
              <button onClick={() => loadSlots(doctor.id)}>View Slots</button>
            </div>
          ))}
        </div>
      </section>

      <section className="card">
        <h2>Available Slots</h2>

        {slots.length === 0 && <p>No slots selected or available.</p>}

        <div className="grid">
          {slots.map((slot) => (
            <div key={slot.id} className="mini-card">
              <p>Slot ID: {slot.id}</p>
              <p>Start: {slot.start_time}</p>
              <p>End: {slot.end_time}</p>
              <p>Status: {slot.status}</p>
              <button onClick={() => bookSlot(slot.id)}>Book Slot</button>
            </div>
          ))}
        </div>
      </section>

      <section className="card">
        <h2>My Consultations</h2>

        <div className="grid">
          {consultations.map((c) => (
            <div key={c.id} className="mini-card">
              <p>Consultation ID: {c.id}</p>
              <p>Status: {c.status}</p>
              <p>Doctor ID: {c.doctor_id}</p>
              <p>Reason: {c.reason}</p>
              <button onClick={() => viewPrescription(c.id)}>View Prescription</button>
            </div>
          ))}
        </div>
      </section>

      {prescription && (
        <section className="card">
          <h2>Prescription</h2>
          <p>Notes: {prescription.notes}</p>

          {prescription.medicines.map((m, index) => (
            <div key={index} className="mini-card">
              <p>Name: {m.name}</p>
              <p>Dosage: {m.dosage}</p>
              <p>Frequency: {m.frequency}</p>
              <p>Duration: {m.duration}</p>
            </div>
          ))}
        </section>
      )}
    </div>
  );
}