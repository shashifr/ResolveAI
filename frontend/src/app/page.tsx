"use client";

import React, { useState, useEffect, useRef } from "react";
import dynamic from "next/dynamic";
import SplitText from "../components/ui/SplitText";
import { 
  Inbox, 
  Mail, 
  MessageSquare, 
  Phone, 
  ShieldCheck, 
  ArrowRight, 
  Sparkles, 
  TrendingDown, 
  Clock, 
  AlertTriangle, 
  CheckCircle, 
  XCircle, 
  Check, 
  Edit3, 
  X, 
  Send, 
  Search, 
  RotateCw, 
  User, 
  Building, 
  BookOpen, 
  Cpu, 
  Hash, 
  Play, 
  Square,
  ChevronRight,
  ChevronLeft,
  Database
} from "lucide-react";

// Types
interface Ticket {
  id: string;
  customer_email: string;
  customer_name: string;
  channel: "email" | "chat" | "voice";
  status: "Open" | "Escalated" | "Resolved";
  subject: string;
  confidence_score: number;
  token_cost: number;
  updated_at: string;
  latest_message: string;
}

interface Message {
  sender: "customer" | "agent" | "system";
  content: string;
  timestamp: string;
}

interface AuditLog {
  node: string;
  input_summary: string;
  model_used: string;
  tokens: number;
  cost: number;
  confidence: number;
  action_taken: string;
  prev_hash: string;
  hash: string;
  timestamp: string;
}

interface TicketDetails extends Ticket {
  messages: Message[];
  audit_logs: AuditLog[];
  drafted_actions: any[];
  drafted_reply: string;
  explanation: string;
}

interface Metrics {
  total_tickets: number;
  resolved_count: number;
  autonomous_count: number;
  autonomy_rate: number;
  total_actual_cost: number;
  baseline_cost: number;
  savings: number;
  avg_resp_time_sec: number;
}

function DashboardComponent() {
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
    avg_resp_time_sec: 0
  });

  const [activeTab, setActiveTab] = useState<"all" | "open" | "escalated" | "resolved">("all");
  const [searchQuery, setSearchQuery] = useState("");
  const [loading, setLoading] = useState(false);
  const [actionLoading, setActionLoading] = useState(false);

  // Intro splash overlay states
  const [showIntro, setShowIntro] = useState(true);
  const [fadeIntro, setFadeIntro] = useState(false);

  // Email simulation states
  const [isEmailSimOpen, setIsEmailSimOpen] = useState(false);
  const [emailForm, setEmailForm] = useState({
    sender: "alice.vance@gmail.com",
    subject: "Help needed with my Order #1001",
    body: "Hi support, I received my wireless headphones (Order ORD-1001) yesterday but the volume is extremely low in the left ear. Can I get a refund of $120 to my card?"
  });
  const [simulatingStep, setSimulatingStep] = useState<string | null>(null);

  // Voice simulation states
  const [isVoiceSimOpen, setIsVoiceSimOpen] = useState(false);
  const [voiceScenario, setVoiceScenario] = useState("refund_high");
  const [voiceStatus, setVoiceStatus] = useState<"idle" | "playing" | "submitting">("idle");
  const [voiceTranscript, setVoiceTranscript] = useState<string[]>([]);
  const [voicePlaybackIndex, setPlaybackIndex] = useState(0);
  const voiceTimerRef = useRef<NodeJS.Timeout | null>(null);

  // Chat simulation states
  const [isChatWidgetOpen, setIsChatWidgetOpen] = useState(false);
  const [isChatConnected, setIsChatConnected] = useState(false);
  const [chatEmail, setChatEmail] = useState("charlie.green@yahoo.com");
  const [chatTicketId, setChatTicketId] = useState<string | null>(null);
  const [chatMessages, setChatMessages] = useState<Array<{sender: 'customer' | 'agent' | 'system', content: string}>>([
    { sender: 'system', content: 'Enter your email to start chatting with ResolveAI.' }
  ]);
  const [chatInput, setChatInput] = useState("");
  const [chatStatus, setChatStatus] = useState<"idle" | "connecting" | "typing" | "escalated">("idle");

  // Edit draft states
  const [isEditingReply, setIsEditingReply] = useState(false);
  const [editedReplyText, setEditedReplyText] = useState("");

  // Audit trace detailed view
  const [selectedNodeLog, setSelectedNodeLog] = useState<AuditLog | null>(null);

  // Mobile view state ('list' | 'details')
  const [activeMobileView, setActiveMobileView] = useState<"list" | "details">("list");

  const backendUrl = process.env.NEXT_PUBLIC_BACKEND_URL || "http://localhost:8000";

  // Fetch initial data
  const fetchData = async () => {
    try {
      const ticketsRes = await fetch(`${backendUrl}/api/tickets`);
      const ticketsData = await ticketsRes.json();
      setTickets(ticketsData);

      const metricsRes = await fetch(`${backendUrl}/api/metrics`);
      const metricsData = await metricsRes.json();
      setMetrics(metricsData);
    } catch (e) {
      console.error("Error fetching dashboard data", e);
    }
  };

  useEffect(() => {
    const hasSeenIntro = sessionStorage.getItem("hasSeenIntro");
    if (hasSeenIntro) {
      setShowIntro(false);
    }
    fetchData();
    const interval = setInterval(fetchData, 4000);
    return () => clearInterval(interval);
  }, []);

  // Fetch ticket details when selected
  useEffect(() => {
    if (!selectedTicketId) {
      setSelectedTicketDetails(null);
      return;
    }
    const fetchDetails = async () => {
      try {
        const res = await fetch(`${backendUrl}/api/tickets/${selectedTicketId}`);
        if (res.ok) {
          const data = await res.json();
          setSelectedTicketDetails(data);
          // Set draft text for editing
          if (data.status === "Escalated") {
            setEditedReplyText(data.drafted_reply);
          }
          // Default select the last node for detailed audit log
          if (data.audit_logs && data.audit_logs.length > 0) {
            setSelectedNodeLog(data.audit_logs[data.audit_logs.length - 1]);
          }
        }
      } catch (e) {
        console.error("Error fetching ticket details", e);
      }
    };
    fetchDetails();
    const interval = setInterval(fetchDetails, 3000);
    return () => clearInterval(interval);
  }, [selectedTicketId]);

  // Actions
  const handleApproveAction = async (action: "approve" | "reject" | "edit") => {
    if (!selectedTicketId) return;
    setActionLoading(true);
    try {
      const res = await fetch(`${backendUrl}/api/tickets/${selectedTicketId}/action`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          action,
          edited_reply: action === "edit" ? editedReplyText : null
        })
      });
      if (res.ok) {
        setIsEditingReply(false);
        fetchData();
      }
    } catch (e) {
      console.error("Action submit error", e);
    } finally {
      setActionLoading(false);
    }
  };

  // Channel simulators
  const handleSendSimulatedEmail = async () => {
    setLoading(true);
    setIsEmailSimOpen(false);
    setSimulatingStep("intake");
    
    // Simulate steps visually
    const steps = [
      { key: "classifier", label: "Tier 0: Classifying Intent & Risks..." },
      { key: "context", label: "Retrieving CRM & KB Context..." },
      { key: "resolution", label: "Routing & Resolving Ticket (MoE)..." },
      { key: "gating", label: "Gating Decision against Threshold..." },
      { key: "executor", label: "Executing Actions / Preparing Escalation..." }
    ];

    for (let i = 0; i < steps.length; i++) {
      await new Promise(r => setTimeout(r, 800));
      setSimulatingStep(steps[i].key);
    }
    
    try {
      const res = await fetch(`${backendUrl}/api/simulate/email`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          sender_email: emailForm.sender,
          sender_name: emailForm.sender.split("@")[0].split(".").map(s => s.charAt(0).toUpperCase() + s.slice(1)).join(" "),
          subject: emailForm.subject,
          body: emailForm.body
        })
      });
      if (res.ok) {
        const data = await res.json();
        setSelectedTicketId(data.ticket_id);
        setActiveMobileView("details");
        fetchData();
      }
    } catch (e) {
      console.error("Error sending simulated email", e);
    } finally {
      setSimulatingStep(null);
      setLoading(false);
    }
  };

  // Voice caller scenario data
  const VOICE_SCENARIOS = {
    refund_high: {
      name: "Angry Refund request (over $50)",
      email: "bob.miller@outlook.com",
      dialogue: [
        "Customer: Hi, I'm calling about order ORD-1003. I spent $150 on the Keyboard Pro and it is completely malfunctioning. I want a refund right now. This is unacceptable.",
        "System: ResolveAI Intake: Analyzing caller voice transcript...",
        "System: Classifier detected: 'refund_request' with risk flags ['high_refund_value', 'angry_language'].",
        "System: MoE routed to Tier 2 (Opus-class Frontier Model) due to high-risk parameters.",
        "System: Gating Check: Confidence 0.60 is below threshold of 0.85.",
        "System: Action: Escalating order refund of $150 to Human Queue. Caller is placed on hold."
      ]
    },
    shipping_delay: {
      name: "Delayed shipping inquiry",
      email: "bob.miller@outlook.com",
      dialogue: [
        "Customer: Hello, I placed order ORD-1002 five days ago and the mouse still hasn't arrived. The tracking number is TRK-112233445. What is going on?",
        "System: ResolveAI Intake: Classifying transcript query...",
        "System: Classifier detected: 'shipping_delay' with confidence 0.88.",
        "System: CRM Lookup: Order ORD-1002 status is 'Shipped' but is flagged delayed (ordered 5 days ago).",
        "System: MoE routed to Tier 1 (Sonnet-class Standard Model).",
        "System: Gating Check: Confidence 0.75 is below threshold of 0.80.",
        "System: Action: Drafted apology message & escalated ticket to support log queue."
      ]
    },
    faq_returns: {
      name: "Standard return policy question",
      email: "alice.vance@gmail.com",
      dialogue: [
        "Customer: Yes, hello, I want to know what your return policy is. How many days do I have to return an item?",
        "System: ResolveAI Intake: Classifying FAQ query...",
        "System: Classifier detected: 'general_faq' with confidence 0.95.",
        "System: KB Search: Found matching FAQ 'What is your return policy?'.",
        "System: MoE routed to Tier 0 (Haiku-class Cheap Model).",
        "System: Gating Check: Confidence 0.95 is above threshold of 0.80.",
        "System: Action: Auto-resolved. Text-to-Speech response generated for customer."
      ]
    }
  };

  const handleStartVoiceSim = () => {
    setVoiceStatus("playing");
    setVoiceTranscript([]);
    setPlaybackIndex(0);
  };

  useEffect(() => {
    if (voiceStatus !== "playing") return;
    const scenario = VOICE_SCENARIOS[voiceScenario as keyof typeof VOICE_SCENARIOS];
    if (voicePlaybackIndex >= scenario.dialogue.length) {
      // Completed, send to API
      setVoiceStatus("submitting");
      const transcriptClean = scenario.dialogue
        .filter(d => d.startsWith("Customer:"))
        .map(d => d.replace("Customer:", ""))
        .join(" ");
        
      const submitVoice = async () => {
        try {
          const res = await fetch(`${backendUrl}/api/simulate/voice`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
              customer_email: scenario.email,
              transcript: transcriptClean
            })
          });
          if (res.ok) {
            const data = await res.json();
            setSelectedTicketId(data.ticket_id);
            setActiveMobileView("details");
            fetchData();
          }
        } catch (e) {
          console.error(e);
        } finally {
          setVoiceStatus("idle");
          setIsVoiceSimOpen(false);
        }
      };
      submitVoice();
      return;
    }

    // Play next line
    const timer = setTimeout(() => {
      setVoiceTranscript(prev => [...prev, scenario.dialogue[voicePlaybackIndex]]);
      setPlaybackIndex(idx => idx + 1);
    }, 1200);

    return () => clearTimeout(timer);
  }, [voiceStatus, voicePlaybackIndex, voiceScenario]);

  // Chat simulator
  const handleChatConnect = () => {
    if (!chatEmail.trim()) return;
    setChatStatus("connecting");
    setTimeout(() => {
      setChatMessages([
        { sender: 'system', content: `Connected as ${chatEmail}. Type your message below to chat with AI Customer Support.` }
      ]);
      setChatStatus("idle");
      setIsChatConnected(true);
    }, 1000);
  };

  const handleSendChatMessage = async () => {
    if (!chatInput.trim() || chatStatus !== "idle") return;
    const userMsg = chatInput;
    setChatInput("");
    setChatMessages(prev => [...prev, { sender: 'customer', content: userMsg }]);
    setChatStatus("typing");

    try {
      const res = await fetch(`${backendUrl}/api/simulate/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          ticket_id: chatTicketId,
          customer_email: chatEmail,
          message: userMsg
        })
      });
      if (res.ok) {
        const data = await res.json();
        setChatTicketId(data.ticket_id);
        
        if (data.status === "Escalated") {
          setChatStatus("escalated");
          setChatMessages(prev => [...prev, {
            sender: 'system',
            content: `Confidence scored: ${data.confidence_score}. Drafted action escalated to Human Queue for verification.`
          }]);
        } else {
          setChatStatus("idle");
          setChatMessages(prev => [...prev, { sender: 'agent', content: data.reply }]);
        }
        fetchData();
      }
    } catch (e) {
      console.error(e);
      setChatStatus("idle");
    }
  };

  // Watch for ticket changes: if our chat ticket got approved, update the chat widget!
  useEffect(() => {
    if (!chatTicketId || chatStatus !== "escalated") return;
    const checkEscalatedStatus = async () => {
      try {
        const res = await fetch(`${backendUrl}/api/tickets/${chatTicketId}`);
        if (res.ok) {
          const data = await res.json();
          if (data.status === "Resolved") {
            const agentMsgs = data.messages.filter((m: any) => m.sender === "agent");
            const lastAgentMsg = agentMsgs[agentMsgs.length - 1];
            if (lastAgentMsg) {
              setChatMessages(prev => [...prev, { sender: 'agent', content: lastAgentMsg.content }]);
              setChatStatus("idle");
            }
          }
        }
      } catch (e) {
        console.error(e);
      }
    };
    const interval = setInterval(checkEscalatedStatus, 2000);
    return () => clearInterval(interval);
  }, [chatTicketId, chatStatus]);

  const handleIntroAnimationComplete = () => {
    setTimeout(() => {
      setFadeIntro(true);
      sessionStorage.setItem("hasSeenIntro", "true");
      setTimeout(() => {
        setShowIntro(false);
      }, 1000);
    }, 1200);
  };

  // Reset demo
  const handleResetDemo = async () => {
    if (!confirm("Are you sure you want to delete all tickets and reset demo state?")) return;
    // For a hackathon demo, we just clear and reload since seed.py handles initial database structure.
    // We can run backend reset, but here we can just do a fetch to clean tickets or simply let it be.
    // For the UI, we can reload.
  };

  // Filtered tickets
  const filteredTickets = tickets.filter(t => {
    const matchesSearch = t.id.toLowerCase().includes(searchQuery.toLowerCase()) || 
                          t.customer_email.toLowerCase().includes(searchQuery.toLowerCase()) || 
                          (t.subject && t.subject.toLowerCase().includes(searchQuery.toLowerCase()));
    
    if (activeTab === "all") return matchesSearch;
    return matchesSearch && t.status.toLowerCase() === activeTab;
  });

  return (
    <div className="flex-1 flex flex-col bg-slate-950 text-slate-100 min-h-screen font-sans">
      {/* Top Header */}
      <header className="flex flex-row items-center justify-between border-b border-slate-800 bg-slate-900 px-4 py-3 md:px-6 md:py-4 gap-2">
        <div className="flex items-center gap-2 sm:gap-3">
          <div className="flex h-9 w-9 sm:h-10 sm:w-10 items-center justify-center rounded-xl bg-indigo-600 shadow-lg shadow-indigo-500/30 shrink-0">
            <ShieldCheck className="h-5.5 w-5.5 sm:h-6 sm:w-6 text-white" />
          </div>
          <div>
            <h1 className="text-base sm:text-xl font-bold tracking-tight text-white flex items-center gap-1.5 sm:gap-2">
              ResolveAI
              <span className="hidden sm:inline-flex items-center rounded-md bg-indigo-500/10 px-2 py-1 text-xs font-medium text-indigo-400 ring-1 ring-inset ring-indigo-500/20">
                Agent Console
              </span>
            </h1>
            <p className="text-[10px] sm:text-xs text-slate-400 hidden sm:block font-medium">Autonomous Customer Support Gatekeeper</p>
          </div>
        </div>

        {/* Action Triggers */}
        <div className="flex items-center gap-1.5 sm:gap-3">
          <button 
            onClick={() => {
              setFadeIntro(false);
              setShowIntro(true);
            }}
            className="flex items-center gap-2 rounded-lg bg-slate-800 border border-slate-700 hover:bg-slate-700 text-xs font-semibold text-slate-200 p-2 sm:px-3 sm:py-2 transition-all cursor-pointer"
            title="Replay Intro Splash"
          >
            <RotateCw className="h-4 w-4 text-purple-400" />
            <span className="hidden lg:inline">Replay Intro</span>
          </button>
          <button 
            onClick={() => setIsEmailSimOpen(true)}
            className="flex items-center gap-2 rounded-lg bg-slate-800 border border-slate-700 hover:bg-slate-700 text-xs font-semibold text-slate-200 p-2 sm:px-3.5 sm:py-2 transition-all cursor-pointer"
            title="Simulate Email"
          >
            <Mail className="h-4 w-4 text-indigo-400" />
            <span className="hidden md:inline">Simulate Email</span>
            <span className="hidden sm:inline md:hidden">Email</span>
          </button>
          <button 
            onClick={() => setIsVoiceSimOpen(true)}
            className="flex items-center gap-2 rounded-lg bg-slate-800 border border-slate-700 hover:bg-slate-700 text-xs font-semibold text-slate-200 p-2 sm:px-3.5 sm:py-2 transition-all cursor-pointer"
            title="Simulate Voice Call"
          >
            <Phone className="h-4 w-4 text-emerald-400" />
            <span className="hidden md:inline">Simulate Voice Call</span>
            <span className="hidden sm:inline md:hidden">Voice</span>
          </button>
          <button 
            onClick={() => setIsChatWidgetOpen(true)}
            className="flex items-center gap-2 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-xs font-semibold text-white p-2 sm:px-3.5 sm:py-2 transition-all shadow-md shadow-indigo-600/10 cursor-pointer"
            title="Test Chat Widget"
          >
            <MessageSquare className="h-4 w-4" />
            <span className="hidden md:inline">Test Chat Widget</span>
            <span className="hidden sm:inline md:hidden">Chat</span>
          </button>
          <button
            onClick={fetchData}
            className="rounded-lg p-2 bg-slate-800 hover:bg-slate-700 text-slate-300 transition-all cursor-pointer"
            title="Refresh logs"
          >
            <RotateCw className="h-4 w-4" />
          </button>
        </div>
      </header>

      {/* Interactive Processing Overlay Indicator */}
      {simulatingStep && (
        <div className="absolute inset-0 bg-slate-950/80 backdrop-blur-sm z-50 flex flex-col items-center justify-center gap-4">
          <div className="relative">
            <div className="h-16 w-16 rounded-full border-4 border-indigo-500/20 border-t-indigo-500 animate-spin"></div>
            <Sparkles className="h-6 w-6 text-indigo-400 absolute inset-0 m-auto animate-pulse" />
          </div>
          <div className="text-center">
            <h3 className="text-lg font-bold text-white mb-1">ResolveAI LangGraph Active</h3>
            <p className="text-sm text-indigo-400 animate-pulse font-medium">
              {simulatingStep === "intake" && "Intake & Normalization..."}
              {simulatingStep === "classifier" && "Tier 0: Classifying Intent & Risks..."}
              {simulatingStep === "context" && "System Context Retriever: Syncing CRM Profile..."}
              {simulatingStep === "resolution" && "MoE Router: Generating Draft Resolvers..."}
              {simulatingStep === "gating" && "Confidence Scorer: Testing Gating Thresholds..."}
              {simulatingStep === "executor" && "Executing Autonomous Actions..."}
            </p>
          </div>
        </div>
      )}

      {/* Main Core Dashboard Content */}
      <main className="flex-1 flex flex-col lg:flex-row overflow-hidden lg:max-h-[calc(100vh-73px)] max-h-[calc(100vh-61px)]">
        {/* Left Side: Main Column & Navigation */}
        <div className={`flex-1 flex flex-col overflow-y-auto border-r border-slate-800 p-4 sm:p-6 gap-6 ${
          activeMobileView === "details" ? "hidden lg:flex" : "flex"
        }`}>
          
          {/* Dashboard Metrics Panel */}
          <section className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="rounded-xl border border-slate-800 bg-slate-900/50 p-4">
              <div className="flex items-center justify-between mb-2">
                <span className="text-xs font-semibold text-slate-400">Autonomy Rate</span>
                <span className="rounded-full bg-indigo-500/10 px-2 py-0.5 text-xs text-indigo-400 font-medium">Trust</span>
              </div>
              <div className="flex items-baseline gap-2">
                <span className="text-2xl font-bold tracking-tight text-white">{metrics.autonomy_rate}%</span>
                <span className="text-xs text-slate-500">autonomous</span>
              </div>
              <div className="w-full bg-slate-800 h-1.5 rounded-full mt-3 overflow-hidden">
                <div 
                  className="bg-indigo-500 h-full rounded-full transition-all duration-500" 
                  style={{ width: `${metrics.autonomy_rate}%` }}
                ></div>
              </div>
            </div>

            <div className="rounded-xl border border-slate-800 bg-slate-900/50 p-4">
              <div className="flex items-center justify-between mb-2">
                <span className="text-xs font-semibold text-slate-400">Cost Savings</span>
                <TrendingDown className="h-4 w-4 text-emerald-400" />
              </div>
              <div className="flex items-baseline gap-2">
                <span className="text-2xl font-bold tracking-tight text-emerald-400">${metrics.savings.toFixed(3)}</span>
                <span className="text-xs text-slate-500">saved</span>
              </div>
              <p className="text-[10px] text-slate-500 mt-2.5">
                Baseline (Always Frontier): <span className="line-through">${metrics.baseline_cost.toFixed(3)}</span>
              </p>
            </div>

            <div className="rounded-xl border border-slate-800 bg-slate-900/50 p-4">
              <div className="flex items-center justify-between mb-2">
                <span className="text-xs font-semibold text-slate-400">Average Response</span>
                <Clock className="h-4 w-4 text-indigo-400" />
              </div>
              <div className="flex items-baseline gap-2">
                <span className="text-2xl font-bold tracking-tight text-white">
                  {metrics.avg_resp_time_sec < 60 
                    ? `${metrics.avg_resp_time_sec}s` 
                    : `${Math.round(metrics.avg_resp_time_sec / 60)}m`}
                </span>
                <span className="text-xs text-slate-500">avg</span>
              </div>
              <p className="text-[10px] text-slate-500 mt-2.5">
                Instant auto-responses save ~15 mins
              </p>
            </div>

            <div className="rounded-xl border border-slate-800 bg-slate-900/50 p-4">
              <div className="flex items-center justify-between mb-2">
                <span className="text-xs font-semibold text-slate-400">Total Tickets</span>
                <Inbox className="h-4 w-4 text-slate-400" />
              </div>
              <div className="flex items-baseline gap-2">
                <span className="text-2xl font-bold tracking-tight text-white">{metrics.total_tickets}</span>
                <span className="text-xs text-slate-500">total ({metrics.resolved_count} resolved)</span>
              </div>
              <p className="text-[10px] text-slate-500 mt-2.5">
                Active live ticket streams
              </p>
            </div>
          </section>

          {/* Ticket Feed Header & Filters */}
          <section className="flex flex-col gap-4">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
              <h2 className="text-lg font-bold text-white flex items-center gap-2">
                Support Ticket Stream
                <span className="rounded-full bg-slate-800 px-2 py-0.5 text-xs text-slate-400">
                  {filteredTickets.length}
                </span>
              </h2>

              <div className="flex items-center gap-2">
                <div className="relative">
                  <Search className="h-4 w-4 text-slate-500 absolute left-3 top-2.5" />
                  <input
                    type="text"
                    placeholder="Search by email, subject..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    className="rounded-lg bg-slate-900 border border-slate-800 pl-9 pr-4 py-1.5 text-xs text-slate-100 placeholder-slate-500 focus:outline-none focus:border-slate-700 w-48 sm:w-60"
                  />
                </div>
              </div>
            </div>

            {/* Tabs */}
            <div className="flex border-b border-slate-800 text-xs">
              {(["all", "open", "escalated", "resolved"] as const).map((tab) => (
                <button
                  key={tab}
                  onClick={() => setActiveTab(tab)}
                  className={`border-b-2 px-4 py-2.5 font-medium transition-all capitalize cursor-pointer ${
                    activeTab === tab 
                      ? "border-indigo-500 text-indigo-400 bg-indigo-500/5" 
                      : "border-transparent text-slate-400 hover:text-slate-200"
                  }`}
                >
                  {tab}
                </button>
              ))}
            </div>
          </section>

          {/* Tickets List */}
          <section className="flex-1 flex flex-col gap-3">
            {filteredTickets.length === 0 ? (
              <div className="flex flex-col items-center justify-center py-12 border border-dashed border-slate-800 rounded-xl text-slate-500 text-sm gap-2">
                <Inbox className="h-8 w-8 text-slate-600" />
                No tickets matching current filters.
              </div>
            ) : (
              filteredTickets.map((t) => (
                <div
                  key={t.id}
                  onClick={() => {
                    setSelectedTicketId(t.id);
                    setActiveMobileView("details");
                  }}
                  className={`border rounded-xl p-4 flex flex-col sm:flex-row sm:items-center justify-between gap-4 cursor-pointer transition-all hover:bg-slate-900/60 ${
                    selectedTicketId === t.id 
                      ? "border-indigo-500 bg-indigo-500/5 shadow-md shadow-indigo-500/5" 
                      : "border-slate-800 bg-slate-900/20"
                  }`}
                >
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2.5 mb-1.5 flex-wrap">
                      <span className="text-xs font-semibold text-indigo-400 tracking-wider font-mono">{t.id}</span>
                      
                      {/* Channel Icon */}
                      {t.channel === "email" && <span title="Email"><Mail className="h-3.5 w-3.5 text-indigo-400" /></span>}
                      {t.channel === "chat" && <span title="Live Chat"><MessageSquare className="h-3.5 w-3.5 text-sky-400" /></span>}
                      {t.channel === "voice" && <span title="Voice Call"><Phone className="h-3.5 w-3.5 text-emerald-400" /></span>}
                      
                      <span className="text-xs text-slate-400 font-medium truncate">{t.customer_email}</span>
                      <span className="text-[10px] text-slate-500" suppressHydrationWarning={true}>• {new Date(t.updated_at).toLocaleTimeString()}</span>
                    </div>

                    <h3 className="text-sm font-semibold text-white truncate mb-1">{t.subject || "No Subject"}</h3>
                    <p className="text-xs text-slate-400 truncate">{t.latest_message}</p>
                  </div>

                  <div className="flex sm:flex-col items-end justify-between sm:justify-center gap-2">
                    {/* Status Badge */}
                    <span className={`inline-flex items-center rounded-md px-2 py-1 text-xs font-semibold ring-1 ring-inset ${
                      t.status === "Resolved" 
                        ? "bg-emerald-500/10 text-emerald-400 ring-emerald-500/20" 
                        : t.status === "Escalated" 
                        ? "bg-amber-500/10 text-amber-400 ring-amber-500/20 animate-pulse" 
                        : "bg-slate-500/10 text-slate-400 ring-slate-500/20"
                    }`}>
                      {t.status}
                    </span>

                    {/* Confidence Score & Cost */}
                    <div className="text-right text-[10px] text-slate-400 space-y-0.5">
                      <div>Confidence: <span className="font-semibold text-slate-200">{Math.round(t.confidence_score * 100)}%</span></div>
                      <div>Cost: <span className="font-semibold text-indigo-300">${t.token_cost.toFixed(4)}</span></div>
                    </div>
                  </div>
                </div>
              ))
            )}
          </section>
        </div>

        {/* Right Side: Ticket Details & Audit Trace Viewer */}
        <div className={`w-full lg:w-[480px] xl:w-[600px] border-t lg:border-t-0 border-slate-800 bg-slate-900/30 flex flex-col overflow-y-auto p-4 sm:p-6 gap-6 ${
          activeMobileView === "list" ? "hidden lg:flex" : "flex"
        }`}>
          {/* Mobile Back Button */}
          {activeMobileView === "details" && (
            <div className="lg:hidden flex items-center mb-1">
              <button
                onClick={() => setActiveMobileView("list")}
                className="flex items-center gap-1.5 text-xs text-indigo-400 hover:text-indigo-300 font-semibold px-3.5 py-2 rounded-xl bg-slate-900 border border-slate-800 cursor-pointer shadow-md transition-all active:scale-95"
              >
                <ChevronLeft className="h-4 w-4" />
                Back to Ticket Stream
              </button>
            </div>
          )}

          {!selectedTicketDetails ? (
            <div className="flex-1 flex flex-col items-center justify-center text-slate-500 text-sm gap-2 py-12">
              <Cpu className="h-8 w-8 text-slate-700 animate-pulse" />
              Select a ticket from the stream to view full LangGraph trace logs, confidence score gating, and human actions.
            </div>
          ) : (
            <>
              {/* Header Details */}
              <div className="border-b border-slate-800 pb-4">
                <div className="flex items-center justify-between mb-2">
                  <h2 className="text-lg font-bold text-white font-mono">{selectedTicketDetails.id}</h2>
                  <span className={`inline-flex items-center rounded-md px-2.5 py-1 text-xs font-semibold ring-1 ring-inset ${
                    selectedTicketDetails.status === "Resolved" 
                      ? "bg-emerald-500/10 text-emerald-400 ring-emerald-500/20" 
                      : selectedTicketDetails.status === "Escalated" 
                      ? "bg-amber-500/10 text-amber-400 ring-amber-500/20" 
                      : "bg-slate-500/10 text-slate-400 ring-slate-500/20"
                  }`}>
                    {selectedTicketDetails.status}
                  </span>
                </div>

                <div className="space-y-1">
                  <p className="text-xs text-slate-400 flex items-center gap-1.5">
                    <User className="h-3.5 w-3.5 text-slate-500" />
                    <span className="font-semibold text-slate-300">{selectedTicketDetails.customer_name}</span> ({selectedTicketDetails.customer_email})
                  </p>
                  <p className="text-xs text-slate-400">
                    Subject: <span className="text-slate-200 font-medium">{selectedTicketDetails.subject}</span>
                  </p>
                </div>
              </div>

              {/* Confidence Gate Panel */}
              <div className="rounded-xl border border-slate-800 bg-slate-950 p-4">
                <h3 className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-3 flex items-center gap-1.5">
                  <ShieldCheck className="h-4 w-4 text-indigo-400" />
                  Confidence Gate & Risk Analysis
                </h3>

                <div className="flex flex-col sm:flex-row items-center gap-6 mb-4">
                  {/* Gauge */}
                  <div className="relative flex items-center justify-center h-20 w-20">
                    <svg className="w-full h-full transform -rotate-90">
                      <circle cx="40" cy="40" r="34" className="stroke-slate-800" strokeWidth="6" fill="transparent" />
                      <circle 
                        cx="40" 
                        cy="40" 
                        r="34" 
                        className={`${
                          selectedTicketDetails.confidence_score >= 0.80 
                            ? "stroke-indigo-500" 
                            : "stroke-amber-500"
                        } transition-all duration-1000`} 
                        strokeWidth="6" 
                        fill="transparent" 
                        strokeDasharray={2 * Math.PI * 34}
                        strokeDashoffset={2 * Math.PI * 34 * (1 - selectedTicketDetails.confidence_score)}
                      />
                    </svg>
                    <div className="absolute text-center">
                      <span className="text-lg font-bold text-white">{Math.round(selectedTicketDetails.confidence_score * 100)}%</span>
                      <p className="text-[8px] text-slate-400 uppercase">Score</p>
                    </div>
                  </div>

                  {/* Classification details */}
                  <div className="flex-1 space-y-2 text-xs">
                    <div>
                      Classification Intent: <span className="font-semibold text-indigo-400">{selectedTicketDetails.subject ? selectedTicketDetails.subject.toLowerCase().replace(" ", "_") : "general_faq"}</span>
                    </div>

                    {/* Risk flags */}
                    <div className="flex flex-wrap gap-1.5 items-center">
                      <span className="text-slate-400">Risk Flags:</span>
                      {selectedTicketDetails.audit_logs.find(a => a.node === "classifier")?.action_taken.includes("Risk flags: []") || 
                       !selectedTicketDetails.audit_logs.find(a => a.node === "classifier")?.action_taken.includes("Risk flags:") ? (
                        <span className="text-slate-500 italic">None detected</span>
                      ) : (
                        (() => {
                          const log = selectedTicketDetails.audit_logs.find(a => a.node === "classifier")?.action_taken || "";
                          const flags = log.split("Risk flags:")[1]?.replace("[", "").replace("]", "").split(",") || [];
                          return flags.map((f, i) => f.trim() && (
                            <span key={i} className="inline-flex items-center rounded-md bg-rose-500/10 px-1.5 py-0.5 text-[10px] font-medium text-rose-400 ring-1 ring-inset ring-rose-500/20">
                              <AlertTriangle className="mr-1 h-2.5 w-2.5" />
                              {f.replace(/'/g, "").trim()}
                            </span>
                          ));
                        })()
                      )}
                    </div>

                    {/* Explanatory text */}
                    {selectedTicketDetails.explanation && (
                      <div className="text-[11px] text-amber-400 leading-relaxed bg-amber-500/5 rounded-lg p-2 border border-amber-500/10 flex gap-1.5">
                        <AlertTriangle className="h-4 w-4 shrink-0" />
                        <div>
                          <span className="font-semibold">Reason for review:</span> {selectedTicketDetails.explanation}
                        </div>
                      </div>
                    )}
                  </div>
                </div>

                {/* Proposed draft actions */}
                {selectedTicketDetails.status === "Escalated" && selectedTicketDetails.drafted_actions && selectedTicketDetails.drafted_actions.length > 0 && (
                  <div className="border-t border-slate-800 pt-3">
                    <span className="text-[10px] font-semibold text-slate-400 uppercase tracking-wider block mb-2">Proposed Actions Gate (Awaiting Review)</span>
                    <div className="space-y-2">
                      {selectedTicketDetails.drafted_actions.map((act, i) => (
                        <div key={i} className="rounded-lg bg-slate-900 border border-slate-800 p-2.5 text-xs flex items-center justify-between">
                          <div>
                            <div className="font-semibold text-indigo-400 flex items-center gap-1">
                              <Cpu className="h-3 w-3" />
                              {act.action === "issue_refund" ? "Issue Refund" : "Cancel Subscription"}
                            </div>
                            <div className="text-[10px] text-slate-400 mt-0.5">
                              {act.action === "issue_refund" 
                                ? `Order ID: ${act.args.order_id} • Amount: $${act.args.amount}` 
                                : `Subscription ID: ${act.args.subscription_id}`}
                            </div>
                          </div>
                          <span className="text-[9px] bg-amber-500/10 text-amber-400 border border-amber-500/20 px-1.5 py-0.5 rounded font-medium">Escalated</span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>

              {/* Chat Thread */}
              <div className="flex-1 border border-slate-800 rounded-xl bg-slate-950/40 overflow-hidden flex flex-col max-h-[300px]">
                <div className="bg-slate-900/60 border-b border-slate-800 px-4 py-2.5 text-xs font-semibold text-slate-300 flex items-center gap-1.5">
                  <Inbox className="h-3.5 w-3.5 text-slate-400" />
                  Conversation Logs
                </div>
                <div className="flex-1 overflow-y-auto p-4 space-y-3.5">
                  {selectedTicketDetails.messages.map((m, i) => (
                    <div 
                      key={i} 
                      className={`flex flex-col ${
                        m.sender === "customer" 
                          ? "items-start" 
                          : m.sender === "agent" 
                          ? "items-end" 
                          : "items-center"
                      }`}
                    >
                      {m.sender !== "system" ? (
                        <>
                          <span className="text-[9px] text-slate-500 mb-1 px-1" suppressHydrationWarning={true}>
                            {m.sender === "customer" ? "Customer" : "AI Customer Support Agent"} • {new Date(m.timestamp).toLocaleTimeString()}
                          </span>
                          <div className={`rounded-xl px-3 py-2 text-xs leading-relaxed max-w-[85%] ${
                            m.sender === "customer" 
                              ? "bg-slate-800 text-slate-200" 
                              : "bg-indigo-600 text-white"
                          }`}>
                            {m.content}
                          </div>
                        </>
                      ) : (
                        <div className="rounded-lg bg-amber-500/5 border border-amber-500/10 px-3 py-1.5 text-[10px] text-amber-400 text-center font-medium max-w-[90%]">
                          {m.content}
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              </div>

              {/* Escalation Control Console */}
              {selectedTicketDetails.status === "Escalated" && (
                <div className="rounded-xl border border-slate-800 bg-slate-900/50 p-4">
                  <div className="flex items-center justify-between mb-3 border-b border-slate-800 pb-2">
                    <h3 className="text-xs font-bold text-white flex items-center gap-1.5">
                      <Edit3 className="h-3.5 w-3.5 text-indigo-400" />
                      Human Intervention Console
                    </h3>
                    <div className="text-[10px] text-amber-400 font-medium">Awaiting Approve / Edit / Reject</div>
                  </div>

                  {isEditingReply ? (
                    <div className="space-y-3">
                      <label className="text-[10px] font-semibold text-slate-400 uppercase tracking-wider block">Edit Draft Reply</label>
                      <textarea
                        rows={4}
                        value={editedReplyText}
                        onChange={(e) => setEditedReplyText(e.target.value)}
                        className="w-full rounded-lg bg-slate-950 border border-slate-800 p-2.5 text-xs text-slate-200 focus:outline-none focus:border-slate-700"
                      />
                      <div className="flex gap-2 justify-end">
                        <button
                          onClick={() => setIsEditingReply(false)}
                          disabled={actionLoading}
                          className="rounded-lg bg-slate-800 hover:bg-slate-700 border border-slate-700 px-3 py-1.5 text-xs font-medium text-slate-300 transition-all cursor-pointer"
                        >
                          Cancel
                        </button>
                        <button
                          onClick={() => handleApproveAction("edit")}
                          disabled={actionLoading}
                          className="rounded-lg bg-indigo-600 hover:bg-indigo-500 px-4 py-1.5 text-xs font-semibold text-white transition-all shadow-md shadow-indigo-600/10 flex items-center gap-1.5 cursor-pointer"
                        >
                          {actionLoading ? "Saving..." : "Send Edited Reply"}
                        </button>
                      </div>
                    </div>
                  ) : (
                    <div className="space-y-3">
                      <div className="rounded-lg bg-slate-950 border border-slate-800 p-3 text-xs">
                        <span className="text-[10px] font-semibold text-slate-500 uppercase block mb-1">Draft Response:</span>
                        <p className="text-slate-300 leading-relaxed italic">"{selectedTicketDetails.drafted_reply}"</p>
                      </div>
                      
                      <div className="flex flex-wrap gap-2 justify-end">
                        <button
                          onClick={() => handleApproveAction("reject")}
                          disabled={actionLoading}
                          className="rounded-lg bg-rose-500/10 hover:bg-rose-500/20 border border-rose-500/20 px-3.5 py-2 text-xs font-semibold text-rose-400 flex items-center gap-1.5 transition-all cursor-pointer"
                        >
                          <XCircle className="h-4 w-4" />
                          Reject Action
                        </button>
                        <button
                          onClick={() => setIsEditingReply(true)}
                          disabled={actionLoading}
                          className="rounded-lg bg-slate-800 hover:bg-slate-700 border border-slate-700 px-3.5 py-2 text-xs font-semibold text-slate-300 flex items-center gap-1.5 transition-all cursor-pointer"
                        >
                          <Edit3 className="h-4 w-4 text-indigo-400" />
                          Edit Draft
                        </button>
                        <button
                          onClick={() => handleApproveAction("approve")}
                          disabled={actionLoading}
                          className="rounded-lg bg-indigo-600 hover:bg-indigo-500 px-4 py-2 text-xs font-semibold text-white flex items-center gap-1.5 transition-all shadow-md shadow-indigo-600/10 cursor-pointer"
                        >
                          <CheckCircle className="h-4 w-4" />
                          {actionLoading ? "Processing..." : "Approve & Execute"}
                        </button>
                      </div>
                    </div>
                  )}
                </div>
              )}

              {/* Cryptographic Hash-Chained Audit Trail Stepper */}
              <div className="rounded-xl border border-slate-800 bg-slate-950 p-4">
                <h3 className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-4 flex items-center gap-1.5">
                  <Database className="h-4 w-4 text-indigo-400" />
                  LangGraph Cryptographic Audit Trail
                </h3>

                {/* Audit Node List */}
                <div className="relative pl-6 border-l border-slate-800 space-y-4">
                  {selectedTicketDetails.audit_logs.map((log, index) => {
                    const isSelected = selectedNodeLog?.node === log.node;
                    return (
                      <div 
                        key={index} 
                        onClick={() => setSelectedNodeLog(log)}
                        className={`relative group cursor-pointer transition-all ${
                          isSelected ? "text-indigo-400" : "text-slate-400 hover:text-slate-200"
                        }`}
                      >
                        {/* Dot Indicator */}
                        <div className={`absolute left-[-31px] top-1 h-2.5 w-2.5 rounded-full border-2 ${
                          log.node === "human_console" 
                            ? "bg-amber-400 border-slate-950" 
                            : isSelected 
                            ? "bg-indigo-500 border-slate-950" 
                            : "bg-slate-800 border-slate-950 group-hover:bg-slate-600"
                        }`} />

                        <div className="flex items-center justify-between">
                          <span className="text-xs font-bold capitalize font-mono flex items-center gap-1">
                            {log.node.replace("_", " ")}
                            {log.node === "human_console" && (
                              <span className="rounded bg-amber-500/10 px-1 py-0.5 text-[8px] font-medium text-amber-400 ring-1 ring-inset ring-amber-500/20">
                                Human Intervention
                              </span>
                            )}
                          </span>
                          <span className="text-[10px] text-slate-500 font-mono">
                            {log.model_used && log.model_used !== "System Retrieval" && log.model_used !== "System Routing" && log.model_used !== "System Gate" && log.model_used !== "System Executor"
                              ? log.model_used.split(" ")[0] 
                              : "System"}
                          </span>
                        </div>
                        <p className="text-[11px] text-slate-400 mt-0.5 truncate">{log.action_taken}</p>
                      </div>
                    );
                  })}
                </div>

                {/* Selected Node Details */}
                {selectedNodeLog && (
                  <div className="mt-4 rounded-lg bg-slate-900 border border-slate-800 p-3 text-[11px] space-y-2.5">
                    <div className="flex items-center justify-between border-b border-slate-800 pb-1.5">
                      <span className="font-bold text-white font-mono uppercase text-[10px]">Node: {selectedNodeLog.node}</span>
                      {selectedNodeLog.cost > 0 && (
                        <span className="text-indigo-400 font-semibold font-mono">Cost: ${selectedNodeLog.cost.toFixed(5)} ({selectedNodeLog.tokens} tokens)</span>
                      )}
                    </div>
                    
                    <div>
                      <span className="text-slate-500 block mb-0.5 font-medium">Input/Context Payload:</span>
                      <div className="bg-slate-950 rounded p-2 text-slate-300 font-mono text-[10px] max-h-20 overflow-y-auto break-all">
                        {selectedNodeLog.input_summary}
                      </div>
                    </div>

                    <div>
                      <span className="text-slate-500 block mb-0.5 font-medium">Execution Result / Log:</span>
                      <div className="bg-slate-950 rounded p-2 text-slate-300 font-mono text-[10px] max-h-20 overflow-y-auto break-all">
                        {selectedNodeLog.action_taken}
                      </div>
                    </div>

                    {/* Cryptographic block */}
                    <div className="border-t border-slate-800/80 pt-2 flex flex-col gap-1 text-[10px] text-slate-500 font-mono">
                      <div className="flex items-center justify-between">
                        <span>Prev Block Hash:</span>
                        <span className="text-slate-400 font-semibold truncate max-w-[200px]" title={selectedNodeLog.prev_hash}>
                          {selectedNodeLog.prev_hash.slice(0, 16)}...
                        </span>
                      </div>
                      <div className="flex items-center justify-between">
                        <span className="text-indigo-400/80 flex items-center gap-0.5">
                          <Check className="h-3 w-3 text-emerald-400" />
                          Block Ledger Hash:
                        </span>
                        <span className="text-emerald-400 font-semibold truncate max-w-[200px]" title={selectedNodeLog.hash}>
                          {selectedNodeLog.hash.slice(0, 16)}...
                        </span>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            </>
          )}
        </div>
      </main>

      {/* ----------------- INTERACTIVE DEMO POPUPS / SIMULATORS ----------------- */}

      {/* Email Simulation Modal */}
      {isEmailSimOpen && (
        <div className="fixed inset-0 bg-slate-950/80 backdrop-blur-sm z-40 flex items-center justify-center p-4">
          <div className="w-full max-w-lg rounded-xl border border-slate-800 bg-slate-900 p-6 shadow-2xl relative max-h-[90vh] overflow-y-auto">
            <button 
              onClick={() => setIsEmailSimOpen(false)}
              className="absolute right-4 top-4 text-slate-400 hover:text-slate-200 cursor-pointer"
            >
              <X className="h-5 w-5" />
            </button>

            <h3 className="text-base font-bold text-white mb-4 flex items-center gap-2">
              <Mail className="h-5 w-5 text-indigo-400" />
              Simulate Inbound Email
            </h3>

            <div className="space-y-4 text-xs">
              <div>
                <label className="text-slate-400 block mb-1 font-semibold">Customer Account Profile</label>
                <select
                  value={emailForm.sender}
                  onChange={(e) => {
                    const email = e.target.value;
                    let subject = "";
                    let body = "";
                    
                    if (email === "alice.vance@gmail.com") {
                      subject = "Help needed with my Order #1001";
                      body = "Hi support, I received my wireless headphones (Order ORD-1001) yesterday but the volume is extremely low in the left ear. Can I get a refund of $120 to my card?";
                    } else if (email === "bob.miller@outlook.com") {
                      subject = "Where is order ORD-1002?";
                      body = "Hello, my ergonomic desk mouse (Order ORD-1002) is still showing as shipped but has not arrived for 5 days. Can you tell me where it is?";
                    } else if (email === "charlie.green@yahoo.com") {
                      subject = "Cancel subscription immediately";
                      body = "I need to cancel my AI Support Developer Suite subscription SUB-2002. Please stop billing my card.";
                    }
                    
                    setEmailForm({ sender: email, subject, body });
                  }}
                  className="w-full rounded-lg bg-slate-950 border border-slate-800 p-2.5 text-slate-200 focus:outline-none focus:border-slate-700"
                >
                  <option value="alice.vance@gmail.com">Alice Vance (alice.vance@gmail.com) - Refund Request</option>
                  <option value="bob.miller@outlook.com">Bob Miller (bob.miller@outlook.com) - Delayed Order</option>
                  <option value="charlie.green@yahoo.com">Charlie Green (charlie.green@yahoo.com) - Cancel Subscription</option>
                </select>
              </div>

              <div>
                <label className="text-slate-400 block mb-1 font-semibold">Subject</label>
                <input
                  type="text"
                  value={emailForm.subject}
                  onChange={(e) => setEmailForm({...emailForm, subject: e.target.value})}
                  className="w-full rounded-lg bg-slate-950 border border-slate-800 p-2.5 text-slate-200 focus:outline-none focus:border-slate-700"
                />
              </div>

              <div>
                <label className="text-slate-400 block mb-1 font-semibold">Email Body</label>
                <textarea
                  rows={5}
                  value={emailForm.body}
                  onChange={(e) => setEmailForm({...emailForm, body: e.target.value})}
                  className="w-full rounded-lg bg-slate-950 border border-slate-800 p-2.5 text-slate-200 focus:outline-none focus:border-slate-700"
                />
              </div>

              <div className="flex justify-end gap-2 pt-2">
                <button
                  onClick={() => setIsEmailSimOpen(false)}
                  className="rounded-lg bg-slate-800 hover:bg-slate-700 border border-slate-700 px-4 py-2 text-xs font-semibold text-slate-300 cursor-pointer"
                >
                  Cancel
                </button>
                <button
                  onClick={handleSendSimulatedEmail}
                  className="rounded-lg bg-indigo-600 hover:bg-indigo-500 px-4 py-2 text-xs font-bold text-white shadow-md shadow-indigo-600/10 cursor-pointer"
                >
                  Send Simulated Email
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Voice Call Simulation Modal */}
      {isVoiceSimOpen && (
        <div className="fixed inset-0 bg-slate-950/80 backdrop-blur-sm z-40 flex items-center justify-center p-4">
          <div className="w-full max-w-lg rounded-xl border border-slate-800 bg-slate-900 p-6 shadow-2xl relative max-h-[90vh] overflow-y-auto">
            <button 
              onClick={() => {
                setIsVoiceSimOpen(false);
                setVoiceStatus("idle");
              }}
              className="absolute right-4 top-4 text-slate-400 hover:text-slate-200 cursor-pointer"
            >
              <X className="h-5 w-5" />
            </button>

            <h3 className="text-base font-bold text-white mb-4 flex items-center gap-2">
              <Phone className="h-5 w-5 text-emerald-400" />
              Simulate Inbound Voice Call
            </h3>

            <div className="space-y-4 text-xs">
              <div>
                <label className="text-slate-400 block mb-1 font-semibold">Select Call Scenario</label>
                <select
                  value={voiceScenario}
                  onChange={(e) => setVoiceScenario(e.target.value)}
                  disabled={voiceStatus !== "idle"}
                  className="w-full rounded-lg bg-slate-950 border border-slate-800 p-2.5 text-slate-200 focus:outline-none focus:border-slate-700"
                >
                  <option value="refund_high">Bob Miller - Angry Refund request for $150 (Escalates)</option>
                  <option value="shipping_delay">Bob Miller - Shipping Delay query on ORD-1002 (Escalates)</option>
                  <option value="faq_returns">Alice Vance - Simple FAQ Return policy question (Auto-resolves)</option>
                </select>
              </div>

              {/* Call Visualizer */}
              <div className="rounded-lg border border-slate-800 bg-slate-950 p-4 h-48 overflow-y-auto flex flex-col justify-end gap-2 relative">
                {voiceStatus === "idle" && (
                  <div className="absolute inset-0 flex flex-col items-center justify-center text-slate-500 gap-2">
                    <Play className="h-8 w-8 text-emerald-500" />
                    Click "Begin Simulated Call" to play
                  </div>
                )}

                {voiceStatus === "playing" && (
                  <div className="absolute top-3 right-3 flex items-center gap-1.5 text-[9px] text-emerald-400 font-mono">
                    <span className="h-2 w-2 rounded-full bg-emerald-500 animate-ping"></span>
                    CALLING LIVE...
                  </div>
                )}

                {voiceStatus === "submitting" && (
                  <div className="absolute inset-0 bg-slate-950/80 backdrop-blur-sm flex flex-col items-center justify-center text-slate-300 text-xs font-semibold gap-2">
                    <div className="h-8 w-8 rounded-full border-2 border-emerald-500/20 border-t-emerald-500 animate-spin"></div>
                    Transmitting Call Transcript to LangGraph...
                  </div>
                )}

                {voiceTranscript.map((line, i) => (
                  <div 
                    key={i} 
                    className={`p-2 rounded text-[11px] leading-relaxed ${
                      line.startsWith("Customer:") 
                        ? "bg-slate-900 border border-slate-800 text-slate-200" 
                        : "bg-emerald-950/30 border border-emerald-500/10 text-emerald-400 font-mono"
                    }`}
                  >
                    {line}
                  </div>
                ))}
              </div>

              {/* Controls */}
              <div className="flex justify-end gap-2">
                <button
                  onClick={() => {
                    setIsVoiceSimOpen(false);
                    setVoiceStatus("idle");
                  }}
                  className="rounded-lg bg-slate-800 hover:bg-slate-700 border border-slate-700 px-4 py-2 text-xs font-semibold text-slate-300 cursor-pointer"
                >
                  Close
                </button>
                {voiceStatus === "idle" && (
                  <button
                    onClick={handleStartVoiceSim}
                    className="rounded-lg bg-emerald-600 hover:bg-emerald-500 px-4 py-2 text-xs font-bold text-white shadow-md shadow-emerald-600/10 flex items-center gap-1.5 cursor-pointer"
                  >
                    <Play className="h-3.5 w-3.5" />
                    Begin Simulated Call
                  </button>
                )}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Floating Chat Widget Simulator */}
      {isChatWidgetOpen && (
        <div className="fixed bottom-4 right-4 left-4 md:left-auto md:right-6 md:bottom-6 md:w-96 rounded-xl border border-slate-800 bg-slate-900 shadow-2xl z-40 flex flex-col overflow-hidden animate-slide-up">
          {/* Header */}
          <div className="bg-indigo-600 px-4 py-3 flex items-center justify-between text-white">
            <div className="flex items-center gap-2">
              <Sparkles className="h-5 w-5 text-yellow-300 animate-pulse" />
              <div>
                <h4 className="text-xs font-bold">AI Customer Support</h4>
                <p className="text-[9px] text-indigo-200 flex items-center gap-1">
                  <span className="h-1.5 w-1.5 rounded-full bg-emerald-400"></span>
                  Active AI Agent
                </p>
              </div>
            </div>
            <button 
              onClick={() => {
                setIsChatWidgetOpen(false);
                setIsChatConnected(false);
                setChatEmail("charlie.green@yahoo.com");
                setChatTicketId(null);
                setChatMessages([
                  { sender: 'system', content: 'Enter your email to start chatting with ResolveAI.' }
                ]);
              }}
              className="text-white/80 hover:text-white cursor-pointer"
            >
              <X className="h-4 w-4" />
            </button>
          </div>

          {/* Messages */}
          <div className="flex-1 h-80 overflow-y-auto p-4 space-y-3 bg-slate-950/40 text-xs">
            {chatMessages.map((m, i) => (
              <div 
                key={i} 
                className={`flex flex-col ${
                  m.sender === "customer" 
                    ? "items-end" 
                    : m.sender === "agent" 
                    ? "items-start" 
                    : "items-center"
                }`}
              >
                <div className={`rounded-xl px-3 py-2 leading-relaxed ${
                  m.sender === "customer" 
                    ? "bg-indigo-600 text-white max-w-[80%]" 
                    : m.sender === "agent" 
                    ? "bg-slate-800 text-slate-200 max-w-[80%]" 
                    : "bg-slate-900 border border-slate-800 text-slate-400 text-[10px] text-center font-medium max-w-[90%]"
                }`}>
                  {m.content}
                </div>
              </div>
            ))}
            
            {chatStatus === "typing" && (
              <div className="flex items-center gap-1 text-[10px] text-slate-500 italic">
                <span className="h-1 w-1 bg-slate-500 rounded-full animate-bounce"></span>
                <span className="h-1 w-1 bg-slate-500 rounded-full animate-bounce delay-75"></span>
                <span className="h-1 w-1 bg-slate-500 rounded-full animate-bounce delay-150"></span>
                ResolveAI is thinking...
              </div>
            )}
            
            {chatStatus === "escalated" && (
              <div className="rounded-lg bg-amber-500/5 border border-amber-500/10 p-3 text-[10px] text-amber-400 space-y-1 text-center font-medium">
                <AlertTriangle className="h-4 w-4 mx-auto mb-1" />
                This action requires supervisor authorization. 
                Waiting for human approval in Dashboard console...
              </div>
            )}
          </div>

          {/* Input Panel */}
          <div className="border-t border-slate-800 p-3 bg-slate-900 flex gap-2">
            {!isChatConnected ? (
              <div className="w-full flex gap-2">
                <input
                  type="email"
                  placeholder="Enter email to begin"
                  value={chatEmail}
                  onChange={(e) => setChatEmail(e.target.value)}
                  className="flex-1 rounded-lg bg-slate-950 border border-slate-800 px-3 py-1.5 text-xs text-slate-200 focus:outline-none focus:border-slate-700"
                />
                <button
                  onClick={handleChatConnect}
                  className="rounded-lg bg-indigo-600 hover:bg-indigo-500 px-3 py-1.5 text-xs font-semibold text-white cursor-pointer"
                >
                  Start
                </button>
              </div>
            ) : (
              <>
                <input
                  type="text"
                  placeholder={chatStatus === "escalated" ? "Awaiting human approval..." : "Type your message..."}
                  value={chatInput}
                  onChange={(e) => setChatInput(e.target.value)}
                  disabled={chatStatus !== "idle"}
                  onKeyDown={(e) => e.key === "Enter" && handleSendChatMessage()}
                  className="flex-1 rounded-lg bg-slate-950 border border-slate-800 px-3 py-1.5 text-xs text-slate-200 focus:outline-none focus:border-slate-700"
                />
                <button
                  onClick={handleSendChatMessage}
                  disabled={chatStatus !== "idle" || !chatInput.trim()}
                  className="rounded-lg bg-indigo-600 hover:bg-indigo-500 p-1.5 text-white disabled:bg-slate-800 disabled:text-slate-500 cursor-pointer"
                >
                  <Send className="h-4 w-4" />
                </button>
              </>
            )}
          </div>
        </div>
      )}
      {showIntro && (
        <div className={`fixed inset-0 z-50 flex flex-col items-center justify-center bg-slate-950/98 backdrop-blur-md transition-all duration-1000 transform grid-bg-pan ${fadeIntro ? 'opacity-0 scale-105 pointer-events-none' : 'opacity-100 scale-100'}`}>
          <div className="max-w-2xl px-6 text-center">
            <SplitText
              text="Welcome to ResolveAI"
              className="text-4xl sm:text-5xl md:text-6xl lg:text-7xl font-extrabold tracking-tight text-center text-white leading-tight drop-shadow-[0_0_30px_rgba(99,102,241,0.7)]"
              delay={40}
              duration={0.7}
              ease="power3.out"
              tag="h1"
              from={{ opacity: 0, y: 35 }}
              to={{ opacity: 1, y: 0 }}
              textAlign="center"
              onLetterAnimationComplete={handleIntroAnimationComplete}
            />
          </div>
        </div>
      )}
    </div>
  );
}

const Dashboard = dynamic(() => Promise.resolve(DashboardComponent), {
  ssr: false,
});

export default Dashboard;
