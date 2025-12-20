export default function Logo({ className = "w-8 h-8", withText = true }) {
    return (
        <div className="flex items-center gap-2">
            <div className={`relative ${className}`}>
                <svg
                    viewBox="0 0 100 100"
                    fill="none"
                    xmlns="http://www.w3.org/2000/svg"
                    className="w-full h-full"
                >
                    <path
                        d="M20 80V30L50 50L80 30V80"
                        stroke="url(#gradient)"
                        strokeWidth="8"
                        strokeLinecap="round"
                        strokeLinejoin="round"
                    />
                    <path
                        d="M30 45V70"
                        stroke="white"
                        strokeWidth="4"
                        strokeLinecap="round"
                        style={{ opacity: 0.5 }}
                    />
                    <path
                        d="M70 45V70"
                        stroke="white"
                        strokeWidth="4"
                        strokeLinecap="round"
                        style={{ opacity: 0.5 }}
                    />
                    <defs>
                        <linearGradient
                            id="gradient"
                            x1="20"
                            y1="30"
                            x2="80"
                            y2="80"
                            gradientUnits="userSpaceOnUse"
                        >
                            <stop stopColor="#1DB954" />
                            <stop offset="1" stopColor="#3b82f6" />
                        </linearGradient>
                    </defs>
                </svg>
            </div>
            {withText && (
                <span className="font-bold text-xl tracking-tight text-white">
                    Mu<span className="text-primary">Sync</span>
                </span>
            )}
        </div>
    );
}
