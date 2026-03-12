import { Link } from 'react-router-dom';

export default function NotFound() {
  return (
    <div className="min-h-screen bg-canvas flex items-center justify-center px-4">
      <div className="text-center">
        <h1 className="text-6xl font-bold text-purple mb-2">404</h1>
        <p className="text-xl text-ink mb-1">Page Not Found</p>
        <p className="text-muted text-sm mb-8">
          The page you're looking for doesn't exist or has been moved.
        </p>
        <Link
          to="/"
          className="bg-purple hover:bg-purple-dark text-white font-semibold px-6 py-2.5 rounded-xl transition-colors shadow-sm"
        >
          Back to Home
        </Link>
      </div>
    </div>
  );
}
