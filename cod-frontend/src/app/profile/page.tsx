'use client';

import React, { useState, useEffect } from 'react';
import Button from '../components/ui/button';

// Updated interfaces to match backend models
interface UserProfile {
  id: number;
  username: string;
  email: string;
  cod_username: string;
  platform: string;
  profile_picture: string | null;
  wallet_balance: number;
}

interface Match {
  id: number;
  player1: { id: number; username: string };
  player2: { id: number; username: string };
  status: 'pending' | 'active' | 'completed' | 'disputed';
  wager_amount: number;
  winner_id: number | null;
}

const ProfilePage = () => {
  const [profile, setProfile] = useState<UserProfile | null>(null);
  const [matches, setMatches] = useState<Match[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      const token = localStorage.getItem('token');
      if (!token) {
        window.location.href = '/authentication/login';
        return;
      }

      try {
        // Fetch profile and matches in parallel
        const [profileResponse, matchesResponse] = await Promise.all([
          fetch('http://localhost:8000/api/v1/auth/me', {
            headers: { 'Authorization': `Bearer ${token}` },
          }),
          fetch('http://localhost:8000/api/v1/matches/me', {
            headers: { 'Authorization': `Bearer ${token}` },
          }),
        ]);

        if (!profileResponse.ok) throw new Error('Failed to fetch profile.');
        if (!matchesResponse.ok) throw new Error('Failed to fetch matches.');

        const profileData = await profileResponse.json();
        const matchesData = await matchesResponse.json();

        setProfile(profileData);
        setMatches(matchesData);

      } catch (err: any) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  const handleLogout = () => {
    localStorage.removeItem('token');
    window.location.href = '/authentication/login';
  };

  const getStatusChip = (status: string, winnerId: number | null, userId: number) => {
    let className = 'px-3 py-1 text-sm font-semibold rounded-full';
    let text = status.charAt(0).toUpperCase() + status.slice(1);

    switch (status) {
      case 'completed':
        className += winnerId === userId ? ' bg-green-500 text-white' : ' bg-red-500 text-white';
        text = winnerId === userId ? 'Won' : 'Lost';
        break;
      case 'active':
        className += ' bg-yellow-500 text-black';
        break;
      case 'pending':
        className += ' bg-gray-500 text-white';
        break;
      default:
        className += ' bg-purple-500 text-white';
    }
    return <span className={className}>{text}</span>;
  };

  if (loading) {
    return <div className="flex items-center justify-center min-h-screen bg-gray-900 text-white">Loading profile...</div>;
  }

  if (error) {
    return <div className="flex items-center justify-center min-h-screen bg-gray-900 text-red-500">Error: {error}</div>;
  }

  return (
    <div className="min-h-screen bg-gray-900 text-white p-4 sm:p-6 lg:p-8">
      <div className="max-w-6xl mx-auto">
        <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center mb-8 gap-4">
          <h1 className="text-4xl font-bold">My Profile</h1>
          <Button onClick={handleLogout} className="w-full sm:w-auto">Logout</Button>
        </div>

        {profile && (
          <div className="bg-gray-800 rounded-lg shadow-lg p-6 mb-8">
            <div className="flex flex-col sm:flex-row items-center space-y-4 sm:space-y-0 sm:space-x-6">
              <img 
                src={profile.profile_picture || 'https://via.placeholder.com/150'}
                alt="Profile"
                className="w-24 h-24 sm:w-32 sm:h-32 rounded-full border-4 border-blue-500 object-cover"
              />
              <div className="text-center sm:text-left">
                <h2 className="text-3xl font-bold">{profile.username}</h2>
                <p className="text-gray-400">{profile.email}</p>
                <p className="text-md text-gray-300 mt-1">{profile.cod_username} ({profile.platform.toUpperCase()})</p>
              </div>
              <div className="pt-4 sm:pt-0 sm:ml-auto text-center sm:text-right">
                  <h3 className="text-lg font-semibold text-gray-400">Wallet</h3>
                  <p className="text-3xl font-bold text-green-400">${profile.wallet_balance.toFixed(2)}</p>
              </div>
            </div>
          </div>
        )}

        <div className="bg-gray-800 rounded-lg shadow-lg p-6">
            <h2 className="text-2xl font-bold mb-4">Match History</h2>
            <div className="overflow-x-auto">
                {matches.length > 0 ? (
                    <ul className="space-y-4">
                        {matches.map(match => {
                            const opponent = match.player1.id === profile?.id ? match.player2 : match.player1;
                            return (
                                <li key={match.id} className="bg-gray-700 p-4 rounded-lg flex flex-col sm:flex-row justify-between items-center gap-4">
                                    <div className="text-lg font-semibold">vs {opponent.username}</div>
                                    <div className="text-md text-gray-300">Wager: ${match.wager_amount}</div>
                                    <div>{getStatusChip(match.status, match.winner_id, profile!.id)}</div>
                                </li>
                            );
                        })}
                    </ul>
                ) : (
                    <p className="text-gray-400 text-center py-4">You haven't played any matches yet.</p>
                )}
            </div>
        </div>
      </div>
    </div>
  );
};

export default ProfilePage;
