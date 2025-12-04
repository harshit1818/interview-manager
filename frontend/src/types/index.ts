// Types matching the Go backend models

export interface InterviewSession {
  id: string;
  candidateName: string;
  topic: string;
  difficulty: string;
  duration: number;
  status: 'waiting' | 'in_progress' | 'completed';
  startedAt?: string;
  endedAt?: string;
  currentQuestion: number;
  questions: Question[];
  transcript: ConversationTurn[];
  integrityEvents: IntegrityEvent[];
  finalReport?: Report;
  metadata: Record<string, any>;
}

export interface Question {
  id: string;
  stem: string;
  difficulty: string;
  followUps: string[];
  evaluationHints: string[];
  redFlags: string[];
  asked: boolean;
  askedAt?: string;
}

export interface ConversationTurn {
  timestamp: string;
  speaker: 'ai' | 'candidate';
  text: string;
  type: 'question' | 'answer' | 'follow_up' | 'acknowledgment';
  evaluation?: Evaluation;
}

export interface Evaluation {
  correctness: number;
  communication: number;
  approach: number;
  edgeCases: number;
  notes: string;
}

export interface IntegrityEvent {
  timestamp: string;
  type: 'TAB_SWITCH' | 'WINDOW_BLUR' | 'MULTIPLE_FACES' | 'GAZE_AWAY' | 'LARGE_PASTE' | 'PROLONGED_SILENCE' | 'SUDDEN_AUDIO_SPIKE' | 'POSSIBLE_BACKGROUND_SPEECH' | 'LONG_SILENCE_ENDED';
  severity: 'low' | 'medium' | 'high';
  metadata: Record<string, any>;
}

export interface Report {
  sessionId: string;
  candidateName: string;
  topic: string;
  difficulty: string;
  duration: number;
  questionsAsked: number;
  overallScore: number;
  scores: Record<string, number>;
  strengths: string[];
  weaknesses: string[];
  integrityScore: number;
  integrityIssues: number;
  recommendation: 'strong_hire' | 'hire' | 'maybe' | 'no_hire';
  generatedAt: string;
}

// API Request/Response types

export interface StartInterviewRequest {
  candidateName: string;
  topic: string;
  difficulty: string;
  duration: number;
}

export interface StartInterviewResponse {
  sessionId: string;
  firstQuestion: Question;
  audioUrl?: string;
}

export interface RespondRequest {
  sessionId: string;
  transcript: string;
  timestamp: number;
}

export interface RespondResponse {
  evaluation?: Evaluation;
  nextAction: 'follow_up' | 'next_question' | 'end_interview';
  nextQuestion?: Question;
  aiResponse: string;
  audioUrl?: string;
}

export interface IntegrityEventRequest {
  sessionId: string;
  eventType: string;
  timestamp: number;
  metadata: Record<string, any>;
}
