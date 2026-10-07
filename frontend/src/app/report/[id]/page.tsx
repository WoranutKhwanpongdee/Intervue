"use client";

import React, { useEffect, useState, use } from "react";
import Link from "next/link";
import { Printer, RotateCcw, ChevronDown, ChevronUp, ArrowRight } from "lucide-react";
import { api } from "@/lib/api";
import { InterviewSession } from "@/types/interview";
import { Button } from "@/components/ui/Button";
import { Badge } from "@/components/ui/Badge";
import { MetricCard } from "@/components/ui/MetricCard";
import { formatDate } from "@/lib/utils";

export default function FinalReportPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const resolvedParams = use(params);
  const sessionId = resolvedParams.id;

  const [session, setSession] = useState<InterviewSession | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [expandedTurns, setExpandedTurns] = useState<Record<string, boolean>>({});

  useEffect(() => {
    const fetchReport = async () => {
      try {
        const data = await api.getInterview(sessionId);
        setSession(data);
      } catch (err: any) {
        setError(err.message || "Failed to load report.");
      } finally {
        setIsLoading(false);
      }
    };

    fetchReport();
  }, [sessionId]);

  const toggleTurn = (turnId: string) => {
    setExpandedTurns((prev) => ({
      ...prev,
      [turnId]: !prev[turnId],
    }));
  };

  if (isLoading) {
    return (
      <div className="flex h-[70vh] items-center justify-center bg-white dark:bg-black">
        <p className="text-xs font-mono text-neutral-500">Compiling evaluation report...</p>
      </div>
    );
  }

  if (error || !session) {
    return (
      <div className="mx-auto max-w-xl py-24 px-6 text-center">
        <h2 className="text-lg font-semibold text-neutral-900 dark:text-neutral-100">Report not found</h2>
        <p className="text-xs text-neutral-500 mt-2 mb-6">{error || "Could not retrieve report data."}</p>
        <Link href="/history">
          <Button variant="outline">Back to History</Button>
        </Link>
      </div>
    );
  }

  const answeredTurns = session.turns.filter((t) => t.user_answer !== null);
  const avgTech =
    answeredTurns.reduce((acc, t) => acc + (t.technical_score || 0), 0) / (answeredTurns.length || 1);
  const avgRel =
    answeredTurns.reduce((acc, t) => acc + (t.relevance_score || 0), 0) / (answeredTurns.length || 1);
  const avgClar =
    answeredTurns.reduce((acc, t) => acc + (t.clarity_score || 0), 0) / (answeredTurns.length || 1);
  const avgComp =
    answeredTurns.reduce((acc, t) => acc + (t.completeness_score || 0), 0) / (answeredTurns.length || 1);

  const overall =
    session.overall_score !== null && session.overall_score !== undefined
      ? Math.round(session.overall_score)
      : Math.round(avgTech * 0.4 + avgRel * 0.25 + avgClar * 0.15 + avgComp * 0.2);

  return (
    <div className="min-h-screen bg-white dark:bg-black py-12 text-neutral-900 dark:text-neutral-100">
      <div className="mx-auto max-w-3xl px-6 space-y-10">
        {/* Header */}
        <div className="flex items-baseline justify-between pb-4 border-b border-neutral-100 dark:border-neutral-900">
          <div>
            <p className="text-xs font-mono uppercase tracking-wider text-neutral-500 mb-1">
              Interview Evaluation Scorecard
            </p>
            <h1 className="text-2xl font-semibold tracking-tight text-neutral-900 dark:text-neutral-50">
              {session.role_title}
            </h1>
            <p className="text-xs text-neutral-500 mt-1">
              {formatDate(session.updated_at)} · {session.experience_level} · <span className="font-medium text-neutral-800 dark:text-neutral-200">🎯 {session.interview_type} Mode</span>
            </p>
          </div>

          <div className="flex items-center gap-2">
            <button
              onClick={() => window.print()}
              className="px-3 py-1.5 rounded border border-neutral-200 dark:border-neutral-800 text-xs text-neutral-700 dark:text-neutral-300 hover:bg-neutral-100 dark:hover:bg-neutral-900 transition-colors cursor-pointer"
            >
              Print / Save PDF
            </button>
            <Link href="/setup">
              <Button size="sm">
                New Interview
              </Button>
            </Link>
          </div>
        </div>

        {/* Scorecard Hero */}
        <div className="p-6 rounded-xl border border-neutral-200 dark:border-neutral-800 bg-neutral-50/50 dark:bg-neutral-950/50 space-y-6">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
            <div>
              <span className="text-xs font-mono uppercase text-neutral-500 block mb-1">Overall Assessment</span>
              <div className="flex items-baseline gap-3">
                <span className="text-4xl sm:text-5xl font-semibold font-mono tracking-tight text-neutral-900 dark:text-neutral-50">
                  {overall}
                </span>
                <span className="text-xs text-neutral-500 font-mono">/ 100</span>
                <Badge variant={overall >= 75 ? "success" : "secondary"} size="sm" className="ml-2">
                  {session.readiness_level || (overall >= 80 ? "Interview Ready" : "Needs Preparation")}
                </Badge>
              </div>
            </div>
          </div>

          {session.summary && (
            <p className="text-xs sm:text-sm text-neutral-700 dark:text-neutral-300 leading-relaxed font-sans border-t border-neutral-200 dark:border-neutral-800 pt-4">
              {session.summary}
            </p>
          )}

          {/* 4 Rubric Metrics */}
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 pt-2 border-t border-neutral-200 dark:border-neutral-800">
            <MetricCard label="Technical" score={avgTech} subtitle="Domain accuracy" />
            <MetricCard label="Relevance" score={avgRel} subtitle="Direct focus" />
            <MetricCard label="Clarity" score={avgClar} subtitle="Structure" />
            <MetricCard label="Depth" score={avgComp} subtitle="Edge cases" />
          </div>
        </div>

        {/* Strengths & Weaknesses */}
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
          <div className="space-y-3">
            <h3 className="text-xs font-mono uppercase tracking-wider text-neutral-500">
              Key Strengths
            </h3>
            <ul className="space-y-2 text-xs text-neutral-700 dark:text-neutral-300">
              {(session.strengths?.length ? session.strengths : ["Structured responses", "Sound architectural fundamentals"]).map((s, i) => (
                <li key={i} className="flex items-start gap-2">
                  <span className="text-emerald-600 dark:text-emerald-400 font-mono">✓</span>
                  <span>{s}</span>
                </li>
              ))}
            </ul>
          </div>

          <div className="space-y-3">
            <h3 className="text-xs font-mono uppercase tracking-wider text-neutral-500">
              Areas to Strengthen
            </h3>
            <ul className="space-y-2 text-xs text-neutral-700 dark:text-neutral-300">
              {(session.weaknesses?.length ? session.weaknesses : ["Detail failure modes more proactively", "Explicitly weigh operational trade-offs"]).map((w, i) => (
                <li key={i} className="flex items-start gap-2">
                  <span className="text-amber-600 dark:text-amber-400 font-mono">•</span>
                  <span>{w}</span>
                </li>
              ))}
            </ul>
          </div>
        </div>

        {/* Practice Topics */}
        {session.recommended_topics && session.recommended_topics.length > 0 && (
          <div className="space-y-2 pt-2">
            <h3 className="text-xs font-mono uppercase tracking-wider text-neutral-500">
              Recommended Topics to Study
            </h3>
            <div className="flex flex-wrap gap-1.5">
              {session.recommended_topics.map((t, idx) => (
                <span
                  key={idx}
                  className="text-xs px-2.5 py-1 rounded border border-neutral-200 dark:border-neutral-800 bg-neutral-50 dark:bg-neutral-900 text-neutral-700 dark:text-neutral-300"
                >
                  {t}
                </span>
              ))}
            </div>
          </div>
        )}

        {/* Detailed Transcript */}
        <div className="space-y-4 pt-6 border-t border-neutral-100 dark:border-neutral-900">
          <div className="flex items-center justify-between">
            <h2 className="text-sm font-semibold text-neutral-900 dark:text-neutral-100">
              Transcript & Model Answers
            </h2>
            <span className="text-xs font-mono text-neutral-500">{answeredTurns.length} turns</span>
          </div>

          <div className="space-y-3">
            {answeredTurns.map((turn, idx) => {
              const isExpanded = expandedTurns[turn.id] ?? true;
              return (
                <div
                  key={turn.id}
                  className="rounded-lg border border-neutral-200 dark:border-neutral-800 bg-white dark:bg-neutral-950 overflow-hidden"
                >
                  <button
                    type="button"
                    onClick={() => toggleTurn(turn.id)}
                    className="w-full p-4 text-left flex items-center justify-between gap-4 cursor-pointer hover:bg-neutral-50 dark:hover:bg-neutral-900/40"
                  >
                    <div className="space-y-0.5">
                      <div className="flex items-center gap-2 text-xs font-mono text-neutral-400">
                        <span>Q{idx + 1} · {turn.question_category}</span>
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
                      <span className="text-xs font-mono font-semibold">
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
                    <div className="p-4 pt-0 border-t border-neutral-100 dark:border-neutral-900 space-y-4 mt-3">
                      {turn.resume_context_used && (
                        <div className="text-[11px] font-mono px-2 py-0.5 rounded bg-emerald-50 dark:bg-emerald-950/40 text-emerald-700 dark:text-emerald-300 border border-emerald-200 dark:border-emerald-800 w-fit">
                          Grounded in: {turn.resume_context_used}
                        </div>
                      )}

                      <div className="space-y-1">
                        <span className="text-[11px] font-mono text-neutral-400 uppercase">Question</span>
                        <p className="text-xs text-neutral-900 dark:text-neutral-100 font-medium">
                          {turn.question_text}
                        </p>
                      </div>

                      <div className="space-y-1">
                        <span className="text-[11px] font-mono text-neutral-400 uppercase">Your Answer</span>
                        <p className="text-xs text-neutral-700 dark:text-neutral-300 bg-neutral-50 dark:bg-neutral-900 p-3 rounded border border-neutral-200 dark:border-neutral-800 whitespace-pre-wrap leading-relaxed font-sans">
                          {turn.user_answer}
                        </p>
                      </div>

                      <div className="grid grid-cols-2 sm:grid-cols-4 gap-2">
                        <MetricCard label="Technical" score={turn.technical_score || 0} />
                        <MetricCard label="Relevance" score={turn.relevance_score || 0} />
                        <MetricCard label="Clarity" score={turn.clarity_score || 0} />
                        <MetricCard label="Depth" score={turn.completeness_score || 0} />
                      </div>

                      {turn.feedback && (
                        <div className="space-y-1">
                          <span className="text-[11px] font-mono text-neutral-400 uppercase">Evaluation</span>
                          <p className="text-xs text-neutral-700 dark:text-neutral-300 leading-relaxed">
                            {turn.feedback}
                          </p>
                        </div>
                      )}

                      {turn.sample_ideal_answer && (
                        <div className="space-y-1">
                          <span className="text-[11px] font-mono text-neutral-400 uppercase">Reference Model Answer</span>
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

        {/* Footer Link */}
        <div className="pt-4 border-t border-neutral-100 dark:border-neutral-900 flex justify-between items-center text-xs text-neutral-500">
          <Link href="/history" className="hover:text-black dark:hover:text-white transition-colors">
            ← View All History
          </Link>
          <Link href="/setup">
            <Button size="sm">Start Another Session</Button>
          </Link>
        </div>
      </div>
    </div>
  );
}
