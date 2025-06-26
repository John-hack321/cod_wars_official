'use client';

import React, { useState, useEffect } from 'react';
import Button from '../components/ui/button';
import Input from '../components/ui/input';

interface Transaction {
  id: number;
  amount: number;
  type: 'deposit' | 'withdrawal' | 'wager' | 'payout';
  timestamp: string;
}

interface User {
    balance: number;
}

const WalletPage = () => {
  const [balance, setBalance] = useState(0);
  const [transactions, setTransactions] = useState<Transaction[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [amount, setAmount] = useState('');

  const getToken = () => typeof window !== 'undefined' ? localStorage.getItem('token') : null;

  useEffect(() => {
    const fetchData = async () => {
      const token = getToken();
      if (!token) {
        window.location.href = '/authentication/login';
        return;
      }

      try {
        // Fetch balance from user profile
        const userRes = await fetch('http://localhost:8000/users/me', {
          headers: { 'Authorization': `Bearer ${token}` },
        });
        if (!userRes.ok) throw new Error('Failed to fetch balance');
        const userData = await userRes.json();
        setBalance(userData.balance);

        // Fetch transactions
        const transRes = await fetch('http://localhost:8000/payments/transactions', {
          headers: { 'Authorization': `Bearer ${token}` },
        });
        if (!transRes.ok) throw new Error('Failed to fetch transactions');
        const transData = await transRes.json();
        setTransactions(transData);

      } catch (err: any) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  const handleTransaction = async (type: 'deposit' | 'withdraw') => {
    const token = getToken();
    if (!token || !amount) return;

    try {
      const response = await fetch(`http://localhost:8000/payments/${type}`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`,
          },
          body: JSON.stringify({ amount: parseFloat(amount) }),
        }
      );

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || `Failed to process ${type}`);
      }

      // Refresh data after transaction
      setAmount('');
      setLoading(true);
      // This is a simplified refresh. In a real app, you might just update state.
      window.location.reload(); 

    } catch (err: any) {
      setError(err.message);
    }
  };

  if (loading) {
    return <div className="flex items-center justify-center min-h-screen bg-gray-900 text-white">Loading...</div>;
  }

  return (
    <div className="min-h-screen bg-gray-900 text-white p-8">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-4xl font-bold mb-8">My Wallet</h1>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mb-8">
          <div className="bg-gray-800 rounded-lg shadow-md p-6 text-center">
            <h2 className="text-lg font-semibold text-gray-400 mb-2">Current Balance</h2>
            <p className="text-4xl font-bold text-green-400">${balance.toFixed(2)}</p>
          </div>
          <div className="md:col-span-2 bg-gray-800 rounded-lg shadow-md p-6">
            <h2 className="text-2xl font-bold mb-4">Manage Funds</h2>
            <div className="flex items-center space-x-4">
              <Input 
                type="number"
                placeholder="Amount"
                value={amount}
                onChange={(e) => setAmount(e.target.value)}
                className="flex-grow"
              />
              <Button onClick={() => handleTransaction('deposit')} className="w-auto bg-green-600 hover:bg-green-700">Deposit</Button>
              <Button onClick={() => handleTransaction('withdraw')} className="w-auto bg-red-600 hover:bg-red-700">Withdraw</Button>
            </div>
            {error && <p className="mt-4 text-sm text-red-500">{error}</p>}
          </div>
        </div>

        <div>
          <h2 className="text-2xl font-bold mb-4">Transaction History</h2>
          <div className="bg-gray-800 rounded-lg shadow-md">
            <ul className="divide-y divide-gray-700">
              {transactions.length > 0 ? transactions.map(tx => (
                <li key={tx.id} className="p-4 flex justify-between items-center">
                  <div>
                    <p className="font-semibold capitalize">{tx.type}</p>
                    <p className="text-sm text-gray-400">{new Date(tx.timestamp).toLocaleString()}</p>
                  </div>
                  <p className={`font-bold text-lg ${tx.amount > 0 ? 'text-green-400' : 'text-red-400'}`}>
                    {tx.amount > 0 ? '+' : ''}${tx.amount.toFixed(2)}
                  </p>
                </li>
              )) : (
                <li className="p-4 text-center text-gray-400">No transactions found.</li>
              )}
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
};

export default WalletPage;
