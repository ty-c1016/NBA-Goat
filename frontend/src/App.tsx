import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Navbar from './components/Navbar';
import Home from './pages/Home';
import Questions from './pages/Questions';
import Results from './pages/Results';

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
            <Route path="*" element={<Home />} />
          </Routes>
        </main>
        <footer className="text-center text-gray-600 text-xs py-6 border-t border-gray-800">
          NBA GOAT Ranker — Data-driven, preference-powered.
        </footer>
      </div>
    </BrowserRouter>
  );
}
