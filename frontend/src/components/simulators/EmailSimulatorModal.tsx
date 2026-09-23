"use client";

import React, { useState, useEffect } from "react";
import { 
  Mail, 
  X, 
  Send, 
  Sparkles, 
  CheckCircle2, 
  AlertTriangle,
  RotateCcw
} from "lucide-react";
import { EmailSimulationForm } from "../../types";

interface EmailSimulatorModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (form: EmailSimulationForm) => void;
  isLoading: boolean;
}

const PRESET_SCENARIOS = [
  {
    name: "High Refund ($120)",
    desc: "Should escalate to human review (> $50)",
    sender: "alice.vance@gmail.com",
    subject: "Refund Request for Order #1001",
    body: "Hi support, I received my wireless headphones (Order ORD-1001) yesterday but the left ear volume is broken. Can I get a full refund of $120 to my card?"
  },
  {
    name: "Return Policy FAQ",
    desc: "Should auto-resolve using Knowledge Base",
    sender: "alice.vance@gmail.com",
    subject: "Return Policy Question",
    body: "Hi! Can you tell me what your return policy is? How long do I have to return an item?"
  },
  {
    name: "Delayed Shipping",
    desc: "Order delayed in transit",
    sender: "bob.miller@outlook.com",
    subject: "Where is order ORD-1002?",
    body: "Hello, I placed order ORD-1002 5 days ago and the mouse still hasn't arrived. The tracking number is TRK-112233445. Can you check what is happening?"
  },
  {
    name: "Cancel Subscription",
    desc: "Strict escalation for user retention",
    sender: "alice.vance@gmail.com",
    subject: "Cancel my Cloud Pro Subscription",
    body: "I want to cancel my active subscription SUB-2001. Please stop charging my credit card."
  }
];

export default function EmailSimulatorModal({
  isOpen,
  onClose,
  onSubmit,
  isLoading
}: EmailSimulatorModalProps) {
  const [form, setForm] = useState<EmailSimulationForm>({
    sender: PRESET_SCENARIOS[0].sender,
    subject: PRESET_SCENARIOS[0].subject,
    body: PRESET_SCENARIOS[0].body
  });

  // ESC key listener to close
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === "Escape" && isOpen) {
        onClose();
      }
    };
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  const handleApplyPreset = (preset: typeof PRESET_SCENARIOS[0]) => {
    setForm({
      sender: preset.sender,
      subject: preset.subject,
      body: preset.body
    });
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSubmit(form);
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-neutral-950/60 backdrop-blur-sm transition-all duration-200">
      <div className="relative w-full max-w-xl rounded-2xl border border-neutral-200 dark:border-neutral-800 bg-white dark:bg-neutral-900 shadow-2xl overflow-hidden transition-all">
        {/* Header */}
        <div className="flex items-center justify-between px-5 py-4 border-b border-neutral-100 dark:border-neutral-800">
          <div className="flex items-center gap-2.5">
            <div className="p-2 rounded-xl bg-indigo-50 dark:bg-indigo-950/60 text-indigo-600 dark:text-indigo-400">
              <Mail className="w-5 h-5" />
            </div>
            <div>
              <h3 className="text-base font-bold text-neutral-900 dark:text-white">
                Simulate Inbound Customer Email
              </h3>
              <p className="text-xs text-neutral-500">
                Test LangGraph intent classification, MoE routing, and confidence gating
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-1.5 rounded-lg text-neutral-400 hover:text-neutral-700 dark:hover:text-neutral-200 hover:bg-neutral-100 dark:hover:bg-neutral-800 transition-all cursor-pointer"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Preset Scenarios Pill Bar */}
        <div className="p-4 bg-neutral-50/50 dark:bg-neutral-950/40 border-b border-neutral-100 dark:border-neutral-800/60 space-y-2">
          <span className="text-[11px] font-semibold text-neutral-500 uppercase tracking-wider block">
            Quick Test Scenarios:
          </span>
          <div className="grid grid-cols-2 gap-2">
            {PRESET_SCENARIOS.map((p, idx) => (
              <button
                key={idx}
                type="button"
                onClick={() => handleApplyPreset(p)}
                className="text-left p-2.5 rounded-lg border border-neutral-200/80 dark:border-neutral-800 bg-white dark:bg-neutral-900 hover:border-indigo-400 dark:hover:border-indigo-600 transition-all cursor-pointer group"
              >
                <span className="text-xs font-bold text-neutral-900 dark:text-neutral-100 group-hover:text-indigo-600 dark:group-hover:text-indigo-400 block">
                  {p.name}
                </span>
                <span className="text-[10px] text-neutral-400 line-clamp-1">
                  {p.desc}
                </span>
              </button>
            ))}
          </div>
        </div>

        {/* Compose Form */}
        <form onSubmit={handleSubmit} className="p-5 space-y-4">
          <div className="space-y-1">
            <label className="text-xs font-semibold text-neutral-700 dark:text-neutral-300">
              Sender Email
            </label>
            <input
              type="email"
              required
              value={form.sender}
              onChange={(e) => setForm({ ...form, sender: e.target.value })}
              className="w-full px-3 py-2 text-xs sm:text-sm rounded-lg border border-neutral-300 dark:border-neutral-700 bg-neutral-50 dark:bg-neutral-950 text-neutral-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-indigo-500/30 focus:border-indigo-500"
            />
          </div>

          <div className="space-y-1">
            <label className="text-xs font-semibold text-neutral-700 dark:text-neutral-300">
              Subject Line
            </label>
            <input
              type="text"
              required
              value={form.subject}
              onChange={(e) => setForm({ ...form, subject: e.target.value })}
              className="w-full px-3 py-2 text-xs sm:text-sm rounded-lg border border-neutral-300 dark:border-neutral-700 bg-neutral-50 dark:bg-neutral-950 text-neutral-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-indigo-500/30 focus:border-indigo-500"
            />
          </div>

          <div className="space-y-1">
            <label className="text-xs font-semibold text-neutral-700 dark:text-neutral-300">
              Email Body
            </label>
            <textarea
              rows={4}
              required
              value={form.body}
              onChange={(e) => setForm({ ...form, body: e.target.value })}
              className="w-full p-3 text-xs sm:text-sm rounded-lg border border-neutral-300 dark:border-neutral-700 bg-neutral-50 dark:bg-neutral-950 text-neutral-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-indigo-500/30 focus:border-indigo-500 leading-relaxed"
            />
          </div>

          {/* Footer Actions */}
          <div className="flex items-center justify-end gap-2.5 pt-2">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 rounded-lg text-xs font-semibold text-neutral-600 dark:text-neutral-400 hover:bg-neutral-100 dark:hover:bg-neutral-800 transition-all cursor-pointer"
            >
              Cancel
            </button>

            <button
              type="submit"
              disabled={isLoading}
              className="flex items-center gap-1.5 px-4 py-2 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-bold shadow-sm shadow-indigo-600/20 transition-all duration-150 cursor-pointer active:scale-95 disabled:opacity-50"
            >
              <Send className="w-3.5 h-3.5" />
              {isLoading ? "Running Pipeline..." : "Dispatch Simulated Email"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
