"use client";

import React from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";

export const Navbar: React.FC = () => {
  const pathname = usePathname();

  return (
    <header className="sticky top-0 z-50 w-full border-b border-black/[0.08] dark:border-white/[0.08] bg-white/80 dark:bg-black/80 backdrop-blur-md">
      <div className="mx-auto flex h-13 max-w-5xl items-center justify-between px-6">
        <div className="flex items-center gap-8">
          <Link href="/" className="font-semibold text-sm tracking-tight text-black dark:text-white">
            Intervue
          </Link>

          <nav className="flex items-center gap-6 text-xs text-neutral-500 dark:text-neutral-400">
            <Link
              href="/"
              className={`transition-colors hover:text-black dark:hover:text-white ${
                pathname === "/" ? "text-black dark:text-white font-medium" : ""
              }`}
            >
              Overview
            </Link>
            <Link
              href="/setup"
              className={`transition-colors hover:text-black dark:hover:text-white ${
                pathname === "/setup" ? "text-black dark:text-white font-medium" : ""
              }`}
            >
              Start
            </Link>
            <Link
              href="/history"
              className={`transition-colors hover:text-black dark:hover:text-white ${
                pathname === "/history" ? "text-black dark:text-white font-medium" : ""
              }`}
            >
              History
            </Link>
          </nav>
        </div>

        <div className="flex items-center gap-3">
          <Link
            href="/setup"
            className="rounded-full bg-black dark:bg-white text-white dark:text-black px-4 py-1.5 text-xs font-medium hover:opacity-90 transition-opacity"
          >
            New Interview
          </Link>
        </div>
      </div>
    </header>
  );
};
