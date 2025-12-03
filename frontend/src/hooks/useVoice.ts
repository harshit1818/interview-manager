import { useState, useEffect, useCallback, useRef } from 'react';

// Configuration for continuous listening
const SILENCE_THRESHOLD_MS = 1500; // Consider utterance complete after 1.5s silence
const MIN_UTTERANCE_LENGTH = 10; // Minimum characters for valid utterance

interface UtteranceEvent {
  text: string;
  timestamp: number;
  isFinal: boolean;
}

// Continuous Speech Recognition with Utterance Detection
export const useContinuousSpeechRecognition = (
  onUtteranceComplete?: (text: string) => void
) => {
  const [isListening, setIsListening] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const [currentTranscript, setCurrentTranscript] = useState('');
  const [finalizedText, setFinalizedText] = useState('');
  const [recognition, setRecognition] = useState<any>(null);
  
  const silenceTimerRef = useRef<NodeJS.Timeout | null>(null);
  const lastSpeechTimeRef = useRef<number>(Date.now());
  const accumulatedTextRef = useRef<string>('');
  const isActiveRef = useRef<boolean>(false);

  // Clear silence timer
  const clearSilenceTimer = useCallback(() => {
    if (silenceTimerRef.current) {
      clearTimeout(silenceTimerRef.current);
      silenceTimerRef.current = null;
    }
  }, []);

  // Handle utterance completion
  const finalizeUtterance = useCallback(() => {
    const text = accumulatedTextRef.current.trim();
    if (text.length >= MIN_UTTERANCE_LENGTH) {
      setFinalizedText(text);
      setIsProcessing(true);
      onUtteranceComplete?.(text);
      setIsProcessing(false);
    }
    accumulatedTextRef.current = '';
    setCurrentTranscript('');
  }, [onUtteranceComplete]);

  // Reset silence timer on speech
  const resetSilenceTimer = useCallback(() => {
    clearSilenceTimer();
    lastSpeechTimeRef.current = Date.now();
    
    silenceTimerRef.current = setTimeout(() => {
      if (isActiveRef.current && accumulatedTextRef.current.trim().length > 0) {
        finalizeUtterance();
      }
    }, SILENCE_THRESHOLD_MS);
  }, [clearSilenceTimer, finalizeUtterance]);

  useEffect(() => {
    if (typeof window !== 'undefined') {
      const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;

      if (SpeechRecognition) {
        const recognitionInstance = new SpeechRecognition();
        recognitionInstance.continuous = true;
        recognitionInstance.interimResults = true;
        recognitionInstance.lang = 'en-US';
        recognitionInstance.maxAlternatives = 1;

        recognitionInstance.onresult = (event: any) => {
          let interimTranscript = '';
          let finalTranscript = '';
          
          for (let i = event.resultIndex; i < event.results.length; i++) {
            const transcript = event.results[i][0].transcript;
            if (event.results[i].isFinal) {
              finalTranscript += transcript + ' ';
            } else {
              interimTranscript += transcript;
            }
          }
          
          // Update accumulated text with final results
          if (finalTranscript) {
            accumulatedTextRef.current += finalTranscript;
            setCurrentTranscript(accumulatedTextRef.current + interimTranscript);
          } else {
            setCurrentTranscript(accumulatedTextRef.current + interimTranscript);
          }
          
          // Reset silence timer on any speech activity
          resetSilenceTimer();
        };

        recognitionInstance.onerror = (event: any) => {
          console.error('Speech recognition error:', event.error);
          // Auto-restart on recoverable errors
          if (event.error === 'no-speech' && isActiveRef.current) {
            try {
              recognitionInstance.start();
            } catch (e) {
              // Already started
            }
          } else if (event.error !== 'aborted') {
            setIsListening(false);
            isActiveRef.current = false;
          }
        };

        recognitionInstance.onend = () => {
          // Auto-restart if still supposed to be listening
          if (isActiveRef.current) {
            try {
              recognitionInstance.start();
            } catch (e) {
              // Already started or error
            }
          } else {
            setIsListening(false);
          }
        };

        setRecognition(recognitionInstance);
      }
    }

    return () => {
      clearSilenceTimer();
    };
  }, [resetSilenceTimer, clearSilenceTimer]);

  const startContinuousListening = useCallback(() => {
    if (recognition && !isActiveRef.current) {
      accumulatedTextRef.current = '';
      setCurrentTranscript('');
      setFinalizedText('');
      isActiveRef.current = true;
      try {
        recognition.start();
        setIsListening(true);
      } catch (e) {
        console.error('Failed to start recognition:', e);
      }
    }
  }, [recognition]);

  const stopContinuousListening = useCallback(() => {
    isActiveRef.current = false;
    clearSilenceTimer();
    if (recognition) {
      try {
        recognition.stop();
      } catch (e) {
        // Already stopped
      }
      setIsListening(false);
    }
    // Finalize any remaining text
    if (accumulatedTextRef.current.trim().length >= MIN_UTTERANCE_LENGTH) {
      finalizeUtterance();
    }
  }, [recognition, clearSilenceTimer, finalizeUtterance]);

  const forceFinalize = useCallback(() => {
    clearSilenceTimer();
    finalizeUtterance();
  }, [clearSilenceTimer, finalizeUtterance]);

  return {
    isListening,
    isProcessing,
    currentTranscript,
    finalizedText,
    startContinuousListening,
    stopContinuousListening,
    forceFinalize,
    isSupported: !!recognition,
  };
};

// Original Speech Recognition (STT) - kept for backward compatibility
export const useSpeechRecognition = () => {
  const [isListening, setIsListening] = useState(false);
  const [transcript, setTranscript] = useState('');
  const [recognition, setRecognition] = useState<any>(null);

  useEffect(() => {
    if (typeof window !== 'undefined') {
      const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;

      if (SpeechRecognition) {
        const recognitionInstance = new SpeechRecognition();
        recognitionInstance.continuous = true;
        recognitionInstance.interimResults = true;
        recognitionInstance.lang = 'en-US';

        recognitionInstance.onresult = (event: any) => {
          let finalTranscript = '';
          for (let i = event.resultIndex; i < event.results.length; i++) {
            const transcriptPiece = event.results[i][0].transcript;
            if (event.results[i].isFinal) {
              finalTranscript += transcriptPiece + ' ';
            }
          }
          if (finalTranscript) {
            setTranscript((prev) => prev + finalTranscript);
          }
        };

        recognitionInstance.onerror = (event: any) => {
          console.error('Speech recognition error:', event.error);
          setIsListening(false);
        };

        recognitionInstance.onend = () => {
          setIsListening(false);
        };

        setRecognition(recognitionInstance);
      }
    }
  }, []);

  const startListening = useCallback(() => {
    if (recognition) {
      setTranscript('');
      recognition.start();
      setIsListening(true);
    }
  }, [recognition]);

  const stopListening = useCallback(() => {
    if (recognition) {
      recognition.stop();
      setIsListening(false);
    }
  }, [recognition]);

  const resetTranscript = useCallback(() => {
    setTranscript('');
  }, []);

  return {
    isListening,
    transcript,
    startListening,
    stopListening,
    resetTranscript,
    isSupported: !!recognition,
  };
};

// Text-to-Speech (TTS)
export const useTextToSpeech = () => {
  const [isSpeaking, setIsSpeaking] = useState(false);

  const speak = useCallback((text: string) => {
    if (typeof window !== 'undefined' && window.speechSynthesis) {
      // Cancel any ongoing speech
      window.speechSynthesis.cancel();

      const utterance = new SpeechSynthesisUtterance(text);
      utterance.rate = 1.0;
      utterance.pitch = 1.0;
      utterance.volume = 1.0;

      utterance.onstart = () => setIsSpeaking(true);
      utterance.onend = () => setIsSpeaking(false);
      utterance.onerror = () => setIsSpeaking(false);

      window.speechSynthesis.speak(utterance);
    }
  }, []);

  const stop = useCallback(() => {
    if (typeof window !== 'undefined' && window.speechSynthesis) {
      window.speechSynthesis.cancel();
      setIsSpeaking(false);
    }
  }, []);

  return {
    speak,
    stop,
    isSpeaking,
    isSupported: typeof window !== 'undefined' && 'speechSynthesis' in window,
  };
};
