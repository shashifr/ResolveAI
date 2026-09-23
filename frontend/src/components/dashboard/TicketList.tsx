"use client";

import React, { useEffect, useRef } from "react";
import { 
  Search, 
  X, 
  Mail, 
  MessageSquare, 
  Phone, 
  AlertCircle, 
  CheckCircle2, 
  Clock3,
  Inbox,
  Filter
} from "lucide-react";
import { Ticket, TabFilter } from "../../types";

interface TicketListProps {
  tickets: Ticket[];
  selectedTicketId: string | null;
  onSelectTicket: (id: string) => void;
  searchQuery: string;
  onSearchChange: (q: string) => void;
  activeTab: TabFilter;
  onTabChange: (tab: TabFilter) => void;
}

export default function TicketList({
  tickets,
  selectedTicketId,
  onSelectTicket,
  searchQuery,
  onSearchChange,
  activeTab,
  onTabChange,
}: TicketListProps) {
  const searchInputRef = useRef<HTMLInputElement>(null);

  // Keyboard shortcut listener: press '/' to focus search
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === "/" && document.activeElement !== searchInputRef.current) {
        e.preventDefault();
        searchInputRef.current?.focus();
      }
    };
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, []);

  const counts = {
    all: tickets.length,
    escalated: tickets.filter(t => t.status === "Escalated").length,
    resolved: tickets.filter(t => t.status === "Resolved").length,
    open: tickets.filter(t => t.status === "Open").length,
  };

  const getChannelIcon = (ch: string) => {
    switch (ch) {
      case "email":
        return <Mail className="w-3.5 h-3.5" />;
      case "chat":
        return <MessageSquare className="w-3.5 h-3.5" />;
      case "voice":
        return <Phone className="w-3.5 h-3.5" />;
      default:
        return <Mail className="w-3.5 h-3.5" />;
    }
  };

  return (
    <div className="flex flex-col h-full bg-white dark:bg-neutral-950 border-r border-neutral-200 dark:border-neutral-800 transition-colors duration-200">
      {/* Search Header */}
      <div className="p-3 sm:p-4 border-b border-neutral-200 dark:border-neutral-800/80 space-y-3">
        <div className="relative">
          <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-neutral-400 dark:text-neutral-500" />
          <input
            ref={searchInputRef}
            type="text"
            placeholder="Search tickets by ID, email, topic... (/ to focus)"
            value={searchQuery}
            onChange={(e) => onSearchChange(e.target.value)}
            className="w-full pl-9 pr-8 py-2 text-xs sm:text-sm rounded-lg border border-neutral-200 dark:border-neutral-800 bg-neutral-50 dark:bg-neutral-900 text-neutral-900 dark:text-white placeholder-neutral-400 dark:placeholder-neutral-500 focus:outline-none focus:ring-2 focus:ring-indigo-500/30 focus:border-indigo-500 transition-all"
          />
          {searchQuery && (
            <button
              onClick={() => onSearchChange("")}
              className="absolute right-2.5 top-1/2 -translate-y-1/2 text-neutral-400 hover:text-neutral-600 dark:hover:text-neutral-300"
            >
              <X className="w-3.5 h-3.5" />
            </button>
          )}
        </div>

        {/* Tab Filters */}
        <div className="flex items-center gap-1 p-0.5 rounded-lg bg-neutral-100 dark:bg-neutral-900 border border-neutral-200/80 dark:border-neutral-800/80 text-xs">
          <button
            onClick={() => onTabChange("all")}
            type="button"
            className={`flex-1 flex items-center justify-center gap-1.5 py-1.5 rounded-md font-medium transition-all duration-150 cursor-pointer ${
              activeTab === "all"
                ? "bg-white dark:bg-neutral-800 text-neutral-900 dark:text-white shadow-xs font-semibold"
                : "text-neutral-600 dark:text-neutral-400 hover:text-neutral-900 dark:hover:text-white"
            }`}
          >
            All
            <span className="text-[10px] px-1.5 py-0.2 rounded-full bg-neutral-200/70 dark:bg-neutral-700/60 font-semibold">
              {counts.all}
            </span>
          </button>

          <button
            onClick={() => onTabChange("escalated")}
            type="button"
            className={`flex-1 flex items-center justify-center gap-1.5 py-1.5 rounded-md font-medium transition-all duration-150 cursor-pointer ${
              activeTab === "escalated"
                ? "bg-white dark:bg-neutral-800 text-amber-600 dark:text-amber-400 shadow-xs font-semibold"
                : "text-neutral-600 dark:text-neutral-400 hover:text-amber-600 dark:hover:text-amber-400"
            }`}
          >
            Review
            {counts.escalated > 0 && (
              <span className="text-[10px] px-1.5 py-0.2 rounded-full bg-amber-100 dark:bg-amber-950/80 text-amber-700 dark:text-amber-400 font-bold animate-pulse">
                {counts.escalated}
              </span>
            )}
          </button>

          <button
            onClick={() => onTabChange("resolved")}
            type="button"
            className={`flex-1 flex items-center justify-center gap-1.5 py-1.5 rounded-md font-medium transition-all duration-150 cursor-pointer ${
              activeTab === "resolved"
                ? "bg-white dark:bg-neutral-800 text-emerald-600 dark:text-emerald-400 shadow-xs font-semibold"
                : "text-neutral-600 dark:text-neutral-400 hover:text-emerald-600 dark:hover:text-emerald-400"
            }`}
          >
            Auto
            <span className="text-[10px] px-1.5 py-0.2 rounded-full bg-neutral-200/70 dark:bg-neutral-700/60 font-semibold">
              {counts.resolved}
            </span>
          </button>
        </div>
      </div>

      {/* Ticket Cards Stream */}
      <div className="flex-1 overflow-y-auto divide-y divide-neutral-100 dark:divide-neutral-800/60">
        {tickets.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-64 p-6 text-center text-neutral-400 dark:text-neutral-500">
            <Inbox className="w-10 h-10 mb-2 stroke-1" />
            <p className="text-sm font-semibold text-neutral-700 dark:text-neutral-300">No tickets found</p>
            <p className="text-xs mt-1">Try simulating an incoming email or chat</p>
          </div>
        ) : (
          tickets.map((t) => {
            const isSelected = selectedTicketId === t.id;
            const isEscalated = t.status === "Escalated";
            const isResolved = t.status === "Resolved";
            const confidencePct = Math.round((t.confidence_score || 0) * 100);

            return (
              <div
                key={t.id}
                onClick={() => onSelectTicket(t.id)}
                className={`relative flex flex-col p-3.5 sm:p-4 cursor-pointer transition-all duration-150 border-l-4 ${
                  isSelected
                    ? "bg-indigo-50/70 dark:bg-indigo-950/30 border-l-indigo-600 dark:border-l-indigo-500 shadow-xs"
                    : "border-l-transparent hover:bg-neutral-50 dark:hover:bg-neutral-900/60"
                }`}
              >
                {/* Header row: ID + Status + Channel */}
                <div className="flex items-center justify-between gap-2 mb-1.5">
                  <div className="flex items-center gap-2">
                    <span className="text-xs font-mono font-bold tracking-tight text-neutral-900 dark:text-neutral-200">
                      {t.id}
                    </span>
                    <span className="flex items-center gap-1 text-[11px] text-neutral-500 dark:text-neutral-400 capitalize">
                      {getChannelIcon(t.channel)}
                      <span className="hidden sm:inline">{t.channel}</span>
                    </span>
                  </div>

                  {/* Status Badge */}
                  <span className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-bold ${
                    isEscalated
                      ? "bg-amber-100 dark:bg-amber-950/70 text-amber-700 dark:text-amber-300 border border-amber-300/60 dark:border-amber-700/60"
                      : isResolved
                      ? "bg-emerald-100 dark:bg-emerald-950/70 text-emerald-700 dark:text-emerald-300 border border-emerald-300/60 dark:border-emerald-700/60"
                      : "bg-blue-100 dark:bg-blue-950/70 text-blue-700 dark:text-blue-300 border border-blue-300/60 dark:border-blue-700/60"
                  }`}>
                    {isEscalated && <AlertCircle className="w-3 h-3" />}
                    {isResolved && <CheckCircle2 className="w-3 h-3" />}
                    {!isEscalated && !isResolved && <Clock3 className="w-3 h-3" />}
                    {isEscalated ? "Escalated" : isResolved ? "Resolved" : "Open"}
                  </span>
                </div>

                {/* Subject & Preview */}
                <h4 className="text-xs sm:text-sm font-semibold text-neutral-900 dark:text-white line-clamp-1 mb-1">
                  {t.subject || "Customer Inquiry"}
                </h4>
                <p className="text-xs text-neutral-500 dark:text-neutral-400 line-clamp-2 mb-2.5">
                  {t.latest_message || "No message content recorded."}
                </p>

                {/* Footer: Customer name & Confidence score gauge */}
                <div className="flex items-center justify-between text-[11px] text-neutral-500 dark:text-neutral-400 pt-1 border-t border-neutral-100 dark:border-neutral-800/40">
                  <span className="truncate max-w-[130px] font-medium text-neutral-700 dark:text-neutral-300">
                    {t.customer_name || t.customer_email}
                  </span>

                  <div className="flex items-center gap-1.5 shrink-0">
                    <span className="text-[10px] text-neutral-400 dark:text-neutral-500">Confidence</span>
                    <span className={`font-mono font-bold text-[11px] ${
                      confidencePct >= 80 ? "text-emerald-600 dark:text-emerald-400" : "text-amber-600 dark:text-amber-400"
                    }`}>
                      {confidencePct}%
                    </span>
                  </div>
                </div>
              </div>
            );
          })
        )}
      </div>
    </div>
  );
}
