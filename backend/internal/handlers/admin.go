package handlers

import (
	"net/http"

	"github.com/gin-gonic/gin"

	"interview-manager/backend/internal/services"
)

type AdminHandler struct {
	sessionService *services.SessionService
}

func NewAdminHandler(sessionService *services.SessionService) *AdminHandler {
	return &AdminHandler{
		sessionService: sessionService,
	}
}

func (h *AdminHandler) CreateSession(c *gin.Context) {
	// Similar to StartInterview but for admin pre-setup
	c.JSON(http.StatusOK, gin.H{"message": "Admin session creation"})
}

func (h *AdminHandler) ListSessions(c *gin.Context) {
	sessions := h.sessionService.ListAllSessions()
	c.JSON(http.StatusOK, gin.H{"sessions": sessions})
}

func (h *AdminHandler) GetReport(c *gin.Context) {
	sessionID := c.Param("sessionId")

	session, err := h.sessionService.GetSession(sessionID)
	if err != nil {
		c.JSON(http.StatusNotFound, gin.H{"error": "Session not found"})
		return
	}

	if session.FinalReport == nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Report not generated yet"})
		return
	}

	c.JSON(http.StatusOK, session.FinalReport)
}
