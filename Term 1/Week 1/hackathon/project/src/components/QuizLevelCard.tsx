import { LucideIcon } from 'lucide-react';

export interface QuizLevel {
  id: string;
  name: string;
  description: string;
  icon: LucideIcon;
  gradient: string;
  iconColor: string;
}

interface QuizLevelCardProps {
  level: QuizLevel;
  index: number;
  onClick: (id: string) => void;
}

export default function QuizLevelCard({ level, index, onClick }: QuizLevelCardProps) {
  const Icon = level.icon;

  return (
    <button
      onClick={() => onClick(level.id)}
      style={{ animationDelay: `${index * 150}ms` }}
      className="group relative flex flex-col items-center gap-5 rounded-3xl border border-white/60 bg-white/50 p-8 backdrop-blur-md shadow-lg shadow-brand-200/30 opacity-0 animate-fade-in-up transition-all duration-300 hover:-translate-y-2 hover:shadow-xl hover:shadow-accent-200/40 hover:border-brand-300/50 focus:outline-none focus-visible:ring-2 focus-visible:ring-brand-400 focus-visible:ring-offset-2 focus-visible:ring-offset-transparent"
    >
      <div
        className={`flex h-20 w-20 items-center justify-center rounded-2xl bg-gradient-to-br ${level.gradient} shadow-md transition-transform duration-300 group-hover:scale-110`}
      >
        <Icon className={`h-10 w-10 ${level.iconColor}`} strokeWidth={1.5} />
      </div>
      <div className="text-center">
        <h2 className="text-xl font-semibold text-brand-800">{level.name}</h2>
        <p className="mt-2 text-sm text-brand-600/70 leading-relaxed max-w-[12rem]">
          {level.description}
        </p>
      </div>
      <span className="mt-1 text-xs font-medium text-brand-400 opacity-0 transition-opacity duration-300 group-hover:opacity-100">
        Click to start &rarr;
      </span>
    </button>
  );
}
