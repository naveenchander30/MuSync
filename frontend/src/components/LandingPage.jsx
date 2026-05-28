import Logo from "./Logo";

export default function LandingPage({ onGetStarted }) {
  const features = [
    {
      icon: "sync_alt",
      title: "Bi-Directional Sync",
      description: "Move libraries between platforms instantly. Changes propagate both ways with zero latency.",
    },
    {
      icon: "search_check",
      title: "Smart Track Matching",
      description: "Proprietary metadata verification ensures the exact version of the track is found every time.",
    },
    {
      icon: "schedule",
      title: "Scheduled Syncs",
      description: "Set it and forget it. Automation keeps your libraries mirrored on a custom interval.",
    },
  ];

  return (
    <div className="min-h-screen bg-black">
      <nav className="fixed top-0 left-0 right-0 z-50 bg-black/80 border-b border-outline-variant">
        <div className="flex items-center justify-between px-unit-8 py-unit-3 max-w-6xl mx-auto">
          <Logo />
          <div className="hidden md:flex items-center gap-unit-6">
            <a className="text-xs text-on-surface-variant hover:text-white transition-colors border-b border-white pb-[1px]" href="#">Features</a>
            <a className="text-xs text-on-surface-variant hover:text-white transition-colors" href="#">How it Works</a>
          </div>
          <button
            onClick={onGetStarted}
            className="px-unit-4 py-unit-2 bg-white text-on-primary text-xs font-medium hover:bg-white/90 transition-colors"
          >
            Get Started
          </button>
        </div>
      </nav>

      <main>
        <section className="min-h-screen flex flex-col justify-center items-center text-center px-unit-4">
          <div className="max-w-3xl">
            <h1 className="text-display-lg mb-unit-4">
              Sync your music.<br />Seamlessly.
            </h1>
            <p className="text-body-lg text-on-surface-variant mb-unit-12 max-w-xl mx-auto">
              The most reliable way to move your playlists between Spotify and YouTube Music. Precision engineering for audiophiles who demand perfect library parity.
            </p>
            <div className="flex flex-col md:flex-row gap-unit-3 justify-center">
              <button
                onClick={onGetStarted}
                className="px-unit-6 py-unit-3 bg-white text-on-primary text-sm font-medium hover:bg-white/90 transition-colors border border-white"
              >
                Connect Spotify
              </button>
              <button
                onClick={onGetStarted}
                className="px-unit-6 py-unit-3 bg-transparent text-white text-sm font-medium border border-white hover:bg-white/10 transition-colors"
              >
                Connect YouTube Music
              </button>
            </div>
          </div>
          <div className="mt-unit-12 w-full max-w-4xl aspect-video border border-outline-variant flex items-center justify-center relative overflow-hidden">
            <div className="flex gap-unit-3">
              <div className="w-[1px] h-24 bg-white/20" />
              <div className="w-[1px] h-24 bg-white/40" />
              <div className="w-[1px] h-24 bg-white/20" />
            </div>
          </div>
        </section>

        <section className="border-y border-outline-variant py-unit-12">
          <div className="max-w-6xl mx-auto px-unit-8 grid grid-cols-1 md:grid-cols-3 gap-unit-8 text-center md:text-left">
            <div>
              <div className="text-headline-md mb-unit-1">10K+</div>
              <div className="text-label-sm text-on-surface-variant uppercase tracking-widest">Active Users</div>
            </div>
            <div>
              <div className="text-headline-md mb-unit-1">50K+</div>
              <div className="text-label-sm text-on-surface-variant uppercase tracking-widest">Playlists Synced</div>
            </div>
            <div>
              <div className="text-headline-md mb-unit-1">99.9%</div>
              <div className="text-label-sm text-on-surface-variant uppercase tracking-widest">Accuracy</div>
            </div>
          </div>
        </section>

        <section className="py-unit-12 px-unit-8 max-w-6xl mx-auto">
          <h2 className="text-headline-lg mb-unit-12 text-center md:text-left">Core Capabilities</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-unit-4">
            {features.map((feature, index) => (
              <div key={index} className="border border-outline-variant p-unit-6 border-l-2 border-l-white hover:bg-white/[0.02] transition-colors">
                <div className="mb-unit-3">
                  <span className="material-symbols-outlined text-white text-2xl">{feature.icon}</span>
                </div>
                <h3 className="text-sm font-medium mb-unit-1">{feature.title}</h3>
                <p className="text-xs text-on-surface-variant leading-relaxed">{feature.description}</p>
              </div>
            ))}
          </div>
        </section>

        <section className="py-unit-12">
          <div className="max-w-6xl mx-auto px-unit-8">
            <div className="border border-outline-variant p-unit-8 flex flex-col md:flex-row items-center justify-between gap-unit-6">
              <div>
                <h2 className="text-sm font-medium mb-unit-1">Ready for precision?</h2>
                <p className="text-xs text-on-surface-variant">Your library, perfected across all platforms.</p>
              </div>
              <button
                onClick={onGetStarted}
                className="px-unit-8 py-unit-3 bg-white text-on-primary text-sm font-medium hover:bg-white/90 transition-colors"
              >
                Start Transfer
              </button>
            </div>
          </div>
        </section>
      </main>

      <footer className="border-t border-outline-variant">
        <div className="flex flex-col md:flex-row justify-between items-center px-unit-8 py-unit-6 max-w-6xl mx-auto gap-unit-3">
          <div>
            <div className="text-label-sm text-white uppercase tracking-widest">MuSync</div>
            <p className="text-xs text-on-surface-variant mt-unit-1">Precision music synchronization</p>
          </div>
          <div className="flex gap-unit-4">
            <a className="text-xs text-on-surface-variant hover:text-white transition-colors" href="#">Privacy</a>
            <a className="text-xs text-on-surface-variant hover:text-white transition-colors" href="#">Terms</a>
            <a className="text-xs text-on-surface-variant hover:text-white transition-colors" href="#">GitHub</a>
          </div>
        </div>
      </footer>
    </div>
  );
}
