import { useEffect, useCallback } from 'react';
import { integrityAPI } from '@/lib/api';

interface UseIntegrityDetectionProps {
  sessionId: string;
  enabled: boolean;
}

export const useIntegrityDetection = ({ sessionId, enabled }: UseIntegrityDetectionProps) => {
  const logEvent = useCallback(async (eventType: string, metadata: Record<string, any> = {}) => {
    if (!enabled || !sessionId) return;

    try {
      await integrityAPI.logEvent({
        sessionId,
        eventType,
        timestamp: Date.now(),
        metadata,
      });
      console.log(`Integrity event logged: ${eventType}`);
    } catch (error) {
      console.error('Failed to log integrity event:', error);
    }
  }, [sessionId, enabled]);

  // Tab switch detection
  useEffect(() => {
    if (!enabled) return;

    const handleVisibilityChange = () => {
      if (document.hidden) {
        logEvent('TAB_SWITCH', { timestamp: Date.now() });
      }
    };

    document.addEventListener('visibilitychange', handleVisibilityChange);
    return () => document.removeEventListener('visibilitychange', handleVisibilityChange);
  }, [enabled, logEvent]);

  // Window blur detection
  useEffect(() => {
    if (!enabled) return;

    const handleBlur = () => {
      logEvent('WINDOW_BLUR', { timestamp: Date.now() });
    };

    window.addEventListener('blur', handleBlur);
    return () => window.removeEventListener('blur', handleBlur);
  }, [enabled, logEvent]);

  return { logEvent };
};

// Code editor paste detection
export const usePasteDetection = (onLargePaste: (length: number) => void) => {
  const handlePaste = useCallback((event: ClipboardEvent) => {
    const pastedText = event.clipboardData?.getData('text') || '';
    const pastedLength = pastedText.length;

    if (pastedLength > 50) {
      onLargePaste(pastedLength);
    }
  }, [onLargePaste]);

  useEffect(() => {
    document.addEventListener('paste', handlePaste);
    return () => document.removeEventListener('paste', handlePaste);
  }, [handlePaste]);
};
