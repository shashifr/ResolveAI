export type ChannelType = "email" | "chat" | "voice";
export type TicketStatus = "Open" | "Escalated" | "Resolved";

export interface Ticket {
  id: string;
  customer_email: string;
  customer_name: string;
  channel: ChannelType;
  status: TicketStatus;
  subject: string;
  confidence_score: number;
  token_cost: number;
  updated_at: string;
  latest_message?: string;
}

export interface Message {
  id?: number | string;
  ticket_id?: string;
  sender: "customer" | "agent" | "system";
  content: string;
  timestamp: string;
}

export interface AuditLog {
  id?: number | string;
  ticket_id?: string;
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

export interface ProposedAction {
  action: string;
  args?: Record<string, any>;
  order_id?: string;
  amount?: number;
  subscription_id?: string;
  reason?: string;
}

export interface TicketDetails extends Ticket {
  messages: Message[];
  audit_logs: AuditLog[];
  drafted_actions: ProposedAction[];
  drafted_reply: string;
  explanation: string;
  risk_flags?: string[];
}

export interface Metrics {
  total_tickets: number;
  resolved_count: number;
  autonomous_count: number;
  autonomy_rate: number;
  total_actual_cost: number;
  baseline_cost: number;
  savings: number;
  avg_resp_time_sec: number;
}

export interface EmailSimulationForm {
  sender: string;
  subject: string;
  body: string;
}

export type TabFilter = "all" | "escalated" | "resolved" | "open";
