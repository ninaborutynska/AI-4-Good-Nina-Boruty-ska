export type QuestionType = 'multiple-choice' | 'open-answer';
export type Level = 'beginner' | 'intermediate' | 'advanced';

export interface Question {
  id: string;
  level: Level;
  type: QuestionType;
  prompt: string;
  options?: string[];
  correctAnswer: string;
  acceptedAnswers?: string[];
}

export const questionsByLevel: Record<Level, Question[]> = {
  beginner: [
    {
      id: 'b1',
      level: 'beginner',
      type: 'open-answer',
      prompt: 'Solve for x:  2x + 5 = 13',
      correctAnswer: '4',
    },
    {
      id: 'b2',
      level: 'beginner',
      type: 'open-answer',
      prompt: 'What is the area of a rectangle with length 6 and width 4?',
      correctAnswer: '24',
    },
    {
      id: 'b3',
      level: 'beginner',
      type: 'open-answer',
      prompt: 'What is the square root of 144?',
      correctAnswer: '12',
    },
    {
      id: 'b4',
      level: 'beginner',
      type: 'open-answer',
      prompt: 'In a right triangle with legs of length 3 and 4, what is the length of the hypotenuse?',
      correctAnswer: '5',
    },
    {
      id: 'b5',
      level: 'beginner',
      type: 'open-answer',
      prompt: 'What is 15% of 200?',
      correctAnswer: '30',
    },
    {
      id: 'b6',
      level: 'beginner',
      type: 'multiple-choice',
      prompt: 'Simplify:  3/4 + 1/4',
      options: ['1', '3/4', '1/2', '7/4'],
      correctAnswer: '1',
    },
    {
      id: 'b7',
      level: 'beginner',
      type: 'open-answer',
      prompt: 'What is the value of 2³?',
      correctAnswer: '8',
    },
    {
      id: 'b8',
      level: 'beginner',
      type: 'open-answer',
      prompt: 'Solve for x:  x − 7 = 3',
      correctAnswer: '10',
    },
    {
      id: 'b9',
      level: 'beginner',
      type: 'open-answer',
      prompt: 'What is the perimeter of a square with side length 5?',
      correctAnswer: '20',
    },
    {
      id: 'b10',
      level: 'beginner',
      type: 'multiple-choice',
      prompt: 'Which fraction is equivalent to 0.5?',
      options: ['1/2', '1/3', '1/4', '2/5'],
      correctAnswer: '1/2',
    },
  ],
  intermediate: [
    {
      id: 'i1',
      level: 'intermediate',
      type: 'open-answer',
      prompt: 'Solve for x:  3x − 7 = 2x + 5',
      correctAnswer: '12',
    },
    {
      id: 'i2',
      level: 'intermediate',
      type: 'multiple-choice',
      prompt: 'Factor:  x² − 9',
      options: ['(x − 3)(x + 3)', '(x − 9)(x + 1)', '(x + 3)²', '(x − 3)²'],
      correctAnswer: '(x − 3)(x + 3)',
    },
    {
      id: 'i3',
      level: 'intermediate',
      type: 'open-answer',
      prompt: 'What is the slope of the line passing through (1, 2) and (3, 8)?',
      correctAnswer: '3',
    },
    {
      id: 'i4',
      level: 'intermediate',
      type: 'multiple-choice',
      prompt: 'Simplify:  (2x²)(3x³)',
      options: ['6x⁵', '6x⁶', '5x⁵', '5x⁶'],
      correctAnswer: '6x⁵',
    },
    {
      id: 'i5',
      level: 'intermediate',
      type: 'open-answer',
      prompt: 'Solve for x (x > 0):  x² = 49',
      correctAnswer: '7',
    },
    {
      id: 'i6',
      level: 'intermediate',
      type: 'open-answer',
      prompt: 'What is the y-intercept of the line  y = 2x + 5?',
      correctAnswer: '5',
    },
    {
      id: 'i7',
      level: 'intermediate',
      type: 'open-answer',
      prompt: 'If  f(x) = 2x + 3,  what is  f(4)?',
      correctAnswer: '11',
    },
    {
      id: 'i8',
      level: 'intermediate',
      type: 'open-answer',
      prompt: 'Solve the system:  x + y = 10,  x − y = 4.  What is x?',
      correctAnswer: '7',
    },
    {
      id: 'i9',
      level: 'intermediate',
      type: 'multiple-choice',
      prompt: 'What is the value of  sin(30°)?',
      options: ['1/2', '√2 / 2', '√3 / 2', '1'],
      correctAnswer: '1/2',
    },
    {
      id: 'i10',
      level: 'intermediate',
      type: 'open-answer',
      prompt: 'Simplify:  12x ÷ 3x',
      correctAnswer: '4',
    },
  ],
  advanced: [
    {
      id: 'a1',
      level: 'advanced',
      type: 'multiple-choice',
      prompt: 'Solve for x:  2x² − 5x − 3 = 0',
      options: ['x = 3 or x = −1/2', 'x = 3 or x = 1/2', 'x = −3 or x = 1/2', 'x = −3 or x = −1/2'],
      correctAnswer: 'x = 3 or x = −1/2',
    },
    {
      id: 'a2',
      level: 'advanced',
      type: 'multiple-choice',
      prompt: 'What is the derivative of  f(x) = 3x² + 2x − 7?',
      options: ['6x + 2', '3x + 2', '6x² + 2', '6x − 7'],
      correctAnswer: '6x + 2',
    },
    {
      id: 'a3',
      level: 'advanced',
      type: 'open-answer',
      prompt: 'Evaluate:  lim(x→0) sin(x) / x',
      correctAnswer: '1',
    },
    {
      id: 'a4',
      level: 'advanced',
      type: 'open-answer',
      prompt: 'Solve for x:  log₂(x) = 5',
      correctAnswer: '32',
    },
    {
      id: 'a5',
      level: 'advanced',
      type: 'multiple-choice',
      prompt: 'What is the integral of  2x dx?',
      options: ['x² + C', 'x²', '2x² + C', 'x + C'],
      correctAnswer: 'x² + C',
    },
    {
      id: 'a6',
      level: 'advanced',
      type: 'open-answer',
      prompt: 'If  f(x) = x² − 3x + 2,  find  f′(2).',
      correctAnswer: '1',
    },
    {
      id: 'a7',
      level: 'advanced',
      type: 'multiple-choice',
      prompt: 'Solve for x:  |2x − 3| = 7',
      options: ['x = 5 or x = −2', 'x = 5 or x = 2', 'x = −5 or x = 2', 'x = 3 or x = −2'],
      correctAnswer: 'x = 5 or x = −2',
    },
    {
      id: 'a8',
      level: 'advanced',
      type: 'open-answer',
      prompt: 'What is the sum of the first 10 terms of the arithmetic sequence  2, 5, 8, …?',
      correctAnswer: '155',
    },
    {
      id: 'a9',
      level: 'advanced',
      type: 'open-answer',
      prompt: 'Simplify:  (x² + 2x − 8) / (x + 4)',
      correctAnswer: 'x − 2',
      acceptedAnswers: ['x-2'],
    },
    {
      id: 'a10',
      level: 'advanced',
      type: 'open-answer',
      prompt: 'What is the area under  y = x²  from  x = 0  to  x = 2?',
      correctAnswer: '8/3',
      acceptedAnswers: ['2 2/3'],
    },
  ],
};

export function normalizeAnswer(answer: string): string {
  return answer.trim().toLowerCase().replace(/\s+/g, ' ');
}

export function checkAnswer(userAnswer: string, question: Question): boolean {
  const normalized = normalizeAnswer(userAnswer);
  if (normalized === '') return false;
  if (normalized === normalizeAnswer(question.correctAnswer)) return true;
  if (question.acceptedAnswers) {
    return question.acceptedAnswers.some(a => normalizeAnswer(a) === normalized);
  }
  return false;
}
