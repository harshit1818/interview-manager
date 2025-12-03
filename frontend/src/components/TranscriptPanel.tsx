interface TranscriptPanelProps {
  transcript: Array<{ speaker: string; text: string }>;
}

export default function TranscriptPanel({ transcript }: TranscriptPanelProps) {
  return (
    <div className="bg-white p-6 rounded-lg shadow h-full">
      <h2 className="text-xl font-bold mb-4">Transcript</h2>
      <div className="space-y-4 max-h-[600px] overflow-y-auto">
        {transcript.length === 0 ? (
          <p className="text-gray-500 text-sm">Conversation will appear here...</p>
        ) : (
          transcript.map((turn, index) => (
            <div
              key={index}
              className={`p-3 rounded-lg ${
                turn.speaker === 'ai'
                  ? 'bg-blue-50 border-l-4 border-blue-500'
                  : 'bg-green-50 border-l-4 border-green-500'
              }`}
            >
              <p className="text-xs font-semibold text-gray-600 mb-1">
                {turn.speaker === 'ai' ? 'AI Interviewer' : 'You'}
              </p>
              <p className="text-sm text-gray-800">{turn.text}</p>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
