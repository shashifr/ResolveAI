"use client";

import React, { useState } from "react";
import { 
  ShieldCheck, 
  Hash, 
  Cpu, 
  Copy, 
  Check, 
  ChevronRight,
  ExternalLink,
  Layers,
  Sparkles
} from "lucide-react";
import { AuditLog } from "../../types";

interface AuditLedgerProps {
  logs: AuditLog[];
}

export default function AuditLedger({ logs }: AuditLedgerProps) {
  const [selectedNodeIndex, setSelectedNodeIndex] = useState<number>(
    logs.length > 0 ? logs.length - 1 : 0
  );
  const [copiedHash, setCopiedHash] = useState<string | null>(null);

  if (!logs || logs.length === 0) {
    return (
      <div className="p-4 rounded-xl border border-neutral-200 dark:border-neutral-800 bg-neutral-50/50 dark:bg-neutral-900/30 text-center text-xs text-neutral-500">
        No cryptographic audit blocks recorded yet.
      </div>
    );
  }

  const activeLog = logs[selectedNodeIndex] || logs[logs.length - 1];

  const handleCopy = (text: string) => {
    navigator.clipboard.writeText(text);
    setCopiedHash(text);
    setTimeout(() => setCopiedHash(null), 2000);
  };

  // Verify chain integrity
  let chainIntact = true;
  for (let i = 1; i < logs.length; i++) {
    if (logs[i].prev_hash && logs[i - 1].hash && logs[i].prev_hash !== logs[i - 1].hash) {
      chainIntact = false;
      break;
    }
  }

  const getNodeColor = (node: string) => {
    switch (node.toLowerCase()) {
      case "intake":
        return "bg-blue-500/10 text-blue-600 dark:text-blue-400 border-blue-200 dark:border-blue-900";
      case "classifier":
        return "bg-purple-500/10 text-purple-600 dark:text-purple-400 border-purple-200 dark:border-purple-900";
      case "context_retriever":
      case "context":
        return "bg-amber-500/10 text-amber-600 dark:text-amber-400 border-amber-200 dark:border-amber-900";
      case "resolution_agent":
      case "resolution":
      case "resolver":
        return "bg-indigo-500/10 text-indigo-600 dark:text-indigo-400 border-indigo-200 dark:border-indigo-900";
      case "confidence_gate":
      case "gating":
        return "bg-pink-500/10 text-pink-600 dark:text-pink-400 border-pink-200 dark:border-pink-900";
      case "human_console":
        return "bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border-emerald-200 dark:border-emerald-900";
      default:
        return "bg-neutral-500/10 text-neutral-600 dark:text-neutral-400 border-neutral-200 dark:border-neutral-800";
    }
  };

  return (
    <div className="rounded-xl border border-neutral-200 dark:border-neutral-800 bg-white dark:bg-neutral-900/90 shadow-sm overflow-hidden transition-colors duration-200">
      {/* Header */}
      <div className="flex items-center justify-between px-4 py-3 border-b border-neutral-200 dark:border-neutral-800/80 bg-neutral-50/50 dark:bg-neutral-900/50">
        <div className="flex items-center gap-2">
          <div className="p-1 rounded-md bg-indigo-50 dark:bg-indigo-950/60 text-indigo-600 dark:text-indigo-400">
            <Layers className="w-4 h-4" />
          </div>
          <span className="text-xs font-bold text-neutral-900 dark:text-white uppercase tracking-wider">
            Cryptographic Execution Ledger
          </span>
          <span className="text-[11px] text-neutral-400 dark:text-neutral-500">
            ({logs.length} blocks)
          </span>
        </div>

        {/* Chain verification badge */}
        <span className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-bold ${
          chainIntact 
            ? "bg-emerald-50 dark:bg-emerald-950/60 text-emerald-600 dark:text-emerald-400 border border-emerald-200 dark:border-emerald-800/60"
            : "bg-rose-50 dark:bg-rose-950/60 text-rose-600 dark:text-rose-400 border border-rose-200 dark:border-rose-800/60"
        }`}>
          <ShieldCheck className="w-3 h-3" />
          {chainIntact ? "SHA-256 Chain Verified" : "Chain Broken"}
        </span>
      </div>

      {/* Interactive Node Breadcrumb Pipeline */}
      <div className="p-3 border-b border-neutral-100 dark:border-neutral-800/50 overflow-x-auto">
        <div className="flex items-center gap-1.5 min-w-max">
          {logs.map((log, idx) => {
            const isSelected = selectedNodeIndex === idx;
            return (
              <React.Fragment key={idx}>
                <button
                  onClick={() => setSelectedNodeIndex(idx)}
                  className={`flex items-center gap-1.5 px-2.5 py-1 rounded-lg text-xs font-semibold border transition-all duration-150 cursor-pointer ${
                    isSelected
                      ? "bg-indigo-600 text-white border-indigo-600 shadow-sm"
                      : "bg-neutral-50 dark:bg-neutral-800/80 hover:bg-neutral-100 dark:hover:bg-neutral-800 text-neutral-700 dark:text-neutral-300 border-neutral-200 dark:border-neutral-700/60"
                  }`}
                >
                  <span className="text-[10px] opacity-70">#{idx + 1}</span>
                  <span className="capitalize">{log.node.replace("_", " ")}</span>
                </button>
                {idx < logs.length - 1 && (
                  <ChevronRight className="w-3.5 h-3.5 text-neutral-300 dark:text-neutral-600 shrink-0" />
                )}
              </React.Fragment>
            );
          })}
        </div>
      </div>

      {/* Active Node Detail Inspector */}
      {activeLog && (
        <div className="p-4 space-y-3.5 bg-neutral-50/30 dark:bg-neutral-950/30">
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
            <div className="p-2.5 rounded-lg border border-neutral-200/70 dark:border-neutral-800 bg-white dark:bg-neutral-900">
              <span className="text-[10px] font-semibold text-neutral-400 uppercase tracking-wider block mb-1">
                Model Used
              </span>
              <div className="flex items-center gap-1.5 text-xs font-semibold text-neutral-900 dark:text-neutral-100 truncate">
                <Cpu className="w-3.5 h-3.5 text-indigo-500 shrink-0" />
                <span className="truncate">{activeLog.model_used || "System"}</span>
              </div>
            </div>

            <div className="p-2.5 rounded-lg border border-neutral-200/70 dark:border-neutral-800 bg-white dark:bg-neutral-900">
              <span className="text-[10px] font-semibold text-neutral-400 uppercase tracking-wider block mb-1">
                Tokens & Cost
              </span>
              <span className="text-xs font-mono font-semibold text-neutral-900 dark:text-neutral-100">
                {activeLog.tokens || 0} tok / ${(activeLog.cost || 0).toFixed(5)}
              </span>
            </div>

            <div className="p-2.5 rounded-lg border border-neutral-200/70 dark:border-neutral-800 bg-white dark:bg-neutral-900">
              <span className="text-[10px] font-semibold text-neutral-400 uppercase tracking-wider block mb-1">
                Confidence
              </span>
              <span className="text-xs font-mono font-bold text-emerald-600 dark:text-emerald-400">
                {Math.round((activeLog.confidence || 0) * 100)}%
              </span>
            </div>

            <div className="p-2.5 rounded-lg border border-neutral-200/70 dark:border-neutral-800 bg-white dark:bg-neutral-900">
              <span className="text-[10px] font-semibold text-neutral-400 uppercase tracking-wider block mb-1">
                Action Executed
              </span>
              <span className="text-xs font-medium text-neutral-800 dark:text-neutral-200 truncate block">
                {activeLog.action_taken || "Logged state transition"}
              </span>
            </div>
          </div>

          {/* Cryptographic Hash Pair */}
          <div className="space-y-1.5 p-3 rounded-lg border border-neutral-200/70 dark:border-neutral-800 bg-neutral-100/50 dark:bg-neutral-900/50 font-mono text-[11px]">
            <div className="flex items-center justify-between gap-2">
              <span className="text-neutral-400 dark:text-neutral-500 shrink-0">Previous Hash:</span>
              <span className="truncate text-neutral-600 dark:text-neutral-400 select-all">
                {activeLog.prev_hash || "0000000000000000000000000000000000000000000000000000000000000000"}
              </span>
            </div>

            <div className="flex items-center justify-between gap-2 pt-1 border-t border-neutral-200/50 dark:border-neutral-800/50">
              <span className="text-neutral-400 dark:text-neutral-500 shrink-0">Block Hash:</span>
              <div className="flex items-center gap-1.5 truncate">
                <span className="truncate font-bold text-indigo-600 dark:text-indigo-400 select-all">
                  {activeLog.hash}
                </span>
                <button
                  onClick={() => handleCopy(activeLog.hash)}
                  className="p-1 rounded hover:bg-neutral-200 dark:hover:bg-neutral-800 text-neutral-500 cursor-pointer"
                  title="Copy SHA-256 hash"
                >
                  {copiedHash === activeLog.hash ? (
                    <Check className="w-3.5 h-3.5 text-emerald-500" />
                  ) : (
                    <Copy className="w-3.5 h-3.5" />
                  )}
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
