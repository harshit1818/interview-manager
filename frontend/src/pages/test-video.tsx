import { useEffect, useRef, useState } from 'react';
import Head from 'next/head';
import { useVideoAnalysis } from '@/hooks/useVideoAnalysis';
import IntegrityWarning from '@/components/IntegrityWarning';

export default function TestVideoPage() {
  const videoRef = useRef<HTMLVideoElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [isVideoEnabled, setIsVideoEnabled] = useState(false);
  const [enableAnalysis, setEnableAnalysis] = useState(false);
  const [currentWarning, setCurrentWarning] = useState<any>(null);
  const [eventLog, setEventLog] = useState<Array<{ type: string; timestamp: number; metadata?: any }>>([]);

  useEffect(() => {
    startVideo();
    return () => stopVideo();
  }, []);

  const startVideo = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        video: { width: 640, height: 480 },
        audio: false,
      });

      if (videoRef.current) {
        videoRef.current.srcObject = stream;
        setIsVideoEnabled(true);
      }
    } catch (error) {
      console.error('Failed to start video:', error);
      alert('Camera access denied. Please allow camera access to test video analysis.');
    }
  };

  const stopVideo = () => {
    if (videoRef.current && videoRef.current.srcObject) {
      const stream = videoRef.current.srcObject as MediaStream;
      stream.getTracks().forEach((track) => track.stop());
    }
  };

  const logEvent = (type: string, metadata?: any) => {
    const event = { type, timestamp: Date.now(), metadata };
    setEventLog((prev) => [event, ...prev].slice(0, 20)); // Keep last 20 events
    setCurrentWarning(type);
  };

  const { isReady, analysisResult } = useVideoAnalysis({
    videoElement: videoRef.current,
    enabled: enableAnalysis && isVideoEnabled,
    onMultipleFaces: () => logEvent('MULTIPLE_FACES'),
    onGazeAway: (direction) => logEvent('GAZE_AWAY', { direction }),
  });

  return (
    <>
      <Head>
        <title>Video Analysis Test - AI Interview System</title>
      </Head>

      <div className="min-h-screen bg-gray-50 p-8">
        <div className="max-w-6xl mx-auto">
          <div className="mb-6">
            <h1 className="text-3xl font-bold text-gray-800 mb-2">Video Analysis Test Page</h1>
            <p className="text-gray-600">Test MediaPipe face detection, gaze tracking, and integrity monitoring</p>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Video Section */}
            <div className="space-y-4">
              {/* Video Display */}
              <div className="bg-white rounded-lg shadow p-6">
                <h2 className="text-xl font-semibold mb-4">Camera Feed</h2>
                <div className="relative">
                  <video
                    ref={videoRef}
                    autoPlay
                    muted
                    playsInline
                    className="w-full h-80 bg-gray-900 rounded-lg object-cover"
                  />
                  <canvas
                    ref={canvasRef}
                    className="absolute top-0 left-0 w-full h-80"
                    style={{ display: 'none' }}
                  />

                  {!isVideoEnabled && (
                    <div className="absolute inset-0 flex items-center justify-center bg-gray-900 rounded-lg">
                      <div className="text-center text-white">
                        <svg
                          className="w-12 h-12 mx-auto mb-2"
                          fill="none"
                          stroke="currentColor"
                          viewBox="0 0 24 24"
                        >
                          <path
                            strokeLinecap="round"
                            strokeLinejoin="round"
                            strokeWidth={2}
                            d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z"
                          />
                        </svg>
                        <p>Camera not available</p>
                      </div>
                    </div>
                  )}
                </div>

                {/* Camera Status */}
                <div className="mt-4 flex items-center justify-between">
                  <div className="flex items-center">
                    <div className={`w-2 h-2 rounded-full mr-2 ${isVideoEnabled ? 'bg-green-500' : 'bg-red-500'}`}></div>
                    <span className="text-sm text-gray-600">
                      Camera: {isVideoEnabled ? 'Connected' : 'Disconnected'}
                    </span>
                  </div>
                </div>
              </div>

              {/* Analysis Controls */}
              <div className="bg-white rounded-lg shadow p-6">
                <h2 className="text-xl font-semibold mb-4">Analysis Controls</h2>

                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <span className="text-sm font-medium text-gray-700">Enable Video Analysis</span>
                    <button
                      onClick={() => setEnableAnalysis(!enableAnalysis)}
                      className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
                        enableAnalysis ? 'bg-blue-600' : 'bg-gray-300'
                      }`}
                      disabled={!isVideoEnabled}
                    >
                      <span
                        className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                          enableAnalysis ? 'translate-x-6' : 'translate-x-1'
                        }`}
                      />
                    </button>
                  </div>

                  {enableAnalysis && (
                    <div className="p-3 bg-blue-50 rounded-lg border border-blue-200">
                      <div className="flex items-center mb-2">
                        <div className={`w-2 h-2 rounded-full mr-2 ${isReady ? 'bg-green-500 animate-pulse' : 'bg-yellow-500'}`}></div>
                        <span className="text-sm font-medium text-blue-900">
                          {isReady ? 'MediaPipe Active' : 'Loading MediaPipe...'}
                        </span>
                      </div>
                      {!isReady && (
                        <p className="text-xs text-blue-700">
                          Downloading face detection models from CDN...
                        </p>
                      )}
                    </div>
                  )}

                  <button
                    onClick={() => setEventLog([])}
                    className="w-full px-4 py-2 bg-gray-200 hover:bg-gray-300 text-gray-700 rounded-lg text-sm font-medium transition"
                  >
                    Clear Event Log
                  </button>
                </div>
              </div>
            </div>

            {/* Analysis Results Section */}
            <div className="space-y-4">
              {/* Real-time Analysis */}
              <div className="bg-white rounded-lg shadow p-6">
                <h2 className="text-xl font-semibold mb-4">Real-time Analysis</h2>

                {!enableAnalysis ? (
                  <p className="text-gray-500 text-sm">Enable analysis to see results...</p>
                ) : !isReady ? (
                  <div className="flex items-center justify-center h-32">
                    <div className="text-center">
                      <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500 mx-auto mb-2"></div>
                      <p className="text-sm text-gray-600">Loading MediaPipe...</p>
                    </div>
                  </div>
                ) : (
                  <div className="space-y-3">
                    {/* Face Count */}
                    <div className="p-3 bg-gray-50 rounded-lg">
                      <div className="flex items-center justify-between">
                        <span className="text-sm font-medium text-gray-700">Faces Detected:</span>
                        <span
                          className={`text-lg font-bold ${
                            analysisResult.faceCount === 1
                              ? 'text-green-600'
                              : analysisResult.faceCount === 0
                              ? 'text-gray-400'
                              : 'text-red-600'
                          }`}
                        >
                          {analysisResult.faceCount}
                        </span>
                      </div>
                      {analysisResult.faceCount > 1 && (
                        <p className="text-xs text-red-600 mt-1">⚠️ Multiple people detected!</p>
                      )}
                      {analysisResult.faceCount === 0 && (
                        <p className="text-xs text-gray-500 mt-1">No face detected in frame</p>
                      )}
                    </div>

                    {/* Gaze Direction */}
                    <div className="p-3 bg-gray-50 rounded-lg">
                      <div className="flex items-center justify-between mb-2">
                        <span className="text-sm font-medium text-gray-700">Gaze Direction:</span>
                        <span
                          className={`text-sm font-semibold ${
                            !analysisResult.isLookingAway ? 'text-green-600' : 'text-amber-600'
                          }`}
                        >
                          {!analysisResult.isLookingAway ? '✓ On Screen' : '⚠️ Looking Away'}
                        </span>
                      </div>
                      <div className="grid grid-cols-2 gap-2 text-xs text-gray-600">
                        <div>Horizontal: {analysisResult.gazeDirection.x.toFixed(2)}</div>
                        <div>Vertical: {analysisResult.gazeDirection.y.toFixed(2)}</div>
                      </div>
                    </div>

                    {/* Confidence */}
                    <div className="p-3 bg-gray-50 rounded-lg">
                      <div className="flex items-center justify-between">
                        <span className="text-sm font-medium text-gray-700">Detection Confidence:</span>
                        <span className="text-sm font-semibold text-blue-600">
                          {(analysisResult.confidence * 100).toFixed(0)}%
                        </span>
                      </div>
                      <div className="mt-2 w-full bg-gray-200 rounded-full h-2">
                        <div
                          className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                          style={{ width: `${analysisResult.confidence * 100}%` }}
                        ></div>
                      </div>
                    </div>
                  </div>
                )}
              </div>

              {/* Event Log */}
              <div className="bg-white rounded-lg shadow p-6">
                <h2 className="text-xl font-semibold mb-4">Integrity Event Log</h2>
                <div className="space-y-2 max-h-96 overflow-y-auto scrollbar-thin">
                  {eventLog.length === 0 ? (
                    <p className="text-gray-500 text-sm text-center py-4">No events logged yet...</p>
                  ) : (
                    eventLog.map((event, index) => (
                      <div
                        key={index}
                        className={`p-3 rounded-lg border-l-4 ${
                          event.type === 'MULTIPLE_FACES'
                            ? 'bg-red-50 border-red-500'
                            : event.type === 'GAZE_AWAY'
                            ? 'bg-amber-50 border-amber-500'
                            : 'bg-blue-50 border-blue-500'
                        }`}
                      >
                        <div className="flex items-center justify-between">
                          <span className="text-sm font-semibold text-gray-800">{event.type}</span>
                          <span className="text-xs text-gray-500">
                            {new Date(event.timestamp).toLocaleTimeString()}
                          </span>
                        </div>
                        {event.metadata && (
                          <pre className="text-xs text-gray-600 mt-1 overflow-x-auto">
                            {JSON.stringify(event.metadata, null, 2)}
                          </pre>
                        )}
                      </div>
                    ))
                  )}
                </div>
              </div>
            </div>
          </div>

          {/* Instructions */}
          <div className="mt-6 bg-gradient-to-r from-blue-500 to-purple-600 rounded-lg p-6 text-white">
            <h3 className="font-semibold text-lg mb-3">Testing Instructions</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
              <div>
                <h4 className="font-semibold mb-2">✅ To Test:</h4>
                <ul className="space-y-1 text-blue-100">
                  <li>1. Allow camera access when prompted</li>
                  <li>2. Enable "Video Analysis" toggle</li>
                  <li>3. Wait for MediaPipe to load (~5-10 seconds)</li>
                  <li>4. See real-time face detection</li>
                </ul>
              </div>
              <div>
                <h4 className="font-semibold mb-2">🧪 Try These:</h4>
                <ul className="space-y-1 text-blue-100">
                  <li>• Look away from screen → Gaze warning</li>
                  <li>• Have someone join you → Multiple faces</li>
                  <li>• Cover your face → No face detected</li>
                  <li>• Look left/right/up/down → Track direction</li>
                </ul>
              </div>
            </div>
          </div>

          {/* Technical Details */}
          <div className="mt-6 bg-white rounded-lg shadow p-6">
            <h3 className="font-semibold text-lg mb-3 text-gray-800">Technical Details</h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
              <div className="p-3 bg-gray-50 rounded">
                <p className="font-medium text-gray-700 mb-1">Technology:</p>
                <p className="text-gray-600">MediaPipe Face Mesh</p>
              </div>
              <div className="p-3 bg-gray-50 rounded">
                <p className="font-medium text-gray-700 mb-1">Landmarks:</p>
                <p className="text-gray-600">468 facial points</p>
              </div>
              <div className="p-3 bg-gray-50 rounded">
                <p className="font-medium text-gray-700 mb-1">Processing:</p>
                <p className="text-gray-600">Client-side (browser)</p>
              </div>
            </div>
          </div>
        </div>

        {/* Warning Overlay */}
        <IntegrityWarning type={currentWarning} onClose={() => setCurrentWarning(null)} />
      </div>
    </>
  );
}
