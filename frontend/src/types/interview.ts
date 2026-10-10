export type ExperienceLevel = 'Junior' | 'Mid' | 'Senior' | 'Lead' | 'Principal';
export type InterviewMode = 'Full-Loop' | 'Technical' | 'Behavioral' | 'HR' | 'Mixed' | 'Job-specific';
export type InterviewType = InterviewMode;
export type Difficulty = 'Easy' | 'Medium' | 'Hard';

export interface HiddenWeakness {
  tag: string;
  insight: string;
  evidence: string;
  coaching_tip: string;
}

export interface SkillAssessment {
  category: string;
  score?: number | null;
  status: 'Mastered' | 'Competent' | 'Needs Practice' | 'Insufficient Data';
  observations: string;
  confidence: 'High' | 'Medium' | 'Insufficient';
}

export interface DepthAuditItem {
  topic: string;
  candidate_claim: string;
  verification_status: 'Verified Depth' | 'Superficial / Probe Triggered';
  probe_question?: string | null;
  coach_observation: string;
}

export interface RoundEvaluation {
  round_name: string;
  interviewer_persona: string;
  verdict: 'Strong Hire' | 'Hire' | 'Lean Hire' | 'Lean No Hire' | 'No Hire';
  score: number;
  key_takeaway: string;
}

export interface ResumeProject {
  name: string;
  technologies: string[];
  description: string;
}

export interface ResumeExperience {
  company: string;
  role: string;
  duration?: string | null;
  highlights: string[];
}

export interface ResumeAnalysis {
  candidate_name?: string | null;
  inferred_role?: string | null;
  skills: string[];
  projects: ResumeProject[];
  experiences: ResumeExperience[];
  suggested_topics: string[];
}

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
  resume_context_used?: string | null;
  adaptive_context?: string | null;
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
  latent_blindspot?: string | null;
  bluff_detected?: boolean;
  buzzwords_detected?: string[];
  probing_rationale?: string | null;
  round_stage?: string | null;
  interviewer_persona?: string | null;
  created_at: string;
}

export interface InterviewSession {
  id: string;
  role_title: string;
  experience_level: ExperienceLevel;
  interview_type: InterviewMode;
  difficulty: Difficulty;
  num_questions: number;
  resume_text?: string | null;
  job_description?: string | null;
  status: 'in_progress' | 'completed' | 'abandoned';
  overall_score?: number | null;
  readiness_level?: string | null;
  summary?: string | null;
  strengths: string[];
  weaknesses: string[];
  hidden_weaknesses?: HiddenWeakness[];
  skill_map?: SkillAssessment[];
  depth_audit?: DepthAuditItem[];
  round_evaluations?: RoundEvaluation[];
  hiring_committee_verdict?: string | null;
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
  interview_type: InterviewMode;
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
  interview_type: InterviewMode;
  difficulty: Difficulty;
  num_questions: number;
  resume_text?: string;
  job_description?: string;
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
    latent_blindspot?: string | null;
    requires_followup: boolean;
    followup_reason?: string | null;
    bluff_detected?: boolean;
    buzzwords_detected?: string[];
    probing_rationale?: string | null;
  };
  turn: QuestionTurn;
  next_question?: QuestionTurn | null;
  is_completed: boolean;
}

export interface ResumeParseResult {
  filename: string;
  extracted_text: string;
  char_count: number;
  analysis?: ResumeAnalysis | null;
}
