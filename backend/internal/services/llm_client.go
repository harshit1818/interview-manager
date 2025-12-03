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

// LLMEvaluationResponse represents the response from LLM service
type LLMEvaluationResponse struct {
	Evaluation *models.Evaluation `json:"evaluation"`
	NextAction string             `json:"nextAction"`
	AIResponse string             `json:"aiResponse"`
}

// GetFirstQuestion gets the first question from LLM service
func (l *LLMClient) GetFirstQuestion(topic, difficulty string) (models.Question, error) {
	payload := map[string]interface{}{
		"topic":      topic,
		"difficulty": difficulty,
		"position":   0,
	}

	var question models.Question
	err := l.post("/api/question/generate", payload, &question)
	return question, err
}

// GetNextQuestion gets the next question
func (l *LLMClient) GetNextQuestion(topic, difficulty string, position int) (models.Question, error) {
	payload := map[string]interface{}{
		"topic":      topic,
		"difficulty": difficulty,
		"position":   position,
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
