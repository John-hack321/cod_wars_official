'use client';

import React, { useState, useEffect } from 'react';

interface PlayerStat {
  rank: number;
  user_id: number;
  username: string;
  wins: number;
  losses: number;
  win_rate: number;
  total_wagered: number;
}

const LeaderboardsPage = () => {
  const [leaderboard, setLeaderboard] = useState<PlayerStat[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchLeaderboard = async () => {
      try {
        // This endpoint needs to be created in the backend
        const response = await fetch('http://localhost:8000/leaderboard/');
        if (!response.ok) {
          throw new Error('Failed to fetch leaderboard data. The endpoint may not be available yet.');
        }
        const data = await response.json();
        // Assuming the backend returns a ranked list
        setLeaderboard(data.map((player: any, index: number) => ({ ...player, rank: index + 1 })));
      } catch (err: any) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    fetchLeaderboard();
  }, []);

  if (loading) {
    return <div className="flex items-center justify-center min-h-screen bg-gray-900 text-white">Loading Leaderboards...</div>;
  }

  return (
    <div className="min-h-screen bg-gray-900 text-white p-8">
      <div className="max-w-6xl mx-auto">
        <h1 className="text-4xl font-bold mb-8 text-center">Leaderboards</h1>
        
        {error ? (
           <div className="text-center bg-red-900/50 border border-red-500 p-6 rounded-lg">
             <h2 className="text-2xl font-bold text-red-400">Could Not Load Leaderboard</h2>
             <p className="text-red-300 mt-2">{error}</p>
             <p className="text-gray-400 mt-4">This feature is still under development. Please check back later.</p>
           </div>
        ) : (
          <div className="bg-gray-800 rounded-lg shadow-md overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-700">
              <thead className="bg-gray-700">
                <tr>
                  <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">Rank</th>
                  <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">Player</th>
                  <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">Wins</th>
                  <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">Losses</th>
                  <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">Win Rate</th>
                  <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">Total Wagered</th>
                </tr>
              </thead>
              <tbody className="bg-gray-800 divide-y divide-gray-700">
                {leaderboard.map(player => (
                  <tr key={player.user_id} className="hover:bg-gray-700/50">
                    <td className="px-6 py-4 whitespace-nowrap text-lg font-bold">#{player.rank}</td>
                    <td className="px-6 py-4 whitespace-nowrap font-semibold">{player.username}</td>
                    <td className="px-6 py-4 whitespace-nowrap text-green-400">{player.wins}</td>
                    <td className="px-6 py-4 whitespace-nowrap text-red-400">{player.losses}</td>
                    <td className="px-6 py-4 whitespace-nowrap">{player.win_rate.toFixed(2)}%</td>
                    <td className="px-6 py-4 whitespace-nowrap font-semibold">${player.total_wagered.toFixed(2)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
};

export default LeaderboardsPage;
