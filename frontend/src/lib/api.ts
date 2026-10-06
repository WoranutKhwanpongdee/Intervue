import {
  CreateInterviewPayload,
  InterviewSession,
  InterviewSessionSummary,
  ResumeParseResult,
  TurnEvaluationResult
} from "@/types/interview";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api";

class ApiClient {
  private async request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
    const url = `${API_BASE_URL}${endpoint}`;
    const headers = {
      "Content-Type": "application/json",
      ...(options.headers || {}),
    };

    const response = await fetch(url, {
      ...options,
      headers,
    });

    if (!response.ok) {
      let errorMessage = `Request failed with status ${response.status}`;
      try {
        const errorData = await response.json();
        if (errorData.detail) {
          errorMessage = typeof errorData.detail === "string" ? errorData.detail : JSON.stringify(errorData.detail);
        }
      } catch {
        // Fallback to text
        const text = await response.text();
        if (text) errorMessage = text;
      }
      throw new Error(errorMessage);
    }

    return response.json();
  }

  // Interview Sessions
  async createInterview(payload: CreateInterviewPayload): Promise<InterviewSession> {
    return this.request<InterviewSession>("/interviews", {
      method: "POST",
      body: JSON.stringify(payload),
    });
  }

  async listInterviews(limit = 50, offset = 0): Promise<InterviewSessionSummary[]> {
    return this.request<InterviewSessionSummary[]>(`/interviews?limit=${limit}&offset=${offset}`);
  }

  async getInterview(id: string): Promise<InterviewSession> {
    return this.request<InterviewSession>(`/interviews/${id}`);
  }

  async submitAnswer(sessionId: string, turnId: string, answer: string): Promise<TurnEvaluationResult> {
    return this.request<TurnEvaluationResult>(`/interviews/${sessionId}/turns/${turnId}/answer`, {
      method: "POST",
      body: JSON.stringify({ answer }),
    });
  }

  async finishInterviewEarly(sessionId: string): Promise<InterviewSession> {
    return this.request<InterviewSession>(`/interviews/${sessionId}/finish`, {
      method: "POST",
    });
  }

  async deleteInterview(sessionId: string): Promise<void> {
    const url = `${API_BASE_URL}/interviews/${sessionId}`;
    const res = await fetch(url, { method: "DELETE" });
    if (!res.ok) {
      throw new Error(`Failed to delete interview (${res.status})`);
    }
  }

  // Resume Upload
  async uploadResume(file: File): Promise<ResumeParseResult> {
    const formData = new FormData();
    formData.append("file", file);

    const response = await fetch(`${API_BASE_URL}/resume/parse`, {
      method: "POST",
      body: formData,
    });

    if (!response.ok) {
      let msg = "Failed to parse resume";
      try {
        const err = await response.json();
        if (err.detail) msg = err.detail;
      } catch {
        // ignore
      }
      throw new Error(msg);
    }

    return response.json();
  }

  // Health check
  async checkHealth(): Promise<{ status: string; llm_provider: string }> {
    return this.request<{ status: string; llm_provider: string }>("/health");
  }
}

export const api = new ApiClient();
