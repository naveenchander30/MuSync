export default function Logo({ className = "w-8 h-8", withText = true }) {
  return (
    <div className="flex items-center gap-2">
      <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" className={className}>
        <rect x="4" y="4" width="16" height="16" stroke="white" strokeWidth="1.5" />
        <path d="M8 8h8v8H8z" fill="white" />
        <path d="M12 16V8" stroke="black" strokeWidth="1.5" />
        <path d="M8 12h8" stroke="black" strokeWidth="1.5" />
      </svg>
      {withText && (
        <span className="text-base tracking-tight text-white">
          <span className="font-normal">Mu</span><span className="font-bold">Sync</span>
        </span>
      )}
    </div>
  );
}
