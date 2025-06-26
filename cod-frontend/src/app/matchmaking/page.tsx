'use client';

import React, { useState, useEffect } from 'react';
import Button from '../components/ui/button';
import LoadingSpinner from '../components/ui/loadingSpinner'; // Assuming this component exists

const MatchmakingPage = () => {
  const [isInQueue, setIsInQueue] = useState(false);
  const [status, setStatus] = useState('Not in queue');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [wager, setWager] = useState(10); // Default wager

  const getToken = () => {
    if (typeof window !== 'undefined') {
      return localStorage.getItem('token');
    }
    return null;
  };

  const handleJoinQueue = async () => {
    setLoading(true);
    setError(null);
    const token = getToken();
    if (!token) {
      setError('You must be logged in to join the queue.');
      setLoading(false);
      return;
    }

    try {
      const response = await fetch('http://localhost:8000/matchmaking/join', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify({ wager_amount: wager }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to join queue');
      }

      setIsInQueue(true);
      setStatus('In queue, searching for match...');
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleLeaveQueue = async () => {
    setLoading(true);
    setError(null);
    const token = getToken();
    if (!token) {
      setError('You must be logged in to leave the queue.');
      setLoading(false);
      return;
    }

    try {
      const response = await fetch('http://localhost:8000/matchmaking/leave', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      if (!response.ok) {
        throw new Error('Failed to leave queue');
      }

      setIsInQueue(false);
      setStatus('Not in queue');
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  // Optional: Add a useEffect to periodically check for a match
  useEffect(() => {
    let interval: NodeJS.Timeout;
    if (isInQueue) {
      interval = setInterval(async () => {
        const token = getToken();
        if (!token) return;

        const response = await fetch('http://localhost:8000/matchmaking/find_match', {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${token}`,
          },
        });

        if (response.ok) {
          const match = await response.json();
          if (match && match.id) {
            setStatus(`Match found! ID: ${match.id}. Redirecting...`);
            setIsInQueue(false);
            // Redirect to the match page (we'll create this later)
            // window.location.href = `/matches/${match.id}`;
          }
        }
      }, 5000); // Check every 5 seconds
    }

    return () => clearInterval(interval);
  }, [isInQueue]);

  return (
    <div className="min-h-screen bg-gray-900 text-white p-8">
      <div className="max-w-2xl mx-auto text-center">
        <h1 className="text-4xl font-bold mb-4">Matchmaking</h1>
        <p className="text-gray-400 mb-8">Find an opponent and compete for a wager.</p>

        <div className="bg-gray-800 rounded-lg shadow-md p-8">
          <h2 className="text-2xl font-bold mb-4">Current Status</h2>
          <p className={`text-lg mb-6 ${isInQueue ? 'text-green-400' : 'text-yellow-400'}`}>{status}</p>

          {isInQueue ? (
            <div className="flex flex-col items-center">
              <LoadingSpinner />
              <p className="mt-4">Searching for an opponent...</p>
              <Button onClick={handleLeaveQueue} disabled={loading} className="mt-6 w-full md:w-auto bg-red-600 hover:bg-red-700">
                {loading ? 'Leaving...' : 'Leave Queue'}
              </Button>
            </div>
          ) : (
            <div className="space-y-6">
              <div>
                <label htmlFor="wager" className="block text-sm font-medium text-gray-300 mb-2">Select Wager Amount</label>
                <select 
                  id="wager"
                  name="wager"
                  value={wager}
                  onChange={(e) => setWager(Number(e.target.value))}
                  className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value={10}>$10</option>
                  <option value={25}>$25</option>
                  <option value={50}>$50</option>
                  <option value={100}>$100</option>
                </select>
              </div>
              <Button onClick={handleJoinQueue} disabled={loading} className="w-full">
                {loading ? 'Joining...' : 'Join Queue'}
              </Button>
            </div>
          )}

          {error && <p className="mt-6 text-sm text-red-500">Error: {error}</p>}
        </div>
      </div>
    </div>
  );
};

export default MatchmakingPage;
