import { useEffect, useState } from 'react';

interface IntegrityWarningProps {
  type: 'MULTIPLE_FACES' | 'GAZE_AWAY' | 'TAB_SWITCH' | 'WINDOW_BLUR' | 'LARGE_PASTE' | null;
  onClose: () => void;
}

export default function IntegrityWarning({ type, onClose }: IntegrityWarningProps) {
  const [isVisible, setIsVisible] = useState(false);

  useEffect(() => {
    if (type) {
      setIsVisible(true);
      // Auto-hide after 5 seconds
      const timer = setTimeout(() => {
        setIsVisible(false);
        setTimeout(onClose, 300); // Wait for fade-out animation
      }, 5000);

      return () => clearTimeout(timer);
    }
  }, [type, onClose]);

  if (!type) return null;

  const warnings = {
    MULTIPLE_FACES: {
      title: 'Multiple Faces Detected',
      message: 'Please ensure you are alone in the frame during the interview.',
      icon: '👥',
      color: 'red',
    },
    GAZE_AWAY: {
      title: 'Looking Away Detected',
      message: 'Please keep your eyes on the screen during the interview.',
      icon: '👀',
      color: 'amber',
    },
    TAB_SWITCH: {
      title: 'Tab Switch Detected',
      message: 'Please keep this tab focused throughout the interview.',
      icon: '🔄',
      color: 'orange',
    },
    WINDOW_BLUR: {
      title: 'Window Lost Focus',
      message: 'Please stay in the interview window.',
      icon: '⚠️',
      color: 'yellow',
    },
    LARGE_PASTE: {
      title: 'Large Paste Detected',
      message: 'Please type your code rather than pasting large blocks.',
      icon: '📋',
      color: 'amber',
    },
  };

  const warning = warnings[type];

  return (
    <div
      className={`fixed top-4 right-4 z-50 transition-all duration-300 transform ${
        isVisible ? 'translate-x-0 opacity-100' : 'translate-x-full opacity-0'
      }`}
    >
      <div
        className={`bg-${warning.color}-50 border-l-4 border-${warning.color}-500 p-4 rounded-lg shadow-lg max-w-md`}
        style={{
          backgroundColor: warning.color === 'red' ? '#fef2f2' :
                          warning.color === 'amber' ? '#fffbeb' :
                          warning.color === 'orange' ? '#fff7ed' : '#fefce8',
          borderColor: warning.color === 'red' ? '#ef4444' :
                      warning.color === 'amber' ? '#f59e0b' :
                      warning.color === 'orange' ? '#f97316' : '#eab308',
        }}
      >
        <div className="flex items-start">
          <div className="text-2xl mr-3">{warning.icon}</div>
          <div className="flex-1">
            <h3 className="font-semibold text-gray-900 mb-1">{warning.title}</h3>
            <p className="text-sm text-gray-700">{warning.message}</p>
          </div>
          <button
            onClick={() => {
              setIsVisible(false);
              setTimeout(onClose, 300);
            }}
            className="ml-3 text-gray-400 hover:text-gray-600"
          >
            <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
              <path
                fillRule="evenodd"
                d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z"
                clipRule="evenodd"
              />
            </svg>
          </button>
        </div>
      </div>
    </div>
  );
}
