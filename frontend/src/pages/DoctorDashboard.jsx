import { useEffect, useState } from "react";
import { api } from "../api/client";

export default function DoctorDashboard() {
  const [slotForm, setSlotForm] = useState({
    start_time: "2026-07-15T10:00:00",
    end_time: "2026-07-15T10:30:00",
  });

  const [consultations, setConsultations] = useState([]);
  const [selectedConsultation, setSelectedConsultation] = useState(null);

  const [prescriptionForm, setPrescriptionForm] = useState({
    name: "Paracetamol",
    dosage: "500mg",
    frequency: "Twice a day",
    duration: "3 days",
    notes: "Drink warm water and take rest.",
  });

  const [message, setMessage] = useState("");
  const [error, setError] = useState("");

  function updateSlot(e) {
    setSlotForm({ ...slotForm, [e.target.name]: e.target.value });
  }

  function updatePrescription(e) {
    setPrescriptionForm({ ...prescriptionForm, [e.target.name]: e.target.value });
  }

  async function createSlot(e) {
    e.preventDefault();
    setMessage("");
    setError("");

    try {
      await api.createAvailability(slotForm);
      setMessage("Availability slot created");
    } catch (err) {
      setError(err.message);
    }
  }

  async function loadConsultations() {
    setError("");

    try {
      const data = await api.listConsultations();
      setConsultations(data);
    } catch (err) {
      setError(err.message);
    }
  }

  async function startConsultation(id) {
    try {
      await api.startConsultation(id);
      setMessage("Consultation started");
      await loadConsultations();
    } catch (err) {
      setError(err.message);
    }
  }

  async function completeConsultation(id) {
    try {
      await api.completeConsultation(id);
      setMessage("Consultation completed");
      await loadConsultations();
    } catch (err) {
      setError(err.message);
    }
  }

  async function addPrescription(e) {
    e.preventDefault();
    setError("");
    setMessage("");

    try {
      await api.createPrescription(selectedConsultation, {
        medicines: [
          {
            name: prescriptionForm.name,
            dosage: prescriptionForm.dosage,
            frequency: prescriptionForm.frequency,
            duration: prescriptionForm.duration,
            instructions: "After food",
          },
        ],
        notes: prescriptionForm.notes,
      });

      setMessage("Prescription created");
    } catch (err) {
      setError(err.message);
    }
  }

  useEffect(() => {
    loadConsultations();
  }, []);

  return (
    <div className="page">
      <h1>Doctor Dashboard</h1>

      {message && <p className="success">{message}</p>}
      {error && <p className="error">{error}</p>}

      <section className="card">
        <h2>Create Availability Slot</h2>

        <form onSubmit={createSlot} className="form">
          <label>Start Time</label>
          <input
            name="start_time"
            value={slotForm.start_time}
            onChange={updateSlot}
          />

          <label>End Time</label>
          <input
            name="end_time"
            value={slotForm.end_time}
            onChange={updateSlot}
          />

          <button type="submit">Create Slot</button>
        </form>
      </section>

      <section className="card">
        <h2>My Consultations</h2>
        <button onClick={loadConsultations}>Refresh</button>

        <div className="grid">
          {consultations.map((c) => (
            <div key={c.id} className="mini-card">
              <p>Consultation ID: {c.id}</p>
              <p>Patient ID: {c.patient_id}</p>
              <p>Status: {c.status}</p>
              <p>Reason: {c.reason}</p>

              <button onClick={() => startConsultation(c.id)}>Start</button>
              <button onClick={() => completeConsultation(c.id)}>Complete</button>
              <button onClick={() => setSelectedConsultation(c.id)}>Add Prescription</button>
            </div>
          ))}
        </div>
      </section>

      {selectedConsultation && (
        <section className="card">
          <h2>Add Prescription for Consultation #{selectedConsultation}</h2>

          <form onSubmit={addPrescription} className="form">
            <label>Medicine Name</label>
            <input name="name" value={prescriptionForm.name} onChange={updatePrescription} />

            <label>Dosage</label>
            <input name="dosage" value={prescriptionForm.dosage} onChange={updatePrescription} />

            <label>Frequency</label>
            <input name="frequency" value={prescriptionForm.frequency} onChange={updatePrescription} />

            <label>Duration</label>
            <input name="duration" value={prescriptionForm.duration} onChange={updatePrescription} />

            <label>Notes</label>
            <textarea name="notes" value={prescriptionForm.notes} onChange={updatePrescription} />

            <button type="submit">Save Prescription</button>
          </form>
        </section>
      )}
    </div>
  );
}