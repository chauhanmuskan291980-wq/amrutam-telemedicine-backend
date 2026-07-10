import { useEffect, useState } from "react";
import { api } from "../api/client";

export default function AdminDashboard() {
  const [summary, setSummary] = useState(null);
  const [auditLogs, setAuditLogs] = useState([]);
  const [error, setError] = useState("");

  async function loadAdminData() {
    setError("");

    try {
      const summaryData = await api.adminSummary();
      const logsData = await api.auditLogs();

      setSummary(summaryData);
      setAuditLogs(logsData);
    } catch (err) {
      setError(err.message);
    }
  }

  useEffect(() => {
    loadAdminData();
  }, []);

  return (
    <div className="page">
      <h1>Admin Dashboard</h1>

      {error && <p className="error">{error}</p>}

      <section className="card">
        <h2>Analytics Summary</h2>

        {summary && (
          <div className="grid">
            <div className="stat">Users: {summary.total_users}</div>
            <div className="stat">Doctors: {summary.total_doctors}</div>
            <div className="stat">Consultations: {summary.total_consultations}</div>
            <div className="stat">Prescriptions: {summary.total_prescriptions}</div>
            <div className="stat">Payments: {summary.total_payments}</div>
          </div>
        )}
      </section>

      <section className="card">
        <h2>Audit Logs</h2>

        <button onClick={loadAdminData}>Refresh</button>

        <div className="table-wrapper">
          <table>
            <thead>
              <tr>
                <th>ID</th>
                <th>User ID</th>
                <th>Action</th>
                <th>Resource</th>
                <th>Created At</th>
              </tr>
            </thead>
            <tbody>
              {auditLogs.map((log) => (
                <tr key={log.id}>
                  <td>{log.id}</td>
                  <td>{log.user_id}</td>
                  <td>{log.action}</td>
                  <td>{log.resource_type}</td>
                  <td>{log.created_at}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>
    </div>
  );
}