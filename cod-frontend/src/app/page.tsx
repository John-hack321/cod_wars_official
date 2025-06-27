'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import Button from './components/ui/button';

const DashboardPage = () => {
  const router = useRouter();
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const token = localStorage.getItem('token');
    if (!token) {
      router.replace('/authentication/login');
    } else {
      setLoading(false);
    }
  }, [router]);

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-gray-900 text-white">
        Loading...
      </div>
    );
  }

  return (
    <div className="text-white">
      <div className="flex justify-between items-center mb-8">
        <h1 className="text-4xl font-bold">Dashboard</h1>
        <Button className="bg-yellow-500 hover:bg-yellow-600 text-black font-bold">
          Create Match
        </Button>
      </div>

      <div>
        <h2 className="text-2xl font-semibold mb-4">Open Matches</h2>
        <div className="bg-gray-800 p-6 rounded-lg">
          <p className="text-gray-400">No open matches right now. Why not create one?</p>
        </div>
      </div>
    </div>
  );
};

export default DashboardPage;


