import { useEffect, useCallback, useRef, useState } from 'react';
import { integrityAPI } from '@/lib/api';

interface UseIntegrityDetectionProps {
  sessionId: string;
  enabled: boolean;
}

interface AudioIntegrityState {
  isMonitoring: boolean;
  lastVoiceActivity: number;
  suspiciousEvents: string[];
  silenceDuration: number;
}

// Configuration for audio integrity monitoring
const SILENCE_ALERT_THRESHOLD_MS = 30000; // Alert after 30s silence
const VOLUME_CHECK_INTERVAL_MS = 100; // Check audio levels every 100ms
const VOICE_ACTIVITY_THRESHOLD = 0.02; // Minimum volume to consider as speech
const MULTIPLE_VOICE_DETECTION_ENABLED = true;

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

// Background Audio Integrity Monitor
export const useAudioIntegrityMonitor = ({ 
  sessionId, 
  enabled 
}: UseIntegrityDetectionProps) => {
  const [state, setState] = useState<AudioIntegrityState>({
    isMonitoring: false,
    lastVoiceActivity: Date.now(),
    suspiciousEvents: [],
    silenceDuration: 0,
  });
  
  const audioContextRef = useRef<AudioContext | null>(null);
  const analyserRef = useRef<AnalyserNode | null>(null);
  const streamRef = useRef<MediaStream | null>(null);
  const monitorIntervalRef = useRef<NodeJS.Timeout | null>(null);
  const silenceStartRef = useRef<number>(Date.now());
  const volumeHistoryRef = useRef<number[]>([]);

  const logIntegrityEvent = useCallback(async (eventType: string, metadata: Record<string, any> = {}) => {
    if (!enabled || !sessionId) return;
    
    try {
      await integrityAPI.logEvent({
        sessionId,
        eventType,
        timestamp: Date.now(),
        metadata,
      });
      
      setState(prev => ({
        ...prev,
        suspiciousEvents: [...prev.suspiciousEvents.slice(-9), eventType]
      }));
    } catch (error) {
      console.error('Failed to log audio integrity event:', error);
    }
  }, [sessionId, enabled]);

  const analyzeAudio = useCallback(() => {
    if (!analyserRef.current) return;
    
    const bufferLength = analyserRef.current.frequencyBinCount;
    const dataArray = new Uint8Array(bufferLength);
    analyserRef.current.getByteFrequencyData(dataArray);
    
    // Calculate average volume
    const average = dataArray.reduce((a, b) => a + b, 0) / bufferLength;
    const normalizedVolume = average / 255;
    
    // Track volume history for pattern analysis
    volumeHistoryRef.current.push(normalizedVolume);
    if (volumeHistoryRef.current.length > 50) {
      volumeHistoryRef.current.shift();
    }
    
    const now = Date.now();
    
    // Detect voice activity
    if (normalizedVolume > VOICE_ACTIVITY_THRESHOLD) {
      const silenceDuration = now - silenceStartRef.current;
      
      // Log if coming back from long silence
      if (silenceDuration > SILENCE_ALERT_THRESHOLD_MS) {
        logIntegrityEvent('LONG_SILENCE_ENDED', { 
          silenceDurationMs: silenceDuration 
        });
      }
      
      silenceStartRef.current = now;
      setState(prev => ({
        ...prev,
        lastVoiceActivity: now,
        silenceDuration: 0
      }));
      
      // Check for multiple voice patterns (sudden volume spikes)
      if (MULTIPLE_VOICE_DETECTION_ENABLED) {
        const recentVolumes = volumeHistoryRef.current.slice(-10);
        const avgRecent = recentVolumes.reduce((a, b) => a + b, 0) / recentVolumes.length;
        
        // Sudden loud sound (potential second voice)
        if (normalizedVolume > avgRecent * 3 && normalizedVolume > 0.15) {
          logIntegrityEvent('SUDDEN_AUDIO_SPIKE', { 
            volume: normalizedVolume,
            avgVolume: avgRecent 
          });
        }
      }
    } else {
      // Update silence duration
      const silenceDuration = now - silenceStartRef.current;
      setState(prev => ({
        ...prev,
        silenceDuration
      }));
      
      // Alert on prolonged silence
      if (silenceDuration > SILENCE_ALERT_THRESHOLD_MS && 
          silenceDuration % SILENCE_ALERT_THRESHOLD_MS < VOLUME_CHECK_INTERVAL_MS) {
        logIntegrityEvent('PROLONGED_SILENCE', { 
          silenceDurationMs: silenceDuration 
        });
      }
    }
    
    // Analyze frequency distribution for background speech detection
    const lowFreq = dataArray.slice(0, bufferLength / 4).reduce((a, b) => a + b, 0);
    const midFreq = dataArray.slice(bufferLength / 4, bufferLength / 2).reduce((a, b) => a + b, 0);
    const highFreq = dataArray.slice(bufferLength / 2).reduce((a, b) => a + b, 0);
    
    // Background speech typically has different frequency profile
    if (midFreq > lowFreq * 2 && midFreq > highFreq * 2 && normalizedVolume > 0.05) {
      // Potential background conversation detected
      const lastEvents = volumeHistoryRef.current.slice(-20);
      const variance = calculateVariance(lastEvents);
      
      if (variance > 0.001) { // Varying volume suggests conversation
        logIntegrityEvent('POSSIBLE_BACKGROUND_SPEECH', { 
          volumeVariance: variance,
          frequencyProfile: { low: lowFreq, mid: midFreq, high: highFreq }
        });
      }
    }
  }, [logIntegrityEvent]);

  const startMonitoring = useCallback(async () => {
    if (state.isMonitoring || !enabled) return;
    
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ 
        audio: {
          echoCancellation: true,
          noiseSuppression: false, // Keep noise for integrity detection
          autoGainControl: false
        } 
      });
      
      streamRef.current = stream;
      audioContextRef.current = new AudioContext();
      analyserRef.current = audioContextRef.current.createAnalyser();
      analyserRef.current.fftSize = 256;
      
      const source = audioContextRef.current.createMediaStreamSource(stream);
      source.connect(analyserRef.current);
      
      silenceStartRef.current = Date.now();
      
      // Start periodic analysis
      monitorIntervalRef.current = setInterval(analyzeAudio, VOLUME_CHECK_INTERVAL_MS);
      
      setState(prev => ({ ...prev, isMonitoring: true }));
    } catch (error) {
      console.error('Failed to start audio monitoring:', error);
    }
  }, [enabled, state.isMonitoring, analyzeAudio]);

  const stopMonitoring = useCallback(() => {
    if (monitorIntervalRef.current) {
      clearInterval(monitorIntervalRef.current);
      monitorIntervalRef.current = null;
    }
    
    if (streamRef.current) {
      streamRef.current.getTracks().forEach(track => track.stop());
      streamRef.current = null;
    }
    
    if (audioContextRef.current) {
      audioContextRef.current.close();
      audioContextRef.current = null;
    }
    
    analyserRef.current = null;
    volumeHistoryRef.current = [];
    
    setState(prev => ({ ...prev, isMonitoring: false }));
  }, []);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      stopMonitoring();
    };
  }, [stopMonitoring]);

  return {
    isMonitoring: state.isMonitoring,
    lastVoiceActivity: state.lastVoiceActivity,
    silenceDuration: state.silenceDuration,
    suspiciousEvents: state.suspiciousEvents,
    startMonitoring,
    stopMonitoring,
  };
};

// Helper function to calculate variance
function calculateVariance(arr: number[]): number {
  if (arr.length === 0) return 0;
  const mean = arr.reduce((a, b) => a + b, 0) / arr.length;
  return arr.reduce((sum, val) => sum + Math.pow(val - mean, 2), 0) / arr.length;
}

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
