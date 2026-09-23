"use client";

import React from "react";
import { 
  ShieldCheck, 
  Mail, 
  MessageSquare, 
  RotateCw, 
  Sparkles,
  Radio
} from "lucide-react";
import ThemeToggle from "../ui/ThemeToggle";

interface HeaderProps {
  onOpenEmailSim: () => void;
  onOpenChatSim: () => void;
  onRefresh: () => void;
  isRefreshing?: boolean;
  isBackendConnected: boolean;
}

export default function Header({
  onOpenEmailSim,
  onOpenChatSim,
  onRefresh,
  isRefreshing = false,
  isBackendConnected
}: HeaderProps) {
  return (
    <header className="sticky top-0 z-30 flex items-center justify-between px-4 py-3 sm:px-6 border-b border-neutral-200 dark:border-neutral-800/80 bg-white/80 dark:bg-neutral-950/80 backdrop-blur-md transition-colors duration-200">
      {/* Brand & System Status */}
      <div className="flex items-center gap-3">
        <div className="relative flex items-center justify-center w-9 h-9 rounded-xl bg-gradient-to-tr from-indigo-600 to-violet-600 text-white shadow-md shadow-indigo-500/20">
          <ShieldCheck className="w-5 h-5" />
          <span className="absolute -top-0.5 -right-0.5 flex h-2.5 w-2.5">
            <span className={`animate-ping absolute inline-flex h-full w-full rounded-full opacity-75 ${
              isBackendConnected ? "bg-emerald-400" : "bg-amber-400"
            }`} />
            <span className={`relative inline-flex rounded-full h-2.5 w-2.5 ${
              isBackendConnected ? "bg-emerald-500" : "bg-amber-500"
            }`} />
          </span>
        </div>

        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-base sm:text-lg font-bold tracking-tight text-neutral-900 dark:text-white">
              ResolveAI
            </h1>
            <span className="hidden sm:inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[11px] font-medium bg-indigo-50 dark:bg-indigo-950/50 text-indigo-700 dark:text-indigo-300 border border-indigo-200/80 dark:border-indigo-800/60">
              <Sparkles className="w-3 h-3 text-indigo-500" />
              Agent Console
            </span>
            <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-medium bg-neutral-100 dark:bg-neutral-800/60 text-neutral-600 dark:text-neutral-400 border border-neutral-200 dark:border-neutral-700/60">
              <span className={`w-1.5 h-1.5 rounded-full ${isBackendConnected ? "bg-emerald-500" : "bg-amber-500"}`} />
              {isBackendConnected ? "Live API" : "Sandbox"}
            </span>
          </div>
          <p className="text-xs text-neutral-500 dark:text-neutral-400 hidden md:block">
            Autonomous Resolution & Cryptographic Gatekeeper
          </p>
        </div>
      </div>

      {/* Simulator Controls & Actions */}
      <div className="flex items-center gap-2 sm:gap-2.5">
        <button
          onClick={onOpenEmailSim}
          type="button"
          className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg border border-neutral-200 dark:border-neutral-800 bg-neutral-50/80 dark:bg-neutral-900/80 hover:bg-neutral-100 dark:hover:bg-neutral-800 text-neutral-700 dark:text-neutral-200 text-xs font-semibold shadow-sm transition-all duration-150 cursor-pointer hover:border-indigo-300 dark:hover:border-indigo-700 active:scale-95"
          title="Simulate Inbound Customer Email"
        >
          <Mail className="w-3.5 h-3.5 text-indigo-600 dark:text-indigo-400" />
          <span className="hidden sm:inline">Simulate Email</span>
          <span className="sm:hidden">Email</span>
        </button>

        <button
          onClick={onOpenChatSim}
          type="button"
          className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold shadow-sm shadow-indigo-600/20 transition-all duration-150 cursor-pointer active:scale-95"
          title="Test Live Chat Experience"
        >
          <MessageSquare className="w-3.5 h-3.5" />
          <span className="hidden sm:inline">Live Chat</span>
          <span className="sm:hidden">Chat</span>
        </button>

        <button
          onClick={onRefresh}
          type="button"
          disabled={isRefreshing}
          className="flex items-center justify-center w-9 h-9 rounded-lg border border-neutral-200 dark:border-neutral-800 bg-white/80 dark:bg-neutral-900/80 hover:bg-neutral-100 dark:hover:bg-neutral-800 text-neutral-600 dark:text-neutral-300 transition-all duration-150 shadow-sm cursor-pointer active:scale-95 disabled:opacity-50"
          title="Refresh ticket stream"
          aria-label="Refresh tickets"
        >
          <RotateCw className={`w-4 h-4 ${isRefreshing ? "animate-spin text-indigo-600 dark:text-indigo-400" : ""}`} />
        </button>

        <div className="h-5 w-[1px] bg-neutral-200 dark:bg-neutral-800 mx-0.5" />

        <ThemeToggle />
      </div>
    </header>
  );
}
