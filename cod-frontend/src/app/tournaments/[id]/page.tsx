'use client';

import React, { useState, useEffect, useCallback } from 'react';
import { useParams, useRouter } from 'next/navigation';
import Button from '../../components/ui/button';

// --- Data Interfaces ---
interface User {
  id: number;
  username: string;
  is_admin?: boolean;
}

interface Participant {
  id: number;
  user_id: number;
  user: User;
}

interface Match {
  id: number;
  player1_id: number;
  player2_id: number;
  winner_id: number | null;
  round_number: number;
  status: string;
}

interface Tournament {
  id: number;
  name: string;
  entry_fee: number;
  max_participants: number;
  current_participants: number;
  status: 'upcoming' | 'ongoing' | 'completed';
  start_date: string;
  participants: Participant[];
  matches: Match[];
}

// --- Helper Functions & Components ---
const getToken = () => typeof window !== 'undefined' ? localStorage.getItem('token') : null;

const groupMatchesByRound = (matches: Match[]) => {
  return matches.reduce((acc, match) => {
    const round = match.round_number || 0;
    if (!acc[round]) {
      acc[round] = [];
    }
    acc[round].push(match);
    return acc;
  }, {} as Record<number, Match[]>);
};

const MatchCard = ({ match, participants }: { match: Match, participants: Participant[] }) => {
  const getParticipant = (id: number) => participants.find(p => p.user_id === id)?.user.username || 'TBD';
  const winner = match.winner_id ? getParticipant(match.winner_id) : null;

  return (
    <div className={`bg-gray-700 p-3 rounded-md border-l-4 ${winner ? 'border-green-500' : 'border-gray-500'}`}>
      <div className="flex justify-between items-center">
        <p className={match.winner_id === match.player1_id ? 'font-bold text-white' : 'text-gray-300'}>
          {getParticipant(match.player1_id)}
        </p>
        <span className="text-xs bg-gray-600 px-2 py-1 rounded">VS</span>
        <p className={match.winner_id === match.player2_id ? 'font-bold text-white' : 'text-gray-300'}>
          {getParticipant(match.player2_id)}
        </p>
      </div>
      {winner && <p className="text-xs text-center mt-2 text-green-400">Winner: {winner}</p>}
    </div>
  );
};

// --- Main Component ---
const TournamentDetailPage = () => {
  const params = useParams();
  const router = useRouter();
  const id = params.id as string;

  const [tournament, setTournament] = useState<Tournament | null>(null);
  const [currentUser, setCurrentUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [actionInProgress, setActionInProgress] = useState(false);

  const fetchDetails = useCallback(async () => {
    const token = getToken();
    if (!id || !token) {
        if (!token) router.push('/authentication/login');
        return;
    }

    try {
      const [tourneyRes, matchesRes, participantsRes, meRes] = await Promise.all([
        fetch(`http://localhost:8000/tournaments/${id}`, { headers: { 'Authorization': `Bearer ${token}` } }),
        fetch(`http://localhost:8000/tournaments/${id}/matches`, { headers: { 'Authorization': `Bearer ${token}` } }),
        fetch(`http://localhost:8000/tournaments/${id}/participants`, { headers: { 'Authorization': `Bearer ${token}` } }),
        fetch('http://localhost:8000/users/me', { headers: { 'Authorization': `Bearer ${token}` } }),
      ]);

      if (!tourneyRes.ok) throw new Error('Failed to fetch tournament details');
      if (!matchesRes.ok) throw new Error('Failed to fetch matches');
      if (!participantsRes.ok) throw new Error('Failed to fetch participants');
      if (!meRes.ok) throw new Error('Failed to fetch user profile');

      const tourneyData = await tourneyRes.json();
      const matchesData = await matchesRes.json();
      const participantsData = await participantsRes.json();
      const meData = await meRes.json();

      setTournament({ ...tourneyData, matches: matchesData, participants: participantsData });
      setCurrentUser(meData);

    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, [id, router]);

  useEffect(() => {
    fetchDetails();
  }, [fetchDetails]);

  const handleAction = async (endpoint: string, method: 'POST' | 'PUT' = 'POST') => {
    const token = getToken();
    setActionInProgress(true);
    setError(null);
    try {
      const response = await fetch(`http://localhost:8000/tournaments/${id}/${endpoint}`, {
        method,
        headers: { 'Authorization': `Bearer ${token}` },
      });
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Action failed');
      }
      await fetchDetails(); // Re-fetch all data to show updated state
    } catch (err: any) {
      setError(err.message);
    } finally {
      setActionInProgress(false);
    }
  };

  // --- Render Logic ---
  if (loading) return <div className="flex items-center justify-center min-h-screen bg-gray-900 text-white">Loading Tournament...</div>;
  if (error) return <div className="flex items-center justify-center min-h-screen bg-gray-900 text-red-500">Error: {error}</div>;
  if (!tournament) return <div className="flex items-center justify-center min-h-screen bg-gray-900 text-white">Tournament not found.</div>;

  const isParticipant = tournament.participants.some(p => p.user_id === currentUser?.id);
  const canJoin = tournament.status === 'upcoming' && !isParticipant && tournament.current_participants < tournament.max_participants;
  const canStart = currentUser?.is_admin && tournament.status === 'upcoming' && tournament.current_participants >= 2;

  const matchesByRound = groupMatchesByRound(tournament.matches);

  return (
    <div className="min-h-screen bg-gray-900 text-white p-4 sm:p-6 lg:p-8">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="bg-gray-800 rounded-lg shadow-lg p-6 mb-8">
          <div className="flex flex-col sm:flex-row justify-between items-start gap-4">
            <div>
              <h1 className="text-4xl font-bold">{tournament.name}</h1>
              <p className="text-gray-400">Starts: {new Date(tournament.start_date).toLocaleString()}</p>
            </div>
            <div className="flex gap-2">
              {canJoin && <Button onClick={() => handleAction('join')} disabled={actionInProgress}>Join Tournament (${tournament.entry_fee})</Button>}
              {canStart && <Button onClick={() => handleAction('start')} disabled={actionInProgress} className="bg-green-600 hover:bg-green-700">Start Tournament</Button>}
            </div>
          </div>
        </div>

        {/* Main Content */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Bracket */}
          <div className="lg:col-span-2 bg-gray-800 rounded-lg shadow-lg p-6">
            <h2 className="text-2xl font-bold mb-6">Tournament Bracket</h2>
            {Object.keys(matchesByRound).length > 0 ? (
              <div className="flex space-x-4 overflow-x-auto pb-4">
                {Object.entries(matchesByRound).sort(([a], [b]) => Number(a) - Number(b)).map(([round, matches]) => (
                  <div key={round} className="flex-shrink-0 w-72">
                    <h3 className="text-lg font-semibold mb-3">Round {round}</h3>
                    <div className="space-y-3">
                      {matches.map(match => <MatchCard key={match.id} match={match} participants={tournament.participants} />)}
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-gray-400">The bracket will be generated once the tournament starts.</p>
            )}
          </div>

          {/* Participants */}
          <div className="bg-gray-800 rounded-lg shadow-lg p-6">
            <h2 className="text-2xl font-bold mb-4">Participants ({tournament.current_participants}/{tournament.max_participants})</h2>
            <ul className="space-y-2">
              {tournament.participants.map(p => (
                <li key={p.id} className="bg-gray-700 p-3 rounded-md text-white">{p.user.username}</li>
              ))}
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
};

export default TournamentDetailPage;
