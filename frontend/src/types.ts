// Shared TypeScript types matching the backend Pydantic schemas

export type Urgency = "critical" | "high" | "medium" | "low";
export type EmailStatus = "unread" | "read" | "responded" | "archived";
export type ReplyTone = "professional" | "friendly" | "concise";
export type ReplyStatus = "draft" | "used" | "discarded";
export type FollowUpStatus = "pending" | "completed" | "snoozed";
export type AccountStatus = "connected" | "error" | "demo" | "disconnected";
export type SyncMode = "imap" | "demo";

export const CATEGORIES = [
  "Work",
  "Personal",
  "Customer Support",
  "Sales",
  "Finance",
  "Meeting",
  "Application/Recruitment",
  "Newsletter",
  "Notification",
  "Spam",
  "Other",
] as const;

export type Category = (typeof CATEGORIES)[number];

export const URGENCIES: Urgency[] = ["critical", "high", "medium", "low"];

export interface AIClassification {
  category: string;
  urgency: Urgency;
  confidence: number;
  explanation: string | null;
  needs_response: boolean;
  suggested_followup: boolean;
  is_manual_override: boolean;
}

export interface ReplySuggestion {
  id: number;
  tone: ReplyTone;
  content: string;
  status: ReplyStatus;
  created_at: string;
}

export interface FollowUpBrief {
  id: number;
  status: FollowUpStatus;
  reminder_at: string;
}

export interface EmailBrief {
  id: number;
  sender_email: string;
  sender_name: string | null;
  subject: string;
  preview: string | null;
  received_at: string;
  status: EmailStatus;
  is_demo: boolean;
  classification: AIClassification | null;
  has_replies: boolean;
  has_followup: boolean;
}

export interface EmailDetail extends EmailBrief {
  recipient_email: string;
  body_text: string | null;
  body_html: string | null;
  responded_at: string | null;
  replies: ReplySuggestion[];
  follow_ups: FollowUpBrief[];
  thread: EmailBrief[];
}

export interface EmailListResponse {
  emails: EmailBrief[];
  total: number;
  page: number;
  page_size: number;
}

export interface FollowUp {
  id: number;
  email_id: number;
  reminder_at: string;
  note: string | null;
  status: FollowUpStatus;
  completed_at: string | null;
  created_at: string;
  email: EmailBrief | null;
}

export interface EmailAccount {
  id: number;
  email_address: string;
  imap_server: string;
  imap_port: number;
  imap_ssl: boolean;
  smtp_server: string | null;
  smtp_port: number | null;
  smtp_ssl: boolean;
  status: AccountStatus;
  last_sync_at: string | null;
  created_at: string;
}

export interface Analytics {
  total_emails: number;
  emails_by_category: Record<string, number>;
  emails_by_urgency: Record<string, number>;
  emails_requiring_response: number;
  emails_responded_to: number;
  pending_responses: number;
  avg_response_time_hours: number | null;
  follow_ups_completed: number;
  follow_ups_overdue: number;
  follow_ups_upcoming: number;
  ai_accuracy: number;
  reply_suggestions_generated: number;
  reply_suggestions_used: number;
  response_rate: number;
  recent_trend: { date: string; count: number }[];
}

export interface UserSettings {
  default_reply_tone: ReplyTone;
  auto_categorize: boolean;
  categorization_aggressiveness: string;
  notifications_enabled: boolean;
  email_notifications: boolean;
  store_email_bodies: boolean;
}

export interface SyncResult {
  status: string;
  new_emails: number;
  total_emails: number;
  message: string;
  mode: SyncMode;
}
