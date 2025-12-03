package services

import (
	"crypto/rand"
	"encoding/hex"
	"errors"
	"sync"

	"interview-manager/backend/internal/models"
)

// SessionService manages interview sessions
type SessionService struct {
	sessions map[string]*models.InterviewSession
	mu       sync.RWMutex
}

func NewSessionService() *SessionService {
	return &SessionService{
		sessions: make(map[string]*models.InterviewSession),
	}
}

// CreateSession creates a new interview session
func (s *SessionService) CreateSession(name, topic, difficulty string, duration int) *models.InterviewSession {
	s.mu.Lock()
	defer s.mu.Unlock()

	session := &models.InterviewSession{
		ID:              generateID(),
		CandidateName:   name,
		Topic:           topic,
		Difficulty:      difficulty,
		Duration:        duration,
		Status:          "waiting",
		CurrentQuestion: 0,
		Questions:       []models.Question{},
		Transcript:      []models.ConversationTurn{},
		IntegrityEvents: []models.IntegrityEvent{},
		Metadata:        make(map[string]interface{}),
	}

	s.sessions[session.ID] = session
	return session
}

// GetSession retrieves a session by ID
func (s *SessionService) GetSession(id string) (*models.InterviewSession, error) {
	s.mu.RLock()
	defer s.mu.RUnlock()

	session, exists := s.sessions[id]
	if !exists {
		return nil, errors.New("session not found")
	}

	return session, nil
}

// UpdateSession updates an existing session
func (s *SessionService) UpdateSession(session *models.InterviewSession) {
	s.mu.Lock()
	defer s.mu.Unlock()

	s.sessions[session.ID] = session
}

// AddConversationTurn adds a conversation turn to the session
func (s *SessionService) AddConversationTurn(sessionID string, turn models.ConversationTurn) error {
	s.mu.Lock()
	defer s.mu.Unlock()

	session, exists := s.sessions[sessionID]
	if !exists {
		return errors.New("session not found")
	}

	session.Transcript = append(session.Transcript, turn)
	return nil
}

// AddIntegrityEvent adds an integrity event to the session
func (s *SessionService) AddIntegrityEvent(sessionID string, event models.IntegrityEvent) error {
	s.mu.Lock()
	defer s.mu.Unlock()

	session, exists := s.sessions[sessionID]
	if !exists {
		return errors.New("session not found")
	}

	session.IntegrityEvents = append(session.IntegrityEvents, event)
	return nil
}

// ListAllSessions returns all sessions
func (s *SessionService) ListAllSessions() []*models.InterviewSession {
	s.mu.RLock()
	defer s.mu.RUnlock()

	sessions := make([]*models.InterviewSession, 0, len(s.sessions))
	for _, session := range s.sessions {
		sessions = append(sessions, session)
	}

	return sessions
}

// generateID generates a random ID for sessions
func generateID() string {
	b := make([]byte, 16)
	rand.Read(b)
	return hex.EncodeToString(b)
}
