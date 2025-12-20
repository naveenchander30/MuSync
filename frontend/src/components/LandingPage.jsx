import Logo from "./Logo";

export default function LandingPage({ onGetStarted }) {
  const features = [
    {
      icon: "🎵",
      title: "Transfer Playlists",
      description:
        "Move your entire music library between Spotify and YouTube Music in minutes",
    },
    {
      icon: "🔄",
      title: "Smart Matching",
      description:
        "Advanced fuzzy matching ensures your tracks are found across platforms",
    },
    {
      icon: "📊",
      title: "Real-Time Progress",
      description:
        "Watch your sync happen live with detailed progress tracking and logs",
    },
    {
      icon: "🔒",
      title: "Secure & Private",
      description:
        "OAuth authentication with official APIs - your data never leaves your device",
    },
    {
      icon: "💾",
      title: "Backup & Export",
      description:
        "Save your playlists locally as JSON for safekeeping and portability",
    },
    {
      icon: "⚡",
      title: "Lightning Fast",
      description:
        "Batch processing and background tasks make transfers blazing fast",
    },
  ];

  const howItWorks = [
    {
      step: "1",
      title: "Connect Your Accounts",
      description:
        "Authenticate with Spotify and YouTube Music using secure OAuth",
    },
    {
      step: "2",
      title: "Choose Your Action",
      description:
        "Export from one platform or import to another - you control the flow",
    },
    {
      step: "3",
      title: "Track Progress",
      description:
        "Watch real-time updates as your music transfers, with full visibility",
    },
  ];

  return (
    <div className="min-h-screen bg-black">
      {/* Hero Section */}
      <div className="relative overflow-hidden">
        {/* Gradient Background */}
        <div className="absolute inset-0 bg-gradient-to-br from-primary/20 via-transparent to-accent-purple/20" />
        <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-primary/10 via-transparent to-transparent" />

        <div className="relative max-w-7xl mx-auto px-6 py-24 md:py-32">
          <div className="text-center space-y-8">
            {/* Logo/Title */}
            {/* Logo/Title */}
            <div className="inline-block hover:scale-105 transition-transform duration-300">
              <Logo className="w-12 h-12" />
            </div>

            {/* Main Heading */}
            <h1 className="text-5xl md:text-7xl lg:text-8xl font-black leading-tight">
              <span className="text-gradient">Transfer Playlists</span>
              <br />
              <span className="text-white">Between Music Services</span>
            </h1>

            {/* Subtitle */}
            <p className="text-xl md:text-2xl text-gray-400 max-w-3xl mx-auto leading-relaxed">
              Move your music library from{" "}
              <span className="text-primary font-semibold">Spotify</span> to{" "}
              <span className="text-red-500 font-semibold">YouTube Music</span>{" "}
              and back. Fast, reliable, and secure.
            </p>

            {/* CTA Buttons */}
            <div className="flex flex-col sm:flex-row gap-4 justify-center items-center pt-8">
              <button
                onClick={onGetStarted}
                className="btn-primary text-lg group"
              >
                Get Started Free
                <span className="inline-block ml-2 group-hover:translate-x-1 transition-transform">
                  →
                </span>
              </button>
              <button className="btn-secondary text-lg">View on GitHub</button>
            </div>

            {/* Platform Logos */}
            <div className="flex justify-center items-center gap-8 pt-12 flex-wrap">
              <div className="flex items-center gap-3 bg-white/5 px-6 py-3 rounded-full backdrop-blur-sm">
                <img
                  src="https://upload.wikimedia.org/wikipedia/commons/1/19/Spotify_logo_without_text.svg"
                  alt="Spotify"
                  className="w-6 h-6"
                />
                <span className="text-sm font-medium">Spotify</span>
              </div>
              <div className="text-2xl text-gray-600">⇄</div>
              <div className="flex items-center gap-3 bg-white/5 px-6 py-3 rounded-full backdrop-blur-sm">
                <img
                  src="https://upload.wikimedia.org/wikipedia/commons/6/6a/Youtube_Music_icon.svg"
                  alt="YouTube Music"
                  className="w-6 h-6"
                />
                <span className="text-sm font-medium">YouTube Music</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Features Section */}
      <div className="max-w-7xl mx-auto px-6 py-24">
        <div className="text-center mb-16">
          <h2 className="section-title">
            <span className="text-gradient">Powerful Features</span>
          </h2>
          <p className="section-subtitle">
            Everything you need to keep your music library in sync across
            platforms
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
          {features.map((feature, index) => (
            <div
              key={index}
              className="card group"
              style={{ animationDelay: `${index * 100}ms` }}
            >
              <div className="text-5xl mb-4 group-hover:scale-110 transition-transform">
                {feature.icon}
              </div>
              <h3 className="text-2xl font-bold mb-3">{feature.title}</h3>
              <p className="text-gray-400 leading-relaxed">
                {feature.description}
              </p>
            </div>
          ))}
        </div>
      </div>

      {/* How It Works Section */}
      <div className="max-w-7xl mx-auto px-6 py-24">
        <div className="text-center mb-16">
          <h2 className="section-title">How It Works</h2>
          <p className="section-subtitle">
            Three simple steps to transfer your entire music library
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-12">
          {howItWorks.map((item, index) => (
            <div key={index} className="relative">
              {/* Step Number */}
              <div className="flex justify-center mb-6">
                <div className="w-16 h-16 rounded-full bg-gradient-to-br from-primary to-primary-light flex items-center justify-center text-3xl font-bold glow-primary">
                  {item.step}
                </div>
              </div>

              {/* Content */}
              <div className="text-center">
                <h3 className="text-2xl font-bold mb-3">{item.title}</h3>
                <p className="text-gray-400 leading-relaxed">
                  {item.description}
                </p>
              </div>

              {/* Arrow (hidden on mobile and last item) */}
              {index < howItWorks.length - 1 && (
                <div className="hidden md:block absolute top-8 -right-6 text-4xl text-primary/30">
                  →
                </div>
              )}
            </div>
          ))}
        </div>
      </div>

      {/* CTA Section */}
      <div className="max-w-7xl mx-auto px-6 py-24">
        <div className="card bg-gradient-to-r from-primary/20 via-accent-purple/20 to-accent-pink/20 border-primary/30 text-center glow-primary">
          <h2 className="text-4xl md:text-5xl font-bold mb-6">
            Ready to Sync Your Music?
          </h2>
          <p className="text-xl text-gray-300 mb-8 max-w-2xl mx-auto">
            Join thousands of users who trust MuSync to keep their music library
            synchronized across platforms.
          </p>
          <button onClick={onGetStarted} className="btn-primary text-xl">
            Launch Dashboard →
          </button>
        </div>
      </div>

      {/* Footer */}
      <footer className="border-t border-white/10 py-12">
        <div className="max-w-7xl mx-auto px-6">
          <div className="flex flex-col md:flex-row justify-between items-center gap-6">
            <div className="flex items-center gap-2">
              <Logo className="w-8 h-8" />
              <span className="text-gray-600 ml-2">v2.0</span>
            </div>
            <p className="text-gray-500 text-sm">
              Built with ❤️ for seamless music synchronization
            </p>
          </div>
        </div>
      </footer>
    </div>
  );
}
