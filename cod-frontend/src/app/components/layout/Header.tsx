'use client';

import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';

const Header = () => {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const router = useRouter();

  useEffect(() => {
    // This effect runs on the client after the component mounts
    const token = localStorage.getItem('token');
    setIsAuthenticated(!!token);

    // Optional: Listen for storage changes to update UI across tabs
    const handleStorageChange = () => {
      const token = localStorage.getItem('token');
      setIsAuthenticated(!!token);
    };
    window.addEventListener('storage', handleStorageChange);
    return () => {
      window.removeEventListener('storage', handleStorageChange);
    };
  }, []);

  const handleLogout = () => {
    localStorage.removeItem('token');
    setIsAuthenticated(false);
    router.push('/authentication/login');
  };

  return (
    <header className="bg-gray-900 text-white shadow-lg sticky top-0 z-50">
      <nav className="container mx-auto px-6 py-4 flex justify-between items-center">
        <div className="text-2xl font-bold tracking-wider">
          <Link href="/" className="hover:text-yellow-400 transition-colors duration-300">
            COD WARS
          </Link>
        </div>
        <div className="flex items-center space-x-6 text-lg">
          {isAuthenticated ? (
            <>
              <Link href="/" className="hover:text-yellow-400 transition-colors duration-300">
                Dashboard
              </Link>
              <Link href="/profile" className="hover:text-yellow-400 transition-colors duration-300">
                Profile
              </Link>
              <button
                onClick={handleLogout}
                className="bg-yellow-500 hover:bg-yellow-600 text-black font-bold py-2 px-4 rounded-lg transition-all duration-300 transform hover:scale-105"
              >
                Logout
              </button>
            </>
          ) : (
            <>
              <Link href="/authentication/login" className="hover:text-yellow-400 transition-colors duration-300">
                Login
              </Link>
              <Link href="/authentication/register" className="bg-yellow-500 hover:bg-yellow-600 text-black font-bold py-2 px-4 rounded-lg transition-all duration-300 transform hover:scale-105">
                Register
              </Link>
            </>
          )}
        </div>
      </nav>
    </header>
  );
};

export default Header;
