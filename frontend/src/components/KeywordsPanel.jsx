import React, { useEffect, useState } from 'react';
import { getKeywords, createKeyword } from '../api';
import { EmptyState } from './Common';

export function KeywordsPanel({ onAlert }) {
  const [keywords, setKeywords] = useState([]);
  const [newKeyword, setNewKeyword] = useState('');

  useEffect(() => {
    loadKeywords();
  }, []);

  const loadKeywords = async () => {
    try {
      const response = await getKeywords();
      setKeywords(response.data.results || response.data);
    } catch (error) {
      console.error('Error loading keywords:', error);
    }
  };

  const handleAddKeyword = async (e) => {
    if (e.key === 'Enter' || e.type === 'click') {
      const name = newKeyword.trim();

      if (!name) {
        onAlert('Please enter a keyword', 'error');
        return;
      }

      try {
        await createKeyword(name);
        setNewKeyword('');
        onAlert(`Keyword "${name}" added!`, 'success');
        loadKeywords();
      } catch (error) {
        const errorMsg = error.response?.data?.name?.[0] || 'Failed to add keyword';
        onAlert('Error: ' + errorMsg, 'error');
      }
    }
  };

  return (
    <div className="card">
      <div className="card-header">
        🏷️ Keywords
      </div>
      <div className="card-body">
        <div className="mb-3">
          <input
            type="text"
            className="form-control form-control-sm"
            placeholder="Add new keyword..."
            value={newKeyword}
            onChange={(e) => setNewKeyword(e.target.value)}
            onKeyPress={handleAddKeyword}
          />
          <button 
            className="btn btn-primary btn-sm w-100 mt-2" 
            onClick={handleAddKeyword}
          >
            Add
          </button>
        </div>
        <div>
          {keywords.length === 0 ? (
            <EmptyState message="Loading keywords..." />
          ) : (
            <div>
              {keywords.map((kw) => (
                <span key={kw.id} className="keyword-chip">
                  {kw.name}
                </span>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
