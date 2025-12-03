import axios from 'axios';
import type {
  StartInterviewRequest,
  StartInterviewResponse,
  RespondRequest,
  RespondResponse,
  IntegrityEventRequest,
  InterviewSession,
  Report
} from '@/types';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8080';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Interview endpoints
export const interviewAPI = {
  start: async (data: StartInterviewRequest): Promise<StartInterviewResponse> => {
    const response = await api.post('/api/interview/start', data);
    return response.data;
  },

  respond: async (data: RespondRequest): Promise<RespondResponse> => {
    const response = await api.post('/api/interview/respond', data);
    return response.data;
  },

  end: async (sessionId: string): Promise<{ report: Report; scores: Record<string, number>; transcript: any[] }> => {
    const response = await api.post('/api/interview/end', { sessionId });
    return response.data;
  },

  getStatus: async (sessionId: string): Promise<{
    currentState: string;
    timeRemaining: number;
    questionsAsked: number;
    currentQuestion: any;
  }> => {
    const response = await api.get(`/api/interview/status/${sessionId}`);
    return response.data;
  },
};

// Integrity endpoints
export const integrityAPI = {
  logEvent: async (data: IntegrityEventRequest): Promise<{ acknowledged: boolean; severity: string }> => {
    const response = await api.post('/api/integrity/event', data);
    return response.data;
  },

  getEvents: async (sessionId: string): Promise<{ events: any[]; count: number }> => {
    const response = await api.get(`/api/integrity/events/${sessionId}`);
    return response.data;
  },
};

// Admin endpoints
export const adminAPI = {
  listSessions: async (): Promise<{ sessions: InterviewSession[] }> => {
    const response = await api.get('/api/admin/sessions');
    return response.data;
  },

  getReport: async (sessionId: string): Promise<Report> => {
    const response = await api.get(`/api/admin/report/${sessionId}`);
    return response.data;
  },
};

export default api;
