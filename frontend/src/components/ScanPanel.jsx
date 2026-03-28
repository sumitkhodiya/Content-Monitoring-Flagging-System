import React, { useState } from 'react';
import { runScan } from '../api';
import { Loading, Alert } from './Common';

export function ScanPanel({ onScanComplete, onAlert }) {
  const [loading, setLoading] = useState(false);
  const [scanResult, setScanResult] = useState(null);

  const handleScan = async () => {
    setLoading(true);
    setScanResult(null);

    try {
      const response = await runScan('mock');
      
      if (response.data.success) {
        setScanResult(response.data.stats);
        onAlert('Scan completed successfully!', 'success');
        onScanComplete();
      } else {
        onAlert('Scan failed: ' + response.data.error, 'error');
      }
    } catch (error) {
      onAlert('Error running scan: ' + error.message, 'error');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="card">
      <div className="card-header">
        🔍 Run Scan
      </div>
      <div className="card-body">
        <p className="text-muted">Trigger a content scan to match keywords against mock data.</p>
        <button 
          className="btn btn-primary w-100" 
          onClick={handleScan}
          disabled={loading}
        >
          <span>{loading ? 'Scanning...' : 'Run Scan'}</span>
          {loading && <Loading />}
        </button>
        
        {scanResult && (
          <div id="scanResult" className="mt-3">
            <small>
              <div><strong>Items:</strong> {scanResult.content_items_processed}</div>
              <div><strong>Created:</strong> {scanResult.flags_created}</div>
              <div><strong>Updated:</strong> {scanResult.flags_updated}</div>
              <div><strong>Suppressed:</strong> {scanResult.flags_suppressed}</div>
            </small>
          </div>
        )}
      </div>
    </div>
  );
}
