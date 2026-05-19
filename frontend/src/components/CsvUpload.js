/**
 * CsvUpload Component
 *
 * Provides a file upload form for importing order data via CSV.
 * Validates that a file is selected before submission, sends the
 * file to the backend import endpoint, and displays success/error
 * messages based on the API response.
 */

import React, { useState } from "react";
import { uploadCsv } from "../services/api";

function CsvUpload() {
  const [file, setFile] = useState(null);
  const [message, setMessage] = useState(null);
  const [error, setError] = useState(null);
  const [uploading, setUploading] = useState(false);

  // Update file state when user selects a file; reset messages
  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
    setMessage(null);
    setError(null);
  };

  // Handle form submission: validate, upload, and display result
  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!file) {
      setError("Please select a CSV file.");
      return;
    }

    setUploading(true);
    setError(null);
    setMessage(null);

    try {
      const response = await uploadCsv(file);
      setMessage(response.data.message);
      setFile(null);
      e.target.reset(); // Reset the file input element
    } catch (err) {
      // Extract error detail from API response or show fallback
      const detail = err.response?.data?.error || "Upload failed.";
      setError(detail);
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="card">
      <div className="card-header bg-secondary text-white">
        <h5 className="mb-0">Import Orders CSV</h5>
      </div>
      <div className="card-body">
        <form onSubmit={handleSubmit}>
          <div className="mb-3">
            <label htmlFor="csvFile" className="form-label">
              Select CSV File
            </label>
            <input
              type="file"
              className="form-control"
              id="csvFile"
              accept=".csv"
              onChange={handleFileChange}
            />
          </div>
          <button
            type="submit"
            className="btn btn-primary"
            disabled={uploading || !file}
          >
            {uploading ? "Uploading..." : "Upload & Import"}
          </button>
        </form>
        {message && (
          <div className="alert alert-success mt-3 mb-0">{message}</div>
        )}
        {error && (
          <div className="alert alert-danger mt-3 mb-0">{error}</div>
        )}
      </div>
    </div>
  );
}

export default CsvUpload;
