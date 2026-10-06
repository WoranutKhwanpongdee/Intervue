"use client";

import React, { useEffect, useState } from "react";
import Link from "next/link";
import { Trash2, ArrowRight } from "lucide-react";
import { api } from "@/lib/api";
import { InterviewSessionSummary } from "@/types/interview";
import { Button } from "@/components/ui/Button";
import { Badge } from "@/components/ui/Badge";
import { formatDate } from "@/lib/utils";

export default function HistoryPage() {
  const [sessions, setSessions] = useState<InterviewSessionSummary[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [deletingId, setDeletingId] = useState<string | null>(null);

  const fetchHistory = async () => {
    try {
      setIsLoading(true);
      const data = await api.listInterviews();
      setSessions(data);
    } catch (err: any) {
      setError(err.message || "Failed to load interview history.");
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchHistory();
  }, []);

  const handleDelete = async (id: string, e: React.MouseEvent) => {
    e.stopPropagation();
    e.preventDefault();
    if (!window.confirm("Delete this session record?")) return;

    setDeletingId(id);
    try {
      await api.deleteInterview(id);
      setSessions((prev) => prev.filter((s) => s.id !== id));
    } catch (err: any) {
      alert(err.message || "Failed to delete interview.");
    } finally {
      setDeletingId(null);
    }
  };

  return (
    <div className="min-h-screen bg-white dark:bg-black py-12 text-neutral-900 dark:text-neutral-100">
      <div className="mx-auto max-w-4xl px-6 space-y-8">
        <div className="flex items-baseline justify-between pb-4 border-b border-neutral-100 dark:border-neutral-900">
          <div>
            <p className="text-xs font-mono uppercase tracking-wider text-neutral-500 mb-1">
              Archive
            </p>
            <h1 className="text-2xl font-semibold tracking-tight text-neutral-900 dark:text-neutral-50">
              Interview History
            </h1>
          </div>

          <Link href="/setup">
            <Button size="sm">New Interview</Button>
          </Link>
        </div>

        {error && (
          <div className="p-3 rounded-lg border border-red-200 dark:border-red-900 bg-red-50 dark:bg-red-950/40 text-red-800 dark:text-red-300 text-xs">
            {error}
          </div>
        )}

        {isLoading ? (
          <div className="py-24 text-center text-xs font-mono text-neutral-500">
            Loading past sessions...
          </div>
        ) : sessions.length === 0 ? (
          <div className="py-24 text-center space-y-3 border border-neutral-200 dark:border-neutral-800 rounded-xl p-8">
            <p className="text-xs sm:text-sm text-neutral-500">No interview sessions recorded yet.</p>
            <Link href="/setup">
              <Button size="sm">Start First Interview</Button>
            </Link>
          </div>
        ) : (
          <div className="divide-y divide-neutral-100 dark:divide-neutral-900 border-y border-neutral-100 dark:border-neutral-900">
            {sessions.map((item) => {
              const isCompleted = item.status === "completed";
              const targetUrl = isCompleted ? `/report/${item.id}` : `/interview/${item.id}`;

              return (
                <div
                  key={item.id}
                  className="py-4 flex flex-col sm:flex-row sm:items-center justify-between gap-4 hover:bg-neutral-50/50 dark:hover:bg-neutral-950/50 px-2 rounded-lg transition-colors group"
                >
                  <div className="space-y-1 flex-1">
                    <div className="flex items-center gap-2">
                      <Link
                        href={targetUrl}
                        className="text-sm font-medium text-neutral-900 dark:text-neutral-100 hover:underline"
                      >
                        {item.role_title}
                      </Link>
                      <Badge variant="outline" size="sm">
                        {item.experience_level}
                      </Badge>
                      <Badge variant="secondary" size="sm">
                        {item.interview_type}
                      </Badge>
                    </div>

                    <div className="flex items-center gap-3 text-[11px] text-neutral-500 font-mono">
                      <span>{formatDate(item.created_at)}</span>
                      <span>·</span>
                      <span>
                        {item.answered_turns_count}/{item.num_questions} questions
                      </span>
                      <span>·</span>
                      <span>{item.difficulty}</span>
                    </div>
                  </div>

                  <div className="flex items-center gap-4 shrink-0">
                    {item.overall_score !== null && item.overall_score !== undefined ? (
                      <div className="text-right">
                        <span className="text-sm font-semibold font-mono">
                          {Math.round(item.overall_score)}/100
                        </span>
                        <span className="text-[10px] text-neutral-400 block font-mono">
                          {item.readiness_level || "Evaluated"}
                        </span>
                      </div>
                    ) : (
                      <span className="text-xs text-neutral-400 font-mono">In Progress</span>
                    )}

                    <div className="flex items-center gap-2">
                      <Link href={targetUrl}>
                        <Button variant="outline" size="sm">
                          {isCompleted ? "View Report" : "Resume"}
                        </Button>
                      </Link>

                      <button
                        type="button"
                        onClick={(e) => handleDelete(item.id, e)}
                        disabled={deletingId === item.id}
                        className="p-1.5 text-neutral-400 hover:text-red-600 transition-colors cursor-pointer"
                        title="Delete"
                      >
                        <Trash2 className="h-3.5 w-3.5" />
                      </button>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
}
