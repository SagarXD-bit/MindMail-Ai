import { useState } from "react";
import { Link } from "react-router-dom";
import {
  Clock,
  CheckCircle2,
  AlertTriangle,
  Calendar,
  Bell,
  Trash2,
  Plus,
} from "lucide-react";
import toast from "react-hot-toast";
import { useFollowUps } from "../hooks/queries";
import { updateFollowUp, deleteFollowUp } from "../api/endpoints";
import {
  LoadingCard,
  EmptyState,
  ErrorState,
} from "../components/ui";
import { ConfirmDialog } from "../components/ConfirmDialog";
import { formatDateTime, formatRelative } from "../utils/helpers";

type Tab = "upcoming" | "overdue" | "completed" | "all";

export function FollowUpsPage() {
  const [tab, setTab] = useState<Tab>("upcoming");
  const [deleteId, setDeleteId] = useState<number | null>(null);

  // Map tab to API status param
  const statusParam =
    tab === "upcoming"
      ? "upcoming"
      : tab === "overdue"
      ? "overdue"
      : tab === "completed"
      ? "completed"
      : undefined;

  const { data, isLoading, isError, refetch } = useFollowUps(statusParam);

  const handleComplete = async (id: number) => {
    try {
      await updateFollowUp(id, { status: "completed" });
      toast.success("Follow-up marked as completed!");
      refetch();
    } catch (err: any) {
      toast.error(`Failed: ${err.detail || err.message}`);
    }
  };

  const handleSnooze = async (id: number) => {
    const snoozed = new Date(Date.now() + 86400000); // +1 day
    try {
      await updateFollowUp(id, {
        status: "snoozed",
        reminder_at: snoozed.toISOString(),
      });
      toast.success("Snoozed for 24 hours.");
      refetch();
    } catch (err: any) {
      toast.error(`Failed: ${err.detail || err.message}`);
    }
  };

  const handleDelete = async () => {
    if (!deleteId) return;
    try {
      await deleteFollowUp(deleteId);
      toast.success("Follow-up deleted.");
      setDeleteId(null);
      refetch();
    } catch (err: any) {
      toast.error(`Failed: ${err.detail || err.message}`);
    }
  };

  const followUps = data || [];

  const tabs: { key: Tab; label: string; icon: typeof Clock }[] = [
    { key: "upcoming", label: "Upcoming", icon: Calendar },
    { key: "overdue", label: "Overdue", icon: AlertTriangle },
    { key: "completed", label: "Completed", icon: CheckCircle2 },
    { key: "all", label: "All", icon: Bell },
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-slate-900">Follow-ups</h1>
        <p className="text-sm text-slate-500">
          Track reminders and stay on top of important responses
        </p>
      </div>

      {/* Tabs */}
      <div className="flex gap-1 border-b border-slate-200 overflow-x-auto">
        {tabs.map((t) => (
          <button
            key={t.key}
            onClick={() => setTab(t.key)}
            className={`flex items-center gap-2 px-4 py-2.5 text-sm font-medium border-b-2 transition-colors whitespace-nowrap ${
              tab === t.key
                ? "border-brand-600 text-brand-600"
                : "border-transparent text-slate-500 hover:text-slate-700"
            }`}
          >
            <t.icon size={16} />
            {t.label}
          </button>
        ))}
      </div>

      {/* Content */}
      {isLoading ? (
        <div className="space-y-3">
          <LoadingCard />
          <LoadingCard />
        </div>
      ) : isError ? (
        <ErrorState
          message="Couldn't load follow-ups."
          onRetry={() => refetch()}
        />
      ) : followUps.length === 0 ? (
        <EmptyState
          icon={Clock}
          title={`No ${tab} follow-ups`}
          description={
            tab === "overdue"
              ? "Great! You're all caught up on your reminders."
              : tab === "completed"
              ? "Completed follow-ups will appear here."
              : "Open an email and create a follow-up reminder to get started."
          }
          action={
            (tab === "upcoming" || tab === "all") && (
              <Link to="/inbox" className="btn-primary">
                <Plus size={16} /> Browse Emails
              </Link>
            )
          }
        />
      ) : (
        <div className="space-y-3">
          {followUps.map((fu) => {
            const isOverdue =
              fu.status === "pending" && new Date(fu.reminder_at) < new Date();
            return (
              <div
                key={fu.id}
                className={`card border-l-4 ${
                  isOverdue
                    ? "border-l-red-500"
                    : fu.status === "completed"
                    ? "border-l-green-500"
                    : "border-l-amber-500"
                }`}
              >
                <div className="flex items-start gap-3">
                  <div
                    className={`w-10 h-10 rounded-lg flex items-center justify-center flex-shrink-0 ${
                      isOverdue
                        ? "bg-red-50"
                        : fu.status === "completed"
                        ? "bg-green-50"
                        : "bg-amber-50"
                    }`}
                  >
                    {fu.status === "completed" ? (
                      <CheckCircle2 className="text-green-500" size={20} />
                    ) : isOverdue ? (
                      <AlertTriangle className="text-red-500" size={20} />
                    ) : (
                      <Clock className="text-amber-500" size={20} />
                    )}
                  </div>
                  <div className="flex-1 min-w-0">
                    {fu.email && (
                      <Link
                        to={`/emails/${fu.email_id}`}
                        className="text-sm font-semibold text-slate-900 hover:text-brand-600 block truncate"
                      >
                        {fu.email.subject}
                      </Link>
                    )}
                    <p className="text-xs text-slate-500 mt-0.5">
                      From: {fu.email?.sender_name || fu.email?.sender_email}
                    </p>
                    <div className="flex items-center gap-3 mt-2">
                      <span
                        className={`text-xs font-medium ${
                          isOverdue ? "text-red-600" : "text-slate-600"
                        }`}
                      >
                        {isOverdue ? "Overdue" : "Due"}:{" "}
                        {formatDateTime(fu.reminder_at)} ({formatRelative(fu.reminder_at)})
                      </span>
                      <span className="badge bg-slate-100 text-slate-600">
                        {fu.status}
                      </span>
                    </div>
                    {fu.note && (
                      <p className="text-sm text-slate-600 mt-2 italic">
                        "{fu.note}"
                      </p>
                    )}
                    {/* Actions */}
                    {fu.status !== "completed" && (
                      <div className="flex flex-wrap gap-2 mt-3">
                        <button
                          onClick={() => handleComplete(fu.id)}
                          className="btn-secondary text-xs"
                        >
                          <CheckCircle2 size={12} /> Complete
                        </button>
                        <button
                          onClick={() => handleSnooze(fu.id)}
                          className="btn-secondary text-xs"
                        >
                          <Clock size={12} /> Snooze 24h
                        </button>
                        <button
                          onClick={() => setDeleteId(fu.id)}
                          className="btn-ghost text-xs text-red-500 hover:bg-red-50"
                        >
                          <Trash2 size={12} /> Delete
                        </button>
                      </div>
                    )}
                    {fu.status === "completed" && fu.completed_at && (
                      <p className="text-xs text-green-600 mt-2">
                        Completed {formatRelative(fu.completed_at)}
                      </p>
                    )}
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      )}

      {/* Delete confirm */}
      <ConfirmDialog
        open={deleteId !== null}
        title="Delete this follow-up?"
        message="This reminder will be permanently removed."
        confirmLabel="Delete"
        danger
        onConfirm={handleDelete}
        onCancel={() => setDeleteId(null)}
      />
    </div>
  );
}
