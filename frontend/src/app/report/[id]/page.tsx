"use client";

import React, { useEffect, useState, use } from "react";
import Link from "next/link";
import {
  Printer,
  RotateCcw,
  ChevronDown,
  ChevronUp,
  ArrowRight,
  AlertTriangle,
  Lightbulb,
  Compass,
  Sparkles,
  FileText,
  ShieldAlert,
  BarChart3,
  Layers,
  CheckCircle2,
  HelpCircle,
  TrendingUp,
  AlertCircle,
  Search
} from "lucide-react";
import { api } from "@/lib/api";
import { InterviewSession, SkillAssessment } from "@/types/interview";
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
  const [skillFilter, setSkillFilter] = useState<"all" | "evaluated" | "insufficient">("all");

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
        <p className="text-xs font-mono text-neutral-500">Compiling evaluation report & skill map...</p>
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

  // Skill Map Analytics
  const skillMap = session.skill_map || [];
  const evaluatedSkills = skillMap.filter((s) => s.status !== "Insufficient Data" && s.score !== null);
  const insufficientSkills = skillMap.filter((s) => s.status === "Insufficient Data" || s.score === null);

  const filteredSkills = skillMap.filter((s) => {
    if (skillFilter === "evaluated") return s.status !== "Insufficient Data" && s.score !== null;
    if (skillFilter === "insufficient") return s.status === "Insufficient Data" || s.score === null;
    return true;
  });

  const topSkill = evaluatedSkills.length > 0
    ? [...evaluatedSkills].sort((a, b) => (b.score || 0) - (a.score || 0))[0]
    : null;

  const lowestSkill = evaluatedSkills.length > 0
    ? [...evaluatedSkills].sort((a, b) => (a.score || 0) - (b.score || 0))[0]
    : null;

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

        {/* 🏢 FULL LOOP HIRING COMMITTEE DEBRIEF */}
        {session.round_evaluations && session.round_evaluations.length > 0 && (
          <div className="space-y-4 pt-2">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
              <div>
                <h3 className="text-xs font-mono uppercase tracking-wider text-neutral-900 dark:text-neutral-100 flex items-center gap-1.5 font-semibold">
                  <Layers className="h-4 w-4 text-neutral-600 dark:text-neutral-400" />
                  <span>Full Loop Hiring Committee Debrief</span>
                </h3>
                <p className="text-[11px] text-neutral-500 mt-0.5">
                  Multi-stage panel feedback synthesized across HR Screening, Systems Architecture, STAR Behavioral, and Executive rounds.
                </p>
              </div>

              {session.hiring_committee_verdict && (
                <span className={`text-[11px] font-mono px-2.5 py-1 rounded border font-semibold shrink-0 ${
                  session.hiring_committee_verdict.includes("Strong") || session.hiring_committee_verdict === "Hire"
                    ? "bg-emerald-50 dark:bg-emerald-950/60 text-emerald-700 dark:text-emerald-300 border-emerald-300 dark:border-emerald-800"
                    : session.hiring_committee_verdict.includes("Lean")
                    ? "bg-amber-50 dark:bg-amber-950/60 text-amber-700 dark:text-amber-300 border-amber-300 dark:border-amber-800"
                    : "bg-red-50 dark:bg-red-950/60 text-red-700 dark:text-red-300 border-red-300 dark:border-red-800"
                }`}>
                  Panel Verdict: {session.hiring_committee_verdict}
                </span>
              )}
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
              {session.round_evaluations.map((round, idx) => {
                const isStrong = round.verdict.includes("Strong");
                const isHire = round.verdict.includes("Hire");
                return (
                  <div
                    key={idx}
                    className="p-4 rounded-xl border border-neutral-200 dark:border-neutral-800 bg-white dark:bg-neutral-950 space-y-2 text-xs"
                  >
                    <div className="flex items-start justify-between gap-2">
                      <div>
                        <span className="font-semibold text-neutral-900 dark:text-neutral-100 block text-xs">
                          {round.round_name}
                        </span>
                        <span className="text-[10px] font-mono text-neutral-400">
                          Interviewer: {round.interviewer_persona}
                        </span>
                      </div>
                      <div className="text-right shrink-0">
                        <span className={`text-[10px] font-mono px-2 py-0.5 rounded border block ${
                          isStrong
                            ? "bg-emerald-50 dark:bg-emerald-950/60 text-emerald-700 dark:text-emerald-300 border-emerald-200 dark:border-emerald-800"
                            : isHire
                            ? "bg-sky-50 dark:bg-sky-950/60 text-sky-700 dark:text-sky-300 border-sky-200 dark:border-sky-800"
                            : "bg-amber-50 dark:bg-amber-950/60 text-amber-700 dark:text-amber-300 border-amber-200 dark:border-amber-800"
                        }`}>
                          {round.verdict}
                        </span>
                        <span className="text-[10px] font-mono text-neutral-500 mt-0.5 block">
                          {Math.round(round.score)}%
                        </span>
                      </div>
                    </div>

                    <p className="text-[11px] text-neutral-600 dark:text-neutral-400 font-sans leading-relaxed pt-1 border-t border-neutral-100 dark:border-neutral-900">
                      {round.key_takeaway}
                    </p>
                  </div>
                );
              })}
            </div>
          </div>
        )}

        {/* 🗺️ INTERVIEW SKILL MAP SECTION */}
        {skillMap.length > 0 && (
          <div className="space-y-4 pt-2">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
              <div>
                <h3 className="text-xs font-mono uppercase tracking-wider text-neutral-900 dark:text-neutral-100 flex items-center gap-1.5 font-semibold">
                  <BarChart3 className="h-4 w-4 text-neutral-600 dark:text-neutral-400" />
                  <span>Interview Skill Map</span>
                </h3>
                <p className="text-[11px] text-neutral-500 mt-0.5">
                  Granular competency breakdown by topic, language, and architectural domain.
                </p>
              </div>

              {/* Filter Tabs */}
              <div className="flex gap-1 bg-neutral-100 dark:bg-neutral-900 p-1 rounded-md text-xs self-start sm:self-auto font-mono">
                <button
                  type="button"
                  onClick={() => setSkillFilter("all")}
                  className={`px-2 py-0.5 rounded cursor-pointer transition-colors ${
                    skillFilter === "all" ? "bg-white dark:bg-neutral-800 font-medium text-neutral-900 dark:text-neutral-100 shadow-sm" : "text-neutral-500 hover:text-neutral-700"
                  }`}
                >
                  All ({skillMap.length})
                </button>
                <button
                  type="button"
                  onClick={() => setSkillFilter("evaluated")}
                  className={`px-2 py-0.5 rounded cursor-pointer transition-colors ${
                    skillFilter === "evaluated" ? "bg-white dark:bg-neutral-800 font-medium text-neutral-900 dark:text-neutral-100 shadow-sm" : "text-neutral-500 hover:text-neutral-700"
                  }`}
                >
                  Evaluated ({evaluatedSkills.length})
                </button>
                <button
                  type="button"
                  onClick={() => setSkillFilter("insufficient")}
                  className={`px-2 py-0.5 rounded cursor-pointer transition-colors ${
                    skillFilter === "insufficient" ? "bg-white dark:bg-neutral-800 font-medium text-neutral-900 dark:text-neutral-100 shadow-sm" : "text-neutral-500 hover:text-neutral-700"
                  }`}
                >
                  Data Gap ({insufficientSkills.length})
                </button>
              </div>
            </div>

            {/* Top Strengths / Opportunities Banner */}
            {topSkill && lowestSkill && topSkill !== lowestSkill && (
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                <div className="p-3 rounded-lg border border-emerald-200/80 dark:border-emerald-900/60 bg-emerald-50/40 dark:bg-emerald-950/20 text-xs">
                  <div className="flex items-center justify-between text-emerald-800 dark:text-emerald-300 font-semibold mb-1">
                    <span className="flex items-center gap-1.5">
                      <TrendingUp className="h-3.5 w-3.5 text-emerald-600 dark:text-emerald-400" />
                      Highest Competency
                    </span>
                    <span className="font-mono">{Math.round(topSkill.score || 0)}%</span>
                  </div>
                  <p className="text-neutral-700 dark:text-neutral-300 font-medium">{topSkill.category}</p>
                </div>

                <div className="p-3 rounded-lg border border-amber-200/80 dark:border-amber-900/60 bg-amber-50/40 dark:bg-amber-950/20 text-xs">
                  <div className="flex items-center justify-between text-amber-800 dark:text-amber-300 font-semibold mb-1">
                    <span className="flex items-center gap-1.5">
                      <AlertCircle className="h-3.5 w-3.5 text-amber-600 dark:text-amber-400" />
                      Prime Growth Area
                    </span>
                    <span className="font-mono">{Math.round(lowestSkill.score || 0)}%</span>
                  </div>
                  <p className="text-neutral-700 dark:text-neutral-300 font-medium">{lowestSkill.category}</p>
                </div>
              </div>
            )}

            {/* Skill Cards Grid */}
            <div className="space-y-3">
              {filteredSkills.map((skill, idx) => {
                const isInsufficient = skill.status === "Insufficient Data" || skill.score === null;
                const score = skill.score || 0;

                let statusBadgeVariant = "bg-neutral-100 dark:bg-neutral-800 text-neutral-600 dark:text-neutral-400";
                let barColor = "bg-neutral-400 dark:bg-neutral-600";

                if (skill.status === "Mastered") {
                  statusBadgeVariant = "bg-emerald-50 dark:bg-emerald-950/60 text-emerald-700 dark:text-emerald-300 border-emerald-200 dark:border-emerald-800";
                  barColor = "bg-emerald-500 dark:bg-emerald-400";
                } else if (skill.status === "Competent") {
                  statusBadgeVariant = "bg-sky-50 dark:bg-sky-950/60 text-sky-700 dark:text-sky-300 border-sky-200 dark:border-sky-800";
                  barColor = "bg-sky-500 dark:bg-sky-400";
                } else if (skill.status === "Needs Practice") {
                  statusBadgeVariant = "bg-amber-50 dark:bg-amber-950/60 text-amber-700 dark:text-amber-300 border-amber-200 dark:border-amber-800";
                  barColor = "bg-amber-500 dark:bg-amber-400";
                } else if (isInsufficient) {
                  statusBadgeVariant = "bg-neutral-100 dark:bg-neutral-900 text-neutral-500 border-neutral-300 dark:border-neutral-800 border-dashed";
                }

                return (
                  <div
                    key={idx}
                    className={`p-4 rounded-xl border text-xs space-y-2.5 transition-colors ${
                      isInsufficient
                        ? "border-dashed border-neutral-300 dark:border-neutral-800 bg-neutral-50/40 dark:bg-neutral-950/30 opacity-90"
                        : "border-neutral-200 dark:border-neutral-800 bg-white dark:bg-neutral-950"
                    }`}
                  >
                    <div className="flex items-start justify-between gap-2">
                      <div className="space-y-0.5">
                        <span className="font-semibold text-neutral-900 dark:text-neutral-100 text-xs sm:text-sm">
                          {skill.category}
                        </span>
                        <div className="text-[11px] font-mono text-neutral-400">
                          Confidence: {skill.confidence || (isInsufficient ? "Insufficient" : "Medium")}
                        </div>
                      </div>

                      <div className="flex items-center gap-2 shrink-0">
                        {!isInsufficient && (
                          <span className="font-mono font-bold text-neutral-900 dark:text-neutral-100 text-xs sm:text-sm">
                            {Math.round(score)}%
                          </span>
                        )}
                        <span className={`text-[10px] font-mono px-2 py-0.5 rounded border ${statusBadgeVariant}`}>
                          {skill.status}
                        </span>
                      </div>
                    </div>

                    {/* Progress Bar (if evaluated) */}
                    {!isInsufficient ? (
                      <div className="w-full bg-neutral-100 dark:bg-neutral-900 h-1.5 rounded-full overflow-hidden">
                        <div
                          className={`h-full rounded-full transition-all duration-500 ${barColor}`}
                          style={{ width: `${Math.min(Math.max(score, 5), 100)}%` }}
                        />
                      </div>
                    ) : (
                      <div className="p-2 rounded bg-neutral-100/70 dark:bg-neutral-900/60 text-[11px] font-mono text-neutral-500 flex items-center gap-1.5">
                        <HelpCircle className="h-3.5 w-3.5 text-neutral-400 shrink-0" />
                        <span>Not enough data from this session to evaluate accurately.</span>
                      </div>
                    )}

                    {/* Specific Observations */}
                    {skill.observations && (
                      <p className="text-[11px] text-neutral-600 dark:text-neutral-400 leading-relaxed font-sans pt-0.5">
                        {skill.observations}
                      </p>
                    )}
                  </div>
                );
              })}
            </div>
          </div>
        )}

        {/* ⚠️ Hidden Weakness & Blindspot Detection Section */}
        {session.hidden_weaknesses && session.hidden_weaknesses.length > 0 && (
          <div className="space-y-4 pt-2">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-xs font-mono uppercase tracking-wider text-amber-600 dark:text-amber-400 flex items-center gap-1.5 font-semibold">
                  <ShieldAlert className="h-4 w-4 text-amber-500" />
                  <span>Hidden Weaknesses & Blindspots</span>
                </h3>
                <p className="text-[11px] text-neutral-500 mt-0.5">
                  Perceptive coach diagnosis of unstated communication and architectural habits.
                </p>
              </div>
              <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-amber-100 dark:bg-amber-950/60 text-amber-800 dark:text-amber-300 border border-amber-200 dark:border-amber-900">
                Coach Diagnosis
              </span>
            </div>

            <div className="space-y-3">
              {session.hidden_weaknesses.map((hw, idx) => (
                <div
                  key={idx}
                  className="p-4 rounded-xl border border-amber-200/80 dark:border-amber-900/60 bg-amber-50/40 dark:bg-amber-950/20 space-y-2.5"
                >
                  <div className="flex items-center justify-between">
                    <span className="text-[10px] font-mono uppercase tracking-wider px-2 py-0.5 rounded bg-white dark:bg-neutral-900 border border-amber-200 dark:border-amber-900 text-amber-800 dark:text-amber-300 font-medium">
                      {hw.tag}
                    </span>
                  </div>

                  <p className="text-xs sm:text-sm font-medium text-neutral-900 dark:text-neutral-100 leading-snug">
                    {hw.insight}
                  </p>

                  {hw.evidence && (
                    <div className="text-xs text-neutral-600 dark:text-neutral-400 bg-white/80 dark:bg-neutral-900/80 p-3 rounded-lg border border-neutral-200/60 dark:border-neutral-800/80 font-sans leading-relaxed">
                      <span className="text-[11px] font-mono uppercase text-neutral-400 block mb-0.5">Observed Pattern / Evidence:</span>
                      {hw.evidence}
                    </div>
                  )}

                  {hw.coaching_tip && (
                    <div className="flex items-start gap-2 text-xs text-amber-900 dark:text-amber-200 pt-1">
                      <Lightbulb className="h-3.5 w-3.5 text-amber-500 shrink-0 mt-0.5" />
                      <div>
                        <span className="font-semibold">Pro Coaching Tip: </span>
                        <span>{hw.coaching_tip}</span>
                      </div>
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}

        {/* 🔍 Interview Bluff Detector · Depth & Authenticity Audit */}
        {session.depth_audit && session.depth_audit.length > 0 && (
          <div className="space-y-4 pt-2">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-xs font-mono uppercase tracking-wider text-indigo-600 dark:text-indigo-400 flex items-center gap-1.5 font-semibold">
                  <Search className="h-4 w-4 text-indigo-500" />
                  <span>Interview Bluff Detector · Depth & Authenticity Audit</span>
                </h3>
                <p className="text-[11px] text-neutral-500 mt-0.5">
                  Probing operational understanding behind claimed technologies & architectures—validating genuine depth without hostility.
                </p>
              </div>
              <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-indigo-50 dark:bg-indigo-950/60 text-indigo-700 dark:text-indigo-300 border border-indigo-200 dark:border-indigo-800">
                Authenticity Matrix
              </span>
            </div>

            <div className="space-y-3">
              {session.depth_audit.map((item, idx) => {
                const isVerified = item.verification_status === "Verified Depth";
                return (
                  <div
                    key={idx}
                    className={`p-4 rounded-xl border space-y-2.5 text-xs transition-colors ${
                      isVerified
                        ? "border-emerald-200/80 dark:border-emerald-900/60 bg-emerald-50/30 dark:bg-emerald-950/20"
                        : "border-amber-200/80 dark:border-amber-900/60 bg-amber-50/30 dark:bg-amber-950/20"
                    }`}
                  >
                    <div className="flex items-start justify-between gap-3">
                      <div className="space-y-0.5">
                        <span className="font-semibold text-neutral-900 dark:text-neutral-100 text-xs sm:text-sm">
                          {item.topic}
                        </span>
                        <p className="text-[11px] text-neutral-500 font-sans">
                          {item.candidate_claim}
                        </p>
                      </div>
                      <span
                        className={`text-[10px] font-mono px-2 py-0.5 rounded border shrink-0 ${
                          isVerified
                            ? "bg-emerald-100 dark:bg-emerald-950 text-emerald-800 dark:text-emerald-300 border-emerald-300 dark:border-emerald-800"
                            : "bg-amber-100 dark:bg-amber-950 text-amber-800 dark:text-amber-300 border-amber-300 dark:border-amber-800"
                        }`}
                      >
                        {isVerified ? "✓ Verified Depth" : "⚡ Probe Triggered"}
                      </span>
                    </div>

                    {item.probe_question && (
                      <div className="p-3 rounded-lg bg-white dark:bg-neutral-900 border border-neutral-200/80 dark:border-neutral-800 font-sans space-y-1">
                        <span className="text-[10px] font-mono uppercase text-neutral-400 block tracking-wider">
                          Targeted Depth Probe Asked:
                        </span>
                        <p className="text-xs text-neutral-800 dark:text-neutral-200 italic">
                          &ldquo;{item.probe_question}&rdquo;
                        </p>
                      </div>
                    )}

                    {item.coach_observation && (
                      <div className="text-[11px] font-sans leading-relaxed text-neutral-700 dark:text-neutral-300 pt-0.5 flex items-start gap-1.5">
                        <span className="font-mono text-neutral-400 shrink-0">💡</span>
                        <span>
                          <strong className="font-medium text-neutral-900 dark:text-neutral-100">Coach Assessment: </strong>
                          {item.coach_observation}
                        </span>
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          </div>
        )}

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

                      {turn.adaptive_context && (
                        <div className="text-[11px] font-mono px-2 py-0.5 rounded bg-amber-50 dark:bg-amber-950/40 text-amber-700 dark:text-amber-300 border border-amber-200 dark:border-amber-800 w-fit">
                          ⚡ {turn.adaptive_context}
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

                      {turn.latent_blindspot && (
                        <div className="p-3 rounded-lg bg-amber-50 dark:bg-amber-950/30 border border-amber-200 dark:border-amber-900 text-xs text-amber-900 dark:text-amber-200 font-sans">
                          <span className="font-semibold text-[11px] font-mono block uppercase text-amber-700 dark:text-amber-400 mb-0.5">
                            Coach Blindspot Note:
                          </span>
                          {turn.latent_blindspot}
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
