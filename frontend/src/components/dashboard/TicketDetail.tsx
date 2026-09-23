"use client";

import React, { useState } from "react";
import { 
  Check, 
  X, 
  Edit3, 
  Send, 
  AlertTriangle, 
  ShieldAlert, 
  DollarSign, 
  User, 
  Mail, 
  MessageSquare, 
  Phone,
  Sparkles,
  RotateCcw,
  CheckCircle2,
  Clock,
  ArrowRight
} from "lucide-react";
import { TicketDetails } from "../../types";
import AuditLedger from "./AuditLedger";

interface TicketDetailProps {
  ticket: TicketDetails | null;
  onApprove: () => void;
  onReject: () => void;
  onEdit: (newReply: string) => void;
  actionLoading: boolean;
}

export default function TicketDetail({
  ticket,
  onApprove,
  onReject,
  onEdit,
  actionLoading,
}: TicketDetailProps) {
  const [isEditing, setIsEditing] = useState(false);
  const [editedText, setEditedText] = useState("");

  if (!ticket) {
    return (
      <div className="flex-1 flex flex-col items-center justify-center p-8 text-center text-neutral-400 dark:text-neutral-500 bg-neutral-50/30 dark:bg-neutral-950/20">
        <div className="w-12 h-12 rounded-2xl bg-neutral-100 dark:bg-neutral-800 flex items-center justify-center mb-3">
          <MessageSquare className="w-6 h-6 stroke-1 text-neutral-400" />
        </div>
        <h3 className="text-base font-semibold text-neutral-800 dark:text-neutral-200">
          No Ticket Selected
        </h3>
        <p className="text-xs text-neutral-500 max-w-sm mt-1">
          Select a ticket from the left sidebar to inspect customer messages, review autonomous decisions, and audit cryptographic traces.
        </p>
      </div>
    );
  }

  const isEscalated = ticket.status === "Escalated";
  const isResolved = ticket.status === "Resolved";
  const confidencePct = Math.round((ticket.confidence_score || 0) * 100);

  const handleStartEdit = () => {
    setEditedText(ticket.drafted_reply || "");
    setIsEditing(true);
  };

  const handleSaveEdit = () => {
    onEdit(editedText);
    setIsEditing(false);
  };

  return (
    <div className="flex-1 flex flex-col h-full overflow-y-auto bg-neutral-50/20 dark:bg-neutral-950/40 p-4 sm:p-6 space-y-6">
      {/* 1. Ticket Meta Header */}
      <div className="p-4 rounded-xl border border-neutral-200 dark:border-neutral-800 bg-white dark:bg-neutral-900 shadow-xs">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-3 border-b border-neutral-100 dark:border-neutral-800/60">
          <div>
            <div className="flex items-center gap-2 mb-1">
              <span className="font-mono text-sm font-bold text-neutral-900 dark:text-white">
                {ticket.id}
              </span>
              <span className={`px-2.5 py-0.5 rounded-full text-xs font-bold ${
                isEscalated
                  ? "bg-amber-100 dark:bg-amber-950/80 text-amber-700 dark:text-amber-300 border border-amber-300 dark:border-amber-800"
                  : isResolved
                  ? "bg-emerald-100 dark:bg-emerald-950/80 text-emerald-700 dark:text-emerald-300 border border-emerald-300 dark:border-emerald-800"
                  : "bg-blue-100 dark:bg-blue-950/80 text-blue-700 dark:text-blue-300 border border-blue-300 dark:border-blue-800"
              }`}>
                {ticket.status}
              </span>
              <span className="text-xs text-neutral-400 capitalize flex items-center gap-1">
                {ticket.channel === "email" && <Mail className="w-3.5 h-3.5" />}
                {ticket.channel === "chat" && <MessageSquare className="w-3.5 h-3.5" />}
                {ticket.channel === "voice" && <Phone className="w-3.5 h-3.5" />}
                {ticket.channel}
              </span>
            </div>
            <h2 className="text-base sm:text-lg font-bold text-neutral-900 dark:text-white">
              {ticket.subject || "Customer Support Case"}
            </h2>
          </div>

          {/* Right Metrics Strip */}
          <div className="flex items-center gap-4 text-xs font-mono">
            <div className="flex flex-col sm:items-end">
              <span className="text-[10px] text-neutral-400 font-sans uppercase">Confidence</span>
              <span className={`font-bold text-sm ${
                confidencePct >= 80 ? "text-emerald-600 dark:text-emerald-400" : "text-amber-600 dark:text-amber-400"
              }`}>
                {confidencePct}%
              </span>
            </div>
            <div className="h-6 w-[1px] bg-neutral-200 dark:bg-neutral-800" />
            <div className="flex flex-col sm:items-end">
              <span className="text-[10px] text-neutral-400 font-sans uppercase">Inference Cost</span>
              <span className="font-bold text-neutral-700 dark:text-neutral-300">
                ${(ticket.token_cost || 0).toFixed(5)}
              </span>
            </div>
          </div>
        </div>

        {/* Customer Information Row */}
        <div className="flex flex-wrap items-center gap-4 sm:gap-6 pt-3 text-xs text-neutral-600 dark:text-neutral-400">
          <div className="flex items-center gap-1.5">
            <User className="w-3.5 h-3.5 text-neutral-400" />
            <span className="font-medium text-neutral-900 dark:text-neutral-200">
              {ticket.customer_name || "Customer"}
            </span>
          </div>
          <div className="flex items-center gap-1.5">
            <Mail className="w-3.5 h-3.5 text-neutral-400" />
            <span className="truncate">{ticket.customer_email}</span>
          </div>
          <div className="flex items-center gap-1.5 ml-auto text-neutral-400 text-[11px]">
            <Clock className="w-3.5 h-3.5" />
            <span>Updated {ticket.updated_at ? new Date(ticket.updated_at).toLocaleTimeString() : "Just now"}</span>
          </div>
        </div>
      </div>

      {/* 2. Human-In-The-Loop Review Banner (If Escalated) */}
      {isEscalated && (
        <div className="p-4 sm:p-5 rounded-xl border border-amber-300 dark:border-amber-700/80 bg-gradient-to-br from-amber-500/5 via-amber-500/10 to-transparent shadow-sm space-y-4">
          <div className="flex items-start justify-between gap-3">
            <div className="flex items-center gap-2.5">
              <div className="p-2 rounded-xl bg-amber-500/20 text-amber-600 dark:text-amber-400 shrink-0">
                <ShieldAlert className="w-5 h-5" />
              </div>
              <div>
                <h3 className="text-sm font-bold text-amber-900 dark:text-amber-200">
                  Human Oversight Required
                </h3>
                <p className="text-xs text-amber-700 dark:text-amber-400 mt-0.5">
                  {ticket.explanation || "Confidence score below autonomous threshold. Review draft & actions before sending."}
                </p>
              </div>
            </div>
          </div>

          {/* Proposed Actions Card */}
          {ticket.drafted_actions && ticket.drafted_actions.length > 0 && (
            <div className="p-3.5 rounded-lg border border-amber-200 dark:border-amber-800/80 bg-white/80 dark:bg-neutral-900/80 space-y-2">
              <span className="text-[11px] font-bold text-amber-900 dark:text-amber-300 uppercase tracking-wider block">
                Proposed Autonomous System Action:
              </span>
              {ticket.drafted_actions.map((act, i) => (
                <div key={i} className="flex items-center gap-2 text-xs font-mono p-2 rounded bg-neutral-100/80 dark:bg-neutral-800/80">
                  <span className="px-1.5 py-0.5 rounded bg-amber-200 dark:bg-amber-900/60 text-amber-800 dark:text-amber-200 font-bold uppercase text-[10px]">
                    {act.action}
                  </span>
                  <span className="text-neutral-700 dark:text-neutral-300">
                    {act.order_id && `Order: ${act.order_id} `}
                    {act.amount && `Amount: $${act.amount} `}
                    {act.subscription_id && `Sub: ${act.subscription_id} `}
                    {act.reason && `(${act.reason})`}
                  </span>
                </div>
              ))}
            </div>
          )}

          {/* Drafted Response Editor */}
          <div className="space-y-2">
            <div className="flex items-center justify-between text-xs">
              <span className="font-semibold text-neutral-700 dark:text-neutral-300">
                AI Drafted Response to Customer:
              </span>
              {!isEditing ? (
                <button
                  onClick={handleStartEdit}
                  className="flex items-center gap-1 text-indigo-600 dark:text-indigo-400 font-semibold hover:underline cursor-pointer"
                >
                  <Edit3 className="w-3.5 h-3.5" />
                  Edit Draft
                </button>
              ) : (
                <button
                  onClick={() => setIsEditing(false)}
                  className="text-neutral-500 hover:text-neutral-700 dark:hover:text-neutral-300 font-semibold"
                >
                  Cancel
                </button>
              )}
            </div>

            {isEditing ? (
              <div className="space-y-2">
                <textarea
                  rows={4}
                  value={editedText}
                  onChange={(e) => setEditedText(e.target.value)}
                  className="w-full p-3 text-xs sm:text-sm rounded-lg border border-neutral-300 dark:border-neutral-700 bg-white dark:bg-neutral-900 text-neutral-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-indigo-500"
                />
                <button
                  onClick={handleSaveEdit}
                  disabled={actionLoading}
                  className="px-3 py-1.5 rounded-lg bg-indigo-600 text-white text-xs font-semibold hover:bg-indigo-500 transition-all cursor-pointer"
                >
                  Save Edited Response & Send
                </button>
              </div>
            ) : (
              <div className="p-3 rounded-lg border border-neutral-200 dark:border-neutral-800 bg-white/80 dark:bg-neutral-900/80 text-xs sm:text-sm text-neutral-800 dark:text-neutral-200 whitespace-pre-wrap">
                {ticket.drafted_reply || "No draft generated."}
              </div>
            )}
          </div>

          {/* Action Buttons: 1-Click Approve / Reject */}
          {!isEditing && (
            <div className="flex flex-wrap items-center gap-2 pt-2">
              <button
                onClick={onApprove}
                disabled={actionLoading}
                className="flex items-center gap-1.5 px-4 py-2 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-bold shadow-sm shadow-emerald-600/20 transition-all duration-150 cursor-pointer active:scale-95 disabled:opacity-50"
              >
                <Check className="w-4 h-4" />
                Approve & Execute Actions
              </button>

              <button
                onClick={handleStartEdit}
                disabled={actionLoading}
                className="flex items-center gap-1.5 px-3.5 py-2 rounded-lg border border-neutral-300 dark:border-neutral-700 bg-white dark:bg-neutral-900 hover:bg-neutral-50 dark:hover:bg-neutral-800 text-neutral-700 dark:text-neutral-200 text-xs font-semibold transition-all duration-150 cursor-pointer active:scale-95"
              >
                <Edit3 className="w-4 h-4" />
                Edit & Approve
              </button>

              <button
                onClick={onReject}
                disabled={actionLoading}
                className="flex items-center gap-1.5 px-3.5 py-2 rounded-lg border border-rose-200 dark:border-rose-900/60 bg-rose-50/50 dark:bg-rose-950/30 hover:bg-rose-100 dark:hover:bg-rose-900/50 text-rose-700 dark:text-rose-300 text-xs font-semibold transition-all duration-150 cursor-pointer active:scale-95 ml-auto"
              >
                <X className="w-4 h-4" />
                Reject
              </button>
            </div>
          )}
        </div>
      )}

      {/* 3. Conversation Message Stream */}
      <div className="rounded-xl border border-neutral-200 dark:border-neutral-800 bg-white dark:bg-neutral-900 shadow-xs overflow-hidden">
        <div className="px-4 py-3 border-b border-neutral-100 dark:border-neutral-800 bg-neutral-50/50 dark:bg-neutral-900/50 flex items-center justify-between">
          <span className="text-xs font-bold text-neutral-900 dark:text-white uppercase tracking-wider">
            Conversation Thread
          </span>
          <span className="text-xs text-neutral-400">
            {ticket.messages?.length || 0} message(s)
          </span>
        </div>

        <div className="p-4 sm:p-5 space-y-4">
          {ticket.messages && ticket.messages.length > 0 ? (
            ticket.messages.map((m, idx) => {
              const isCustomer = m.sender === "customer";
              return (
                <div
                  key={idx}
                  className={`flex gap-3 max-w-2xl ${isCustomer ? "mr-auto" : "ml-auto flex-row-reverse"}`}
                >
                  <div className={`w-8 h-8 rounded-full flex items-center justify-center shrink-0 text-xs font-bold ${
                    isCustomer 
                      ? "bg-neutral-200 dark:bg-neutral-800 text-neutral-700 dark:text-neutral-300"
                      : "bg-indigo-600 text-white"
                  }`}>
                    {isCustomer ? <User className="w-4 h-4" /> : <Sparkles className="w-4 h-4" />}
                  </div>

                  <div className={`p-3.5 rounded-2xl text-xs sm:text-sm space-y-1 shadow-xs ${
                    isCustomer
                      ? "bg-neutral-100 dark:bg-neutral-800 text-neutral-900 dark:text-neutral-100 rounded-tl-none"
                      : "bg-indigo-600 text-white rounded-tr-none"
                  }`}>
                    <div className="flex items-center justify-between gap-3 text-[10px] opacity-75">
                      <span className="font-semibold capitalize">{m.sender}</span>
                      <span>{m.timestamp ? new Date(m.timestamp).toLocaleTimeString() : "Just now"}</span>
                    </div>
                    <p className="whitespace-pre-wrap leading-relaxed">{m.content}</p>
                  </div>
                </div>
              );
            })
          ) : (
            <p className="text-xs text-neutral-400 text-center py-4">No messages yet.</p>
          )}
        </div>
      </div>

      {/* 4. Cryptographic Audit Ledger */}
      <AuditLedger logs={ticket.audit_logs || []} />
    </div>
  );
}
