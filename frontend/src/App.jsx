import React, { useState, useCallback } from 'react';
import { Statistics } from './components/Statistics';
import { ScanPanel } from './components/ScanPanel';
import { KeywordsPanel } from './components/KeywordsPanel';
import { FlagsPanel } from './components/FlagsPanel';
import { Alert } from './components/Common';
import './App.css';

function App() {
  const [alerts, setAlerts] = useState([]);
  const [refreshTrigger, setRefreshTrigger] = useState(0);

  const showAlert = useCallback((message, type = 'success') => {
    const id = Date.now();
    setAlerts((prev) => [...prev, { id, message, type }]);
  }, []);

  const removeAlert = useCallback((id) => {
    setAlerts((prev) => prev.filter((alert) => alert.id !== id));
  }, []);

  const handleScanComplete = () => {
    setRefreshTrigger((prev) => prev + 1);
  };

  return (
    <div className="page-background">
      <div className="container container-main">
        {/* Header */}
        <div className="header">
          <h1>📊 Content Monitoring System</h1>
          <p className="subtitle">Smart keyword tracking with intelligent suppression</p>
        </div>

        {/* Alerts */}
        <div className="alert-container">
          {alerts.map((alert) => (
            <Alert
              key={alert.id}
              message={alert.message}
              type={alert.type}
              onClose={() => removeAlert(alert.id)}
            />
          ))}
        </div>

        {/* Statistics */}
        <Statistics refreshTrigger={refreshTrigger} />

        {/* Main Content */}
        <div className="row">
          <div className="col-lg-4">
            <ScanPanel onScanComplete={handleScanComplete} onAlert={showAlert} />
            <KeywordsPanel onAlert={showAlert} />
          </div>
          <div className="col-lg-8">
            <FlagsPanel refreshTrigger={refreshTrigger} onAlert={showAlert} />
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;
