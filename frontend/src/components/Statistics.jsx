import React, { useEffect, useState } from 'react';
import { StatBox } from './Common';
import { getFlagStats } from '../api';

export function Statistics({ refreshTrigger }) {
  const [stats, setStats] = useState({
    total_flags: 0,
    by_status: { pending: 0, relevant: 0, irrelevant: 0 },
  });

  useEffect(() => {
    loadStats();
  }, [refreshTrigger]);

  const loadStats = async () => {
    try {
      const response = await getFlagStats();
      setStats(response.data);
    } catch (error) {
      console.error('Error loading stats:', error);
    }
  };

  return (
    <div className="row mb-4">
      <div className="col-md-3 col-sm-6">
        <StatBox number={stats.total_flags} label="Total Flags" className="stat-total" />
      </div>
      <div className="col-md-3 col-sm-6">
        <StatBox number={stats.by_status.pending} label="Pending Review" className="stat-pending" />
      </div>
      <div className="col-md-3 col-sm-6">
        <StatBox number={stats.by_status.relevant} label="Relevant" className="stat-relevant" />
      </div>
      <div className="col-md-3 col-sm-6">
        <StatBox number={stats.by_status.irrelevant} label="Irrelevant" className="stat-irrelevant" />
      </div>
    </div>
  );
}
