/**
 * API Service
 *
 * Centralized HTTP client for communicating with the Django REST backend.
 * Base URL is configurable via REACT_APP_API_URL environment variable.
 */

import axios from "axios";

// Read API URL from environment or default to localhost for development
const API_URL = process.env.REACT_APP_API_URL || "http://localhost:8000";

const api = axios.create({
  baseURL: `${API_URL}/api`,
});

/** Fetch all orders from the database */
export const getOrders = () => api.get("/orders/");

/** Fetch analytics: total revenue and best-selling SKU */
export const getAnalytics = () => api.get("/orders/analytics/");

/** Upload a CSV file to import orders into the database */
export const uploadCsv = (file) => {
  const formData = new FormData();
  formData.append("file", file);
  return api.post("/orders/import/", formData, {
    headers: { "Content-Type": "multipart/form-data" },
  });
};

export default api;
