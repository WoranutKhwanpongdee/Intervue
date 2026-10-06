"use client";

import React, { useState } from "react";
import { useRouter } from "next/navigation";
import { AlertCircle, X, Upload, Check } from "lucide-react";
import { api } from "@/lib/api";
import {
  CreateInterviewPayload,
  Difficulty,
  ExperienceLevel,
  InterviewType,
} from "@/types/interview";
import { Button } from "@/components/ui/Button";

const ROLE_PRESETS = [
  "Senior Frontend Engineer",
  "Full-Stack Software Engineer",
  "Backend Distributed Systems",
  "Cloud & DevOps Platform",
  "Engineering Manager / Tech Lead",
];

const EXPERIENCE_LEVELS: { id: ExperienceLevel; label: string; desc: string }[] = [
  { id: "Junior", label: "Junior", desc: "0-2 years · Fundamentals & syntax" },
  { id: "Mid", label: "Mid-Level", desc: "3-5 years · Systems & trade-offs" },
  { id: "Senior", label: "Senior", desc: "5-8 years · Architecture & edge cases" },
  { id: "Lead", label: "Lead", desc: "8+ years · Cross-team design & vision" },
  { id: "Principal", label: "Principal", desc: "High scale & organizational strategy" },
];

const INTERVIEW_TYPES: { id: InterviewType; label: string; desc: string }[] = [
  { id: "Technical", label: "Technical Deep-Dive", desc: "Internals, concurrency, algorithms & debugging" },
  { id: "System Design", label: "System Design", desc: "Scalability, caching, databases & throughput" },
  { id: "Behavioral", label: "Behavioral (STAR)", desc: "Conflict resolution, stakeholder management" },
  { id: "Leadership", label: "Engineering Leadership", desc: "Technical debt, mentoring, roadmaps" },
  { id: "Mixed", label: "Comprehensive", desc: "Balanced blend of architecture & behavioral" },
];

const DIFFICULTIES: { id: Difficulty; label: string }[] = [
  { id: "Easy", label: "Foundational" },
  { id: "Medium", label: "Standard Bar" },
  { id: "Hard", label: "High Bar" },
];

export default function SetupPage() {
  const router = useRouter();

  const [roleTitle, setRoleTitle] = useState("Senior Frontend Engineer");
  const [experienceLevel, setExperienceLevel] = useState<ExperienceLevel>("Senior");
  const [interviewType, setInterviewType] = useState<InterviewType>("Technical");
  const [difficulty, setDifficulty] = useState<Difficulty>("Medium");
  const [numQuestions, setNumQuestions] = useState<number>(5);

  const [resumeMode, setResumeMode] = useState<"none" | "upload" | "paste">("none");
  const [resumeText, setResumeText] = useState("");
  const [resumeFilename, setResumeFilename] = useState("");
  const [isUploadingResume, setIsUploadingResume] = useState(false);

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
    } catch (err: any) {
      setErrorMessage(err.message || "Failed to process resume file.");
    } finally {
      setIsUploadingResume(false);
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
      interview_type: interviewType,
      difficulty: difficulty,
      num_questions: numQuestions,
      resume_text: resumeMode !== "none" && resumeText.trim() ? resumeText.trim() : undefined,
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
    <div className="py-12 bg-white dark:bg-black min-h-screen">
      <div className="mx-auto max-w-2xl px-6">
        <div className="mb-8">
          <p className="text-xs font-mono uppercase tracking-wider text-neutral-500 mb-1">
            Session Configuration
          </p>
          <h1 className="text-2xl font-semibold tracking-tight text-neutral-900 dark:text-neutral-100">
            Configure Interview
          </h1>
          <p className="text-xs text-neutral-500 mt-1">
            Set your target position, level, and depth.
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

        <form onSubmit={handleCreateInterview} className="space-y-6">
          {/* Role */}
          <div className="space-y-2">
            <label className="text-xs font-medium text-neutral-700 dark:text-neutral-300">
              Target Position
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

          {/* Level */}
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

          {/* Type */}
          <div className="space-y-2">
            <label className="text-xs font-medium text-neutral-700 dark:text-neutral-300">
              Interview Track
            </label>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
              {INTERVIEW_TYPES.map((type) => {
                const isSelected = interviewType === type.id;
                return (
                  <button
                    key={type.id}
                    type="button"
                    onClick={() => setInterviewType(type.id)}
                    className={`p-3 rounded-lg border text-left cursor-pointer transition-colors ${
                      isSelected
                        ? "border-black dark:border-white bg-neutral-50 dark:bg-neutral-900 text-neutral-900 dark:text-neutral-100"
                        : "border-neutral-200 dark:border-neutral-800 hover:border-neutral-300 text-neutral-600 dark:text-neutral-400"
                    }`}
                  >
                    <div className="text-xs font-medium">{type.label}</div>
                    <div className="text-[11px] text-neutral-500 mt-0.5">{type.desc}</div>
                  </button>
                );
              })}
            </div>
          </div>

          {/* Difficulty & Count */}
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

          {/* Resume Upload (Optional) */}
          <div className="pt-2 border-t border-neutral-100 dark:border-neutral-900 space-y-3">
            <div className="flex items-center justify-between">
              <div>
                <span className="text-xs font-medium text-neutral-700 dark:text-neutral-300">
                  Resume Context (Optional)
                </span>
                <p className="text-[11px] text-neutral-500">
                  Provide your resume to ground questions in your real tech stack.
                </p>
              </div>

              <div className="flex gap-1 bg-neutral-100 dark:bg-neutral-900 p-1 rounded-md text-xs">
                <button
                  type="button"
                  onClick={() => setResumeMode(resumeMode === "upload" ? "none" : "upload")}
                  className={`px-2 py-0.5 rounded cursor-pointer ${
                    resumeMode === "upload" ? "bg-white dark:bg-neutral-800 font-medium" : "text-neutral-500"
                  }`}
                >
                  Upload File
                </button>
                <button
                  type="button"
                  onClick={() => setResumeMode(resumeMode === "paste" ? "none" : "paste")}
                  className={`px-2 py-0.5 rounded cursor-pointer ${
                    resumeMode === "paste" ? "bg-white dark:bg-neutral-800 font-medium" : "text-neutral-500"
                  }`}
                >
                  Paste Text
                </button>
              </div>
            </div>

            {resumeMode === "upload" && (
              <div className="border border-neutral-200 dark:border-neutral-800 rounded-lg p-5 text-center">
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
                  className="cursor-pointer flex flex-col items-center justify-center space-y-1.5"
                >
                  <Upload className="h-4 w-4 text-neutral-400" />
                  <span className="text-xs text-neutral-700 dark:text-neutral-300 font-medium">
                    {isUploadingResume
                      ? "Extracting resume..."
                      : resumeFilename
                      ? `Attached: ${resumeFilename}`
                      : "Upload PDF or TXT"}
                  </span>
                  <span className="text-[10px] text-neutral-400">PDF, TXT up to 10MB</span>
                </label>
              </div>
            )}

            {resumeMode === "paste" && (
              <textarea
                rows={4}
                value={resumeText}
                onChange={(e) => setResumeText(e.target.value)}
                placeholder="Paste relevant resume experience here..."
                className="w-full p-3 text-xs rounded-lg border border-neutral-300 dark:border-neutral-800 bg-white dark:bg-neutral-950 text-neutral-900 dark:text-neutral-100 font-mono"
              />
            )}
          </div>

          {/* Action */}
          <div className="pt-4">
            <Button type="submit" size="lg" className="w-full" isLoading={isLoading}>
              Start Interview
            </Button>
          </div>
        </form>
      </div>
    </div>
  );
}
