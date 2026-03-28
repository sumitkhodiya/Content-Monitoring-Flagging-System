import React from 'react';

export function StatBox({ number, label, className }) {
  return (
    <div className={`stat-box ${className}`}>
      <span className="stat-number">{number}</span>
      <span className="stat-label">{label}</span>
    </div>
  );
}

export function Alert({ message, type = 'success', onClose }) {
  React.useEffect(() => {
    const timer = setTimeout(onClose, 3000);
    return () => clearTimeout(timer);
  }, [onClose]);

  return (
    <div className={`alert alert-${type}`}>
      {message}
    </div>
  );
}

export function Loading() {
  return <span className="loading"></span>;
}

export function FlagCard({ flag, onUpdate }) {
  return (
    <div className={`flag-item ${flag.status}`}>
      <div className="d-flex justify-content-between align-items-start">
        <div style={{ flex: 1 }}>
          <div style={{ marginBottom: '8px' }}>
            <strong>{flag.keyword_name}</strong>
            <span className={`status-badge status-${flag.status}`}>
              {flag.status.toUpperCase()}
            </span>
          </div>
          <small className="text-muted">{flag.content_item_title}</small>
          <div style={{ marginTop: '8px' }}>
            <small>
              Score:
              <span className="score-bar">
                <span className="score-fill" style={{ width: `${flag.score}%` }}></span>
              </span>
              {flag.score}
            </small>
          </div>
        </div>
        <div>
          {flag.status === 'pending' ? (
            <>
              <button
                className="btn btn-success btn-sm me-2"
                onClick={() => onUpdate(flag.id, 'relevant')}
              >
                ✓
              </button>
              <button
                className="btn btn-danger btn-sm"
                onClick={() => onUpdate(flag.id, 'irrelevant')}
              >
                ✗
              </button>
            </>
          ) : null}
        </div>
      </div>
    </div>
  );
}

export function EmptyState({ message }) {
  return (
    <div className="empty-state">
      <small>{message}</small>
    </div>
  );
}
