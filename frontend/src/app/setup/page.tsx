"use client";

import React, { useState } from "react";
import { useRouter } from "next/navigation";
import {
  AlertCircle,
  X,
  Upload,
  Sparkles,
  Briefcase,
  Layers,
  FolderGit2,
  CheckCircle2,
  ChevronRight,
  FileText
} from "lucide-react";
import { api } from "@/lib/api";
import {
  CreateInterviewPayload,
  Difficulty,
  ExperienceLevel,
  InterviewMode,
  ResumeAnalysis,
} from "@/types/interview";
import { Button } from "@/components/ui/Button";

const ROLE_PRESETS = [
  "Senior Frontend Engineer",
  "Full-Stack Software Engineer",
  "Backend Distributed Systems",
  "Cloud & DevOps Platform",
  "Engineering Manager / Tech Lead",
];

const INTERVIEW_MODES: {
  id: InterviewMode;
  label: string;
  badge: string;
  desc: string;
}[] = [
  {
    id: "Technical",
    label: "Technical",
    badge: "Code & Architecture",
    desc: "System design, core invariants, concurrency, algorithms & debugging.",
  },
  {
    id: "Behavioral",
    label: "Behavioral",
    badge: "STAR Method",
    desc: "Teamwork, handling disagreement, ownership, and leadership situations.",
  },
  {
    id: "HR",
    label: "HR Screening",
    badge: "Culture & Fit",
    desc: "Career trajectory, motivations, salary discussion handling & work ethics.",
  },
  {
    id: "Mixed",
    label: "Mixed",
    badge: "Comprehensive",
    desc: "A balanced simulation across technical depth, culture fit, and behavior.",
  },
  {
    id: "Job-specific",
    label: "Job-Specific",
    badge: "Role Tailored",
    desc: "Grounded strictly in the target job description, tools & industry domain.",
  },
];

const EXPERIENCE_LEVELS: { id: ExperienceLevel; label: string; desc: string }[] = [
  { id: "Junior", label: "Junior", desc: "0-2 years · Core fundamentals & syntax" },
  { id: "Mid", label: "Mid-Level", desc: "3-5 years · Systems & practical trade-offs" },
  { id: "Senior", label: "Senior", desc: "5-8 years · Architecture & production edge cases" },
  { id: "Lead", label: "Lead", desc: "8+ years · Cross-team technical vision & impact" },
  { id: "Principal", label: "Principal", desc: "High scale, organizational strategy & trade-offs" },
];

const DIFFICULTIES: { id: Difficulty; label: string }[] = [
  { id: "Easy", label: "Foundational" },
  { id: "Medium", label: "Standard Bar" },
  { id: "Hard", label: "High Bar" },
];

export default function SetupPage() {
  const router = useRouter();

  // Mode Selection
  const [interviewMode, setInterviewMode] = useState<InterviewMode>("Technical");
  const [roleTitle, setRoleTitle] = useState("Senior Frontend Engineer");
  const [experienceLevel, setExperienceLevel] = useState<ExperienceLevel>("Senior");
  const [difficulty, setDifficulty] = useState<Difficulty>("Medium");
  const [numQuestions, setNumQuestions] = useState<number>(5);

  // Job Description
  const [jobDescription, setJobDescription] = useState("");

  // Resume State
  const [resumeMode, setResumeMode] = useState<"none" | "upload" | "paste">("none");
  const [resumeText, setResumeText] = useState("");
  const [resumeFilename, setResumeFilename] = useState("");
  const [resumeAnalysis, setResumeAnalysis] = useState<ResumeAnalysis | null>(null);
  const [isUploadingResume, setIsUploadingResume] = useState(false);
  const [isAnalyzingText, setIsAnalyzingText] = useState(false);

  const [isLoading, setIsLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setIsUploadingResume(true);
    setErrorMessage(null);
    try {
      const res = await api.uploadResume(file);
      setResumeText(res.extracted_text);
      setResumeFilename(res.filename);
      setResumeMode("upload");
      if (res.analysis) {
        setResumeAnalysis(res.analysis);
        if (res.analysis.inferred_role && !roleTitle) {
          setRoleTitle(res.analysis.inferred_role);
        }
      }
    } catch (err: any) {
      setErrorMessage(err.message || "Failed to process resume file.");
    } finally {
      setIsUploadingResume(false);
    }
  };

  const handleAnalyzePastedText = async () => {
    if (!resumeText.trim()) return;
    setIsAnalyzingText(true);
    setErrorMessage(null);
    try {
      const analysis = await api.analyzeResumeText(resumeText.trim());
      setResumeAnalysis(analysis);
      if (analysis.inferred_role) {
        setRoleTitle(analysis.inferred_role);
      }
    } catch (err: any) {
      setErrorMessage(err.message || "Failed to analyze resume text.");
    } finally {
      setIsAnalyzingText(false);
    }
  };

  const applyInferredRole = () => {
    if (!resumeAnalysis?.inferred_role) return;
    const inferred = resumeAnalysis.inferred_role;
    setRoleTitle(inferred);

    const lower = inferred.toLowerCase();
    if (lower.includes("lead") || lower.includes("staff")) {
      setExperienceLevel("Lead");
    } else if (lower.includes("principal") || lower.includes("director") || lower.includes("vp")) {
      setExperienceLevel("Principal");
    } else if (lower.includes("senior") || lower.includes("sr")) {
      setExperienceLevel("Senior");
    } else if (lower.includes("junior") || lower.includes("jr") || lower.includes("intern")) {
      setExperienceLevel("Junior");
    } else {
      setExperienceLevel("Mid");
    }
  };

  const handleCreateInterview = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!roleTitle.trim()) {
      setErrorMessage("Please enter a target job role.");
      return;
    }

    setIsLoading(true);
    setErrorMessage(null);

    const payload: CreateInterviewPayload = {
      role_title: roleTitle.trim(),
      experience_level: experienceLevel,
      interview_type: interviewMode,
      difficulty: difficulty,
      num_questions: numQuestions,
      resume_text: resumeMode !== "none" && resumeText.trim() ? resumeText.trim() : undefined,
      job_description: jobDescription.trim() ? jobDescription.trim() : undefined,
    };

    try {
      const session = await api.createInterview(payload);
      router.push(`/interview/${session.id}`);
    } catch (err: any) {
      setErrorMessage(err.message || "Failed to start interview. Check backend connection.");
      setIsLoading(false);
    }
  };

  return (
    <div className="py-12 bg-white dark:bg-black min-h-screen text-neutral-900 dark:text-neutral-100">
      <div className="mx-auto max-w-2xl px-6">
        <div className="mb-8">
          <p className="text-xs font-mono uppercase tracking-wider text-neutral-500 mb-1">
            Session Calibration
          </p>
          <h1 className="text-2xl font-semibold tracking-tight">
            Configure Interview
          </h1>
          <p className="text-xs text-neutral-500 mt-1">
            Upload your resume or configure manually to generate targeted questions.
          </p>
        </div>

        {errorMessage && (
          <div className="mb-6 flex items-start gap-3 p-3.5 rounded-lg border border-red-200 dark:border-red-900 bg-red-50 dark:bg-red-950/40 text-red-800 dark:text-red-300 text-xs">
            <AlertCircle className="h-4 w-4 shrink-0 mt-0.5" />
            <div className="flex-1">{errorMessage}</div>
            <button onClick={() => setErrorMessage(null)} className="cursor-pointer">
              <X className="h-4 w-4" />
            </button>
          </div>
        )}

        <form onSubmit={handleCreateInterview} className="space-y-7">
          {/* Section: Resume-Based Interview Upload & Analysis */}
          <div className="p-5 rounded-xl border border-neutral-200 dark:border-neutral-800 bg-neutral-50/50 dark:bg-neutral-950/50 space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <span className="text-xs font-semibold uppercase tracking-wider text-neutral-900 dark:text-neutral-100 flex items-center gap-1.5">
                  <FileText className="h-3.5 w-3.5 text-neutral-500" />
                  <span>Resume-Based Grounding</span>
                </span>
                <p className="text-[11px] text-neutral-500 mt-0.5">
                  AI extracts your skills, projects & work history to ask authentic interview questions.
                </p>
              </div>

              <div className="flex gap-1 bg-neutral-200/60 dark:bg-neutral-900 p-1 rounded-md text-xs">
                <button
                  type="button"
                  onClick={() => setResumeMode(resumeMode === "upload" ? "none" : "upload")}
                  className={`px-2.5 py-1 rounded cursor-pointer transition-colors ${
                    resumeMode === "upload" ? "bg-white dark:bg-neutral-800 font-medium text-neutral-900 dark:text-neutral-100 shadow-sm" : "text-neutral-500 hover:text-neutral-700"
                  }`}
                >
                  Upload File
                </button>
                <button
                  type="button"
                  onClick={() => setResumeMode(resumeMode === "paste" ? "none" : "paste")}
                  className={`px-2.5 py-1 rounded cursor-pointer transition-colors ${
                    resumeMode === "paste" ? "bg-white dark:bg-neutral-800 font-medium text-neutral-900 dark:text-neutral-100 shadow-sm" : "text-neutral-500 hover:text-neutral-700"
                  }`}
                >
                  Paste Text
                </button>
              </div>
            </div>

            {resumeMode === "upload" && (
              <div className="border border-dashed border-neutral-300 dark:border-neutral-800 rounded-lg p-5 text-center bg-white dark:bg-neutral-900/40">
                <input
                  type="file"
                  id="resume-file"
                  accept=".pdf,.txt,.md"
                  onChange={handleFileUpload}
                  className="hidden"
                  disabled={isUploadingResume}
                />
                <label
                  htmlFor="resume-file"
                  className="cursor-pointer flex flex-col items-center justify-center space-y-2"
                >
                  <Upload className="h-5 w-5 text-neutral-400" />
                  <span className="text-xs text-neutral-800 dark:text-neutral-200 font-medium">
                    {isUploadingResume
                      ? "AI reading resume skills & projects..."
                      : resumeFilename
                      ? `Attached: ${resumeFilename}`
                      : "Click to upload Resume (PDF / TXT)"}
                  </span>
                  <span className="text-[10px] text-neutral-400">PDF or TXT up to 10MB</span>
                </label>
              </div>
            )}

            {resumeMode === "paste" && (
              <div className="space-y-2">
                <textarea
                  rows={4}
                  value={resumeText}
                  onChange={(e) => setResumeText(e.target.value)}
                  placeholder="Paste your resume, skills, and past projects summary here..."
                  className="w-full p-3 text-xs rounded-lg border border-neutral-300 dark:border-neutral-800 bg-white dark:bg-neutral-950 text-neutral-900 dark:text-neutral-100 font-mono"
                />
                <div className="flex justify-end">
                  <button
                    type="button"
                    onClick={handleAnalyzePastedText}
                    disabled={isAnalyzingText || !resumeText.trim()}
                    className="text-xs px-3 py-1.5 rounded bg-neutral-900 text-white dark:bg-neutral-100 dark:text-neutral-900 cursor-pointer disabled:opacity-50 flex items-center gap-1.5 font-medium"
                  >
                    {isAnalyzingText ? "Analyzing..." : "✨ Extract Skills & Projects"}
                  </button>
                </div>
              </div>
            )}

            {/* Extracted Resume Intelligence Preview */}
            {resumeAnalysis && (
              <div className="mt-3 p-4 rounded-lg border border-neutral-200 dark:border-neutral-800 bg-white dark:bg-neutral-900 space-y-3.5">
                <div className="flex items-center justify-between border-b border-neutral-100 dark:border-neutral-800 pb-2.5">
                  <div className="flex items-center gap-2">
                    <CheckCircle2 className="h-4 w-4 text-emerald-600 dark:text-emerald-400" />
                    <span className="text-xs font-semibold text-neutral-900 dark:text-neutral-100">
                      Resume Analyzed: {resumeAnalysis.candidate_name || "Profile Grounded"}
                    </span>
                  </div>
                  {resumeAnalysis.inferred_role && (
                    <button
                      type="button"
                      onClick={applyInferredRole}
                      className="text-[11px] font-mono px-2 py-0.5 rounded border border-neutral-300 dark:border-neutral-700 bg-neutral-50 dark:bg-neutral-800 text-neutral-700 dark:text-neutral-300 hover:border-black dark:hover:border-white transition-colors cursor-pointer"
                    >
                      Use Role: {resumeAnalysis.inferred_role}
                    </button>
                  )}
                </div>

                {/* Skills tags */}
                {resumeAnalysis.skills?.length > 0 && (
                  <div className="space-y-1.5">
                    <span className="text-[11px] font-mono uppercase text-neutral-400 flex items-center gap-1">
                      <Layers className="h-3 w-3" /> Extracted Skills ({resumeAnalysis.skills.length})
                    </span>
                    <div className="flex flex-wrap gap-1">
                      {resumeAnalysis.skills.map((s, i) => (
                        <span
                          key={i}
                          className="text-[11px] font-mono px-2 py-0.5 rounded bg-neutral-100 dark:bg-neutral-800 text-neutral-700 dark:text-neutral-300"
                        >
                          {s}
                        </span>
                      ))}
                    </div>
                  </div>
                )}

                {/* Projects */}
                {resumeAnalysis.projects?.length > 0 && (
                  <div className="space-y-1.5 pt-1">
                    <span className="text-[11px] font-mono uppercase text-neutral-400 flex items-center gap-1">
                      <FolderGit2 className="h-3 w-3" /> Key Projects ({resumeAnalysis.projects.length})
                    </span>
                    <div className="space-y-1.5">
                      {resumeAnalysis.projects.map((p, idx) => (
                        <div
                          key={idx}
                          className="p-2.5 rounded border border-neutral-100 dark:border-neutral-800/80 bg-neutral-50/50 dark:bg-neutral-950/50 text-xs space-y-1"
                        >
                          <div className="flex items-center justify-between">
                            <span className="font-semibold text-neutral-900 dark:text-neutral-100">
                              {p.name}
                            </span>
                            <div className="flex gap-1">
                              {p.technologies?.slice(0, 3).map((t, ti) => (
                                <span
                                  key={ti}
                                  className="text-[10px] font-mono px-1.5 py-0.2 rounded bg-neutral-200/50 dark:bg-neutral-800 text-neutral-600 dark:text-neutral-400"
                                >
                                  {t}
                                </span>
                              ))}
                            </div>
                          </div>
                          {p.description && (
                            <p className="text-[11px] text-neutral-500 leading-snug line-clamp-2">
                              {p.description}
                            </p>
                          )}
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Work Experience */}
                {resumeAnalysis.experiences?.length > 0 && (
                  <div className="space-y-1.5 pt-1">
                    <span className="text-[11px] font-mono uppercase text-neutral-400 flex items-center gap-1">
                      <Briefcase className="h-3 w-3" /> Experience ({resumeAnalysis.experiences.length})
                    </span>
                    <div className="space-y-1">
                      {resumeAnalysis.experiences.map((exp, ei) => (
                        <div key={ei} className="text-xs text-neutral-600 dark:text-neutral-400 flex items-baseline justify-between">
                          <span className="font-medium text-neutral-800 dark:text-neutral-200">
                            {exp.role} @ {exp.company}
                          </span>
                          {exp.duration && (
                            <span className="text-[10px] font-mono text-neutral-400">{exp.duration}</span>
                          )}
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>

          {/* Section 1: 🎯 Interview Mode */}
          <div className="space-y-2.5">
            <div className="flex items-center justify-between">
              <label className="text-xs font-semibold uppercase tracking-wider text-neutral-700 dark:text-neutral-300 flex items-center gap-1.5">
                <span>🎯</span>
                <span>Interview Mode</span>
              </label>
              <span className="text-[11px] font-mono text-neutral-400">
                Mode: {interviewMode}
              </span>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
              {INTERVIEW_MODES.map((mode) => {
                const isSelected = interviewMode === mode.id;
                return (
                  <button
                    key={mode.id}
                    type="button"
                    onClick={() => setInterviewMode(mode.id)}
                    className={`p-3.5 rounded-lg border text-left cursor-pointer transition-colors ${
                      isSelected
                        ? "border-black dark:border-white bg-neutral-50 dark:bg-neutral-900 text-neutral-900 dark:text-neutral-100"
                        : "border-neutral-200 dark:border-neutral-800 hover:border-neutral-300 text-neutral-600 dark:text-neutral-400"
                    }`}
                  >
                    <div className="flex items-center justify-between">
                      <span className="text-xs font-semibold">{mode.label}</span>
                      <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-neutral-200/60 dark:bg-neutral-800 text-neutral-600 dark:text-neutral-400">
                        {mode.badge}
                      </span>
                    </div>
                    <p className="text-[11px] text-neutral-500 mt-1 leading-snug">
                      {mode.desc}
                    </p>
                  </button>
                );
              })}
            </div>
          </div>

          {/* Section 2: Target Position */}
          <div className="space-y-2">
            <label className="text-xs font-medium text-neutral-700 dark:text-neutral-300">
              Target Position / Title
            </label>
            <input
              type="text"
              value={roleTitle}
              onChange={(e) => setRoleTitle(e.target.value)}
              placeholder="e.g. Senior Frontend Engineer"
              required
              className="w-full px-3.5 py-2 text-sm rounded-lg border border-neutral-300 dark:border-neutral-800 bg-white dark:bg-neutral-950 text-neutral-900 dark:text-neutral-100 focus:outline-none focus:border-black dark:focus:border-white transition-colors"
            />
            <div className="flex flex-wrap gap-1.5 pt-1">
              {ROLE_PRESETS.map((preset) => (
                <button
                  key={preset}
                  type="button"
                  onClick={() => setRoleTitle(preset)}
                  className={`text-xs px-2.5 py-1 rounded-md border cursor-pointer transition-colors ${
                    roleTitle === preset
                      ? "bg-neutral-900 text-white border-neutral-900 dark:bg-neutral-100 dark:text-neutral-900"
                      : "bg-neutral-50 dark:bg-neutral-900 text-neutral-600 dark:text-neutral-400 border-neutral-200 dark:border-neutral-800 hover:border-neutral-400"
                  }`}
                >
                  {preset}
                </button>
              ))}
            </div>
          </div>

          {/* Job-specific Description Field */}
          {(interviewMode === "Job-specific" || jobDescription) && (
            <div className="p-4 rounded-lg border border-neutral-200 dark:border-neutral-800 bg-neutral-50/60 dark:bg-neutral-950/60 space-y-2">
              <div className="flex items-center justify-between">
                <label className="text-xs font-medium text-neutral-700 dark:text-neutral-300">
                  Target Job Description & Requirements
                </label>
                <span className="text-[10px] text-neutral-400 uppercase font-mono">
                  {interviewMode === "Job-specific" ? "Recommended for this mode" : "Optional"}
                </span>
              </div>
              <textarea
                rows={3}
                value={jobDescription}
                onChange={(e) => setJobDescription(e.target.value)}
                placeholder="Paste key responsibilities, required tech stack (e.g., Next.js, Kafka, Kubernetes), and deliverables..."
                className="w-full p-2.5 text-xs rounded-md border border-neutral-300 dark:border-neutral-800 bg-white dark:bg-neutral-900 text-neutral-900 dark:text-neutral-100 font-sans"
              />
            </div>
          )}

          {/* Section 3: Seniority Level */}
          <div className="space-y-2">
            <label className="text-xs font-medium text-neutral-700 dark:text-neutral-300">
              Seniority Level
            </label>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
              {EXPERIENCE_LEVELS.map((lvl) => {
                const isSelected = experienceLevel === lvl.id;
                return (
                  <button
                    key={lvl.id}
                    type="button"
                    onClick={() => setExperienceLevel(lvl.id)}
                    className={`p-3 rounded-lg border text-left cursor-pointer transition-colors ${
                      isSelected
                        ? "border-black dark:border-white bg-neutral-50 dark:bg-neutral-900 text-neutral-900 dark:text-neutral-100"
                        : "border-neutral-200 dark:border-neutral-800 hover:border-neutral-300 text-neutral-600 dark:text-neutral-400"
                    }`}
                  >
                    <div className="text-xs font-medium">{lvl.label}</div>
                    <div className="text-[11px] text-neutral-500 mt-0.5">{lvl.desc}</div>
                  </button>
                );
              })}
            </div>
          </div>

          {/* Section 4: Rigor & Count */}
          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <label className="text-xs font-medium text-neutral-700 dark:text-neutral-300">
                Difficulty
              </label>
              <div className="grid grid-cols-3 gap-1.5">
                {DIFFICULTIES.map((d) => (
                  <button
                    key={d.id}
                    type="button"
                    onClick={() => setDifficulty(d.id)}
                    className={`py-2 text-xs rounded-md border text-center cursor-pointer transition-colors ${
                      difficulty === d.id
                        ? "bg-neutral-900 text-white border-neutral-900 dark:bg-neutral-100 dark:text-neutral-900"
                        : "border-neutral-200 dark:border-neutral-800 text-neutral-600 dark:text-neutral-400 hover:border-neutral-300"
                    }`}
                  >
                    {d.label}
                  </button>
                ))}
              </div>
            </div>

            <div className="space-y-2">
              <label className="text-xs font-medium text-neutral-700 dark:text-neutral-300">
                Number of Questions
              </label>
              <div className="grid grid-cols-4 gap-1.5">
                {[3, 5, 7, 10].map((num) => (
                  <button
                    key={num}
                    type="button"
                    onClick={() => setNumQuestions(num)}
                    className={`py-2 text-xs rounded-md border text-center cursor-pointer transition-colors ${
                      numQuestions === num
                        ? "bg-neutral-900 text-white border-neutral-900 dark:bg-neutral-100 dark:text-neutral-900"
                        : "border-neutral-200 dark:border-neutral-800 text-neutral-600 dark:text-neutral-400 hover:border-neutral-300"
                    }`}
                  >
                    {num}
                  </button>
                ))}
              </div>
            </div>
          </div>

          {/* Action */}
          <div className="pt-4">
            <Button type="submit" size="lg" className="w-full" isLoading={isLoading}>
              Start {interviewMode} Interview {resumeAnalysis ? "· Grounded in Resume" : ""}
            </Button>
          </div>
        </form>
      </div>
    </div>
  );
}
