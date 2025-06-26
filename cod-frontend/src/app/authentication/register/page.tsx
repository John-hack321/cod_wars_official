'use client';

import React, { useState } from 'react';
import Input from '../../components/ui/input';
import Button from '../../components/ui/button';
import Link from 'next/link';

const RegisterPage = () => {
  const [formData, setFormData] = useState({
    email: '',
    username: '',
    password: '',
    phone_number: '',
    cod_username: '', // Corrected field name
    platform: 'battle', // Default platform
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      const response = await fetch('http://localhost:8000/api/v1/auth/register', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          ...formData,
          profile_picture: 'default.jpg' // Placeholder
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Registration failed');
      }

      window.location.href = '/authentication/login';

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
            <h1 className="text-3xl font-bold">Create an Account</h1>
            <p className="text-gray-400">Join WageWars and start competing!</p>
        </div>
        <form onSubmit={handleSubmit} className="space-y-4">
          <Input
            label="Email"
            name="email"
            type="email"
            placeholder="you@example.com"
            value={formData.email}
            onChange={handleChange}
            required
          />
          <Input
            label="Username"
            name="username"
            type="text"
            placeholder="YourUsername"
            value={formData.username}
            onChange={handleChange}
            required
          />
          <Input
            label="Password"
            name="password"
            type="password"
            placeholder="••••••••"
            value={formData.password}
            onChange={handleChange}
            required
          />
          <Input
            label="Activision ID"
            name="cod_username"
            type="text"
            placeholder="YourActivisionID#12345"
            value={formData.cod_username}
            onChange={handleChange}
            required
          />
          <Input
            label="Phone Number"
            name="phone_number"
            type="tel"
            placeholder="+254712345678"
            value={formData.phone_number}
            onChange={handleChange}
            required
          />
          <div>
            <label htmlFor="platform" className="block text-sm font-medium text-gray-300 mb-1">Platform</label>
            <select
              id="platform"
              name="platform"
              value={formData.platform}
              onChange={handleChange}
              required
              className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="battle">Battle.net</option>
              <option value="steam">Steam</option>
              <option value="psn">PlayStation</option>
              <option value="xbl">Xbox</option>
              <option value="acti">Activision</option>
            </select>
          </div>
          <Button type="submit" disabled={loading} className="w-full">
            {loading ? 'Creating Account...' : 'Create Account'}
          </Button>
        </form>
        {error && <p className="mt-4 text-sm text-red-500 text-center">{error}</p>}
        <p className="text-sm text-center text-gray-400">
          Already have an account?{' '}
          <Link href="/authentication/login" className="font-medium text-blue-500 hover:underline">
            Log in
          </Link>
        </p>
      </div>
    </div>
  );
};

export default RegisterPage;
