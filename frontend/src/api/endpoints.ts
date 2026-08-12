// API functions for all endpoints

import { apiFetch } from "./client";
import type {
  EmailListResponse,
  EmailDetail,
  EmailBrief,
  EmailAccount,
  FollowUp,
  Analytics,
  UserSettings,
  SyncResult,
  ReplySuggestion,
  AIClassification,
} from "../types";

// ---- Health ----
export const checkHealth = () => apiFetch<{ status: string; database: string }>("/health");

// ---- Settings ----
export const getSettings = () => apiFetch<UserSettings>("/settings");
export const updateSettings = (payload: Partial<UserSettings>) =>
  apiFetch<UserSettings>("/settings", {
    method: "PUT",
    body: JSON.stringify(payload),
  });

// ---- Accounts ----
export const getAccounts = () => apiFetch<EmailAccount[]>("/accounts");
export const createAccount = (payload: {
  email_address: string;
  imap_server: string;
  imap_port: number;
  imap_ssl: boolean;
  smtp_server?: string;
  smtp_port?: number;
  smtp_ssl: boolean;
  password: string;
}) =>
  apiFetch<EmailAccount>("/accounts", {
    method: "POST",
    body: JSON.stringify(payload),
  });
export const deleteAccount = (id: number) =>
  apiFetch<{ message: string }>(`/accounts/${id}`, { method: "DELETE" });
export const testAccount = (id: number) =>
  apiFetch<{ message: string; detail: string }>(`/accounts/${id}/test`, {
    method: "POST",
  });
export const syncEmails = (forceDemo = false) =>
  apiFetch<SyncResult>(`/accounts/sync?force_demo=${forceDemo}`, { method: "POST" });

// ---- Emails ----
export interface EmailQuery {
  search?: string;
  category?: string;
  urgency?: string;
  status?: string;
  follow_up?: string;
  sort?: string;
  page?: number;
  page_size?: number;
}

export const getEmails = (query: EmailQuery = {}) => {
  const params = new URLSearchParams();
  Object.entries(query).forEach(([key, value]) => {
    if (value !== undefined && value !== null && value !== "") {
      params.append(key, String(value));
    }
  });
  return apiFetch<EmailListResponse>(`/emails?${params.toString()}`);
};

export const getEmail = (id: number) => apiFetch<EmailDetail>(`/emails/${id}`);

export const updateEmailStatus = (id: number, status: string) =>
  apiFetch<EmailBrief>(`/emails/${id}/status`, {
    method: "PATCH",
    body: JSON.stringify({ status }),
  });

export const updateClassification = (
  id: number,
  payload: { category?: string; urgency?: string }
) =>
  apiFetch<AIClassification>(`/emails/${id}/classification`, {
    method: "PATCH",
    body: JSON.stringify(payload),
  });

// ---- Replies ----
export const generateReply = (emailId: number, tone: string) =>
  apiFetch<ReplySuggestion>(`/emails/${emailId}/replies`, {
    method: "POST",
    body: JSON.stringify({ tone }),
  });

export const updateReply = (
  emailId: number,
  replyId: number,
  payload: { content?: string; status?: string }
) =>
  apiFetch<ReplySuggestion>(`/emails/${emailId}/replies/${replyId}`, {
    method: "PATCH",
    body: JSON.stringify(payload),
  });

export const sendReply = (emailId: number, replyId: number) =>
  apiFetch<EmailBrief>(`/emails/${emailId}/send`, {
    method: "POST",
    body: JSON.stringify({ reply_id: replyId, confirm: true }),
  });

// ---- Follow-ups ----
export const getFollowUps = (status?: string) => {
  const params = status ? `?status=${status}` : "";
  return apiFetch<FollowUp[]>(`/follow-ups${params}`);
};

export const createFollowUp = (payload: {
  email_id: number;
  reminder_at: string;
  note?: string;
}) =>
  apiFetch<FollowUp>("/follow-ups", {
    method: "POST",
    body: JSON.stringify(payload),
  });

export const updateFollowUp = (
  id: number,
  payload: { reminder_at?: string; note?: string; status?: string }
) =>
  apiFetch<FollowUp>(`/follow-ups/${id}`, {
    method: "PATCH",
    body: JSON.stringify(payload),
  });

export const deleteFollowUp = (id: number) =>
  apiFetch<{ message: string }>(`/follow-ups/${id}`, { method: "DELETE" });

// ---- Analytics ----
export const getAnalytics = () => apiFetch<Analytics>("/analytics");
