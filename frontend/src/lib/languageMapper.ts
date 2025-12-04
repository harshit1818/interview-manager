// Map interview topics to appropriate programming languages

export const getDefaultLanguageForTopic = (topic: string): string => {
  const topicLower = topic.toLowerCase();

  // Topic-based language mapping
  const topicLanguageMap: Record<string, string> = {
    'dsa': 'python',              // Data Structures & Algorithms - Python is popular
    'data structures': 'python',
    'algorithms': 'python',
    'react': 'javascript',        // React - JavaScript/JSX
    'frontend': 'javascript',
    'javascript': 'javascript',
    'typescript': 'typescript',
    'backend apis': 'javascript', // Backend APIs - Node.js
    'nodejs': 'javascript',
    'node': 'javascript',
    'python': 'python',
    'django': 'python',
    'flask': 'python',
    'java': 'java',
    'spring': 'java',
    'c++': 'cpp',
    'cpp': 'cpp',
    'go': 'go',
    'golang': 'go',
    'rust': 'rust',
    'c#': 'csharp',
    'dotnet': 'csharp',
    '.net': 'csharp',
    'ruby': 'ruby',
    'rails': 'ruby',
    'php': 'php',
    'laravel': 'php',
    'swift': 'swift',
    'ios': 'swift',
    'kotlin': 'kotlin',
    'android': 'kotlin',
    'sql': 'sql',
    'database': 'sql',
    'system design': 'python',   // System Design - often uses Python for examples
  };

  // Check for matches
  for (const [key, lang] of Object.entries(topicLanguageMap)) {
    if (topicLower.includes(key)) {
      return lang;
    }
  }

  // Default to JavaScript if no match
  return 'javascript';
};

export const getLanguageDisplayName = (languageCode: string): string => {
  const displayNames: Record<string, string> = {
    'javascript': 'JavaScript',
    'typescript': 'TypeScript',
    'python': 'Python',
    'java': 'Java',
    'cpp': 'C++',
    'c': 'C',
    'go': 'Go',
    'rust': 'Rust',
    'csharp': 'C#',
    'ruby': 'Ruby',
    'php': 'PHP',
    'swift': 'Swift',
    'kotlin': 'Kotlin',
    'sql': 'SQL',
  };

  return displayNames[languageCode] || languageCode.toUpperCase();
};
