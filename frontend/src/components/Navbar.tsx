import { Link } from 'react-router-dom';

export default function Navbar() {
  return (
    <nav className="bg-surface border-b border-rim shadow-sm sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-14">
          <Link to="/" className="flex items-center gap-1.5 font-extrabold text-lg tracking-tight hover:opacity-80 transition-opacity">
            <span className="text-purple">NBA</span>
            <span className="text-sky-dark">GOAT</span>
          </Link>
          <Link
            to="/questions"
            className="bg-purple hover:bg-purple-dark text-white text-sm font-semibold px-4 py-1.5 rounded-lg transition-colors shadow-sm"
          >
            Rank Players
          </Link>
        </div>
      </div>
    </nav>
  );
}
