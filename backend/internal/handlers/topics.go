package handlers

import (
	"bytes"
	"encoding/json"
	"io"
	"net/http"

	"github.com/gin-gonic/gin"

	"interview-manager/backend/internal/models"
	"interview-manager/backend/internal/services"
)

// TopicsHandler handles topic-related requests
type TopicsHandler struct {
	llmClient *services.LLMClient
}

func NewTopicsHandler(llmClient *services.LLMClient) *TopicsHandler {
	return &TopicsHandler{llmClient: llmClient}
}

// ListTopics returns all available interview topics
func (h *TopicsHandler) ListTopics(c *gin.Context) {
	resp, err := http.Get(h.llmClient.BaseURL() + "/api/topics")
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to fetch topics"})
		return
	}
	defer resp.Body.Close()

	var result map[string]interface{}
	json.NewDecoder(resp.Body).Decode(&result)
	c.JSON(resp.StatusCode, result)
}

// ListDomains returns all available domains
func (h *TopicsHandler) ListDomains(c *gin.Context) {
	resp, err := http.Get(h.llmClient.BaseURL() + "/api/topics/domains")
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to fetch domains"})
		return
	}
	defer resp.Body.Close()

	var result map[string]interface{}
	json.NewDecoder(resp.Body).Decode(&result)
	c.JSON(resp.StatusCode, result)
}

// ListTopicsByDomain returns topics filtered by domain
func (h *TopicsHandler) ListTopicsByDomain(c *gin.Context) {
	domain := c.Param("domain")
	resp, err := http.Get(h.llmClient.BaseURL() + "/api/topics/domain/" + domain)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to fetch topics"})
		return
	}
	defer resp.Body.Close()

	var result map[string]interface{}
	json.NewDecoder(resp.Body).Decode(&result)
	c.JSON(resp.StatusCode, result)
}

// JDHandler handles job description related requests
type JDHandler struct {
	llmClient      *services.LLMClient
	sessionService *services.SessionService
}

func NewJDHandler(llmClient *services.LLMClient, sessionService *services.SessionService) *JDHandler {
	return &JDHandler{
		llmClient:      llmClient,
		sessionService: sessionService,
	}
}

// UploadJD handles PDF job description upload
func (h *JDHandler) UploadJD(c *gin.Context) {
	file, err := c.FormFile("file")
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "No file uploaded"})
		return
	}

	sessionID := c.PostForm("session_id")
	if sessionID == "" {
		c.JSON(http.StatusBadRequest, gin.H{"error": "session_id is required"})
		return
	}

	// Open the file
	src, err := file.Open()
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to open file"})
		return
	}
	defer src.Close()

	// Read file content
	content, err := io.ReadAll(src)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to read file"})
		return
	}

	// Create multipart form for LLM service
	// Forward to LLM service using form data
	req, err := http.NewRequest("POST", h.llmClient.BaseURL()+"/api/jd/upload", bytes.NewReader(content))
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to create request"})
		return
	}

	// Use multipart form
	var b bytes.Buffer
	w := NewMultipartWriter(&b)
	fw, _ := w.CreateFormFile("file", file.Filename)
	fw.Write(content)
	w.WriteField("session_id", sessionID)
	w.Close()

	req, _ = http.NewRequest("POST", h.llmClient.BaseURL()+"/api/jd/upload", &b)
	req.Header.Set("Content-Type", w.FormDataContentType())

	client := &http.Client{}
	resp, err := client.Do(req)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to process JD: " + err.Error()})
		return
	}
	defer resp.Body.Close()

	var result map[string]interface{}
	json.NewDecoder(resp.Body).Decode(&result)

	// Store JD info in session if it exists
	if session, err := h.sessionService.GetSession(sessionID); err == nil && result["extracted"] != nil {
		extracted := result["extracted"].(map[string]interface{})
		session.JobDescription = &models.JobDescriptionInfo{
			Title:            getString(extracted, "title"),
			Domain:           getString(extracted, "domain"),
			ExperienceLevel:  getString(extracted, "experienceLevel"),
			InterviewContext: getString(result, "interviewContext"),
		}
		h.sessionService.UpdateSession(session)
	}

	c.JSON(resp.StatusCode, result)
}

// ProcessJDText handles raw text job description
func (h *JDHandler) ProcessJDText(c *gin.Context) {
	var req struct {
		Text      string `json:"text" binding:"required"`
		SessionID string `json:"sessionId" binding:"required"`
	}

	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	// Forward to LLM service
	payload := map[string]string{
		"text":      req.Text,
		"sessionId": req.SessionID,
	}
	jsonData, _ := json.Marshal(payload)

	resp, err := http.Post(
		h.llmClient.BaseURL()+"/api/jd/text",
		"application/json",
		bytes.NewBuffer(jsonData),
	)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to process JD"})
		return
	}
	defer resp.Body.Close()

	var result map[string]interface{}
	json.NewDecoder(resp.Body).Decode(&result)

	// Store JD info in session if it exists
	if session, err := h.sessionService.GetSession(req.SessionID); err == nil && result["extracted"] != nil {
		extracted := result["extracted"].(map[string]interface{})
		session.JobDescription = &models.JobDescriptionInfo{
			Title:            getString(extracted, "title"),
			Domain:           getString(extracted, "domain"),
			ExperienceLevel:  getString(extracted, "experienceLevel"),
			InterviewContext: getString(result, "interviewContext"),
		}
		h.sessionService.UpdateSession(session)
	}

	c.JSON(resp.StatusCode, result)
}

// GetJDContext retrieves stored JD context
func (h *JDHandler) GetJDContext(c *gin.Context) {
	sessionID := c.Param("sessionId")

	resp, err := http.Get(h.llmClient.BaseURL() + "/api/jd/" + sessionID)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to fetch JD context"})
		return
	}
	defer resp.Body.Close()

	var result map[string]interface{}
	json.NewDecoder(resp.Body).Decode(&result)
	c.JSON(resp.StatusCode, result)
}

// ClearJDContext removes JD context for a session
func (h *JDHandler) ClearJDContext(c *gin.Context) {
	sessionID := c.Param("sessionId")

	req, _ := http.NewRequest("DELETE", h.llmClient.BaseURL()+"/api/jd/"+sessionID, nil)
	client := &http.Client{}
	resp, err := client.Do(req)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to clear JD context"})
		return
	}
	defer resp.Body.Close()

	// Also clear from session
	if session, err := h.sessionService.GetSession(sessionID); err == nil {
		session.JobDescription = nil
		h.sessionService.UpdateSession(session)
	}

	c.JSON(http.StatusOK, gin.H{"success": true})
}

// Helper to safely get string from map
func getString(m map[string]interface{}, key string) string {
	if v, ok := m[key]; ok {
		if s, ok := v.(string); ok {
			return s
		}
	}
	return ""
}

// Simple multipart writer helper
type MultipartWriter struct {
	w        io.Writer
	boundary string
}

func NewMultipartWriter(w io.Writer) *MultipartWriter {
	return &MultipartWriter{
		w:        w,
		boundary: "----WebKitFormBoundary7MA4YWxkTrZu0gW",
	}
}

func (m *MultipartWriter) CreateFormFile(fieldname, filename string) (io.Writer, error) {
	m.w.Write([]byte("--" + m.boundary + "\r\n"))
	m.w.Write([]byte("Content-Disposition: form-data; name=\"" + fieldname + "\"; filename=\"" + filename + "\"\r\n"))
	m.w.Write([]byte("Content-Type: application/pdf\r\n\r\n"))
	return m.w, nil
}

func (m *MultipartWriter) WriteField(fieldname, value string) error {
	m.w.Write([]byte("\r\n--" + m.boundary + "\r\n"))
	m.w.Write([]byte("Content-Disposition: form-data; name=\"" + fieldname + "\"\r\n\r\n"))
	m.w.Write([]byte(value))
	return nil
}

func (m *MultipartWriter) Close() error {
	m.w.Write([]byte("\r\n--" + m.boundary + "--\r\n"))
	return nil
}

func (m *MultipartWriter) FormDataContentType() string {
	return "multipart/form-data; boundary=" + m.boundary
}
