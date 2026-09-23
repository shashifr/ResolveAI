"use client";

import React, { useState, useRef, useEffect } from "react";
import { 
  MessageSquare, 
  X, 
  Send, 
  Bot, 
  User, 
  Sparkles, 
  AlertCircle,
  Minimize2
} from "lucide-react";

interface ChatSimulatorWidgetProps {
  isOpen: boolean;
  onClose: () => void;
  onSendMessage: (email: string, message: string) => Promise<void>;
  messages: Array<{ sender: "customer" | "agent" | "system"; content: string }>;
  status: "idle" | "typing" | "escalated";
  customerEmail: string;
  onEmailChange: (e: string) => void;
}

export default function ChatSimulatorWidget({
  isOpen,
  onClose,
  onSendMessage,
  messages,
  status,
  customerEmail,
  onEmailChange
}: ChatSimulatorWidgetProps) {
  const [inputText, setInputText] = useState("");
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (isOpen) {
      messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    }
  }, [messages, isOpen, status]);

  if (!isOpen) return null;

  const handleSend = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!inputText.trim() || status === "typing") return;
    const msg = inputText.trim();
    setInputText("");
    await onSendMessage(customerEmail, msg);
  };

  return (
    <div className="fixed bottom-4 right-4 z-50 w-full sm:w-96 rounded-2xl border border-neutral-200 dark:border-neutral-800 bg-white dark:bg-neutral-900 shadow-2xl overflow-hidden flex flex-col h-[520px] transition-all duration-200">
      {/* Header */}
      <div className="flex items-center justify-between px-4 py-3 bg-gradient-to-r from-indigo-600 to-violet-600 text-white shadow-xs">
        <div className="flex items-center gap-2.5">
          <div className="relative flex items-center justify-center w-8 h-8 rounded-full bg-white/20">
            <Bot className="w-4 h-4 text-white" />
            <span className="absolute bottom-0 right-0 w-2 h-2 rounded-full bg-emerald-400 ring-2 ring-indigo-600" />
          </div>
          <div>
            <h4 className="text-xs font-bold leading-tight">ResolveAI Assistant</h4>
            <span className="text-[10px] text-indigo-100 flex items-center gap-1">
              <span className="w-1 h-1 rounded-full bg-emerald-300" />
              Live Customer Widget
            </span>
          </div>
        </div>

        <button
          onClick={onClose}
          className="p-1 rounded-lg hover:bg-white/20 text-white/80 hover:text-white transition-all cursor-pointer"
          title="Minimize Chat"
        >
          <Minimize2 className="w-4 h-4" />
        </button>
      </div>

      {/* Customer Email Header Strip */}
      <div className="px-3.5 py-2 bg-neutral-100/70 dark:bg-neutral-950/70 border-b border-neutral-200/80 dark:border-neutral-800/80 flex items-center justify-between text-xs">
        <span className="text-[11px] text-neutral-500">Customer:</span>
        <input
          type="email"
          value={customerEmail}
          onChange={(e) => onEmailChange(e.target.value)}
          className="text-right text-xs font-semibold text-neutral-800 dark:text-neutral-200 bg-transparent border-none focus:outline-none focus:underline"
          title="Click to change customer email"
        />
      </div>

      {/* Message List */}
      <div className="flex-1 p-4 overflow-y-auto space-y-3 bg-neutral-50/40 dark:bg-neutral-950/40">
        {messages.map((m, idx) => {
          if (m.sender === "system") {
            return (
              <div key={idx} className="flex items-center justify-center my-2">
                <span className="text-[10px] text-amber-700 dark:text-amber-400 bg-amber-50 dark:bg-amber-950/60 border border-amber-200 dark:border-amber-800/60 px-2.5 py-1 rounded-full flex items-center gap-1.5 font-medium text-center max-w-[90%]">
                  <AlertCircle className="w-3 h-3 shrink-0" />
                  {m.content}
                </span>
              </div>
            );
          }

          const isCustomer = m.sender === "customer";
          return (
            <div
              key={idx}
              className={`flex gap-2 max-w-[85%] ${isCustomer ? "ml-auto flex-row-reverse" : "mr-auto"}`}
            >
              <div className={`w-6 h-6 rounded-full flex items-center justify-center shrink-0 text-[10px] font-bold ${
                isCustomer ? "bg-neutral-300 dark:bg-neutral-700 text-neutral-800 dark:text-white" : "bg-indigo-600 text-white"
              }`}>
                {isCustomer ? <User className="w-3 h-3" /> : <Sparkles className="w-3 h-3" />}
              </div>

              <div className={`p-2.5 rounded-2xl text-xs leading-relaxed ${
                isCustomer
                  ? "bg-indigo-600 text-white rounded-tr-none"
                  : "bg-white dark:bg-neutral-800 text-neutral-900 dark:text-neutral-100 border border-neutral-200/80 dark:border-neutral-700/60 rounded-tl-none shadow-xs"
              }`}>
                {m.content}
              </div>
            </div>
          );
        })}

        {/* Typing indicator */}
        {status === "typing" && (
          <div className="flex gap-2 mr-auto max-w-[85%] items-center">
            <div className="w-6 h-6 rounded-full bg-indigo-600 text-white flex items-center justify-center shrink-0 text-[10px]">
              <Sparkles className="w-3 h-3 animate-pulse" />
            </div>
            <div className="p-3 rounded-2xl bg-white dark:bg-neutral-800 border border-neutral-200/80 dark:border-neutral-700/60 rounded-tl-none shadow-xs flex items-center gap-1">
              <span className="w-1.5 h-1.5 rounded-full bg-indigo-500 animate-bounce" style={{ animationDelay: "0ms" }} />
              <span className="w-1.5 h-1.5 rounded-full bg-indigo-500 animate-bounce" style={{ animationDelay: "150ms" }} />
              <span className="w-1.5 h-1.5 rounded-full bg-indigo-500 animate-bounce" style={{ animationDelay: "300ms" }} />
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input bar */}
      <form onSubmit={handleSend} className="p-3 border-t border-neutral-200 dark:border-neutral-800 bg-white dark:bg-neutral-900 flex items-center gap-2">
        <input
          type="text"
          placeholder="Type your message..."
          value={inputText}
          onChange={(e) => setInputText(e.target.value)}
          disabled={status === "typing"}
          className="flex-1 px-3 py-2 text-xs rounded-lg border border-neutral-300 dark:border-neutral-700 bg-neutral-50 dark:bg-neutral-950 text-neutral-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-indigo-500/30"
        />
        <button
          type="submit"
          disabled={!inputText.trim() || status === "typing"}
          className="p-2 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white disabled:opacity-40 transition-all cursor-pointer"
        >
          <Send className="w-4 h-4" />
        </button>
      </form>
    </div>
  );
}
