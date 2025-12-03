import { useRef } from 'react';
import Editor from '@monaco-editor/react';

interface CodeEditorProps {
  onPaste: (length: number) => void;
}

export default function CodeEditor({ onPaste }: CodeEditorProps) {
  const editorRef = useRef<any>(null);

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

  return (
    <div className="bg-white p-6 rounded-lg shadow">
      <h2 className="text-xl font-bold mb-4">Code Editor</h2>
      <div className="border border-gray-300 rounded-lg overflow-hidden">
        <Editor
          height="400px"
          defaultLanguage="javascript"
          defaultValue="// Write your code here..."
          theme="vs-light"
          onMount={handleEditorDidMount}
          options={{
            minimap: { enabled: false },
            fontSize: 14,
            lineNumbers: 'on',
            scrollBeyondLastLine: false,
            automaticLayout: true,
          }}
        />
      </div>
    </div>
  );
}
