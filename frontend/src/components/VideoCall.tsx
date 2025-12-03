import { useEffect, useRef, useState } from 'react';
import { useVideoAnalysis } from '@/hooks/useVideoAnalysis';

interface VideoCallProps {
  sessionId: string;
  onIntegrityEvent?: (eventType: string, metadata: any) => void;
  enableAnalysis?: boolean;
}

export default function VideoCall({
  sessionId,
  onIntegrityEvent,
  enableAnalysis = true
}: VideoCallProps) {
  const videoRef = useRef<HTMLVideoElement>(null);
  const [isVideoEnabled, setIsVideoEnabled] = useState(false);
  const [showAnalysisOverlay, setShowAnalysisOverlay] = useState(true);

  useEffect(() => {
    startVideo();

    return () => {
      stopVideo();
    };
  }, []);

  const startVideo = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        video: true,
        audio: true,
      });

      if (videoRef.current) {
        videoRef.current.srcObject = stream;
        setIsVideoEnabled(true);
      }
    } catch (error) {
      console.error('Failed to start video:', error);
    }
  };

  const stopVideo = () => {
    if (videoRef.current && videoRef.current.srcObject) {
      const stream = videoRef.current.srcObject as MediaStream;
      stream.getTracks().forEach((track) => track.stop());
    }
  };

  // Video analysis with MediaPipe
  const { isReady, analysisResult } = useVideoAnalysis({
    videoElement: videoRef.current,
    enabled: enableAnalysis && isVideoEnabled,
    onMultipleFaces: () => {
      console.log('Multiple faces detected!');
      onIntegrityEvent?.('MULTIPLE_FACES', { timestamp: Date.now() });
    },
    onGazeAway: (direction) => {
      console.log('Gaze away detected:', direction);
      onIntegrityEvent?.('GAZE_AWAY', { direction, timestamp: Date.now() });
    },
  });

  return (
    <div className="bg-white p-6 rounded-lg shadow">
      <h2 className="text-xl font-bold mb-4">Video Interview</h2>
      <div className="grid grid-cols-2 gap-4">
        {/* Candidate video */}
        <div className="relative">
          <video
            ref={videoRef}
            autoPlay
            muted
            className="w-full h-64 bg-gray-900 rounded-lg object-cover"
          />
          <div className="absolute bottom-2 left-2 bg-black bg-opacity-50 text-white px-2 py-1 rounded text-sm">
            You
          </div>
          {!isVideoEnabled && (
            <div className="absolute inset-0 flex items-center justify-center bg-gray-900 rounded-lg">
              <p className="text-white">Camera not available</p>
            </div>
          )}
        </div>

        {/* AI interviewer avatar */}
        <div className="relative bg-gradient-to-br from-blue-500 to-purple-600 rounded-lg h-64 flex items-center justify-center">
          <div className="text-center">
            <div className="w-24 h-24 bg-white rounded-full mx-auto mb-4 flex items-center justify-center">
              <svg
                className="w-16 h-16 text-blue-500"
                fill="currentColor"
                viewBox="0 0 20 20"
              >
                <path
                  fillRule="evenodd"
                  d="M10 9a3 3 0 100-6 3 3 0 000 6zm-7 9a7 7 0 1114 0H3z"
                  clipRule="evenodd"
                />
              </svg>
            </div>
            <p className="text-white font-semibold">AI Interviewer</p>
          </div>
          <div className="absolute top-2 right-2">
            <span className="inline-block w-3 h-3 bg-green-400 rounded-full animate-pulse"></span>
          </div>
        </div>
      </div>

      {/* Recording indicator and video analysis status */}
      <div className="mt-4 space-y-2">
        <div className="flex items-center gap-2">
          <span className="inline-block w-3 h-3 bg-red-500 rounded-full animate-pulse"></span>
          <span className="text-sm text-gray-600">Recording in progress</span>
        </div>

        {/* Video Analysis Overlay */}
        {enableAnalysis && isVideoEnabled && showAnalysisOverlay && (
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-3">
            <div className="flex items-start justify-between mb-2">
              <div className="flex items-center">
                <div className={`w-2 h-2 rounded-full mr-2 ${isReady ? 'bg-green-500' : 'bg-yellow-500'}`}></div>
                <span className="text-xs font-medium text-blue-900">
                  Video Analysis: {isReady ? 'Active' : 'Initializing...'}
                </span>
              </div>
              <button
                onClick={() => setShowAnalysisOverlay(false)}
                className="text-blue-400 hover:text-blue-600"
              >
                <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                  <path
                    fillRule="evenodd"
                    d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z"
                    clipRule="evenodd"
                  />
                </svg>
              </button>
            </div>

            {isReady && (
              <div className="grid grid-cols-2 gap-2 text-xs">
                <div className="flex items-center">
                  <span className="text-blue-700">Faces detected:</span>
                  <span className={`ml-1 font-semibold ${analysisResult.faceCount === 1 ? 'text-green-600' : 'text-red-600'}`}>
                    {analysisResult.faceCount}
                  </span>
                </div>
                <div className="flex items-center">
                  <span className="text-blue-700">Looking at screen:</span>
                  <span className={`ml-1 font-semibold ${!analysisResult.isLookingAway ? 'text-green-600' : 'text-amber-600'}`}>
                    {!analysisResult.isLookingAway ? 'Yes' : 'No'}
                  </span>
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
