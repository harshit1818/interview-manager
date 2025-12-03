package models

import "time"

// InterviewSession represents an interview session
type InterviewSession struct {
	ID               string                 `json:"id"`
	CandidateName    string                 `json:"candidateName"`
	Topic            string                 `json:"topic"`
	Difficulty       string                 `json:"difficulty"`
	Duration         int                    `json:"duration"` // in minutes
	Status           string                 `json:"status"`   // "waiting", "in_progress", "completed"
	StartedAt        *time.Time             `json:"startedAt,omitempty"`
	EndedAt          *time.Time             `json:"endedAt,omitempty"`
	CurrentQuestion  int                    `json:"currentQuestion"`
	Questions        []Question             `json:"questions"`
	Transcript       []ConversationTurn     `json:"transcript"`
	IntegrityEvents  []IntegrityEvent       `json:"integrityEvents"`
	FinalReport      *Report                `json:"finalReport,omitempty"`
	Metadata         map[string]interface{} `json:"metadata"`
}

// Question represents an interview question
type Question struct {
	ID              string   `json:"id"`
	Stem            string   `json:"stem"`
	Difficulty      string   `json:"difficulty"`
	FollowUps       []string `json:"followUps"`
	EvaluationHints []string `json:"evaluationHints"`
	RedFlags        []string `json:"redFlags"`
	Asked           bool     `json:"asked"`
	AskedAt         *time.Time `json:"askedAt,omitempty"`
}

// ConversationTurn represents a Q&A turn
type ConversationTurn struct {
	Timestamp time.Time `json:"timestamp"`
	Speaker   string    `json:"speaker"` // "ai" or "candidate"
	Text      string    `json:"text"`
	Type      string    `json:"type"` // "question", "answer", "follow_up", "acknowledgment"
	Evaluation *Evaluation `json:"evaluation,omitempty"`
}

// Evaluation represents the evaluation of an answer
type Evaluation struct {
	Correctness   int    `json:"correctness"`   // 1-5
	Communication int    `json:"communication"` // 1-5
	Approach      int    `json:"approach"`      // 1-5
	EdgeCases     int    `json:"edgeCases"`     // 1-5
	Notes         string `json:"notes"`
}

// IntegrityEvent represents a potential integrity issue
type IntegrityEvent struct {
	Timestamp time.Time              `json:"timestamp"`
	Type      string                 `json:"type"` // "TAB_SWITCH", "WINDOW_BLUR", "MULTIPLE_FACES", etc.
	Severity  string                 `json:"severity"` // "low", "medium", "high"
	Metadata  map[string]interface{} `json:"metadata"`
}

// Report represents the final interview report
type Report struct {
	SessionID        string            `json:"sessionId"`
	CandidateName    string            `json:"candidateName"`
	Topic            string            `json:"topic"`
	Difficulty       string            `json:"difficulty"`
	Duration         int               `json:"duration"`
	QuestionsAsked   int               `json:"questionsAsked"`
	OverallScore     float64           `json:"overallScore"`
	Scores           map[string]float64 `json:"scores"`
	Strengths        []string          `json:"strengths"`
	Weaknesses       []string          `json:"weaknesses"`
	IntegrityScore   float64           `json:"integrityScore"`
	IntegrityIssues  int               `json:"integrityIssues"`
	Recommendation   string            `json:"recommendation"` // "strong_hire", "hire", "maybe", "no_hire"
	GeneratedAt      time.Time         `json:"generatedAt"`
}

// Request/Response types

type StartInterviewRequest struct {
	CandidateName string `json:"candidateName" binding:"required"`
	Topic         string `json:"topic" binding:"required"`
	Difficulty    string `json:"difficulty" binding:"required"`
	Duration      int    `json:"duration" binding:"required"`
}

type StartInterviewResponse struct {
	SessionID     string   `json:"sessionId"`
	FirstQuestion Question `json:"firstQuestion"`
	AudioURL      string   `json:"audioUrl,omitempty"`
}

type RespondRequest struct {
	SessionID  string `json:"sessionId" binding:"required"`
	Transcript string `json:"transcript" binding:"required"`
	Timestamp  int64  `json:"timestamp"`
}

type RespondResponse struct {
	Evaluation   *Evaluation `json:"evaluation,omitempty"`
	NextAction   string      `json:"nextAction"` // "follow_up", "next_question", "end_interview"
	NextQuestion *Question   `json:"nextQuestion,omitempty"`
	AIResponse   string      `json:"aiResponse"`
	AudioURL     string      `json:"audioUrl,omitempty"`
}

type IntegrityEventRequest struct {
	SessionID string                 `json:"sessionId" binding:"required"`
	EventType string                 `json:"eventType" binding:"required"`
	Timestamp int64                  `json:"timestamp"`
	Metadata  map[string]interface{} `json:"metadata"`
}
