'use client';

import React, { useState } from 'react';
import { useRouter } from 'next/navigation';
import Button from '../../components/ui/button';
import Input from '../../components/ui/input';

const CreateTournamentPage = () => {
  const [formData, setFormData] = useState({
    name: '',
    entry_fee: '0',
    max_participants: '16',
    start_date: '',
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const router = useRouter();

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    const token = localStorage.getItem('token');
    if (!token) {
      router.push('/authentication/login');
      return;
    }

    // Convert to the correct types for the backend
    const tournamentData = {
      ...formData,
      entry_fee: parseFloat(formData.entry_fee),
      max_participants: parseInt(formData.max_participants, 10),
      start_date: new Date(formData.start_date).toISOString(),
    };

    try {
      const response = await fetch('http://localhost:8000/tournaments/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify(tournamentData),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to create tournament.');
      }

      router.push('/tournaments'); // Redirect to the list of tournaments on success

    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-900 text-white p-4 sm:p-6 lg:p-8 flex items-center justify-center">
      <div className="w-full max-w-2xl bg-gray-800 rounded-lg shadow-lg p-8">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold">Create New Tournament</h1>
          <p className="text-gray-400">Set up the details for your next big event.</p>
        </div>
        <form onSubmit={handleSubmit} className="space-y-6">
          <Input
            label="Tournament Name"
            name="name"
            type="text"
            placeholder="e.g., Weekly Warzone Showdown"
            value={formData.name}
            onChange={handleChange}
            required
          />
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <Input
              label="Entry Fee (KES)"
              name="entry_fee"
              type="number"
              placeholder="100.00"
              value={formData.entry_fee}
              onChange={handleChange}
              required
              min="0"
            />
            <Input
              label="Max Participants"
              name="max_participants"
              type="number"
              placeholder="16"
              value={formData.max_participants}
              onChange={handleChange}
              required
              min="2"
            />
          </div>
          <Input
            label="Start Date & Time"
            name="start_date"
            type="datetime-local"
            value={formData.start_date}
            onChange={handleChange}
            required
          />
          <Button type="submit" disabled={loading} className="w-full">
            {loading ? 'Creating...' : 'Create Tournament'}
          </Button>
        </form>
        {error && <p className="mt-4 text-sm text-red-500 text-center">{error}</p>}
      </div>
    </div>
  );
};

export default CreateTournamentPage;
