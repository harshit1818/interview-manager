package handlers

import (
	"net/http"
	"time"

	"github.com/gin-gonic/gin"

	"interview-manager/backend/internal/models"
	"interview-manager/backend/internal/services"
)

type IntegrityHandler struct {
	sessionService *services.SessionService
}

func NewIntegrityHandler(sessionService *services.SessionService) *IntegrityHandler {
	return &IntegrityHandler{
		sessionService: sessionService,
	}
}

// LogEvent logs an integrity event
func (h *IntegrityHandler) LogEvent(c *gin.Context) {
	var req models.IntegrityEventRequest
	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	// Determine severity based on event type
	severity := determineSeverity(req.EventType)

	event := models.IntegrityEvent{
		Timestamp: time.Now(),
		Type:      req.EventType,
		Severity:  severity,
		Metadata:  req.Metadata,
	}

	if err := h.sessionService.AddIntegrityEvent(req.SessionID, event); err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to log event"})
		return
	}

	c.JSON(http.StatusOK, gin.H{
		"acknowledged": true,
		"severity":     severity,
	})
}

// GetEvents retrieves all integrity events for a session
func (h *IntegrityHandler) GetEvents(c *gin.Context) {
	sessionID := c.Param("sessionId")

	session, err := h.sessionService.GetSession(sessionID)
	if err != nil {
		c.JSON(http.StatusNotFound, gin.H{"error": "Session not found"})
		return
	}

	c.JSON(http.StatusOK, gin.H{
		"events": session.IntegrityEvents,
		"count":  len(session.IntegrityEvents),
	})
}

func determineSeverity(eventType string) string {
	switch eventType {
	case "MULTIPLE_FACES", "POSSIBLE_BACKGROUND_SPEECH":
		return "high"
	case "TAB_SWITCH", "WINDOW_BLUR", "SUDDEN_AUDIO_SPIKE":
		return "medium"
	case "GAZE_AWAY", "LARGE_PASTE", "PROLONGED_SILENCE", "LONG_SILENCE_ENDED":
		return "low"
	default:
		return "low"
	}
}
