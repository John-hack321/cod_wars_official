'use client';

import React, { useState, useEffect } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import Input from '../../components/ui/input';
import Button from '../../components/ui/button';

const VerifyPage = () => {
  const router = useRouter();
  const searchParams = useSearchParams();
  const [code, setCode] = useState('');
  const [phoneNumber, setPhoneNumber] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const phone = searchParams.get('phone_number');
    if (phone) {
      setPhoneNumber(phone);
    } else {
      setError('Phone number not provided. Please register again.');
    }
  }, [searchParams]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      const response = await fetch('http://localhost:8000/api/v1/auth/verify-phone', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ phone_number: phoneNumber, code }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Verification failed');
      }

      // On successful verification, redirect to the login page
      router.push('/authentication/login');

    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex items-center justify-center min-h-screen bg-gray-900 text-white p-4 sm:p-6 lg:p-8">
      <div className="w-full max-w-md p-8 space-y-6 bg-gray-800 rounded-lg shadow-lg">
        <div className="text-center">
            <h1 className="text-3xl font-bold">Verify Your Phone</h1>
            <p className="text-gray-400">Enter the code sent to {phoneNumber}</p>
        </div>
        <form onSubmit={handleSubmit} className="space-y-4">
          <Input
            label="Verification Code"
            name="code"
            type="text"
            placeholder="123456"
            value={code}
            onChange={(e) => setCode(e.target.value)}
            required
          />
          <Button type="submit" disabled={loading || !phoneNumber} className="w-full">
            {loading ? 'Verifying...' : 'Verify'}
          </Button>
        </form>
        {error && <p className="mt-4 text-sm text-red-500 text-center">{error}</p>}
      </div>
    </div>
  );
};

export default VerifyPage;
