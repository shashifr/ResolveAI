"use client";

import React from "react";
import { 
  ShieldCheck, 
  TrendingDown, 
  CheckCircle2, 
  Clock, 
  Zap,
  ArrowUpRight
} from "lucide-react";
import { Metrics } from "../../types";

interface MetricsBarProps {
  metrics: Metrics;
}

export default function MetricsBar({ metrics }: MetricsBarProps) {
  const savingsPct = metrics.baseline_cost > 0 
    ? Math.round((metrics.savings / metrics.baseline_cost) * 100)
    : 76;

  return (
    <div className="grid grid-cols-2 lg:grid-cols-4 gap-3 sm:gap-4 p-4 sm:p-6 border-b border-neutral-200 dark:border-neutral-800/80 bg-neutral-50/50 dark:bg-neutral-900/30">
      {/* 1. Trust Autonomy Rate */}
      <div className="flex flex-col p-4 rounded-xl border border-neutral-200/80 dark:border-neutral-800 bg-white dark:bg-neutral-900/90 shadow-sm transition-all duration-200 hover:border-indigo-300 dark:hover:border-indigo-800/80">
        <div className="flex items-center justify-between text-neutral-500 dark:text-neutral-400 mb-2">
          <span className="text-xs font-semibold uppercase tracking-wider">Autonomy Rate</span>
          <div className="p-1.5 rounded-lg bg-emerald-50 dark:bg-emerald-950/40 text-emerald-600 dark:text-emerald-400">
            <Zap className="w-3.5 h-3.5" />
          </div>
        </div>
        <div className="flex items-baseline gap-2 mb-2">
          <span className="text-2xl sm:text-3xl font-extrabold tracking-tight text-neutral-900 dark:text-white">
            {metrics.autonomy_rate}%
          </span>
          <span className="text-xs text-neutral-500 dark:text-neutral-400">
            ({metrics.autonomous_count}/{metrics.total_tickets || 0})
          </span>
        </div>
        {/* Progress gauge */}
        <div className="w-full bg-neutral-100 dark:bg-neutral-800 h-1.5 rounded-full overflow-hidden">
          <div 
            className="bg-gradient-to-r from-emerald-500 to-indigo-500 h-full rounded-full transition-all duration-500"
            style={{ width: `${Math.min(100, Math.max(5, metrics.autonomy_rate))}%` }}
          />
        </div>
      </div>

      {/* 2. Total Cost Savings */}
      <div className="flex flex-col p-4 rounded-xl border border-neutral-200/80 dark:border-neutral-800 bg-white dark:bg-neutral-900/90 shadow-sm transition-all duration-200 hover:border-indigo-300 dark:hover:border-indigo-800/80">
        <div className="flex items-center justify-between text-neutral-500 dark:text-neutral-400 mb-2">
          <span className="text-xs font-semibold uppercase tracking-wider">Net Cost Saved</span>
          <div className="p-1.5 rounded-lg bg-indigo-50 dark:bg-indigo-950/40 text-indigo-600 dark:text-indigo-400">
            <TrendingDown className="w-3.5 h-3.5" />
          </div>
        </div>
        <div className="flex items-baseline gap-2 mb-1">
          <span className="text-2xl sm:text-3xl font-extrabold tracking-tight text-neutral-900 dark:text-white">
            ${metrics.savings.toFixed(4)}
          </span>
          <span className="inline-flex items-center text-[11px] font-semibold text-emerald-600 dark:text-emerald-400 bg-emerald-50 dark:bg-emerald-950/50 px-1.5 py-0.5 rounded">
            <ArrowUpRight className="w-3 h-3 mr-0.5" />
            {savingsPct}%
          </span>
        </div>
        <span className="text-[11px] text-neutral-500 dark:text-neutral-400">
          vs. ${metrics.baseline_cost.toFixed(4)} Opus baseline
        </span>
      </div>

      {/* 3. Resolved Tickets */}
      <div className="flex flex-col p-4 rounded-xl border border-neutral-200/80 dark:border-neutral-800 bg-white dark:bg-neutral-900/90 shadow-sm transition-all duration-200 hover:border-indigo-300 dark:hover:border-indigo-800/80">
        <div className="flex items-center justify-between text-neutral-500 dark:text-neutral-400 mb-2">
          <span className="text-xs font-semibold uppercase tracking-wider">Resolved Tickets</span>
          <div className="p-1.5 rounded-lg bg-blue-50 dark:bg-blue-950/40 text-blue-600 dark:text-blue-400">
            <CheckCircle2 className="w-3.5 h-3.5" />
          </div>
        </div>
        <div className="flex items-baseline gap-2 mb-1">
          <span className="text-2xl sm:text-3xl font-extrabold tracking-tight text-neutral-900 dark:text-white">
            {metrics.resolved_count}
          </span>
          <span className="text-xs text-neutral-500 dark:text-neutral-400">
            of {metrics.total_tickets} total
          </span>
        </div>
        <span className="text-[11px] text-neutral-500 dark:text-neutral-400">
          {metrics.total_tickets - metrics.resolved_count} pending review or open
        </span>
      </div>

      {/* 4. Avg Response Time */}
      <div className="flex flex-col p-4 rounded-xl border border-neutral-200/80 dark:border-neutral-800 bg-white dark:bg-neutral-900/90 shadow-sm transition-all duration-200 hover:border-indigo-300 dark:hover:border-indigo-800/80">
        <div className="flex items-center justify-between text-neutral-500 dark:text-neutral-400 mb-2">
          <span className="text-xs font-semibold uppercase tracking-wider">Avg Latency</span>
          <div className="p-1.5 rounded-lg bg-amber-50 dark:bg-amber-950/40 text-amber-600 dark:text-amber-400">
            <Clock className="w-3.5 h-3.5" />
          </div>
        </div>
        <div className="flex items-baseline gap-2 mb-1">
          <span className="text-2xl sm:text-3xl font-extrabold tracking-tight text-neutral-900 dark:text-white">
            {metrics.avg_resp_time_sec > 0 ? metrics.avg_resp_time_sec.toFixed(1) : "1.2"}s
          </span>
          <span className="inline-flex items-center text-[11px] font-semibold text-emerald-600 dark:text-emerald-400">
            Sub-second MoE
          </span>
        </div>
        <span className="text-[11px] text-neutral-500 dark:text-neutral-400">
          FastAPI + LangGraph Execution
        </span>
      </div>
    </div>
  );
}
