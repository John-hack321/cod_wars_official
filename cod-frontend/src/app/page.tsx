import Link from 'next/link';
import Button from './components/ui/button';

export default function Home() {
  return (
    <div className="flex flex-col items-center justify-center min-h-screen bg-gray-900 text-white text-center p-8">
      <main className="max-w-4xl">
        <h1 className="text-6xl font-extrabold tracking-tight text-transparent bg-clip-text bg-gradient-to-r from-blue-500 to-teal-400">
          Welcome to WageWars
        </h1>
        <p className="mt-4 text-xl text-gray-300">
          The ultimate platform for competitive Call of Duty wagers. Challenge opponents, join tournaments, and climb the leaderboards.
        </p>
        <div className="mt-10 flex justify-center gap-4">
          <Link href="/authentication/register" passHref>
            <Button className="bg-blue-600 hover:bg-blue-700 text-lg px-8 py-3">
              Get Started
            </Button>
          </Link>
          <Link href="/authentication/login" passHref>
            <Button className="bg-gray-700 hover:bg-gray-600 text-lg px-8 py-3">
              Login
            </Button>
          </Link>
        </div>
      </main>
      <footer className="absolute bottom-8 text-gray-500">
        <p>&copy; {new Date().getFullYear()} WageWars. All rights reserved.</p>
      </footer>
    </div>
  );
}

