export type ExperienceLevel = 'Junior' | 'Mid' | 'Senior' | 'Lead' | 'Principal';
export type InterviewType = 'Technical' | 'Behavioral' | 'System Design' | 'Leadership' | 'Mixed';
export type Difficulty = 'Easy' | 'Medium' | 'Hard';

export interface QuestionTurn {
  id: string;
  session_id: string;
  turn_number: number;
  is_followup: boolean;
  parent_turn_id?: string | null;
  question_text: string;
  question_category: string;
  difficulty: string;
  expected_points: string[];
  user_answer?: string | null;
  answered_at?: string | null;
  technical_score?: number | null;
  relevance_score?: number | null;
  clarity_score?: number | null;
  completeness_score?: number | null;
  turn_score?: number | null;
  feedback?: string | null;
  key_positives: string[];
  areas_for_improvement: string[];
  sample_ideal_answer?: string | null;
  created_at: string;
}

export interface InterviewSession {
  id: string;
  role_title: string;
  experience_level: ExperienceLevel;
  interview_type: InterviewType;
  difficulty: Difficulty;
  num_questions: number;
  resume_text?: string | null;
  status: 'in_progress' | 'completed' | 'abandoned';
  overall_score?: number | null;
  readiness_level?: string | null;
  summary?: string | null;
  strengths: string[];
  weaknesses: string[];
  recommended_topics: string[];
  closing_advice?: string | null;
  created_at: string;
  updated_at: string;
  turns: QuestionTurn[];
}

export interface InterviewSessionSummary {
  id: string;
  role_title: string;
  experience_level: ExperienceLevel;
  interview_type: InterviewType;
  difficulty: Difficulty;
  num_questions: number;
  status: 'in_progress' | 'completed' | 'abandoned';
  overall_score?: number | null;
  readiness_level?: string | null;
  created_at: string;
  updated_at: string;
  answered_turns_count: number;
  total_turns_count: number;
}

export interface CreateInterviewPayload {
  role_title: string;
  experience_level: ExperienceLevel;
  interview_type: InterviewType;
  difficulty: Difficulty;
  num_questions: number;
  resume_text?: string;
}

export interface TurnEvaluationResult {
  evaluation: {
    technical_score: number;
    relevance_score: number;
    clarity_score: number;
    completeness_score: number;
    turn_score: number;
    feedback: string;
    key_positives: string[];
    areas_for_improvement: string[];
    sample_ideal_answer: string;
    requires_followup: boolean;
    followup_reason?: string | null;
  };
  turn: QuestionTurn;
  next_question?: QuestionTurn | null;
  is_completed: boolean;
}

export interface ResumeParseResult {
  filename: string;
  extracted_text: string;
  char_count: number;
}
