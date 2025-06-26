'use client';

import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import Button from '../components/ui/button';

interface Tournament {
  id: number;
  name: string;
  entry_fee: number;
  max_participants: number;
  current_participants: number;
  status: 'upcoming' | 'ongoing' | 'completed';
  start_date: string; // ISO date string
}

const TournamentCard = ({ tournament }: { tournament: Tournament }) => (
  <div className="bg-gray-800 rounded-lg shadow-lg p-6 hover:bg-gray-700 transition-colors duration-200">
    <h3 className="text-xl font-bold text-white mb-2">{tournament.name}</h3>
    <div className="text-sm text-gray-400 mb-4">
      <p>Starts: {new Date(tournament.start_date).toLocaleString()}</p>
      <p>Status: <span className="font-semibold capitalize">{tournament.status}</span></p>
    </div>
    <div className="flex justify-between items-center mb-4">
      <div>
        <p className="text-gray-300">Entry Fee</p>
        <p className="text-lg font-bold text-green-400">${tournament.entry_fee}</p>
      </div>
      <div>
        <p className="text-gray-300">Participants</p>
        <p className="text-lg font-bold">{tournament.current_participants} / {tournament.max_participants}</p>
      </div>
    </div>
    <Link href={`/tournaments/${tournament.id}`} passHref>
      <Button className="w-full">View Details</Button>
    </Link>
  </div>
);

const TournamentsPage = () => {
  const [tournaments, setTournaments] = useState<Tournament[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const router = useRouter();

  useEffect(() => {
    const fetchTournaments = async () => {
      const token = localStorage.getItem('token');
      if (!token) {
        router.push('/authentication/login');
        return;
      }

      try {
        const response = await fetch('http://localhost:8000/tournaments/', {
          headers: { 'Authorization': `Bearer ${token}` },
        });

        if (!response.ok) {
          throw new Error('Failed to fetch tournaments.');
        }

        const data = await response.json();
        setTournaments(data);
      } catch (err: any) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    fetchTournaments();
  }, [router]);

  if (loading) {
    return <div className="flex items-center justify-center min-h-screen bg-gray-900 text-white">Loading tournaments...</div>;
  }

  if (error) {
    return <div className="flex items-center justify-center min-h-screen bg-gray-900 text-red-500">Error: {error}</div>;
  }

  return (
    <div className="min-h-screen bg-gray-900 text-white p-4 sm:p-6 lg:p-8">
      <div className="max-w-7xl mx-auto">
        <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center mb-8 gap-4">
          <h1 className="text-4xl font-bold">Tournaments</h1>
          <Link href="/tournaments/create" passHref>
             <Button className="w-full sm:w-auto">Create Tournament</Button>
          </Link>
        </div>
        {tournaments.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {tournaments.map(t => <TournamentCard key={t.id} tournament={t} />)}
          </div>
        ) : (
          <div className="text-center py-16 bg-gray-800 rounded-lg">
            <h2 className="text-2xl font-bold">No Tournaments Found</h2>
            <p className="text-gray-400 mt-2">Check back later or create a new tournament to get started!</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default TournamentsPage;