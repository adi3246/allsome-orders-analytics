/**
 * App Component (Root)
 *
 * Main application layout with two-column responsive grid:
 * - Left: CSV file upload form for importing order data
 * - Right: Analytics dashboard showing revenue and best-selling SKU
 */

import React from "react";
import OrderAnalytics from "./components/OrderAnalytics";
import CsvUpload from "./components/CsvUpload";

function App() {
  return (
    <div className="container py-5">
      <header className="mb-4">
        <h1 className="text-primary">Allsome Orders Analytics</h1>
        <p className="text-muted">
          Process order data and view revenue analytics
        </p>
      </header>
      <div className="row">
        {/* CSV Upload Section */}
        <div className="col-md-6 mb-4">
          <CsvUpload />
        </div>
        {/* Analytics Display Section */}
        <div className="col-md-6 mb-4">
          <OrderAnalytics />
        </div>
      </div>
    </div>
  );
}

export default App;
