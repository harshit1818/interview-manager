import { useEffect, useRef, useState, useCallback } from 'react';

interface VideoAnalysisResult {
  faceCount: number;
  isLookingAway: boolean;
  gazeDirection: {
    x: number;
    y: number;
  };
  confidence: number;
}

interface UseVideoAnalysisProps {
  videoElement: HTMLVideoElement | null;
  enabled: boolean;
  onMultipleFaces: () => void;
  onGazeAway: (direction: { x: number; y: number }) => void;
}

export const useVideoAnalysis = ({
  videoElement,
  enabled,
  onMultipleFaces,
  onGazeAway,
}: UseVideoAnalysisProps) => {
  const [faceMesh, setFaceMesh] = useState<any>(null);
  const [isReady, setIsReady] = useState(false);
  const [analysisResult, setAnalysisResult] = useState<VideoAnalysisResult>({
    faceCount: 0,
    isLookingAway: false,
    gazeDirection: { x: 0, y: 0 },
    confidence: 0,
  });
  const lastGazeWarning = useRef<number>(0);
  const lastMultiFaceWarning = useRef<number>(0);

  useEffect(() => {
    if (!enabled || typeof window === 'undefined' || !videoElement) return;

    // Dynamically import MediaPipe
    const initMediaPipe = async () => {
      try {
        const { FaceMesh } = await import('@mediapipe/face_mesh');

        const faceMeshInstance = new FaceMesh({
          locateFile: (file) => {
            return `https://cdn.jsdelivr.net/npm/@mediapipe/face_mesh/${file}`;
          },
        });

        faceMeshInstance.setOptions({
          maxNumFaces: 3,
          refineLandmarks: true,
          minDetectionConfidence: 0.5,
          minTrackingConfidence: 0.5,
        });

        faceMeshInstance.onResults(onResults);

        setFaceMesh(faceMeshInstance);
        setIsReady(true);

        // Manual frame processing loop
        const processFrame = async () => {
          if (videoElement && videoElement.readyState === 4) {
            await faceMeshInstance.send({ image: videoElement });
          }
          requestAnimationFrame(processFrame);
        };

        requestAnimationFrame(processFrame);
      } catch (error) {
        console.error('Failed to initialize MediaPipe:', error);
      }
    };

    initMediaPipe();

    return () => {
      if (faceMesh) {
        faceMesh.close();
      }
    };
  }, [enabled, videoElement]);

  const onResults = useCallback(
    (results: any) => {
      const faceCount = results.multiFaceLandmarks?.length || 0;

      // Multiple face detection
      if (faceCount > 1) {
        const now = Date.now();
        // Throttle warnings to every 5 seconds
        if (now - lastMultiFaceWarning.current > 5000) {
          onMultipleFaces();
          lastMultiFaceWarning.current = now;
        }
      }

      // Gaze detection (if at least one face detected)
      if (faceCount > 0 && results.multiFaceLandmarks[0]) {
        const landmarks = results.multiFaceLandmarks[0];
        const gazeDirection = calculateGazeDirection(landmarks);
        const isLookingAway = Math.abs(gazeDirection.x) > 0.3 || Math.abs(gazeDirection.y) > 0.3;

        if (isLookingAway) {
          const now = Date.now();
          // Throttle warnings to every 10 seconds
          if (now - lastGazeWarning.current > 10000) {
            onGazeAway(gazeDirection);
            lastGazeWarning.current = now;
          }
        }

        setAnalysisResult({
          faceCount,
          isLookingAway,
          gazeDirection,
          confidence: 0.8, // Simplified confidence
        });
      } else {
        setAnalysisResult({
          faceCount,
          isLookingAway: false,
          gazeDirection: { x: 0, y: 0 },
          confidence: 0,
        });
      }
    },
    [onMultipleFaces, onGazeAway]
  );

  return {
    isReady,
    analysisResult,
  };
};

// Calculate gaze direction from face landmarks
function calculateGazeDirection(landmarks: any[]): { x: number; y: number } {
  // Using simplified gaze estimation
  // In production, use iris landmarks for better accuracy

  // Key landmarks for gaze estimation
  // 468 landmarks total, we use key eye landmarks

  // Left eye: 133, 33, 160, 159, 158, 144, 145, 153
  // Right eye: 362, 263, 387, 386, 385, 373, 374, 380

  const leftEye = landmarks[33]; // Left eye center
  const rightEye = landmarks[263]; // Right eye center
  const noseTip = landmarks[1]; // Nose tip
  const foreheadCenter = landmarks[10]; // Forehead

  if (!leftEye || !rightEye || !noseTip || !foreheadCenter) {
    return { x: 0, y: 0 };
  }

  // Calculate horizontal gaze (left/right)
  const eyeCenter = {
    x: (leftEye.x + rightEye.x) / 2,
    y: (leftEye.y + rightEye.y) / 2,
  };

  const horizontalOffset = noseTip.x - eyeCenter.x;
  const verticalOffset = noseTip.y - eyeCenter.y;

  // Normalize to -1 to 1 range
  // Negative x = looking left, Positive x = looking right
  // Negative y = looking up, Positive y = looking down
  const gazeX = horizontalOffset * 10; // Scale factor
  const gazeY = verticalOffset * 10;

  return {
    x: Math.max(-1, Math.min(1, gazeX)),
    y: Math.max(-1, Math.min(1, gazeY)),
  };
}

// Simpler hook for basic face detection without MediaPipe (fallback)
export const useBasicFaceDetection = ({
  videoElement,
  enabled,
  onMultipleFaces,
}: {
  videoElement: HTMLVideoElement | null;
  enabled: boolean;
  onMultipleFaces: () => void;
}) => {
  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  const [faceCount, setFaceCount] = useState(0);

  useEffect(() => {
    if (!enabled || !videoElement || typeof window === 'undefined') return;

    // Create canvas for analysis
    const canvas = document.createElement('canvas');
    canvas.width = 640;
    canvas.height = 480;
    canvasRef.current = canvas;

    // Note: For prototype, you can use browser's experimental FaceDetector API
    // or integrate with MediaPipe via CDN

    const interval = setInterval(async () => {
      // Placeholder for face detection
      // In production, implement actual face detection here
      console.log('Video analysis running...');
    }, 2000);

    return () => clearInterval(interval);
  }, [enabled, videoElement]);

  return { faceCount };
};
