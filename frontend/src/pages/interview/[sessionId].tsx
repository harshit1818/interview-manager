import { useEffect, useState } from 'react';
import { useRouter } from 'next/router';
import { interviewAPI } from '@/lib/api';
import { useSpeechRecognition, useTextToSpeech } from '@/hooks/useVoice';
import { useIntegrityDetection } from '@/hooks/useIntegrityDetection';
import type { Question, RespondResponse } from '@/types';

import VideoCall from '@/components/VideoCall';
import CodeEditor from '@/components/CodeEditor';
import TranscriptPanel from '@/components/TranscriptPanel';

export default function InterviewPage() {
  const router = useRouter();
  const { sessionId } = router.query;

  const [currentQuestion, setCurrentQuestion] = useState<Question | null>(null);
  const [isInterviewActive, setIsInterviewActive] = useState(false);
  const [transcript, setTranscript] = useState<any[]>([]);

  const { isListening, transcript: spokenText, startListening, stopListening, resetTranscript } = useSpeechRecognition();
  const { speak, isSpeaking } = useTextToSpeech();
  const { logEvent } = useIntegrityDetection({
    sessionId: sessionId as string,
    enabled: isInterviewActive,
  });

  useEffect(() => {
    if (sessionId) {
      loadInterviewStatus();
    }
  }, [sessionId]);

  const loadInterviewStatus = async () => {
    try {
      const status = await interviewAPI.getStatus(sessionId as string);
      setCurrentQuestion(status.currentQuestion);
      setIsInterviewActive(status.currentState === 'in_progress');

      // Speak the current question
      if (status.currentQuestion) {
        speak(status.currentQuestion.stem);
      }
    } catch (error) {
      console.error('Failed to load interview status:', error);
    }
  };

  const handleSubmitAnswer = async () => {
    if (!spokenText || !sessionId) return;

    stopListening();

    try {
      const response: RespondResponse = await interviewAPI.respond({
        sessionId: sessionId as string,
        transcript: spokenText,
        timestamp: Date.now(),
      });

      // Add to transcript
      setTranscript((prev) => [
        ...prev,
        { speaker: 'candidate', text: spokenText },
        { speaker: 'ai', text: response.aiResponse },
      ]);

      // Speak AI response
      speak(response.aiResponse);

      // Handle next action
      if (response.nextAction === 'next_question' && response.nextQuestion) {
        setCurrentQuestion(response.nextQuestion);
      } else if (response.nextAction === 'end_interview') {
        await endInterview();
      }

      resetTranscript();
    } catch (error) {
      console.error('Failed to submit answer:', error);
    }
  };

  const endInterview = async () => {
    try {
      const result = await interviewAPI.end(sessionId as string);
      router.push(`/report/${sessionId}`);
    } catch (error) {
      console.error('Failed to end interview:', error);
    }
  };

  return (
    <div className="min-h-screen bg-gray-100 p-4">
      <div className="max-w-7xl mx-auto">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
          {/* Main area */}
          <div className="lg:col-span-2 space-y-4">
            {/* Video Call */}
            <VideoCall sessionId={sessionId as string} />

            {/* Current Question */}
            {currentQuestion && (
              <div className="bg-white p-6 rounded-lg shadow">
                <h2 className="text-xl font-bold mb-4">Current Question</h2>
                <p className="text-gray-700">{currentQuestion.stem}</p>
              </div>
            )}

            {/* Code Editor */}
            <CodeEditor onPaste={(length) => logEvent('LARGE_PASTE', { length })} />

            {/* Answer Controls */}
            <div className="bg-white p-6 rounded-lg shadow">
              <div className="flex gap-4">
                <button
                  onClick={isListening ? stopListening : startListening}
                  className={`px-6 py-3 rounded-lg font-semibold ${
                    isListening
                      ? 'bg-red-500 hover:bg-red-600'
                      : 'bg-blue-500 hover:bg-blue-600'
                  } text-white`}
                  disabled={isSpeaking}
                >
                  {isListening ? 'Stop Recording' : 'Start Recording'}
                </button>

                <button
                  onClick={handleSubmitAnswer}
                  className="px-6 py-3 bg-green-500 hover:bg-green-600 text-white rounded-lg font-semibold"
                  disabled={!spokenText || isSpeaking}
                >
                  Submit Answer
                </button>

                <button
                  onClick={endInterview}
                  className="px-6 py-3 bg-gray-500 hover:bg-gray-600 text-white rounded-lg font-semibold"
                >
                  End Interview
                </button>
              </div>

              {spokenText && (
                <div className="mt-4 p-4 bg-gray-50 rounded">
                  <p className="text-sm text-gray-600">Your answer:</p>
                  <p className="text-gray-800">{spokenText}</p>
                </div>
              )}
            </div>
          </div>

          {/* Sidebar */}
          <div className="lg:col-span-1">
            <TranscriptPanel transcript={transcript} />
          </div>
        </div>
      </div>
    </div>
  );
}
