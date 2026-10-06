import React from "react";
import Link from "next/link";
import { Layers } from "lucide-react";

export const Footer: React.FC = () => {
  return (
    <footer className="border-t border-black/[0.06] dark:border-white/[0.08] bg-[#fbfbfd] dark:bg-black py-10 text-[#86868b] text-[11px] leading-relaxed">
      <div className="mx-auto max-w-5xl px-4 sm:px-8 space-y-4">
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
          <div className="flex items-center gap-2">
            <div className="flex h-5 w-5 items-center justify-center rounded bg-[#1d1d1f] text-white dark:bg-[#f5f5f7] dark:text-[#1d1d1f]">
              <Layers className="h-3 w-3" />
            </div>
            <span className="font-semibold text-[#1d1d1f] dark:text-[#f5f5f7]">Intervue</span>
            <span>— The Adaptive AI Mock Interview Coach</span>
          </div>

          <div className="flex items-center gap-5">
            <Link href="/" className="hover:text-[#1d1d1f] dark:hover:text-[#f5f5f7] transition-colors">
              Overview
            </Link>
            <Link href="/setup" className="hover:text-[#1d1d1f] dark:hover:text-[#f5f5f7] transition-colors">
              Calibrate
            </Link>
            <Link href="/history" className="hover:text-[#1d1d1f] dark:hover:text-[#f5f5f7] transition-colors">
              History
            </Link>
            <a
              href="http://localhost:8000/docs"
              target="_blank"
              rel="noopener noreferrer"
              className="hover:text-[#1d1d1f] dark:hover:text-[#f5f5f7] transition-colors"
            >
              API Reference
            </a>
          </div>
        </div>

        <div className="pt-2 border-t border-black/[0.04] dark:border-white/[0.04] flex flex-col sm:flex-row items-center justify-between gap-2 text-[#a1a1a6]">
          <p>© 2026 Intervue Technologies Inc. Designed with Apple human interface principles.</p>
          <p>Powered by Structured LLM & Pydantic Engine</p>
        </div>
      </div>
    </footer>
  );
};
