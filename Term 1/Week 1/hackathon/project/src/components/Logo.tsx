export default function Logo() {
  return (
    <div className="flex flex-col items-center gap-2 opacity-0 animate-fade-in-scale">
      <h1 className="text-5xl font-bold tracking-tight sm:text-6xl">
        <span className="text-gradient">ReL</span>
        <span className="text-gradient inline-block animate-float">&#8734;</span>
        <span className="text-gradient">p</span>
      </h1>
      <p className="text-sm font-medium text-brand-600/70 tracking-wide">
        Master math, one level at a time
      </p>
    </div>
  );
}
