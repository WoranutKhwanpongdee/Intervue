"use client";

import React, { useEffect, useState, use } from "react";
import { useRouter } from "next/navigation";
import { Clock, Send, CornerDownLeft, ChevronDown, ChevronUp, AlertCircle, LogOut, FileText, Sparkles } from "lucide-react";
import { api } from "@/lib/api";
import { InterviewSession, QuestionTurn } from "@/types/interview";
import { Button } from "@/components/ui/Button";
import { Badge } from "@/components/ui/Badge";
import { MetricCard } from "@/components/ui/MetricCard";

export default function InterviewRoomPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const router = useRouter();
  const resolvedParams = use(params);
  const sessionId = resolvedParams.id;

  const [session, setSession] = useState<InterviewSession | null>(null);
  const [currentTurn, setCurrentTurn] = useState<QuestionTurn | null>(null);
  const [userAnswer, setUserAnswer] = useState("");
  const [isLoading, setIsLoading] = useState(true);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isFinishingEarly, setIsFinishingEarly] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [elapsedSeconds, setElapsedSeconds] = useState(0);
  const [expandedTurnId, setExpandedTurnId] = useState<string | null>(null);

  useEffect(() => {
    let timer: NodeJS.Timeout;
    const fetchSession = async () => {
      try {
        const data = await api.getInterview(sessionId);
        setSession(data);

        if (data.status === "completed") {
          router.replace(`/report/${sessionId}`);
          return;
        }

        const unanswered = data.turns.find((t) => t.user_answer === null);
        if (unanswered) {
          setCurrentTurn(unanswered);
        } else if (data.turns.length > 0) {
          setCurrentTurn(data.turns[data.turns.length - 1]);
        }
      } catch (err: any) {
        setErrorMessage(err.message || "Failed to load interview session.");
      } finally {
        setIsLoading(false);
      }
    };

    fetchSession();

    timer = setInterval(() => {
      setElapsedSeconds((prev) => prev + 1);
    }, 1000);

    return () => clearInterval(timer);
  }, [sessionId, router]);

  const formatTimer = (totalSeconds: number) => {
    const mins = Math.floor(totalSeconds / 60);
    const secs = totalSeconds % 60;
    return `${mins.toString().padStart(2, "0")}:${secs.toString().padStart(2, "0")}`;
  };

  const handleSubmitAnswer = async () => {
    if (!currentTurn || !userAnswer.trim()) return;

    if (userAnswer.trim().length < 10) {
      setErrorMessage("Please provide a more detailed technical response.");
      return;
    }

    setIsSubmitting(true);
    setErrorMessage(null);

    try {
      const result = await api.submitAnswer(sessionId, currentTurn.id, userAnswer.trim());
      setUserAnswer("");

      const updatedSession = await api.getInterview(sessionId);
      setSession(updatedSession);

      if (result.is_completed || updatedSession.status === "completed") {
        router.push(`/report/${sessionId}`);
        return;
      }

      if (result.next_question) {
        setCurrentTurn(result.next_question);
      }
    } catch (err: any) {
      setErrorMessage(err.message || "Failed to submit answer.");
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleFinishEarly = async () => {
    if (!window.confirm("Conclude this interview session now and compile report?")) return;

    setIsFinishingEarly(true);
    try {
      await api.finishInterviewEarly(sessionId);
      router.push(`/report/${sessionId}`);
    } catch (err: any) {
      setErrorMessage(err.message || "Failed to conclude interview.");
      setIsFinishingEarly(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if ((e.ctrlKey || e.metaKey) && e.key === "Enter") {
      e.preventDefault();
      handleSubmitAnswer();
    }
  };

  if (isLoading) {
    return (
      <div className="flex h-[70vh] items-center justify-center bg-white dark:bg-black">
        <p className="text-xs font-mono text-neutral-500">Loading interview room...</p>
      </div>
    );
  }

  if (!session || !currentTurn) {
    return (
      <div className="mx-auto max-w-xl py-24 px-6 text-center">
        <h2 className="text-lg font-semibold text-neutral-900 dark:text-neutral-100">Session not found</h2>
        <p className="text-xs text-neutral-500 mt-2 mb-6">{errorMessage || "Could not retrieve session data."}</p>
        <Button onClick={() => router.push("/setup")}>Start New Interview</Button>
      </div>
    );
  }

  const answeredTurns = session.turns.filter((t) => t.user_answer !== null);

  return (
    <div className="min-h-screen bg-white dark:bg-black pb-24 text-neutral-900 dark:text-neutral-100">
      {/* Session Top Bar */}
      <div className="border-b border-neutral-100 dark:border-neutral-900 bg-white/90 dark:bg-black/90 sticky top-13 z-30">
        <div className="mx-auto max-w-4xl px-6 py-3 flex items-center justify-between">
          <div className="flex items-center gap-2 sm:gap-3">
            <span className="font-medium text-xs text-neutral-900 dark:text-neutral-100">
              {session.role_title}
            </span>
            <span className="text-neutral-300 dark:text-neutral-700">/</span>
            <span className="text-[11px] font-mono px-2 py-0.5 rounded bg-neutral-100 dark:bg-neutral-800 text-neutral-600 dark:text-neutral-300">
              🎯 {session.interview_type}
            </span>
            <span className="text-neutral-300 dark:text-neutral-700 hidden sm:inline">/</span>
            <span className="text-xs text-neutral-500 hidden sm:inline">
              Q{answeredTurns.length + 1} of {session.num_questions}
            </span>
          </div>

          <div className="flex items-center gap-4 text-xs font-mono text-neutral-500">
            <span className="hidden sm:inline-flex items-center gap-1 text-[11px] px-2 py-0.5 rounded bg-amber-50 dark:bg-amber-950/40 text-amber-700 dark:text-amber-400 border border-amber-200 dark:border-amber-900/50">
              <Sparkles className="h-3 w-3 animate-pulse text-amber-500" />
              <span>Adaptive AI Active</span>
            </span>
            <span className="flex items-center gap-1.5">
              <Clock className="h-3 w-3" />
              {formatTimer(elapsedSeconds)}
            </span>
            <button
              onClick={handleFinishEarly}
              disabled={isFinishingEarly}
              className="text-neutral-400 hover:text-red-600 transition-colors cursor-pointer text-xs font-sans"
            >
              Finish Early
            </button>
          </div>
        </div>
      </div>

      <div className="mx-auto max-w-3xl px-6 pt-10 space-y-8">
        {errorMessage && (
          <div className="p-3 rounded-lg border border-red-200 dark:border-red-900 bg-red-50 dark:bg-red-950/40 text-red-800 dark:text-red-300 text-xs">
            {errorMessage}
          </div>
        )}

        {/* Current Question Block */}
        <div className="space-y-4">
          <div className="flex flex-wrap items-center gap-2">
            <span className="text-xs font-mono text-neutral-400 uppercase">
              {currentTurn.is_followup ? "Follow-up Probe" : `Question 0${currentTurn.turn_number}`}
            </span>
            <span>·</span>
            <span className="text-xs font-medium text-neutral-500">{currentTurn.question_category}</span>

            {/* Resume Grounding Badge */}
            {currentTurn.resume_context_used && (
              <>
                <span>·</span>
                <span className="inline-flex items-center gap-1 text-[11px] font-mono px-2 py-0.5 rounded bg-emerald-50 dark:bg-emerald-950/50 text-emerald-700 dark:text-emerald-300 border border-emerald-200 dark:border-emerald-800">
                  <FileText className="h-3 w-3" />
                  Grounded: {currentTurn.resume_context_used}
                </span>
              </>
            )}

            {/* Adaptive Context Badge */}
            {currentTurn.adaptive_context && (
              <>
                <span>·</span>
                <span className="inline-flex items-center gap-1 text-[11px] font-mono px-2 py-0.5 rounded bg-amber-50 dark:bg-amber-950/50 text-amber-700 dark:text-amber-300 border border-amber-200 dark:border-amber-800">
                  <Sparkles className="h-3 w-3 text-amber-500" />
                  {currentTurn.adaptive_context}
                </span>
              </>
            )}
          </div>

          <h2 className="text-xl sm:text-2xl font-medium tracking-tight text-neutral-900 dark:text-neutral-50 leading-relaxed">
            {currentTurn.question_text}
          </h2>

          {currentTurn.is_followup && (
            <p className="text-xs text-neutral-500 border-l-2 border-neutral-400 pl-3 py-0.5">
              Targeted follow-up: The interviewer is exploring trade-offs or edge cases from your previous response.
            </p>
          )}

          {currentTurn.expected_points && currentTurn.expected_points.length > 0 && (
            <div className="pt-1 flex flex-wrap gap-1.5">
              {currentTurn.expected_points.map((p, idx) => (
                <span
                  key={idx}
                  className="text-[11px] font-mono px-2 py-0.5 rounded bg-neutral-100 dark:bg-neutral-900 text-neutral-600 dark:text-neutral-400"
                >
                  {p}
                </span>
              ))}
            </div>
          )}
        </div>

        {/* Response Input */}
        <div className="space-y-3 pt-2">
          <textarea
            rows={9}
            value={userAnswer}
            onChange={(e) => setUserAnswer(e.target.value)}
            onKeyDown={handleKeyDown}
            disabled={isSubmitting}
            placeholder="Type your response here. Explain architecture, edge cases, and rationale..."
            className="w-full p-4 text-sm rounded-lg border border-neutral-300 dark:border-neutral-800 bg-white dark:bg-neutral-950 text-neutral-900 dark:text-neutral-100 focus:outline-none focus:border-black dark:focus:border-white transition-colors leading-relaxed font-sans"
          />

          <div className="flex items-center justify-between">
            <div className="text-[11px] font-mono text-neutral-400">
              {userAnswer.trim().split(/\s+/).filter(Boolean).length} words · Press ⌘/Ctrl+Enter
            </div>

            <Button
              onClick={handleSubmitAnswer}
              disabled={isSubmitting || !userAnswer.trim()}
              isLoading={isSubmitting}
              size="md"
            >
              {isSubmitting ? "Evaluating..." : "Submit Response"}
            </Button>
          </div>
        </div>

        {/* Answered Turns Review */}
        {answeredTurns.length > 0 && (
          <div className="pt-8 border-t border-neutral-100 dark:border-neutral-900 space-y-4">
            <p className="text-xs font-mono uppercase tracking-wider text-neutral-500">
              Completed Turns ({answeredTurns.length})
            </p>

            <div className="space-y-3">
              {answeredTurns.map((turn) => {
                const isExpanded = expandedTurnId === turn.id;
                return (
                  <div
                    key={turn.id}
                    className="rounded-lg border border-neutral-200 dark:border-neutral-800 bg-neutral-50/50 dark:bg-neutral-950/50 overflow-hidden"
                  >
                    <button
                      type="button"
                      onClick={() => setExpandedTurnId(isExpanded ? null : turn.id)}
                      className="w-full p-4 text-left flex items-center justify-between gap-4 cursor-pointer"
                    >
                      <div className="space-y-0.5">
                        <div className="flex items-center gap-2 text-xs font-mono text-neutral-400">
                          <span>Question 0{turn.turn_number} · {turn.question_category}</span>
                          {turn.resume_context_used && (
                            <span className="text-[10px] text-emerald-600 dark:text-emerald-400">
                              · Grounded in {turn.resume_context_used}
                            </span>
                          )}
                        </div>
                        <div className="text-xs sm:text-sm font-medium text-neutral-900 dark:text-neutral-100 line-clamp-1">
                          {turn.question_text}
                        </div>
                      </div>

                      <div className="flex items-center gap-3 shrink-0">
                        <span className="text-xs font-mono font-semibold text-neutral-900 dark:text-neutral-100">
                          {Math.round(turn.turn_score || 0)}/100
                        </span>
                        {isExpanded ? (
                          <ChevronUp className="h-3.5 w-3.5 text-neutral-400" />
                        ) : (
                          <ChevronDown className="h-3.5 w-3.5 text-neutral-400" />
                        )}
                      </div>
                    </button>

                    {isExpanded && (
                      <div className="p-4 pt-0 border-t border-neutral-200 dark:border-neutral-800 space-y-4 mt-3">
                        {turn.adaptive_context && (
                          <div className="text-[11px] font-mono px-2 py-0.5 rounded bg-amber-50 dark:bg-amber-950/40 text-amber-700 dark:text-amber-300 border border-amber-200 dark:border-amber-800 w-fit">
                            ⚡ {turn.adaptive_context}
                          </div>
                        )}

                        {/* Candidate response */}
                        <div className="space-y-1">
                          <span className="text-[11px] font-mono text-neutral-400 uppercase">Your Answer</span>
                          <p className="text-xs text-neutral-700 dark:text-neutral-300 leading-relaxed font-sans bg-white dark:bg-neutral-900 p-3 rounded border border-neutral-200 dark:border-neutral-800 whitespace-pre-wrap">
                            {turn.user_answer}
                          </p>
                        </div>

                        {/* Metric Grid */}
                        <div className="grid grid-cols-2 sm:grid-cols-4 gap-2">
                          <MetricCard label="Technical" score={turn.technical_score || 0} />
                          <MetricCard label="Relevance" score={turn.relevance_score || 0} />
                          <MetricCard label="Clarity" score={turn.clarity_score || 0} />
                          <MetricCard label="Depth" score={turn.completeness_score || 0} />
                        </div>

                        {/* Constructive feedback */}
                        {turn.feedback && (
                          <div className="space-y-1">
                            <span className="text-[11px] font-mono text-neutral-400 uppercase">Feedback</span>
                            <p className="text-xs text-neutral-700 dark:text-neutral-300 leading-relaxed">
                              {turn.feedback}
                            </p>
                          </div>
                        )}

                        {/* Sample Ideal Answer */}
                        {turn.sample_ideal_answer && (
                          <div className="space-y-1">
                            <span className="text-[11px] font-mono text-neutral-400 uppercase">Reference Answer</span>
                            <p className="text-xs text-neutral-600 dark:text-neutral-400 leading-relaxed bg-neutral-100 dark:bg-neutral-900/80 p-3 rounded font-sans">
                              {turn.sample_ideal_answer}
                            </p>
                          </div>
                        )}
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
