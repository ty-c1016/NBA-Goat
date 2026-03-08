import { Link } from 'react-router-dom';

const features = [
  {
    icon: '🏀',
    title: 'Set Your Priorities',
    desc: 'Weight what matters most — offense, defense, championships, longevity, and more.',
  },
  {
    icon: '📊',
    title: 'Algorithm-Driven Rankings',
    desc: 'A multi-factor scoring engine evaluates every eligible player against your weights.',
  },
  {
    icon: '🏆',
    title: 'Your Personal GOAT List',
    desc: "See a personalized top-100 ranked by your criteria, not someone else's opinion.",
  },
];

export default function Home() {
  return (
    <div className="min-h-screen">
      {/* Hero */}
      <section className="bg-gradient-to-b from-purple-subtle via-sky-subtle to-bg py-24 px-4 text-center">
        <div className="inline-block bg-sky-light text-sky-dark text-xs font-semibold px-3 py-1 rounded-full mb-6 tracking-wide uppercase">
          Data-Driven · All Eras
        </div>
        <h1 className="text-5xl sm:text-6xl font-extrabold tracking-tight text-ink mb-4 leading-tight">
          Who Is The{' '}
          <span className="text-purple">Greatest</span>
          <br />
          <span className="text-sky-dark">Of All Time?</span>
        </h1>
        <p className="text-muted text-lg sm:text-xl max-w-2xl mx-auto mb-10">
          Stop arguing. Start ranking. Customize your criteria and let the data decide your NBA GOAT.
        </p>
        <Link
          to="/questions"
          className="inline-block bg-purple-subtle border border-purple text-purple hover:bg-purple hover:text-white font-bold text-lg px-10 py-4 rounded-xl transition-colors shadow-md"
        >
          Start the Analysis
        </Link>
      </section>

      {/* How it works */}
      <section className="max-w-5xl mx-auto px-4 py-20">
        <h2 className="text-2xl font-bold text-center text-ink mb-2">How It Works</h2>
        <p className="text-muted text-center text-sm mb-12">Three steps to your personalized rankings</p>
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-6">
          {features.map((f, i) => (
            <div
              key={f.title}
              className="bg-surface border border-rim rounded-2xl p-6 text-center hover:border-purple-light hover:shadow-md transition-all"
            >
              <div className="w-12 h-12 rounded-full bg-purple-subtle flex items-center justify-center mx-auto mb-4 text-2xl">
                {f.icon}
              </div>
              <div className="text-xs font-bold text-purple-light uppercase tracking-widest mb-2">
                Step {i + 1}
              </div>
              <h3 className="text-ink font-semibold text-base mb-2">{f.title}</h3>
              <p className="text-muted text-sm leading-relaxed">{f.desc}</p>
            </div>
          ))}
        </div>
      </section>
    </div>
  );
}
