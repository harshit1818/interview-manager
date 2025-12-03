import { useRef, useState } from 'react';
import Editor from '@monaco-editor/react';

interface CodeEditorProps {
  onPaste: (length: number) => void;
  initialLanguage?: string;
  onCodeChange?: (code: string, language: string) => void;
}

const SUPPORTED_LANGUAGES = [
  { value: 'javascript', label: 'JavaScript' },
  { value: 'typescript', label: 'TypeScript' },
  { value: 'python', label: 'Python' },
  { value: 'java', label: 'Java' },
  { value: 'cpp', label: 'C++' },
  { value: 'c', label: 'C' },
  { value: 'go', label: 'Go' },
  { value: 'rust', label: 'Rust' },
  { value: 'csharp', label: 'C#' },
  { value: 'ruby', label: 'Ruby' },
  { value: 'php', label: 'PHP' },
  { value: 'swift', label: 'Swift' },
  { value: 'kotlin', label: 'Kotlin' },
  { value: 'sql', label: 'SQL' },
];

const DEFAULT_CODE_TEMPLATES: Record<string, string> = {
  javascript: '// Write your JavaScript code here...\n\nfunction solution() {\n  \n}',
  typescript: '// Write your TypeScript code here...\n\nfunction solution(): void {\n  \n}',
  python: '# Write your Python code here...\n\ndef solution():\n    pass',
  java: '// Write your Java code here...\n\npublic class Solution {\n    public void solve() {\n        \n    }\n}',
  cpp: '// Write your C++ code here...\n\n#include <iostream>\nusing namespace std;\n\nint main() {\n    \n    return 0;\n}',
  c: '// Write your C code here...\n\n#include <stdio.h>\n\nint main() {\n    \n    return 0;\n}',
  go: '// Write your Go code here...\n\npackage main\n\nfunc main() {\n    \n}',
  rust: '// Write your Rust code here...\n\nfn main() {\n    \n}',
  csharp: '// Write your C# code here...\n\nusing System;\n\nclass Program {\n    static void Main() {\n        \n    }\n}',
  ruby: '# Write your Ruby code here...\n\ndef solution\n  \nend',
  php: '<?php\n// Write your PHP code here...\n\nfunction solution() {\n    \n}\n?>',
  swift: '// Write your Swift code here...\n\nfunc solution() {\n    \n}',
  kotlin: '// Write your Kotlin code here...\n\nfun main() {\n    \n}',
  sql: '-- Write your SQL query here...\n\nSELECT * FROM table_name;',
};

export default function CodeEditor({ onPaste, initialLanguage = 'javascript', onCodeChange }: CodeEditorProps) {
  const editorRef = useRef<any>(null);
  const [language, setLanguage] = useState(initialLanguage);
  const [code, setCode] = useState(DEFAULT_CODE_TEMPLATES[initialLanguage] || '// Write your code here...');
  const [isRunning, setIsRunning] = useState(false);
  const [output, setOutput] = useState<string>('');
  const [showOutput, setShowOutput] = useState(false);

  const handleCodeChange = (value: string | undefined) => {
    const newCode = value || '';
    setCode(newCode);
    // Notify parent component of code changes
    onCodeChange?.(newCode, language);
  };

  const handleEditorDidMount = (editor: any) => {
    editorRef.current = editor;

    // Detect large pastes
    editor.onDidPaste((e: any) => {
      const model = editor.getModel();
      if (model) {
        const text = model.getValue();
        if (text.length > 50) {
          onPaste(text.length);
        }
      }
    });
  };

  const handleLanguageChange = (newLanguage: string) => {
    setLanguage(newLanguage);
    const newCode = DEFAULT_CODE_TEMPLATES[newLanguage] || '// Write your code here...';
    setCode(newCode);
    onCodeChange?.(newCode, newLanguage);
  };

  // Expose method to get current code
  const getCode = () => {
    return {
      code,
      language,
      hasCode: code.trim().length > 0 && code !== DEFAULT_CODE_TEMPLATES[language]
    };
  };

  // Run code using Piston API (completely free, no API key needed!)
  const handleRunCode = async () => {
    setIsRunning(true);
    setShowOutput(true);
    setOutput('Compiling and running...');

    try {
      // Map our language names to Piston API language names
      const languageMap: Record<string, { language: string; version: string }> = {
        'javascript': { language: 'javascript', version: '18.15.0' },
        'typescript': { language: 'typescript', version: '5.0.3' },
        'python': { language: 'python', version: '3.10.0' },
        'java': { language: 'java', version: '15.0.2' },
        'cpp': { language: 'c++', version: '10.2.0' },
        'c': { language: 'c', version: '10.2.0' },
        'go': { language: 'go', version: '1.16.2' },
        'rust': { language: 'rust', version: '1.68.2' },
        'csharp': { language: 'csharp', version: '6.12.0' },
        'ruby': { language: 'ruby', version: '3.0.1' },
        'php': { language: 'php', version: '8.2.3' },
        'swift': { language: 'swift', version: '5.3.3' },
        'kotlin': { language: 'kotlin', version: '1.8.20' },
        'sql': { language: 'sqlite3', version: '3.36.0' },
      };

      const pistonLang = languageMap[language] || { language: 'javascript', version: '18.15.0' };

      // Submit code to Piston API (completely free!)
      const response = await fetch('https://emkc.org/api/v2/piston/execute', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          language: pistonLang.language,
          version: pistonLang.version,
          files: [
            {
              name: `main.${getFileExtension(language)}`,
              content: code,
            },
          ],
        }),
      });

      const result = await response.json();

      // Display output
      if (result.run) {
        if (result.run.stdout) {
          setOutput(`✅ Output:\n${result.run.stdout}`);
        } else if (result.run.stderr) {
          setOutput(`❌ Error:\n${result.run.stderr}`);
        } else if (result.run.output) {
          setOutput(`ℹ️ ${result.run.output}`);
        } else {
          setOutput('✅ Code executed successfully (no output)');
        }
      } else if (result.message) {
        setOutput(`❌ ${result.message}`);
      } else {
        setOutput('✅ Code executed successfully');
      }
    } catch (error) {
      setOutput(`❌ Failed to run code: ${error instanceof Error ? error.message : 'Unknown error'}\n\nTip: Check your internet connection.`);
    } finally {
      setIsRunning(false);
    }
  };

  // Helper function to get file extension
  const getFileExtension = (lang: string): string => {
    const extensions: Record<string, string> = {
      'javascript': 'js',
      'typescript': 'ts',
      'python': 'py',
      'java': 'java',
      'cpp': 'cpp',
      'c': 'c',
      'go': 'go',
      'rust': 'rs',
      'csharp': 'cs',
      'ruby': 'rb',
      'php': 'php',
      'swift': 'swift',
      'kotlin': 'kt',
      'sql': 'sql',
    };
    return extensions[lang] || 'txt';
  };

  return (
    <div className="bg-white p-6 rounded-lg shadow">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-xl font-bold">Code Editor</h2>

        <div className="flex items-center gap-3">
          {/* Run Button */}
          <button
            onClick={handleRunCode}
            disabled={isRunning || !code.trim()}
            className="flex items-center gap-2 px-4 py-2 bg-green-500 hover:bg-green-600 text-white rounded-lg text-sm font-medium transition disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isRunning ? (
              <>
                <svg className="animate-spin h-4 w-4" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                Running...
              </>
            ) : (
              <>
                <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM9.555 7.168A1 1 0 008 8v4a1 1 0 001.555.832l3-2a1 1 0 000-1.664l-3-2z" clipRule="evenodd" />
                </svg>
                Run Code
              </>
            )}
          </button>

          {/* Language Selector */}
          <div className="flex items-center gap-2">
            <label className="text-sm font-medium text-gray-700">Language:</label>
            <select
              value={language}
              onChange={(e) => handleLanguageChange(e.target.value)}
              className="px-3 py-1.5 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              {SUPPORTED_LANGUAGES.map((lang) => (
                <option key={lang.value} value={lang.value}>
                  {lang.label}
                </option>
              ))}
            </select>
          </div>
        </div>
      </div>

      <div className="border border-gray-300 rounded-lg overflow-hidden">
        <Editor
          height="400px"
          language={language}
          value={code}
          onChange={handleCodeChange}
          theme="vs-light"
          onMount={handleEditorDidMount}
          options={{
            minimap: { enabled: false },
            fontSize: 14,
            lineNumbers: 'on',
            scrollBeyondLastLine: false,
            automaticLayout: true,
            tabSize: language === 'python' ? 4 : 2,
            insertSpaces: true,
            wordWrap: 'on',
            formatOnPaste: true,
            formatOnType: true,
          }}
        />
      </div>

      {/* Output Panel */}
      {showOutput && (
        <div className="mt-4 border border-gray-300 rounded-lg overflow-hidden">
          <div className="flex items-center justify-between bg-gray-100 px-4 py-2 border-b border-gray-300">
            <div className="flex items-center gap-2">
              <svg className="w-4 h-4 text-gray-600" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
              </svg>
              <span className="text-sm font-medium text-gray-700">Output</span>
            </div>
            <button
              onClick={() => setShowOutput(false)}
              className="text-gray-400 hover:text-gray-600"
            >
              <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clipRule="evenodd" />
              </svg>
            </button>
          </div>
          <pre className="p-4 bg-gray-900 text-green-400 text-sm font-mono overflow-x-auto max-h-48 overflow-y-auto">
            {output}
          </pre>
        </div>
      )}

      {/* Language Info */}
      <div className="mt-2 text-xs text-gray-500 flex items-center justify-between">
        <span>
          {language === 'python' && '💡 Python uses 4-space indentation'}
          {language === 'javascript' && '💡 Use modern ES6+ syntax'}
          {language === 'java' && '💡 Remember to handle exceptions'}
          {language === 'cpp' && '💡 Remember to include necessary headers'}
          {language === 'go' && '💡 Use gofmt-style formatting'}
        </span>
        {showOutput && (
          <button
            onClick={() => setOutput('')}
            className="text-blue-500 hover:text-blue-600 text-xs"
          >
            Clear Output
          </button>
        )}
      </div>
    </div>
  );
}
