package handlers

import (
	"fmt"
	"net/http"
	"time"

	"github.com/gin-gonic/gin"

	"interview-manager/backend/internal/models"
	"interview-manager/backend/internal/services"
)

type InterviewHandler struct {
	sessionService *services.SessionService
	llmClient      *services.LLMClient
}

func NewInterviewHandler(sessionService *services.SessionService, llmClient *services.LLMClient) *InterviewHandler {
	return &InterviewHandler{
		sessionService: sessionService,
		llmClient:      llmClient,
	}
}

// StartInterview creates a new interview session and returns the first question
func (h *InterviewHandler) StartInterview(c *gin.Context) {
	var req models.StartInterviewRequest
	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	// Create session
	session := h.sessionService.CreateSession(req.CandidateName, req.Topic, req.Difficulty, req.Duration)

	now := time.Now()
	session.StartedAt = &now
	session.Status = "in_progress"

	// AI Introduction and greeting
	aiGreeting := fmt.Sprintf("Hello %s! Welcome to your %s interview for a %s level position. I'm your AI interviewer today. This interview will last approximately %d minutes. Let's start by getting to know you better. Please introduce yourself and tell me a bit about your background and experience.",
		req.CandidateName, req.Topic, req.Difficulty, req.Duration)

	// Log AI's greeting
	h.sessionService.AddConversationTurn(session.ID, models.ConversationTurn{
		Timestamp: time.Now(),
		Speaker:   "ai",
		Text:      aiGreeting,
		Type:      "greeting",
	})

	// Create introduction question
	introQuestion := models.Question{
		ID:              "intro_001",
		Stem:            "Please introduce yourself and tell me about your background, experience, and what interests you about this role.",
		Difficulty:      "introduction",
		FollowUps:       []string{"What motivated you to apply for this position?", "Tell me about a recent project you're proud of."},
		EvaluationHints: []string{"Clear communication", "Relevant experience", "Enthusiasm"},
		RedFlags:        []string{"Unclear communication", "Lack of preparation"},
		Asked:           true,
		AskedAt:         &now,
	}

	session.Questions = append(session.Questions, introQuestion)

	// Save session
	h.sessionService.UpdateSession(session)

	// Log introduction question
	h.sessionService.AddConversationTurn(session.ID, models.ConversationTurn{
		Timestamp: time.Now(),
		Speaker:   "ai",
		Text:      introQuestion.Stem,
		Type:      "question",
	})

	c.JSON(http.StatusOK, models.StartInterviewResponse{
		SessionID:     session.ID,
		FirstQuestion: introQuestion,
		Greeting:      aiGreeting,
	})
}

// HandleResponse processes candidate's answer and returns next action
func (h *InterviewHandler) HandleResponse(c *gin.Context) {
	var req models.RespondRequest
	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	session, err := h.sessionService.GetSession(req.SessionID)
	if err != nil {
		c.JSON(http.StatusNotFound, gin.H{"error": "Session not found"})
		return
	}

	h.sessionService.AddConversationTurn(session.ID, models.ConversationTurn{
		Timestamp: time.Now(),
		Speaker:   "candidate",
		Text:      req.Transcript,
		Type:      "answer",
	})

	llmResponse, err := h.llmClient.EvaluateAndDecideNext(
		session.Questions[session.CurrentQuestion],
		req.Transcript,
		session.Transcript,
	)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to evaluate response"})
		return
	}

	const maxFollowUps = 2
	qIdx := session.CurrentQuestion
	if session.FollowUpCounts == nil {
		session.FollowUpCounts = make(map[int]int)
	}

	if llmResponse.NextAction == "follow_up" {
		if session.FollowUpCounts[qIdx] >= maxFollowUps {
			llmResponse.NextAction = "next_question"
			llmResponse.AIResponse = "Good effort on this question. Let's move on to the next one."
		} else {
			session.FollowUpCounts[qIdx]++
		}
	}

	h.sessionService.AddConversationTurn(session.ID, models.ConversationTurn{
		Timestamp:  time.Now(),
		Speaker:    "ai",
		Text:       llmResponse.AIResponse,
		Type:       llmResponse.NextAction,
		Evaluation: llmResponse.Evaluation,
	})

	var nextQuestion *models.Question
	if llmResponse.NextAction == "next_question" {
		nextQ, err := h.llmClient.GetNextQuestion(session.Topic, session.Difficulty, session.CurrentQuestion+1)
		if err == nil {
			nextQuestion = &nextQ
			session.Questions = append(session.Questions, nextQ)
			session.CurrentQuestion++
		} else {
			llmResponse.NextAction = "end_interview"
		}
	}

	h.sessionService.UpdateSession(session)

	c.JSON(http.StatusOK, models.RespondResponse{
		Evaluation:   llmResponse.Evaluation,
		NextAction:   llmResponse.NextAction,
		NextQuestion: nextQuestion,
		AIResponse:   llmResponse.AIResponse,
	})
}

// EndInterview ends the session and generates report
func (h *InterviewHandler) EndInterview(c *gin.Context) {
	var req struct {
		SessionID string `json:"sessionId" binding:"required"`
	}
	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}
	sessionID := req.SessionID

	session, err := h.sessionService.GetSession(sessionID)
	if err != nil {
		c.JSON(http.StatusNotFound, gin.H{"error": "Session not found"})
		return
	}

	// Generate report
	report, err := h.llmClient.GenerateReport(session)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to generate report"})
		return
	}

	// Update session
	now := time.Now()
	session.EndedAt = &now
	session.Status = "completed"
	session.FinalReport = &report
	h.sessionService.UpdateSession(session)

	c.JSON(http.StatusOK, gin.H{
		"report":     report,
		"scores":     report.Scores,
		"transcript": session.Transcript,
	})
}

// GetStatus returns current interview status
func (h *InterviewHandler) GetStatus(c *gin.Context) {
	sessionID := c.Param("sessionId")

	session, err := h.sessionService.GetSession(sessionID)
	if err != nil {
		c.JSON(http.StatusNotFound, gin.H{"error": "Session not found"})
		return
	}

	var timeRemaining int
	if session.StartedAt != nil {
		elapsed := time.Since(*session.StartedAt).Minutes()
		timeRemaining = session.Duration - int(elapsed)
		if timeRemaining < 0 {
			timeRemaining = 0
		}
	}

	c.JSON(http.StatusOK, gin.H{
		"currentState":    session.Status,
		"timeRemaining":   timeRemaining,
		"questionsAsked":  session.CurrentQuestion + 1,
		"currentQuestion": session.Questions[session.CurrentQuestion],
	})
}
