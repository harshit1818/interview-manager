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
  ];

  // Introduction/discussion keywords (no code needed)
  const discussionKeywords = [
    'introduce yourself',
    'tell me about',
    'explain your',
    'describe your',
    'walk me through',
    'what is your experience',
    'why do you',
    'how do you',
  ];

  // Check for discussion keywords first (higher priority)
  const hasDiscussionKeyword = discussionKeywords.some(keyword =>
    lowerQuestion.includes(keyword)
  );

  if (hasDiscussionKeyword) {
    return false; // Don't show code editor for discussions
  }

  // Check for coding keywords
  const hasCodingKeyword = codingKeywords.some(keyword =>
    lowerQuestion.includes(keyword)
  );

  return hasCodingKeyword;
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
