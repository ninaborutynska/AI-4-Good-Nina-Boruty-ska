import { useState, useEffect, useMemo } from 'react';
import { Check, X, RotateCcw, ArrowLeft, Trophy } from 'lucide-react';
import type { Question } from '@/data/questions';
import { checkAnswer } from '@/data/questions';

interface ResultsScreenProps {
  levelName: string;
  questions: Question[];
  answers: (string | null)[];
  onRetry: () => void;
  onBackToLevels: () => void;
}

function getScoreColor(percentage: number): string {
  if (percentage >= 80) return '#22c55e';
  if (percentage >= 50) return '#4268e0';
  return '#9333ea';
}

function getMessage(percentage: number): string {
  if (percentage === 100) return 'Perfect score! You have mastered this level.';
  if (percentage >= 80) return 'Great work! You are well on your way.';
  if (percentage >= 50) return 'Good effort! Keep practicing to improve.';
  return 'Keep going! Review the questions below and try again.';
}

export default function ResultsScreen({
  levelName,
  questions,
  answers,
  onRetry,
  onBackToLevels,
}: ResultsScreenProps) {
  const [animatedPercentage, setAnimatedPercentage] = useState(0);

  const { score, total, percentage, wrongAnswers } = useMemo(() => {
    const results = questions.map((q, i) => ({
      question: q,
      userAnswer: answers[i],
      isCorrect: answers[i] !== null && checkAnswer(answers[i]!, q),
    }));
    const correct = results.filter(r => r.isCorrect).length;
    const pct = Math.round((correct / questions.length) * 100);
    const wrong = results.filter(r => !r.isCorrect);
    return { score: correct, total: questions.length, percentage: pct, wrongAnswers: wrong };
  }, [questions, answers]);

  useEffect(() => {
    const timer = setTimeout(() => setAnimatedPercentage(percentage), 200);
    return () => clearTimeout(timer);
  }, [percentage]);

  const radius = 52;
  const circumference = 2 * Math.PI * radius;
  const strokeDashoffset = circumference - (animatedPercentage / 100) * circumference;
  const scoreColor = getScoreColor(percentage);

  return (
    <div className="math-texture animated-gradient animate-gradient-drift flex min-h-full flex-col items-center px-6 py-12">
      <div className="w-full max-w-2xl opacity-0 animate-fade-in-up">
        {/* Score section */}
        <div className="flex flex-col items-center">
          <span className="mb-6 rounded-full bg-brand-500/10 px-5 py-2 text-sm font-semibold text-brand-700">
            {levelName} — Results
          </span>

          <svg width="140" height="140" viewBox="0 0 140 140" className="mb-6">
            <circle cx="70" cy="70" r={radius} fill="none" stroke="#e0ecff" strokeWidth="10" />
            <circle
              cx="70"
              cy="70"
              r={radius}
              fill="none"
              stroke={scoreColor}
              strokeWidth="10"
              strokeLinecap="round"
              strokeDasharray={circumference}
              strokeDashoffset={strokeDashoffset}
              transform="rotate(-90 70 70)"
              style={{ transition: 'stroke-dashoffset 1.2s ease-out' }}
            />
            <text
              x="70"
              y="76"
              textAnchor="middle"
              fontSize="28"
              fontWeight="700"
              fill={scoreColor}
            >
              {percentage}%
            </text>
          </svg>

          <h2 className="text-2xl font-bold text-brand-800">
            You got {score} out of {total} correct
          </h2>
          <p className="mt-2 text-center text-base text-brand-600/70">
            {getMessage(percentage)}
          </p>
        </div>

        {/* Review section */}
        <div className="mt-10">
          <div className="mb-5 flex items-center gap-3">
            <h3 className="text-lg font-semibold text-brand-700">Review</h3>
            <div className="h-px flex-1 bg-brand-200/50" />
          </div>

          {wrongAnswers.length === 0 ? (
            <div className="flex flex-col items-center gap-4 rounded-3xl border border-success-200/60 bg-success-50/40 p-10 text-center backdrop-blur-sm">
              <Trophy className="h-12 w-12 text-success-500" strokeWidth={1.5} />
              <p className="text-lg font-medium text-success-700">
                Every question correct — nothing to review!
              </p>
            </div>
          ) : (
            <div className="flex flex-col gap-4">
              {wrongAnswers.map(({ question, userAnswer }) => (
                <div
                  key={question.id}
                  className="rounded-2xl border border-brand-100/60 bg-white/50 p-5 backdrop-blur-sm shadow-sm"
                >
                  <p className="mb-4 text-sm font-medium text-brand-500">
                    Question {questions.indexOf(question) + 1}
                  </p>
                  <p className="mb-4 text-base font-semibold text-brand-800">
                    {question.prompt}
                  </p>
                  <div className="flex flex-col gap-2">
                    <div className="flex items-start gap-2.5 rounded-xl bg-red-50/70 px-4 py-3">
                      <X className="mt-0.5 h-5 w-5 flex-shrink-0 text-red-500" strokeWidth={2} />
                      <div>
                        <p className="text-xs font-medium uppercase tracking-wide text-red-400">
                          Your answer
                        </p>
                        <p className="text-base text-red-700">
                          {userAnswer && userAnswer.trim() !== '' ? userAnswer : 'Not answered'}
                        </p>
                      </div>
                    </div>
                    <div className="flex items-start gap-2.5 rounded-xl bg-green-50/70 px-4 py-3">
                      <Check className="mt-0.5 h-5 w-5 flex-shrink-0 text-green-500" strokeWidth={2} />
                      <div>
                        <p className="text-xs font-medium uppercase tracking-wide text-green-500">
                          Correct answer
                        </p>
                        <p className="text-base text-green-700">
                          {question.correctAnswer}
                        </p>
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Actions */}
        <div className="mt-10 flex flex-col gap-3 sm:flex-row sm:justify-center">
          <button
            onClick={onRetry}
            className="flex items-center justify-center gap-2 rounded-full bg-gradient-to-r from-brand-500 to-accent-500 px-6 py-3 text-sm font-semibold text-white shadow-lg shadow-brand-300/40 transition-all hover:shadow-xl hover:shadow-accent-300/40 hover:-translate-y-0.5 focus:outline-none focus-visible:ring-2 focus-visible:ring-brand-400 focus-visible:ring-offset-2"
          >
            <RotateCcw className="h-4 w-4" strokeWidth={2} />
            Retry this level
          </button>
          <button
            onClick={onBackToLevels}
            className="flex items-center justify-center gap-2 rounded-full border border-brand-200/60 bg-white/50 px-6 py-3 text-sm font-medium text-brand-700 backdrop-blur-sm transition-all hover:bg-white/80 hover:border-brand-300 focus:outline-none focus-visible:ring-2 focus-visible:ring-brand-400"
          >
            <ArrowLeft className="h-4 w-4" strokeWidth={2} />
            Back to levels
          </button>
        </div>
      </div>
    </div>
  );
}
