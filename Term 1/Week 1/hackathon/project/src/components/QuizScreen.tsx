import { useState, useRef, useEffect } from 'react';
import { ArrowLeft, ArrowRight, X } from 'lucide-react';
import type { Question } from '@/data/questions';

interface QuizScreenProps {
  levelName: string;
  questions: Question[];
  onSubmit: (answers: (string | null)[]) => void;
  onQuit: () => void;
}

const OPTION_LABELS = ['A', 'B', 'C', 'D', 'E'];

export default function QuizScreen({ levelName, questions, onSubmit, onQuit }: QuizScreenProps) {
  const [currentIndex, setCurrentIndex] = useState(0);
  const [answers, setAnswers] = useState<(string | null)[]>(() => questions.map(() => null));
  const inputRef = useRef<HTMLInputElement>(null);

  const currentQuestion = questions[currentIndex];
  const currentAnswer = answers[currentIndex];
  const isAnswered = currentAnswer !== null && currentAnswer.trim() !== '';
  const isLast = currentIndex === questions.length - 1;
  const progress = ((currentIndex + 1) / questions.length) * 100;

  useEffect(() => {
    if (currentQuestion.type === 'open-answer') {
      inputRef.current?.focus();
    }
  }, [currentIndex, currentQuestion.type]);

  const setAnswer = (value: string) => {
    setAnswers(prev => {
      const next = [...prev];
      next[currentIndex] = value;
      return next;
    });
  };

  const handleNext = () => {
    if (!isAnswered) return;
    if (isLast) {
      onSubmit(answers);
    } else {
      setCurrentIndex(i => i + 1);
    }
  };

  const handleBack = () => {
    if (currentIndex > 0) setCurrentIndex(i => i - 1);
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && isAnswered) {
      e.preventDefault();
      handleNext();
    }
  };

  return (
    <div className="math-texture animated-gradient animate-gradient-drift flex min-h-full flex-col">
      {/* Header */}
      <div className="relative z-10 flex items-center justify-between px-6 py-5 sm:px-10">
        <button
          onClick={onQuit}
          className="flex items-center gap-1.5 rounded-full border border-brand-200/60 bg-white/50 px-4 py-2 text-sm font-medium text-brand-700 backdrop-blur-sm transition-all hover:bg-white/80 hover:border-brand-300 focus:outline-none focus-visible:ring-2 focus-visible:ring-brand-400"
        >
          <X className="h-4 w-4" strokeWidth={2} />
          Quit
        </button>
        <span className="rounded-full bg-brand-500/10 px-5 py-2 text-sm font-semibold text-brand-700">
          {levelName}
        </span>
        <div className="w-[72px]" />
      </div>

      {/* Progress bar */}
      <div className="relative z-10 px-6 sm:px-10">
        <div className="h-2 w-full overflow-hidden rounded-full bg-brand-100/60">
          <div
            className="h-full rounded-full bg-gradient-to-r from-brand-400 to-accent-400 transition-all duration-500 ease-out"
            style={{ width: `${progress}%` }}
          />
        </div>
      </div>

      {/* Question */}
      <div className="relative z-10 flex flex-1 flex-col items-center justify-center px-6 py-8">
        <div
          key={currentIndex}
          className="w-full max-w-2xl opacity-0 animate-fade-in-up"
        >
          <p className="mb-4 text-center text-sm font-medium text-brand-500">
            Question {currentIndex + 1} of {questions.length}
          </p>
          <h2 className="mb-8 text-center text-xl font-semibold leading-relaxed text-brand-800 sm:text-2xl">
            {currentQuestion.prompt}
          </h2>

          {currentQuestion.type === 'multiple-choice' ? (
            <div className="flex flex-col gap-3">
              {currentQuestion.options!.map((option, i) => {
                const selected = currentAnswer === option;
                return (
                  <button
                    key={i}
                    onClick={() => setAnswer(option)}
                    className={`group flex w-full items-center gap-4 rounded-2xl border-2 p-4 text-left transition-all duration-200 focus:outline-none focus-visible:ring-2 focus-visible:ring-brand-400 ${
                      selected
                        ? 'border-brand-400 bg-brand-50 shadow-md shadow-brand-200/40'
                        : 'border-brand-100/80 bg-white/40 hover:border-brand-200 hover:bg-white/70'
                    }`}
                  >
                    <span
                      className={`flex h-9 w-9 flex-shrink-0 items-center justify-center rounded-full text-sm font-bold transition-colors ${
                        selected
                          ? 'bg-brand-500 text-white'
                          : 'bg-brand-100 text-brand-500 group-hover:bg-brand-200'
                      }`}
                    >
                      {OPTION_LABELS[i]}
                    </span>
                    <span className={`text-base font-medium ${selected ? 'text-brand-800' : 'text-brand-700'}`}>
                      {option}
                    </span>
                  </button>
                );
              })}
            </div>
          ) : (
            <div>
              <input
                ref={inputRef}
                type="text"
                value={currentAnswer ?? ''}
                onChange={e => setAnswer(e.target.value)}
                onKeyDown={handleKeyDown}
                placeholder="Type your answer…"
                className="w-full rounded-2xl border-2 border-brand-100/80 bg-white/50 p-4 text-lg text-brand-800 placeholder:text-brand-300 backdrop-blur-sm transition-all focus:border-brand-400 focus:outline-none focus:ring-2 focus:ring-brand-200"
              />
              <p className="mt-3 text-center text-xs text-brand-400">
                Press Enter to continue
              </p>
            </div>
          )}
        </div>
      </div>

      {/* Navigation */}
      <div className="relative z-10 flex items-center justify-between px-6 py-5 sm:px-10">
        <button
          onClick={handleBack}
          disabled={currentIndex === 0}
          className="flex items-center gap-2 rounded-full border border-brand-200/60 bg-white/50 px-5 py-2.5 text-sm font-medium text-brand-700 backdrop-blur-sm transition-all hover:bg-white/80 hover:border-brand-300 disabled:pointer-events-none disabled:opacity-40 focus:outline-none focus-visible:ring-2 focus-visible:ring-brand-400"
        >
          <ArrowLeft className="h-4 w-4" strokeWidth={2} />
          Back
        </button>
        <button
          onClick={handleNext}
          disabled={!isAnswered}
          className="flex items-center gap-2 rounded-full bg-gradient-to-r from-brand-500 to-accent-500 px-6 py-2.5 text-sm font-semibold text-white shadow-lg shadow-brand-300/40 transition-all hover:shadow-xl hover:shadow-accent-300/40 hover:-translate-y-0.5 disabled:pointer-events-none disabled:opacity-40 disabled:shadow-none disabled:hover:translate-y-0 focus:outline-none focus-visible:ring-2 focus-visible:ring-brand-400 focus-visible:ring-offset-2"
        >
          {isLast ? 'Submit' : 'Next'}
          {!isLast && <ArrowRight className="h-4 w-4" strokeWidth={2} />}
        </button>
      </div>
    </div>
  );
}
