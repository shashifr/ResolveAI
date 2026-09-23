"use client";

import React, { useState, useEffect, useRef, useCallback } from "react";
import Header from "../components/dashboard/Header";
import MetricsBar from "../components/dashboard/MetricsBar";
import TicketList from "../components/dashboard/TicketList";
import TicketDetail from "../components/dashboard/TicketDetail";
import EmailSimulatorModal from "../components/simulators/EmailSimulatorModal";
import ChatSimulatorWidget from "../components/simulators/ChatSimulatorWidget";
import { 
  Ticket, 
  TicketDetails, 
  Metrics, 
  TabFilter, 
  EmailSimulationForm 
} from "../types";
import { ChevronLeft } from "lucide-react";

const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL || "http://localhost:8000";

const API_HEADERS = {
  "Content-Type": "application/json",
  "Authorization": "Bearer resolveai-demo-token"
};

const STATIC_TIMESTAMP = "2026-09-23T12:00:00.000Z";

const INITIAL_DEMO_STORE: Record<string, TicketDetails> = {
  "TKT-1001": {
    id: "TKT-1001",
    customer_email: "alice.vance@gmail.com",
    customer_name: "Alice Vance",
    channel: "email",
    status: "Escalated",
    subject: "Refund Request for Order #1001",
    confidence_score: 0.60,
    token_cost: 0.0177,
    updated_at: STATIC_TIMESTAMP,
    latest_message: "Hi, I received my headphones ORD-1001 but they are broken. I would like a full refund of $120.",
    drafted_reply: "Hi Alice Vance, I have drafted a refund of $120.0 for your order ORD-1001. Since this is above our automatic refund threshold of $50, I've requested a support agent to approve this refund immediately.",
    drafted_actions: [
      { action: "issue_refund", order_id: "ORD-1001", amount: 120.0, reason: "Customer request (high-value)" }
    ],
    explanation: "Refund amount $120.0 is above the automated $50 threshold. Requires human confirmation.",
    messages: [
      {
        id: 1,
        sender: "customer",
        content: "Hi, I received my headphones ORD-1001 but they are broken. I would like a full refund of $120.",
        timestamp: STATIC_TIMESTAMP
      }
    ],
    audit_logs: [
      { node: "intake", input_summary: "Inbound email logged", model_used: "System", tokens: 50, cost: 0.0001, confidence: 1.0, action_taken: "Registered thread", prev_hash: "00000000000000000000000000000000", hash: "a1b2c3d4e5f67890123456789abcdef0", timestamp: STATIC_TIMESTAMP },
      { node: "classifier", input_summary: "Intent: refund_request", model_used: "Gemini 1.5 Flash", tokens: 180, cost: 0.0002, confidence: 0.94, action_taken: "Classified refund request", prev_hash: "a1b2c3d4e5f67890123456789abcdef0", hash: "b2c3d4e5f67890123456789abcdef012", timestamp: STATIC_TIMESTAMP },
      { node: "context_retriever", input_summary: "CRM Order ORD-1001 found", model_used: "SQLAlchemy", tokens: 100, cost: 0.0, confidence: 1.0, action_taken: "Fetched customer profile", prev_hash: "b2c3d4e5f67890123456789abcdef012", hash: "c3d4e5f67890123456789abcdef01234", timestamp: STATIC_TIMESTAMP },
      { node: "resolution_agent", input_summary: "Proposed $120 refund", model_used: "Gemini 1.5 Pro", tokens: 520, cost: 0.015, confidence: 0.60, action_taken: "Drafted response & proposed refund", prev_hash: "c3d4e5f67890123456789abcdef01234", hash: "d4e5f67890123456789abcdef0123456", timestamp: STATIC_TIMESTAMP },
      { node: "confidence_gate", input_summary: "Confidence 0.60 < 0.85 threshold", model_used: "Gatekeeper", tokens: 10, cost: 0.0, confidence: 0.60, action_taken: "Escalated to Human Review Console", prev_hash: "d4e5f67890123456789abcdef0123456", hash: "e5f67890123456789abcdef012345678", timestamp: STATIC_TIMESTAMP }
    ]
  },
  "TKT-1002": {
    id: "TKT-1002",
    customer_email: "alice.vance@gmail.com",
    customer_name: "Alice Vance",
    channel: "email",
    status: "Resolved",
    subject: "Return Policy Inquiry",
    confidence_score: 0.95,
    token_cost: 0.0008,
    updated_at: STATIC_TIMESTAMP,
    latest_message: "Hi, can you tell me what your return policy is? How long do I have to return my items?",
    drafted_reply: "Hi Alice Vance, We offer a 30-day return policy for all unused products in their original packaging. Refunds are processed back to the original payment method within 5-7 business days of receiving the returned item.",
    drafted_actions: [],
    explanation: "Resolved via Knowledge Base article: 'What is your return policy?'.",
    messages: [
      {
        id: 1,
        sender: "customer",
        content: "Hi, can you tell me what your return policy is? How long do I have to return my items?",
        timestamp: STATIC_TIMESTAMP
      },
      {
        id: 2,
        sender: "agent",
        content: "Hi Alice Vance,\n\nHere is what I found regarding your question:\n\nWe offer a 30-day return policy for all unused products in their original packaging. Refunds are processed back to the original payment method within 5-7 business days of receiving the returned item.",
        timestamp: STATIC_TIMESTAMP
      }
    ],
    audit_logs: [
      { node: "intake", input_summary: "Inbound FAQ email", model_used: "System", tokens: 40, cost: 0.0001, confidence: 1.0, action_taken: "Registered thread", prev_hash: "00000000000000000000000000000000", hash: "11111111111111111111111111111111", timestamp: STATIC_TIMESTAMP },
      { node: "classifier", input_summary: "Intent: general_faq", model_used: "Gemini 1.5 Flash", tokens: 120, cost: 0.0001, confidence: 0.95, action_taken: "Classified general FAQ", prev_hash: "11111111111111111111111111111111", hash: "22222222222222222222222222222222", timestamp: STATIC_TIMESTAMP },
      { node: "resolution_agent", input_summary: "KB Match: Return Policy", model_used: "Gemini 1.5 Flash", tokens: 280, cost: 0.0006, confidence: 0.95, action_taken: "Autonomous resolution sent", prev_hash: "22222222222222222222222222222222", hash: "33333333333333333333333333333333", timestamp: STATIC_TIMESTAMP }
    ]
  }
};

export default function Home() {
  const [tickets, setTickets] = useState<Ticket[]>([]);
  const [selectedTicketId, setSelectedTicketId] = useState<string | null>(null);
  const [selectedTicketDetails, setSelectedTicketDetails] = useState<TicketDetails | null>(null);
  const [metrics, setMetrics] = useState<Metrics>({
    total_tickets: 0,
    resolved_count: 0,
    autonomous_count: 0,
    autonomy_rate: 0,
    total_actual_cost: 0,
    baseline_cost: 0,
    savings: 0,
    avg_resp_time_sec: 1.2
  });

  const [activeTab, setActiveTab] = useState<TabFilter>("all");
  const [searchQuery, setSearchQuery] = useState("");
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [isBackendConnected, setIsBackendConnected] = useState(true);
  const [actionLoading, setActionLoading] = useState(false);

  // Modals & Simulators
  const [isEmailSimOpen, setIsEmailSimOpen] = useState(false);
  const [emailLoading, setEmailLoading] = useState(false);

  const [isChatWidgetOpen, setIsChatWidgetOpen] = useState(false);
  const [chatEmail, setChatEmail] = useState("charlie.green@yahoo.com");
  const [chatTicketId, setChatTicketId] = useState<string | null>(null);
  const [chatMessages, setChatMessages] = useState<Array<{ sender: "customer" | "agent" | "system"; content: string }>>([
    { sender: "system", content: "Connected to ResolveAI. How can we help you today?" }
  ]);
  const [chatStatus, setChatStatus] = useState<"idle" | "typing" | "escalated">("idle");

  // Mobile View Toggle
  const [mobileView, setMobileView] = useState<"list" | "detail">("list");

  // Local demo fallback store (guarantees 100% uptime with zero uncaught errors)
  const demoStoreRef = useRef<Record<string, TicketDetails>>(INITIAL_DEMO_STORE);

  // Fetch tickets and metrics
  const fetchData = useCallback(async () => {
    try {
      const ticketsRes = await fetch(`${BACKEND_URL}/api/tickets`, { headers: API_HEADERS });
      if (!ticketsRes.ok) throw new Error("Backend tickets unavailable");
      const ticketsData: Ticket[] = await ticketsRes.json();
      setTickets(ticketsData);
      setIsBackendConnected(true);

      // Auto-select first ticket if none selected
      setSelectedTicketId(prev => prev || (ticketsData.length > 0 ? ticketsData[0].id : null));

      const metricsRes = await fetch(`${BACKEND_URL}/api/metrics`, { headers: API_HEADERS });
      if (metricsRes.ok) {
        const metricsData = await metricsRes.json();
        setMetrics(metricsData);
      }
    } catch {
      // Graceful fallback to local demo store
      setIsBackendConnected(false);
      const allStoreDetails = Object.values(demoStoreRef.current);
      const summaries: Ticket[] = allStoreDetails.map(d => ({
        id: d.id,
        customer_email: d.customer_email,
        customer_name: d.customer_name,
        channel: d.channel,
        status: d.status,
        subject: d.subject,
        confidence_score: d.confidence_score,
        token_cost: d.token_cost,
        updated_at: d.updated_at,
        latest_message: d.messages && d.messages.length > 0 ? d.messages[d.messages.length - 1].content : ""
      })).sort((a, b) => new Date(b.updated_at).getTime() - new Date(a.updated_at).getTime());

      setTickets(summaries);
      setSelectedTicketId(prev => prev || (summaries.length > 0 ? summaries[0].id : null));

      const total = summaries.length;
      const resolved = summaries.filter(t => t.status === "Resolved").length;
      const auto = summaries.filter(t => t.status === "Resolved" && t.confidence_score >= 0.8).length;
      const rate = total > 0 ? Math.round((auto / total) * 100) : 67;
      const actualCost = summaries.reduce((sum, t) => sum + (t.token_cost || 0), 0);
      const baseline = total * 0.075;

      setMetrics({
        total_tickets: total,
        resolved_count: resolved,
        autonomous_count: auto,
        autonomy_rate: rate,
        total_actual_cost: parseFloat(actualCost.toFixed(5)),
        baseline_cost: parseFloat(baseline.toFixed(5)),
        savings: parseFloat(Math.max(0, baseline - actualCost).toFixed(5)),
        avg_resp_time_sec: 1.2
      });
    }
  }, []);

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 4000);
    return () => clearInterval(interval);
  }, [fetchData]);

  // Fetch ticket details when selected
  useEffect(() => {
    if (!selectedTicketId) {
      setSelectedTicketDetails(null);
      return;
    }

    const fetchDetails = async () => {
      try {
        const res = await fetch(`${BACKEND_URL}/api/tickets/${selectedTicketId}`, { headers: API_HEADERS });
        if (res.ok) {
          const data = await res.json();
          setSelectedTicketDetails(data);
        } else {
          throw new Error("Details fetch failed");
        }
      } catch {
        const local = demoStoreRef.current[selectedTicketId];
        if (local) {
          setSelectedTicketDetails(local);
        }
      }
    };

    fetchDetails();
  }, [selectedTicketId]);

  const handleManualRefresh = async () => {
    setIsRefreshing(true);
    await fetchData();
    setTimeout(() => setIsRefreshing(false), 500);
  };

  // Human Review Actions: Approve / Edit / Reject
  const handleTicketAction = async (action: "approve" | "reject" | "edit", editedReply?: string) => {
    if (!selectedTicketId) return;
    setActionLoading(true);

    try {
      const res = await fetch(`${BACKEND_URL}/api/tickets/${selectedTicketId}/action`, {
        method: "POST",
        headers: API_HEADERS,
        body: JSON.stringify({
          action,
          edited_reply: action === "edit" ? editedReply : null
        })
      });

      if (res.ok) {
        await fetchData();
        // Re-fetch details
        const detRes = await fetch(`${BACKEND_URL}/api/tickets/${selectedTicketId}`, { headers: API_HEADERS });
        if (detRes.ok) {
          setSelectedTicketDetails(await detRes.json());
        }
        return;
      }
      throw new Error("Action failed");
    } catch {
      // Local fallback execution
      const target = demoStoreRef.current[selectedTicketId];
      if (target) {
        target.status = action === "reject" ? "Open" : "Resolved";
        const reply = action === "edit" ? editedReply! : target.drafted_reply;
        target.messages.push({
          id: Date.now(),
          sender: "agent",
          content: reply || "Human agent verified and executed order action.",
          timestamp: new Date().toISOString()
        });
        target.audit_logs.push({
          node: "human_console",
          input_summary: `Human action: ${action.toUpperCase()}`,
          model_used: "Human Supervisor",
          tokens: 0,
          cost: 0.0,
          confidence: 1.0,
          action_taken: `Executed ${action.toUpperCase()} action`,
          prev_hash: target.audit_logs[target.audit_logs.length - 1].hash,
          hash: Math.random().toString(36).substring(2) + Math.random().toString(36).substring(2),
          timestamp: new Date().toISOString()
        });
        setSelectedTicketDetails({ ...target });
        await fetchData();
      }
    } finally {
      setActionLoading(false);
    }
  };

  // Email simulation submit handler
  const handleSimulateEmail = async (form: EmailSimulationForm) => {
    setEmailLoading(true);
    try {
      const res = await fetch(`${BACKEND_URL}/api/simulate/email`, {
        method: "POST",
        headers: API_HEADERS,
        body: JSON.stringify({
          sender_email: form.sender,
          sender_name: form.sender.split("@")[0].split(".").map(s => s.charAt(0).toUpperCase() + s.slice(1)).join(" "),
          subject: form.subject,
          body: form.body
        })
      });

      if (res.ok) {
        const data = await res.json();
        setIsEmailSimOpen(false);
        setSelectedTicketId(data.ticket_id);
        setMobileView("detail");
        await fetchData();
        return;
      }
      throw new Error("Email simulation offline");
    } catch {
      // Local fallback simulation
      const tid = `TKT-${Math.random().toString(36).substring(2, 8).toUpperCase()}`;
      const isFAQ = form.subject.toLowerCase().includes("return") || form.body.toLowerCase().includes("policy");
      const conf = isFAQ ? 0.95 : 0.60;
      const status = isFAQ ? "Resolved" : "Escalated";

      const newTicket: TicketDetails = {
        id: tid,
        customer_email: form.sender,
        customer_name: form.sender.split("@")[0].split(".").map(s => s.charAt(0).toUpperCase() + s.slice(1)).join(" "),
        channel: "email",
        status: status,
        subject: form.subject,
        confidence_score: conf,
        token_cost: 0.0015,
        updated_at: new Date().toISOString(),
        latest_message: form.body,
        drafted_reply: isFAQ 
          ? "We offer a 30-day return policy for all products in original packaging."
          : `I have drafted a refund for your request. Since it exceeds $50, our team will review and approve.`,
        drafted_actions: isFAQ ? [] : [{ action: "issue_refund", amount: 120.0, order_id: "ORD-1001" }],
        explanation: isFAQ ? "Resolved via FAQ Knowledge Base" : "Exceeds $50 threshold. Escalated to human queue.",
        messages: [
          { id: 1, sender: "customer", content: form.body, timestamp: new Date().toISOString() },
          ...(isFAQ ? [{ id: 2, sender: "agent" as const, content: "We offer a 30-day return policy for all products in original packaging.", timestamp: new Date().toISOString() }] : [])
        ],
        audit_logs: [
          { node: "intake", input_summary: form.subject, model_used: "System", tokens: 60, cost: 0.0001, confidence: 1.0, action_taken: "Email registered", prev_hash: "00000000000000000000000000000000", hash: "aa11bb22cc33dd44ee55ff6677889900", timestamp: new Date().toISOString() },
          { node: "classifier", input_summary: "Classification", model_used: "Gemini 1.5 Flash", tokens: 120, cost: 0.0001, confidence: conf, action_taken: `Classified status: ${status}`, prev_hash: "aa11bb22cc33dd44ee55ff6677889900", hash: "bb22cc33dd44ee55ff6677889900aa11", timestamp: new Date().toISOString() }
        ]
      };

      demoStoreRef.current[tid] = newTicket;
      setIsEmailSimOpen(false);
      setSelectedTicketId(tid);
      setMobileView("detail");
      await fetchData();
    } finally {
      setEmailLoading(false);
    }
  };

  // Live chat message send handler
  const handleSendChatMessage = async (email: string, text: string) => {
    setChatMessages(prev => [...prev, { sender: "customer", content: text }]);
    setChatStatus("typing");

    try {
      const res = await fetch(`${BACKEND_URL}/api/simulate/chat`, {
        method: "POST",
        headers: API_HEADERS,
        body: JSON.stringify({
          customer_email: email,
          message: text,
          ticket_id: chatTicketId
        })
      });

      if (res.ok) {
        const data = await res.json();
        setChatTicketId(data.ticket_id);
        setSelectedTicketId(data.ticket_id);
        fetchData();

        if (data.is_auto_resolved) {
          setChatStatus("idle");
          setChatMessages(prev => [...prev, { sender: "agent", content: data.reply }]);
        } else {
          setChatStatus("escalated");
          setChatMessages(prev => [...prev, { 
            sender: "system", 
            content: "Your query has been escalated to a live agent for verification. Review pending in the Console." 
          }]);
        }
        return;
      }
      throw new Error("Chat offline");
    } catch {
      setTimeout(() => {
        setChatStatus("idle");
        setChatMessages(prev => [
          ...prev, 
          { sender: "agent", content: "Thank you for contacting support! I've logged your request in the Console." }
        ]);
      }, 1000);
    }
  };

  // Filter tickets by tab and search
  const filteredTickets = tickets.filter(t => {
    const matchesSearch = 
      t.id.toLowerCase().includes(searchQuery.toLowerCase()) || 
      t.customer_email.toLowerCase().includes(searchQuery.toLowerCase()) || 
      (t.subject && t.subject.toLowerCase().includes(searchQuery.toLowerCase())) ||
      (t.latest_message && t.latest_message.toLowerCase().includes(searchQuery.toLowerCase()));

    if (!matchesSearch) return false;
    if (activeTab === "all") return true;
    return t.status.toLowerCase() === activeTab.toLowerCase();
  });

  return (
    <div className="flex flex-col min-h-screen bg-neutral-50 dark:bg-neutral-950 text-neutral-900 dark:text-neutral-100 font-sans transition-colors duration-200">
      {/* 1. Header Bar */}
      <Header
        onOpenEmailSim={() => setIsEmailSimOpen(true)}
        onOpenChatSim={() => setIsChatWidgetOpen(true)}
        onRefresh={handleManualRefresh}
        isRefreshing={isRefreshing}
        isBackendConnected={isBackendConnected}
      />

      {/* 2. Top Executive Metrics Bar */}
      <MetricsBar metrics={metrics} />

      {/* 3. Main Split View: Ticket Explorer (Left) & Ticket Console (Right) */}
      <main className="flex-1 flex flex-col lg:flex-row overflow-hidden max-h-[calc(100vh-140px)]">
        {/* Mobile View Back Button */}
        {mobileView === "detail" && (
          <div className="lg:hidden p-3 border-b border-neutral-200 dark:border-neutral-800 bg-white dark:bg-neutral-900">
            <button
              onClick={() => setMobileView("list")}
              className="flex items-center gap-1.5 text-xs font-semibold text-indigo-600 dark:text-indigo-400"
            >
              <ChevronLeft className="w-4 h-4" />
              Back to Ticket List
            </button>
          </div>
        )}

        {/* Left Side: Ticket Explorer */}
        <div className={`w-full lg:w-96 shrink-0 h-full overflow-hidden ${
          mobileView === "detail" ? "hidden lg:block" : "block"
        }`}>
          <TicketList
            tickets={filteredTickets}
            selectedTicketId={selectedTicketId}
            onSelectTicket={(id) => {
              setSelectedTicketId(id);
              setMobileView("detail");
            }}
            searchQuery={searchQuery}
            onSearchChange={setSearchQuery}
            activeTab={activeTab}
            onTabChange={setActiveTab}
          />
        </div>

        {/* Right Side: Ticket Details & Human Review */}
        <div className={`flex-1 h-full overflow-y-auto ${
          mobileView === "list" ? "hidden lg:flex" : "flex"
        }`}>
          <TicketDetail
            ticket={selectedTicketDetails}
            onApprove={() => handleTicketAction("approve")}
            onReject={() => handleTicketAction("reject")}
            onEdit={(text) => handleTicketAction("edit", text)}
            actionLoading={actionLoading}
          />
        </div>
      </main>

      {/* Email Simulation Slide-Over Modal */}
      <EmailSimulatorModal
        isOpen={isEmailSimOpen}
        onClose={() => setIsEmailSimOpen(false)}
        onSubmit={handleSimulateEmail}
        isLoading={emailLoading}
      />

      {/* Customer Live Chat Simulator Floating Widget */}
      <ChatSimulatorWidget
        isOpen={isChatWidgetOpen}
        onClose={() => setIsChatWidgetOpen(false)}
        onSendMessage={handleSendChatMessage}
        messages={chatMessages}
        status={chatStatus}
        customerEmail={chatEmail}
        onEmailChange={setChatEmail}
      />
    </div>
  );
}
