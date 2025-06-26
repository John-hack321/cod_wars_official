'use client';

import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import Button from '../components/ui/button';
import Input from '../components/ui/input';

interface User {
  id: number;
  username: string;
}

const CreateMatchPage = () => {
  const [users, setUsers] = useState<User[]>([]);
  const [currentUser, setCurrentUser] = useState<User | null>(null);
  const [selectedOpponent, setSelectedOpponent] = useState<string>('');
  const [wagerAmount, setWagerAmount] = useState<string>('0');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const router = useRouter();

  useEffect(() => {
    const fetchData = async () => {
      const token = localStorage.getItem('token');
      if (!token) {
        router.push('/authentication/login');
        return;
      }

      try {
        const [usersResponse, meResponse] = await Promise.all([
          fetch('http://localhost:8000/users/', { 
            headers: { 'Authorization': `Bearer ${token}` }
          }),
          fetch('http://localhost:8000/users/me', { 
            headers: { 'Authorization': `Bearer ${token}` }
          }),
        ]);

        if (!usersResponse.ok || !meResponse.ok) {
          throw new Error('Failed to fetch user data.');
        }

        const usersData = await usersResponse.json();
        const meData = await meResponse.json();
        
        setCurrentUser(meData);
        // Filter out the current user from the list of opponents
        setUsers(usersData.filter((user: User) => user.id !== meData.id));

      } catch (err: any) {
        setError(err.message);
      }
    };

    fetchData();
  }, [router]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedOpponent || !wagerAmount) {
      setError('Please select an opponent and enter a wager amount.');
      return;
    }
    
    setLoading(true);
    setError(null);

    const token = localStorage.getItem('token');

    try {
      const response = await fetch('http://localhost:8000/matches/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify({
          player1_id: currentUser?.id,
          player2_id: parseInt(selectedOpponent, 10),
          wager_amount: parseFloat(wagerAmount),
          tournament_id: null, // Not a tournament match
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to create match.');
      }

      // On success, redirect to profile to see the new match
      router.push('/profile');

    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-900 text-white p-4 sm:p-6 lg:p-8 flex items-center justify-center">
      <div className="w-full max-w-lg bg-gray-800 rounded-lg shadow-lg p-8">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold">Create a New Match</h1>
          <p className="text-gray-400">Challenge an opponent and set your wager.</p>
        </div>
        <form onSubmit={handleSubmit} className="space-y-6">
          <div>
            <label htmlFor="opponent" className="block text-sm font-medium text-gray-300 mb-1">Challenge Opponent</label>
            <select
              id="opponent"
              name="opponent"
              value={selectedOpponent}
              onChange={(e) => setSelectedOpponent(e.target.value)}
              required
              className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="" disabled>Select a player...</option>
              {users.map(user => (
                <option key={user.id} value={user.id}>{user.username}</option>
              ))}
            </select>
          </div>
          <Input
            label="Wager Amount (KES)"
            name="wagerAmount"
            type="number"
            placeholder="0.00"
            value={wagerAmount}
            onChange={(e) => setWagerAmount(e.target.value)}
            required
            min="0"
          />
          <Button type="submit" disabled={loading} className="w-full">
            {loading ? 'Creating Match...' : 'Send Challenge'}
          </Button>
        </form>
        {error && <p className="mt-4 text-sm text-red-500 text-center">{error}</p>}
      </div>
    </div>
  );
};

export default CreateMatchPage;