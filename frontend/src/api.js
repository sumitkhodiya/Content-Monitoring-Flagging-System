import axios from 'axios';

const API_BASE = 'http://localhost:8000/api';

export const api = axios.create({
  baseURL: API_BASE,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Keywords
export const getKeywords = () => api.get('/keywords/');
export const createKeyword = (name) => api.post('/keywords/', { name });

// Flags
export const getFlags = (filters = {}) => {
  let url = '/flags/';
  const params = new URLSearchParams();
  
  if (filters.status) params.append('status', filters.status);
  if (filters.keyword_id) params.append('keyword_id', filters.keyword_id);
  if (filters.min_score) params.append('min_score', filters.min_score);
  
  if (params.toString()) {
    url += '?' + params.toString();
  }
  
  return api.get(url);
};

export const updateFlagStatus = (id, status) => 
  api.patch(`/flags/${id}/`, { status });

export const getFlagStats = () => api.get('/flags/stats/');

// Scan
export const runScan = (source = 'mock') => 
  api.post('/scan/', { source });
