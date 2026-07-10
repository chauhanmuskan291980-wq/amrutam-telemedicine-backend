const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000";

export function getToken() {
  return localStorage.getItem("access_token");
}

export function setToken(token) {
  localStorage.setItem("access_token", token);
}

export function clearToken() {
  localStorage.removeItem("access_token");
  localStorage.removeItem("user");
}

export function getStoredUser() {
  const user = localStorage.getItem("user");
  return user ? JSON.parse(user) : null;
}

export function setStoredUser(user) {
  localStorage.setItem("user", JSON.stringify(user));
}

async function apiFetch(path, options = {}) {
  const token = getToken();

  const headers = {
    "Content-Type": "application/json",
    ...(options.headers || {}),
  };

  if (token) {
    headers.Authorization = `Bearer ${token}`;
  }

  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...options,
    headers,
  });

  const contentType = response.headers.get("content-type");
  const data = contentType?.includes("application/json")
    ? await response.json()
    : await response.text();

  if (!response.ok) {
    const message = data?.detail || data || "Something went wrong";
    throw new Error(typeof message === "string" ? message : JSON.stringify(message));
  }

  return data;
}

export const api = {
  register: (payload) =>
    apiFetch("/auth/register", {
      method: "POST",
      body: JSON.stringify(payload),
    }),

  login: (payload) =>
    apiFetch("/auth/login", {
      method: "POST",
      body: JSON.stringify(payload),
    }),

  me: () => apiFetch("/auth/me"),

  searchDoctors: (specialization = "") =>
    apiFetch(`/doctors?specialization=${encodeURIComponent(specialization)}&min_rating=0&limit=20&offset=0`),

  getDoctorSlots: (doctorId) => apiFetch(`/doctors/${doctorId}/slots`),

  createAvailability: (payload) =>
    apiFetch("/doctors/availability", {
      method: "POST",
      body: JSON.stringify(payload),
    }),

  bookConsultation: (payload) =>
    apiFetch("/consultations/book", {
      method: "POST",
      headers: {
        "Idempotency-Key": `booking-${Date.now()}`,
      },
      body: JSON.stringify(payload),
    }),

  listConsultations: () => apiFetch("/consultations"),

  startConsultation: (id) =>
    apiFetch(`/consultations/${id}/start`, {
      method: "PATCH",
    }),

  completeConsultation: (id) =>
    apiFetch(`/consultations/${id}/complete`, {
      method: "PATCH",
    }),

  cancelConsultation: (id) =>
    apiFetch(`/consultations/${id}/cancel`, {
      method: "PATCH",
    }),

  createPrescription: (consultationId, payload) =>
    apiFetch(`/consultations/${consultationId}/prescription`, {
      method: "POST",
      body: JSON.stringify(payload),
    }),

  getPrescription: (consultationId) =>
    apiFetch(`/consultations/${consultationId}/prescription`),

  getPayment: (paymentId) => apiFetch(`/payments/${paymentId}`),

  confirmPayment: (payload) =>
    apiFetch("/payments/mock-confirm", {
      method: "POST",
      body: JSON.stringify(payload),
    }),

  adminSummary: () => apiFetch("/admin/analytics/summary"),

  auditLogs: () => apiFetch("/admin/audit-logs?limit=50&offset=0"),
};