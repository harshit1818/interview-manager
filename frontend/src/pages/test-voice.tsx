import { useState, useEffect } from 'react';
import Head from 'next/head';
import { useSpeechRecognition, useTextToSpeech } from '@/hooks/useVoice';

export default function TestVoicePage() {
  const { isListening, transcript, startListening, stopListening, resetTranscript, isSupported: sttSupported } = useSpeechRecognition();
  const { speak, stop, isSpeaking, isSupported: ttsSupported } = useTextToSpeech();
  const [testText, setTestText] = useState('Hello! This is a test of the text to speech system.');
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  return (
    <>
      <Head>
        <title>Voice Integration Test</title>
      </Head>

      <div className="min-h-screen bg-gray-50 p-8">
        <div className="max-w-4xl mx-auto">
          <h1 className="text-3xl font-bold text-gray-800 mb-8">Voice Integration Test Page</h1>

          {!mounted ? (
            <div className="text-center py-8">Loading...</div>
          ) : (
            <>
              {/* Browser Support Check */}
              <div className="bg-white rounded-lg shadow p-6 mb-6">
                <h2 className="text-xl font-semibold mb-4">Browser Support</h2>
                <div className="space-y-2">
                  <div className="flex items-center">
                    <div className={`w-4 h-4 rounded-full mr-2 ${sttSupported ? 'bg-green-500' : 'bg-red-500'}`}></div>
                    <span>Speech Recognition (STT): {sttSupported ? '✓ Supported' : '✗ Not Supported'}</span>
                  </div>
                  <div className="flex items-center">
                    <div className={`w-4 h-4 rounded-full mr-2 ${ttsSupported ? 'bg-green-500' : 'bg-red-500'}`}></div>
                    <span>Text-to-Speech (TTS): {ttsSupported ? '✓ Supported' : '✗ Not Supported'}</span>
                  </div>
                </div>
            {!sttSupported && (
              <p className="mt-4 text-sm text-amber-600">
                Note: Speech Recognition works best in Chrome. Try using Chrome if it's not working.
              </p>
            )}
          </div>

          {/* Text-to-Speech Test */}
          <div className="bg-white rounded-lg shadow p-6 mb-6">
            <h2 className="text-xl font-semibold mb-4">Text-to-Speech Test</h2>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Text to speak:
                </label>
                <textarea
                  value={testText}
                  onChange={(e) => setTestText(e.target.value)}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  rows={3}
                />
              </div>
              <div className="flex gap-4">
                <button
                  onClick={() => speak(testText)}
                  disabled={!ttsSupported || isSpeaking}
                  className="px-6 py-2 bg-blue-500 hover:bg-blue-600 text-white rounded-lg disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {isSpeaking ? 'Speaking...' : 'Speak Text'}
                </button>
                <button
                  onClick={stop}
                  disabled={!isSpeaking}
                  className="px-6 py-2 bg-red-500 hover:bg-red-600 text-white rounded-lg disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  Stop
                </button>
              </div>
              {isSpeaking && (
                <div className="p-3 bg-blue-50 rounded-lg">
                  <p className="text-sm text-blue-700">🔊 Speaking...</p>
                </div>
              )}
            </div>
          </div>

          {/* Speech Recognition Test */}
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-xl font-semibold mb-4">Speech Recognition Test</h2>
            <div className="space-y-4">
              <div className="flex gap-4">
                <button
                  onClick={isListening ? stopListening : startListening}
                  disabled={!sttSupported}
                  className={`px-6 py-2 rounded-lg font-semibold ${
                    isListening
                      ? 'bg-red-500 hover:bg-red-600'
                      : 'bg-green-500 hover:bg-green-600'
                  } text-white disabled:opacity-50 disabled:cursor-not-allowed`}
                >
                  {isListening ? '🔴 Stop Listening' : '🎤 Start Listening'}
                </button>
                <button
                  onClick={resetTranscript}
                  className="px-6 py-2 bg-gray-500 hover:bg-gray-600 text-white rounded-lg"
                >
                  Clear
                </button>
              </div>

              {isListening && (
                <div className="p-4 bg-green-50 rounded-lg border border-green-200">
                  <div className="flex items-center">
                    <div className="flex space-x-1 mr-3">
                      <div className="w-2 h-4 bg-green-500 rounded animate-pulse"></div>
                      <div className="w-2 h-6 bg-green-500 rounded animate-pulse" style={{ animationDelay: '0.2s' }}></div>
                      <div className="w-2 h-8 bg-green-500 rounded animate-pulse" style={{ animationDelay: '0.4s' }}></div>
                      <div className="w-2 h-6 bg-green-500 rounded animate-pulse" style={{ animationDelay: '0.6s' }}></div>
                    </div>
                    <p className="text-sm text-green-700 font-medium">Listening... Speak now!</p>
                  </div>
                </div>
              )}

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Transcript:
                </label>
                <div className="min-h-[100px] w-full px-4 py-3 border border-gray-300 rounded-lg bg-gray-50">
                  {transcript ? (
                    <p className="text-gray-800">{transcript}</p>
                  ) : (
                    <p className="text-gray-400 italic">
                      Click "Start Listening" and speak. Your words will appear here...
                    </p>
                  )}
                </div>
              </div>

              {transcript && (
                <button
                  onClick={() => speak(transcript)}
                  disabled={!ttsSupported || isSpeaking}
                  className="px-6 py-2 bg-purple-500 hover:bg-purple-600 text-white rounded-lg disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  🔊 Speak Back Transcript
                </button>
              )}
            </div>
          </div>

          {/* Instructions */}
          <div className="mt-6 p-4 bg-blue-50 border border-blue-200 rounded-lg">
            <h3 className="font-semibold text-blue-900 mb-2">Testing Instructions:</h3>
            <ol className="list-decimal list-inside space-y-1 text-sm text-blue-800">
              <li>Test Text-to-Speech: Click "Speak Text" button and listen</li>
              <li>Test Speech Recognition: Click "Start Listening" and speak clearly</li>
              <li>Check browser console for any errors</li>
              <li>Make sure you allow microphone access when prompted</li>
              <li>Works best in Chrome browser</li>
            </ol>
          </div>
          </>
          )}
        </div>
      </div>
    </>
  );
}
