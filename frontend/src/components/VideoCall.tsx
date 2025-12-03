import { useEffect, useRef, useState } from 'react';

interface VideoCallProps {
  sessionId: string;
}

export default function VideoCall({ sessionId }: VideoCallProps) {
  const videoRef = useRef<HTMLVideoElement>(null);
  const [isVideoEnabled, setIsVideoEnabled] = useState(false);

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

      {/* Recording indicator */}
      <div className="mt-4 flex items-center gap-2">
        <span className="inline-block w-3 h-3 bg-red-500 rounded-full animate-pulse"></span>
        <span className="text-sm text-gray-600">Recording in progress</span>
      </div>
    </div>
  );
}
