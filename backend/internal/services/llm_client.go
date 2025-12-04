package services

import (
	"bytes"
	"encoding/json"
	"fmt"
	"net/http"

	"interview-manager/backend/internal/models"
)

// LLMClient communicates with the Python LLM service
type LLMClient struct {
	baseURL string
	client  *http.Client
}

func NewLLMClient(baseURL string) *LLMClient {
	if baseURL == "" {
		baseURL = "http://localhost:8000" // Default Python service URL
	}

	return &LLMClient{
		baseURL: baseURL,
		client:  &http.Client{},
	}
}

// BaseURL returns the LLM service base URL
func (l *LLMClient) BaseURL() string {
	return l.baseURL
}

// LLMEvaluationResponse represents the response from LLM service
type LLMEvaluationResponse struct {
	Evaluation *models.Evaluation `json:"evaluation"`
	NextAction string             `json:"nextAction"`
	AIResponse string             `json:"aiResponse"`
}

// GetFirstQuestion gets the first question from LLM service
func (l *LLMClient) GetFirstQuestion(topic, difficulty, sessionID string) (models.Question, error) {
	payload := map[string]interface{}{
		"topic":      topic,
		"difficulty": difficulty,
		"position":   0,
	}
	if sessionID != "" {
		payload["sessionId"] = sessionID
	}

	var question models.Question
	err := l.post("/api/question/generate", payload, &question)
	return question, err
}

// GetNextQuestion gets the next question
func (l *LLMClient) GetNextQuestion(topic, difficulty string, position int, sessionID string) (models.Question, error) {
	payload := map[string]interface{}{
		"topic":      topic,
		"difficulty": difficulty,
		"position":   position,
	}
	if sessionID != "" {
		payload["sessionId"] = sessionID
	}

	var question models.Question
	err := l.post("/api/question/generate", payload, &question)
	return question, err
}

// EvaluateAndDecideNext evaluates answer and decides next action
func (l *LLMClient) EvaluateAndDecideNext(
	question models.Question,
	answer string,
	history []models.ConversationTurn,
) (*LLMEvaluationResponse, error) {
	payload := map[string]interface{}{
		"question": question,
		"answer":   answer,
		"history":  history,
	}

	var response LLMEvaluationResponse
	err := l.post("/api/evaluate", payload, &response)
	return &response, err
}

// GenerateReport generates final interview report
func (l *LLMClient) GenerateReport(session *models.InterviewSession) (models.Report, error) {
	payload := map[string]interface{}{
		"session": session,
	}

	var report models.Report
	err := l.post("/api/report/generate", payload, &report)
	return report, err
}

// AddToContext adds an exchange to the context manager
func (l *LLMClient) AddToContext(sessionID, speaker, text, exchangeType string, evaluation *models.Evaluation) error {
	payload := map[string]interface{}{
		"sessionId":    sessionID,
		"speaker":      speaker,
		"text":         text,
		"exchangeType": exchangeType,
	}
	if evaluation != nil {
		payload["evaluation"] = evaluation
	}

	var response map[string]interface{}
	return l.post("/api/context/add", payload, &response)
}

// GetContext retrieves the formatted context for LLM consumption
func (l *LLMClient) GetContext(sessionID string) (string, error) {
	var response struct {
		Context string                 `json:"context"`
		Stats   map[string]interface{} `json:"stats"`
	}
	
	err := l.get(fmt.Sprintf("/api/context/%s", sessionID), &response)
	if err != nil {
		return "", err
	}
	return response.Context, nil
}

// AdvanceQuestion marks that interview moved to next question
func (l *LLMClient) AdvanceQuestion(sessionID string) error {
	var response map[string]interface{}
	return l.post(fmt.Sprintf("/api/context/%s/advance", sessionID), nil, &response)
}

// ClearContext removes context for a completed session
func (l *LLMClient) ClearContext(sessionID string) error {
	return l.delete(fmt.Sprintf("/api/context/%s", sessionID))
}

// CopyJDContext copies JD context from one session to another
func (l *LLMClient) CopyJDContext(fromSessionID, toSessionID string) error {
	// Get JD context from source session
	var jdResponse struct {
		SessionID string `json:"sessionId"`
		Context   string `json:"context"`
	}
	
	err := l.get(fmt.Sprintf("/api/jd/%s", fromSessionID), &jdResponse)
	if err != nil {
		return err // No JD context to copy
	}
	
	// Store it for the new session
	payload := map[string]interface{}{
		"text":      jdResponse.Context,
		"sessionId": toSessionID,
	}
	
	var response map[string]interface{}
	return l.post("/api/jd/text", payload, &response)
}

// Helper method for GET requests
func (l *LLMClient) get(endpoint string, response interface{}) error {
	url := l.baseURL + endpoint
	req, err := http.NewRequest("GET", url, nil)
	if err != nil {
		return err
	}

	resp, err := l.client.Do(req)
	if err != nil {
		return fmt.Errorf("failed to connect to LLM service: %w", err)
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		var errBody map[string]interface{}
		json.NewDecoder(resp.Body).Decode(&errBody)
		return fmt.Errorf("LLM service error %s: %v", resp.Status, errBody)
	}

	return json.NewDecoder(resp.Body).Decode(response)
}

// Helper method for DELETE requests
func (l *LLMClient) delete(endpoint string) error {
	url := l.baseURL + endpoint
	req, err := http.NewRequest("DELETE", url, nil)
	if err != nil {
		return err
	}

	resp, err := l.client.Do(req)
	if err != nil {
		return fmt.Errorf("failed to connect to LLM service: %w", err)
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		var errBody map[string]interface{}
		json.NewDecoder(resp.Body).Decode(&errBody)
		return fmt.Errorf("LLM service error %s: %v", resp.Status, errBody)
	}

	return nil
}

// Helper method for POST requests
func (l *LLMClient) post(endpoint string, payload interface{}, response interface{}) error {
	jsonData, err := json.Marshal(payload)
	if err != nil {
		return err
	}

	url := l.baseURL + endpoint
	req, err := http.NewRequest("POST", url, bytes.NewBuffer(jsonData))
	if err != nil {
		return err
	}

	req.Header.Set("Content-Type", "application/json")

	resp, err := l.client.Do(req)
	if err != nil {
		return fmt.Errorf("failed to connect to LLM service: %w", err)
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		var errBody map[string]interface{}
		json.NewDecoder(resp.Body).Decode(&errBody)
		return fmt.Errorf("LLM service error %s: %v", resp.Status, errBody)
	}

	return json.NewDecoder(resp.Body).Decode(response)
}
