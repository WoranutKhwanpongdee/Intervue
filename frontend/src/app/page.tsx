import Link from "next/link";
import { ArrowRight, Check } from "lucide-react";
import { Button } from "@/components/ui/Button";

export default function LandingPage() {
  return (
    <div className="flex flex-col min-h-screen bg-white dark:bg-black text-black dark:text-white">
      {/* Editorial Hero */}
      <section className="pt-20 pb-16 sm:pt-28 sm:pb-24 border-b border-neutral-100 dark:border-neutral-900">
        <div className="mx-auto max-w-4xl px-6">
          <div className="space-y-6">
            <p className="text-xs font-mono uppercase tracking-wider text-neutral-500">
              Technical Mock Interviews
            </p>

            <h1 className="text-3xl sm:text-5xl font-semibold tracking-tight text-neutral-900 dark:text-neutral-50 max-w-2xl leading-[1.15]">
              Technical interview practice that adapts to your actual answers.
            </h1>

            <p className="text-base sm:text-lg text-neutral-600 dark:text-neutral-400 font-normal leading-relaxed max-w-2xl">
              Intervue is designed for engineering roles. It tests architectural reasoning, probes trade-offs with targeted follow-ups, and scores each response on technical accuracy, clarity, and completeness.
            </p>

            <div className="flex items-center gap-4 pt-2">
              <Link href="/setup">
                <Button size="lg">
                  Start an Interview
                  <ArrowRight className="h-4 w-4 ml-2" />
                </Button>
              </Link>
              <Link href="/history">
                <Button variant="outline" size="lg">
                  View Past History
                </Button>
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* Realistic Technical Preview (Clean code-style dossier, NO traffic light dots) */}
      <section className="py-20 border-b border-neutral-100 dark:border-neutral-900 bg-neutral-50/50 dark:bg-neutral-950/50">
        <div className="mx-auto max-w-4xl px-6 space-y-8">
          <div>
            <p className="text-xs font-mono uppercase tracking-wider text-neutral-500 mb-2">
              How the interview behaves
            </p>
            <h2 className="text-xl sm:text-2xl font-semibold tracking-tight text-neutral-900 dark:text-neutral-100">
              Not a static questionnaire.
            </h2>
          </div>

          <div className="rounded-xl border border-neutral-200 dark:border-neutral-800 bg-white dark:bg-black p-6 sm:p-8 space-y-6">
            {/* Question Step */}
            <div className="space-y-2">
              <div className="flex items-center gap-2 text-xs font-mono text-neutral-500">
                <span>01. INITIAL PROMPT</span>
                <span>·</span>
                <span>SYSTEM DESIGN</span>
              </div>
              <p className="text-sm sm:text-base font-medium text-neutral-900 dark:text-neutral-100">
                &ldquo;Design a rate limiter handling 50,000 requests per second across three geographic regions. How do you prevent race conditions while maintaining low latency?&rdquo;
              </p>
            </div>

            {/* Answer Step */}
            <div className="p-4 rounded-lg bg-neutral-50 dark:bg-neutral-900/60 border border-neutral-200 dark:border-neutral-800 space-y-2">
              <span className="text-[11px] font-mono text-neutral-500 uppercase">
                Candidate Answer
              </span>
              <p className="text-xs sm:text-sm text-neutral-700 dark:text-neutral-300 leading-relaxed font-sans">
                &ldquo;I would deploy local Redis clusters in each region using a sliding-window log counter, executing a Lua script to keep reads and increments atomic. For global limits, we synchronize via asynchronous event streams.&rdquo;
              </p>
            </div>

            {/* Adaptive Follow-up Step */}
            <div className="border-l-2 border-neutral-900 dark:border-neutral-100 pl-4 py-1 space-y-1">
              <span className="text-[11px] font-mono text-neutral-500 uppercase">
                Adaptive Follow-up (AI Probing Edge Case)
              </span>
              <p className="text-xs sm:text-sm font-medium text-neutral-900 dark:text-neutral-100">
                &ldquo;Because asynchronous stream sync introduces eventual consistency, how do you handle cross-region quota starvation during sudden traffic spikes in Region A?&rdquo;
              </p>
            </div>

            {/* Rubric metrics bar */}
            <div className="pt-4 border-t border-neutral-100 dark:border-neutral-900 grid grid-cols-2 sm:grid-cols-4 gap-4 text-xs">
              <div>
                <span className="text-neutral-500 block">Technical Accuracy</span>
                <span className="font-semibold text-neutral-900 dark:text-neutral-100 font-mono">88/100</span>
              </div>
              <div>
                <span className="text-neutral-500 block">Direct Relevance</span>
                <span className="font-semibold text-neutral-900 dark:text-neutral-100 font-mono">92/100</span>
              </div>
              <div>
                <span className="text-neutral-500 block">Communication</span>
                <span className="font-semibold text-neutral-900 dark:text-neutral-100 font-mono">85/100</span>
              </div>
              <div>
                <span className="text-neutral-500 block">Completeness</span>
                <span className="font-semibold text-neutral-900 dark:text-neutral-100 font-mono">80/100</span>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Feature Principles */}
      <section className="py-20 border-b border-neutral-100 dark:border-neutral-900">
        <div className="mx-auto max-w-4xl px-6">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <div className="space-y-2">
              <h3 className="text-sm font-semibold text-neutral-900 dark:text-neutral-100">
                1. Contextual Follow-ups
              </h3>
              <p className="text-xs text-neutral-600 dark:text-neutral-400 leading-relaxed">
                Intervue analyzes the specific technologies and trade-offs you mention. It doesn&apos;t move on until you defend your architecture.
              </p>
            </div>

            <div className="space-y-2">
              <h3 className="text-sm font-semibold text-neutral-900 dark:text-neutral-100">
                2. Four-Dimensional Rubric
              </h3>
              <p className="text-xs text-neutral-600 dark:text-neutral-400 leading-relaxed">
                Answers are evaluated on Technical Accuracy, Relevance, Communication Clarity, and Completeness—the exact dimensions used in real interviews.
              </p>
            </div>

            <div className="space-y-2">
              <h3 className="text-sm font-semibold text-neutral-900 dark:text-neutral-100">
                3. Grounded in Your Resume
              </h3>
              <p className="text-xs text-neutral-600 dark:text-neutral-400 leading-relaxed">
                Optionally upload a PDF resume. The interviewer extracts your real stack and projects to construct realistic interview scenarios.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Bottom Minimal CTA */}
      <section className="py-20 text-center">
        <div className="mx-auto max-w-2xl px-6 space-y-4">
          <h2 className="text-2xl font-semibold tracking-tight text-neutral-900 dark:text-neutral-100">
            Ready to practice?
          </h2>
          <p className="text-xs sm:text-sm text-neutral-500">
            Configure your target position, level, and question count in under a minute.
          </p>
          <div className="pt-2">
            <Link href="/setup">
              <Button size="lg">Start Session</Button>
            </Link>
          </div>
        </div>
      </section>
    </div>
  );
}
