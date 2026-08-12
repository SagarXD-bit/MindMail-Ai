// Utility functions for the frontend

import type { Urgency } from "../types";

export function formatDate(date: string | Date): string {
  const d = typeof date === "string" ? new Date(date) : date;
  return d.toLocaleDateString("en-US", {
    month: "short",
    day: "numeric",
    year: "numeric",
  });
}

export function formatDateTime(date: string | Date): string {
  const d = typeof date === "string" ? new Date(date) : date;
  return d.toLocaleString("en-US", {
    month: "short",
    day: "numeric",
    hour: "numeric",
    minute: "2-digit",
  });
}

export function formatRelative(date: string | Date): string {
  const d = typeof date === "string" ? new Date(date) : date;
  const now = new Date();
  const diffMs = now.getTime() - d.getTime();
  const diffMin = Math.floor(diffMs / 60000);
  const diffHr = Math.floor(diffMin / 60);
  const diffDay = Math.floor(diffHr / 24);

  if (diffMin < 1) return "just now";
  if (diffMin < 60) return `${diffMin}m ago`;
  if (diffHr < 24) return `${diffHr}h ago`;
  if (diffDay < 7) return `${diffDay}d ago`;
  return formatDate(d);
}

export function urgencyColor(urgency: Urgency): string {
  switch (urgency) {
    case "critical":
      return "bg-red-100 text-red-700 border-red-200";
    case "high":
      return "bg-orange-100 text-orange-700 border-orange-200";
    case "medium":
      return "bg-yellow-100 text-yellow-700 border-yellow-200";
    case "low":
      return "bg-green-100 text-green-700 border-green-200";
    default:
      return "bg-slate-100 text-slate-700 border-slate-200";
  }
}

export function urgencyDot(urgency: Urgency): string {
  switch (urgency) {
    case "critical":
      return "bg-red-500";
    case "high":
      return "bg-orange-500";
    case "medium":
      return "bg-yellow-500";
    case "low":
      return "bg-green-500";
    default:
      return "bg-slate-400";
  }
}

export function categoryColor(category: string): string {
  const map: Record<string, string> = {
    Work: "bg-blue-100 text-blue-700",
    Personal: "bg-pink-100 text-pink-700",
    "Customer Support": "bg-cyan-100 text-cyan-700",
    Sales: "bg-emerald-100 text-emerald-700",
    Finance: "bg-amber-100 text-amber-700",
    Meeting: "bg-violet-100 text-violet-700",
    "Application/Recruitment": "bg-indigo-100 text-indigo-700",
    Newsletter: "bg-teal-100 text-teal-700",
    Notification: "bg-slate-100 text-slate-700",
    Spam: "bg-red-100 text-red-700",
    Other: "bg-gray-100 text-gray-700",
  };
  return map[category] || "bg-gray-100 text-gray-700";
}

export function statusColor(status: string): string {
  switch (status) {
    case "unread":
      return "bg-blue-100 text-blue-700";
    case "read":
      return "bg-slate-100 text-slate-600";
    case "responded":
      return "bg-green-100 text-green-700";
    case "archived":
      return "bg-gray-100 text-gray-500";
    default:
      return "bg-slate-100 text-slate-600";
  }
}

export function confidenceLabel(confidence: number): string {
  if (confidence >= 0.85) return "High";
  if (confidence >= 0.65) return "Medium";
  return "Low";
}

export function toLocalDatetimeInput(date: Date): string {
  // Format: YYYY-MM-DDTHH:MM for datetime-local input
  const tzOffset = date.getTimezoneOffset() * 60000;
  const local = new Date(date.getTime() - tzOffset);
  return local.toISOString().slice(0, 16);
}
