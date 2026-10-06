import React from "react";
import { cn } from "@/lib/utils";

interface MetricCardProps {
  label: string;
  score: number; // 0 to 100
  subtitle?: string;
  className?: string;
}

export const MetricCard: React.FC<MetricCardProps> = ({
  label,
  score,
  subtitle,
  className,
}) => {
  return (
    <div
      className={cn(
        "p-4 rounded-lg border border-neutral-200 dark:border-neutral-800 bg-neutral-50/50 dark:bg-neutral-900/50",
        className
      )}
    >
      <div className="flex items-baseline justify-between mb-2">
        <span className="text-[11px] font-medium tracking-tight text-neutral-500 dark:text-neutral-400 uppercase">
          {label}
        </span>
        <span className="text-lg font-semibold tracking-tight text-neutral-900 dark:text-neutral-100 font-mono">
          {Math.round(score)}
          <span className="text-xs text-neutral-400 font-normal">/100</span>
        </span>
      </div>
      <div className="h-1 w-full bg-neutral-200 dark:bg-neutral-800 rounded-full overflow-hidden mb-1.5">
        <div
          className="h-full bg-neutral-900 dark:bg-neutral-100 rounded-full transition-all duration-300"
          style={{ width: `${Math.min(Math.max(score, 0), 100)}%` }}
        />
      </div>
      {subtitle && (
        <p className="text-[11px] text-neutral-500 dark:text-neutral-400 line-clamp-1">
          {subtitle}
        </p>
      )}
    </div>
  );
};
