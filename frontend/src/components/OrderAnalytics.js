/**
 * OrderAnalytics Component
 *
 * Displays the order analytics dashboard showing:
 * - Total revenue (sum of quantity * price for all orders)
 * - Best-selling SKU (SKU with highest total quantity)
 *
 * Fetches data from the backend API on mount and provides
 * a refresh button for manual updates.
 */

import React, { useState, useEffect } from "react";
import { getAnalytics } from "../services/api";

function OrderAnalytics() {
  const [analytics, setAnalytics] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Fetch analytics data from the backend API
  const fetchAnalytics = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await getAnalytics();
      setAnalytics(response.data);
    } catch (err) {
      setError("Failed to load analytics. Is the backend running?");
    } finally {
      setLoading(false);
    }
  };

  // Load analytics on component mount
  useEffect(() => {
    fetchAnalytics();
  }, []);

  if (loading) {
    return (
      <div className="card">
        <div className="card-body text-center">
          <div className="spinner-border text-primary" role="status">
            <span className="visually-hidden">Loading...</span>
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="card border-danger">
        <div className="card-body">
          <p className="text-danger mb-2">{error}</p>
          <button className="btn btn-outline-primary btn-sm" onClick={fetchAnalytics}>
            Retry
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="card">
      <div className="card-header bg-primary text-white">
        <h5 className="mb-0">Order Analytics</h5>
      </div>
      <div className="card-body">
        <div className="mb-3">
          <h6 className="text-muted">Total Revenue</h6>
          <h3 className="text-success">
            ${analytics?.total_revenue?.toFixed(2) ?? "0.00"}
          </h3>
        </div>
        <hr />
        <div>
          <h6 className="text-muted">Best Selling SKU</h6>
          {analytics?.best_selling_sku ? (
            <div>
              <p className="mb-1">
                <strong>SKU:</strong> {analytics.best_selling_sku.sku}
              </p>
              <p className="mb-0">
                <strong>Total Quantity:</strong>{" "}
                {analytics.best_selling_sku.total_quantity}
              </p>
            </div>
          ) : (
            <p className="text-muted">No orders found</p>
          )}
        </div>
        <hr />
        <button className="btn btn-outline-primary btn-sm" onClick={fetchAnalytics}>
          Refresh
        </button>
        <hr />
        <div>
          <h6 className="text-muted">Raw JSON Response</h6>
          <pre
            className="bg-light p-3 rounded"
            style={{ maxHeight: "400px", overflow: "auto", fontSize: "0.85rem" }}
          >
            {JSON.stringify(analytics, null, 2)}
          </pre>
        </div>
      </div>
    </div>
  );
}

export default OrderAnalytics;
