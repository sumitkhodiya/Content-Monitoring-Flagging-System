import React, { useEffect, useState } from 'react';
import { getFlags, updateFlagStatus } from '../api';
import { FlagCard, EmptyState } from './Common';

export function FlagsPanel({ refreshTrigger, onAlert }) {
  const [flags, setFlags] = useState([]);
  const [filter, setFilter] = useState('all');

  useEffect(() => {
    loadFlags();
  }, [refreshTrigger]);

  const loadFlags = async () => {
    try {
      const filters = filter !== 'all' ? { status: filter } : {};
      const response = await getFlags(filters);
      setFlags(response.data.results || response.data);
    } catch (error) {
      console.error('Error loading flags:', error);
    }
  };

  useEffect(() => {
    loadFlags();
  }, [filter]);

  const handleUpdateFlag = async (id, status) => {
    try {
      await updateFlagStatus(id, status);
      onAlert(`Flag marked as ${status}`, 'success');
      loadFlags();
    } catch (error) {
      onAlert('Error updating flag: ' + error.message, 'error');
    }
  };

  return (
    <div className="card">
      <div className="card-header">
        🚩 Flags
      </div>
      <div className="card-body">
        {/* Tabs */}
        <div className="tabs">
          {['all', 'pending', 'relevant', 'irrelevant'].map((status) => (
            <button
              key={status}
              className={`tab-button ${filter === status ? 'active' : ''}`}
              onClick={() => setFilter(status)}
            >
              {status.charAt(0).toUpperCase() + status.slice(1)}
            </button>
          ))}
        </div>

        {/* Flags List */}
        <div>
          {flags.length === 0 ? (
            <EmptyState message="No flags match your filter" />
          ) : (
            flags.map((flag) => (
              <FlagCard
                key={flag.id}
                flag={flag}
                onUpdate={handleUpdateFlag}
              />
            ))
          )}
        </div>
      </div>
    </div>
  );
}
