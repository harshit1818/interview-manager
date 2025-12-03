import { useEffect, useState } from 'react';
import { useRouter } from 'next/router';
import Head from 'next/head';
import { interviewAPI } from '@/lib/api';
import { useSpeechRecognition, useTextToSpeech } from '@/hooks/useVoice';
import { useIntegrityDetection } from '@/hooks/useIntegrityDetection';
import type { Question, RespondResponse } from '@/types';

import VideoCall from '@/components/VideoCall';
import CodeEditor from '@/components/CodeEditor';
import TranscriptPanel from '@/components/TranscriptPanel';
import Loading from '@/components/Loading';

export default function InterviewPage() {
  const router = useRouter();
  const { sessionId } = router.query;

  const [currentQuestion, setCurrentQuestion] = useState<Question | null>(null);
  const [isInterviewActive, setIsInterviewActive] = useState(false);
  const [transcript, setTranscript] = useState<any[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [timeRemaining, setTimeRemaining] = useState<number>(0);

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
    if (!sessionId) return;

    try {
      setIsLoading(true);
      const status = await interviewAPI.getStatus(sessionId as string);
      setCurrentQuestion(status.currentQuestion);
      setIsInterviewActive(status.currentState === 'in_progress');
      setTimeRemaining(status.timeRemaining);

      // Speak the current question
      if (status.currentQuestion) {
        speak(status.currentQuestion.stem);
      }
    } catch (error) {
      console.error('Failed to load interview status:', error);
      setError('Failed to load interview. Please check if the backend is running.');
    } finally {
      setIsLoading(false);
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

  if (isLoading) {
    return <Loading message="Loading interview..." />;
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center p-4">
        <div className="bg-white rounded-lg shadow-lg p-8 max-w-md w-full text-center">
          <svg
            className="w-16 h-16 text-red-500 mx-auto mb-4"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
            />
          </svg>
          <h2 className="text-xl font-bold text-gray-800 mb-2">Error</h2>
          <p className="text-gray-600 mb-6">{error}</p>
          <button
            onClick={() => router.push('/')}
            className="px-6 py-2 bg-blue-500 hover:bg-blue-600 text-white rounded-lg"
          >
            Go Back
          </button>
        </div>
      </div>
    );
  }

  return (
    <>
      <Head>
        <title>Interview in Progress - AI Interview System</title>
      </Head>

      <div className="min-h-screen bg-gray-50 p-4">
        {/* Header Bar */}
        <div className="max-w-7xl mx-auto mb-4">
          <div className="bg-white rounded-lg shadow px-6 py-4 flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <div className="flex items-center">
                <div className="w-3 h-3 bg-red-500 rounded-full animate-pulse mr-2"></div>
                <span className="text-sm font-medium text-gray-700">Interview in Progress</span>
              </div>
              <div className="border-l pl-4 text-sm text-gray-600">
                Time Remaining: <span className="font-semibold">{timeRemaining} min</span>
              </div>
            </div>
            <button
              onClick={endInterview}
              className="px-4 py-2 bg-gray-200 hover:bg-gray-300 text-gray-700 rounded-lg text-sm font-medium transition"
            >
              End Interview
            </button>
          </div>
        </div>

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
              <div className="grid grid-cols-2 gap-4">
                <button
                  onClick={isListening ? stopListening : startListening}
                  className={`flex items-center justify-center px-6 py-4 rounded-lg font-semibold transition-all ${
                    isListening
                      ? 'bg-red-500 hover:bg-red-600 shadow-lg shadow-red-500/50'
                      : 'bg-blue-500 hover:bg-blue-600 shadow-lg shadow-blue-500/50'
                  } text-white`}
                  disabled={isSpeaking}
                >
                  <svg
                    className="w-5 h-5 mr-2"
                    fill="currentColor"
                    viewBox="0 0 20 20"
                  >
                    {isListening ? (
                      <path
                        fillRule="evenodd"
                        d="M10 18a8 8 0 100-16 8 8 0 000 16zM8 7a1 1 0 00-1 1v4a1 1 0 001 1h4a1 1 0 001-1V8a1 1 0 00-1-1H8z"
                        clipRule="evenodd"
                      />
                    ) : (
                      <path d="M7 4a3 3 0 016 0v4a3 3 0 11-6 0V4zm4 10.93A7.001 7.001 0 0017 8a1 1 0 10-2 0A5 5 0 015 8a1 1 0 00-2 0 7.001 7.001 0 006 6.93V17H6a1 1 0 100 2h8a1 1 0 100-2h-3v-2.07z" />
                    )}
                  </svg>
                  {isListening ? 'Stop Recording' : 'Start Recording'}
                </button>

                <button
                  onClick={handleSubmitAnswer}
                  className="flex items-center justify-center px-6 py-4 bg-gradient-to-r from-green-500 to-emerald-600 hover:from-green-600 hover:to-emerald-700 text-white rounded-lg font-semibold shadow-lg shadow-green-500/50 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
                  disabled={!spokenText || isSpeaking}
                >
                  <svg
                    className="w-5 h-5 mr-2"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
                    />
                  </svg>
                  Submit Answer
                </button>
              </div>

              {isListening && (
                <div className="mt-4 p-4 bg-blue-50 rounded-lg border border-blue-200">
                  <div className="flex items-center">
                    <div className="flex space-x-1 mr-3">
                      <div className="w-2 h-4 bg-blue-500 rounded animate-pulse"></div>
                      <div className="w-2 h-6 bg-blue-500 rounded animate-pulse" style={{ animationDelay: '0.2s' }}></div>
                      <div className="w-2 h-8 bg-blue-500 rounded animate-pulse" style={{ animationDelay: '0.4s' }}></div>
                      <div className="w-2 h-6 bg-blue-500 rounded animate-pulse" style={{ animationDelay: '0.6s' }}></div>
                    </div>
                    <p className="text-sm text-blue-700 font-medium">Listening...</p>
                  </div>
                </div>
              )}

              {spokenText && !isListening && (
                <div className="mt-4 p-4 bg-green-50 rounded-lg border border-green-200">
                  <p className="text-sm font-medium text-green-700 mb-2">Your answer:</p>
                  <p className="text-gray-800 leading-relaxed">{spokenText}</p>
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
    </>
  );
}
