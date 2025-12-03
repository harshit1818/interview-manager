// Mock data for testing frontend independently without backend

import type { Question, Report } from '@/types';

export const mockQuestion: Question = {
  id: 'mock_q1',
  stem: 'Given an array of integers, find two numbers that add up to a specific target sum. Return the indices of these two numbers.',
  difficulty: 'easy',
  followUps: [
    'What is the time complexity of your solution?',
    'Can you optimize the space complexity?',
    'How would you handle duplicate numbers?',
  ],
  evaluationHints: [
    'Hash map approach for O(n) time',
    'Two-pointer technique',
    'Consider edge cases like empty array',
  ],
  redFlags: [
    'Nested loops without optimization discussion',
    'Not considering edge cases',
  ],
  asked: true,
  askedAt: new Date().toISOString(),
};

export const mockQuestions: Question[] = [
  mockQuestion,
  {
    id: 'mock_q2',
    stem: 'Explain how you would reverse a linked list. Can you do it iteratively and recursively?',
    difficulty: 'medium',
    followUps: [
      'What is the space complexity of the recursive approach?',
      'How would you handle a circular linked list?',
    ],
    evaluationHints: [
      'Three-pointer iterative approach',
      'Recursive base case and logic',
    ],
    redFlags: ['Not mentioning space complexity', 'Not handling null cases'],
    asked: false,
  },
  {
    id: 'mock_q3',
    stem: 'Design a data structure that supports insert, delete, and getRandom in O(1) time.',
    difficulty: 'hard',
    followUps: [
      'How do you ensure getRandom is truly random?',
      'What happens if we delete an element that doesn\'t exist?',
    ],
    evaluationHints: [
      'Combination of HashMap and ArrayList',
      'Swap-and-pop technique for delete',
    ],
    redFlags: ['Not achieving O(1) for all operations'],
    asked: false,
  },
];

export const mockReport: Report = {
  sessionId: 'mock-session-123',
  candidateName: 'John Doe',
  topic: 'DSA',
  difficulty: 'Junior',
  duration: 30,
  questionsAsked: 3,
  overallScore: 4.2,
  scores: {
    correctness: 4.0,
    communication: 4.5,
    approach: 4.0,
    edgeCases: 3.5,
  },
  strengths: [
    'Clear and structured communication',
    'Good understanding of time complexity',
    'Systematic problem-solving approach',
  ],
  weaknesses: [
    'Could improve on edge case handling',
    'Hesitation on space complexity analysis',
  ],
  integrityScore: 85.0,
  integrityIssues: 2,
  recommendation: 'hire',
  generatedAt: new Date().toISOString(),
};

export const mockTranscript = [
  {
    timestamp: new Date().toISOString(),
    speaker: 'ai',
    text: 'Hello John! Welcome to your technical interview. Let\'s start with a question about arrays.',
    type: 'question',
  },
  {
    timestamp: new Date().toISOString(),
    speaker: 'candidate',
    text: 'I would use a hash map to store the numbers I\'ve seen so far, and for each number, check if the complement exists in the hash map.',
    type: 'answer',
  },
  {
    timestamp: new Date().toISOString(),
    speaker: 'ai',
    text: 'Excellent approach! Can you tell me what the time complexity of this solution is?',
    type: 'follow_up',
  },
  {
    timestamp: new Date().toISOString(),
    speaker: 'candidate',
    text: 'The time complexity would be O(n) where n is the length of the array, since we iterate through it once.',
    type: 'answer',
  },
];
