import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Navbar from './components/Navbar';
import Home from './pages/Home';
import Questions from './pages/Questions';
import Results from './pages/Results';
import NotFound from './pages/NotFound';

export default function App() {
  return (
    <BrowserRouter>
      <div className="min-h-screen flex flex-col">
        <Navbar />
        <main className="flex-1">
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/questions" element={<Questions />} />
            <Route path="/results/:sessionId" element={<Results />} />
            <Route path="*" element={<NotFound />} />
          </Routes>
        </main>
        <footer className="text-center text-muted text-xs py-6 border-t border-rim bg-surface">
          NBA GOAT Ranker — Data-driven, preference-powered.
        </footer>
      </div>
    </BrowserRouter>
  );
}
