// Detect if a question requires code implementation

export const needsCodeEditor = (questionText: string): boolean => {
  if (!questionText) return false;

  const lowerQuestion = questionText.toLowerCase();

  // Keywords that indicate coding is needed
  const codingKeywords = [
    'implement',
    'write a function',
    'write code',
    'code',
    'algorithm',
    'write a program',
    'create a function',
    'solve',
    'return',
    'given an array',
    'find',
    'calculate',
    'optimize',
    'reverse',
    'sort',
    'search',
    'merge',
    'build',
    'design a class',
    'create a method',
    'write a solution',
    'dsa problem',
    'coding challenge',
    'programming',
    'array',
    'linked list',
    'tree',
    'graph',
    'hash',
  ];

  // Introduction/discussion keywords (no code needed) - must be very specific
  const discussionKeywords = [
    'introduce yourself',
    'tell me about yourself',
    'tell me about your background',
    'tell me about your experience',
    'what is your experience',
    'why do you',
  ];

  // Check for discussion keywords first (higher priority) - but only for personal questions
  const hasDiscussionKeyword = discussionKeywords.some(keyword =>
    lowerQuestion.includes(keyword)
  );

  if (hasDiscussionKeyword && !lowerQuestion.includes('dsa') && !lowerQuestion.includes('problem')) {
    return false; // Don't show code editor for personal discussions only
  }

  // Check for coding keywords
  const hasCodingKeyword = codingKeywords.some(keyword =>
    lowerQuestion.includes(keyword)
  );

  // Default to showing code editor for technical topics
  const isTechnicalTopic = lowerQuestion.includes('dsa') ||
                           lowerQuestion.includes('algorithm') ||
                           lowerQuestion.includes('data structure') ||
                           lowerQuestion.includes('coding') ||
                           lowerQuestion.includes('programming');

  return hasCodingKeyword || isTechnicalTopic;
};

export const getQuestionType = (questionText: string): 'introduction' | 'discussion' | 'coding' | 'conceptual' => {
  if (!questionText) return 'conceptual';

  const lowerQuestion = questionText.toLowerCase();

  // Introduction questions
  if (
    lowerQuestion.includes('introduce') ||
    lowerQuestion.includes('tell me about yourself') ||
    lowerQuestion.includes('walk me through your background')
  ) {
    return 'introduction';
  }

  // Coding questions
  if (needsCodeEditor(questionText)) {
    return 'coding';
  }

  // Discussion questions
  if (
    lowerQuestion.includes('explain') ||
    lowerQuestion.includes('describe') ||
    lowerQuestion.includes('discuss') ||
    lowerQuestion.includes('what are') ||
    lowerQuestion.includes('how would you')
  ) {
    return 'discussion';
  }

  return 'conceptual';
};
