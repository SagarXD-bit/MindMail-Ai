import { useState } from "react";
import { useParams, useNavigate, Link } from "react-router-dom";
import {
  ArrowLeft,
  Clock,
  Sparkles,
  Copy,
  RefreshCw,
  Send,
  Trash2,
  CheckCircle2,
  AlertCircle,
  ChevronDown,
  ChevronUp,
  MessageSquare,
  Mail,
} from "lucide-react";
import toast from "react-hot-toast";
import { useEmail, useInvalidateAll } from "../hooks/queries";
import {
  generateReply,
  updateReply,
  sendReply,
  updateClassification,
  updateEmailStatus,
  createFollowUp,
} from "../api/endpoints";
import {
  LoadingCard,
  ErrorState,
  Badge,
} from "../components/ui";
import { ConfirmDialog } from "../components/ConfirmDialog";
import {
  formatDateTime,
  categoryColor,
  urgencyDot,
  confidenceLabel,
  toLocalDatetimeInput,
} from "../utils/helpers";
import { CATEGORIES, URGENCIES, type ReplyTone } from "../types";

export function EmailDetailPage() {
  const { id } = useParams();
  const navigate = useNavigate();
  const emailId = id ? parseInt(id) : null;
  const { data: email, isLoading, isError, refetch } = useEmail(emailId);
  const invalidateAll = useInvalidateAll();

  const [generatingTone, setGeneratingTone] = useState<ReplyTone | null>(null);
  const [editingReply, setEditingReply] = useState<number | null>(null);
  const [editContent, setEditContent] = useState("");
  const [showSendConfirm, setShowSendConfirm] = useState<number | null>(null);
  const [showFollowUpForm, setShowFollowUpForm] = useState(false);
  const [followUpDate, setFollowUpDate] = useState(
    toLocalDatetimeInput(new Date(Date.now() + 86400000))
  );
  const [followUpNote, setFollowUpNote] = useState("");
  const [showThread, setShowThread] = useState(false);

  const handleGenerateReply = async (tone: ReplyTone) => {
    if (!emailId) return;
    setGeneratingTone(tone);
    try {
      await generateReply(emailId, tone);
      toast.success(`${tone} reply generated!`);
      refetch();
      invalidateAll();
    } catch (err: any) {
      toast.error(`Failed to generate reply: ${err.detail || err.message}`);
    } finally {
      setGeneratingTone(null);
    }
  };

  const handleSaveEdit = async (replyId: number) => {
    if (!emailId) return;
    try {
      await updateReply(emailId, replyId, { content: editContent });
      toast.success("Reply updated.");
      setEditingReply(null);
      refetch();
    } catch (err: any) {
      toast.error(`Failed to save: ${err.detail || err.message}`);
    }
  };

  const handleCopy = (content: string) => {
    navigator.clipboard.writeText(content);
    toast.success("Copied to clipboard!");
  };

  const handleDiscard = async (replyId: number) => {
    if (!emailId) return;
    try {
      await updateReply(emailId, replyId, { status: "discarded" });
      toast.success("Reply discarded.");
      refetch();
    } catch (err: any) {
      toast.error(`Failed: ${err.detail || err.message}`);
    }
  };

  const handleSend = async (replyId: number) => {
    if (!emailId) return;
    try {
      await sendReply(emailId, replyId);
      toast.success("Reply sent! Email marked as responded.");
      setShowSendConfirm(null);
      refetch();
      invalidateAll();
    } catch (err: any) {
      // The backend returns 200 with detail for demo mode (no SMTP)
      if (err.status === 200 || err.detail?.includes("demo")) {
        toast.success("Reply marked as sent (demo mode). Email marked as responded.");
        setShowSendConfirm(null);
        refetch();
        invalidateAll();
      } else {
        toast.error(`Failed to send: ${err.detail || err.message}`);
      }
    }
  };

  const handleMarkResponded = async () => {
    if (!emailId) return;
    try {
      await updateEmailStatus(emailId, "responded");
      toast.success("Marked as responded.");
      refetch();
      invalidateAll();
    } catch (err: any) {
      toast.error(`Failed: ${err.detail || err.message}`);
    }
  };

  const handleClassificationChange = async (
    field: "category" | "urgency",
    value: string
  ) => {
    if (!emailId) return;
    try {
      await updateClassification(emailId, { [field]: value });
      toast.success(`${field} updated.`);
      refetch();
      invalidateAll();
    } catch (err: any) {
      toast.error(`Failed: ${err.detail || err.message}`);
    }
  };

  const handleCreateFollowUp = async () => {
    if (!emailId) return;
    try {
      await createFollowUp({
        email_id: emailId,
        reminder_at: new Date(followUpDate).toISOString(),
        note: followUpNote || undefined,
      });
      toast.success("Follow-up reminder created!");
      setShowFollowUpForm(false);
      setFollowUpNote("");
      refetch();
      invalidateAll();
    } catch (err: any) {
      toast.error(`Failed: ${err.detail || err.message}`);
    }
  };

  if (isLoading) {
    return (
      <div className="space-y-4">
        <button
          onClick={() => navigate(-1)}
          className="text-sm text-slate-500 hover:text-slate-700 flex items-center gap-1"
        >
          <ArrowLeft size={16} /> Back
        </button>
        <LoadingCard />
        <LoadingCard />
      </div>
    );
  }

  if (isError || !email) {
    return (
      <div>
        <button
          onClick={() => navigate(-1)}
          className="text-sm text-slate-500 hover:text-slate-700 flex items-center gap-1 mb-4"
        >
          <ArrowLeft size={16} /> Back
        </button>
        <ErrorState
          message="This email couldn't be found or loaded."
          onRetry={() => navigate("/inbox")}
        />
      </div>
    );
  }

  const cls = email.classification;

  return (
    <div className="space-y-6">
      {/* Back button */}
      <button
        onClick={() => navigate(-1)}
        className="text-sm text-slate-500 hover:text-slate-700 flex items-center gap-1"
      >
        <ArrowLeft size={16} /> Back to inbox
      </button>

      {/* Email header */}
      <div className="card">
        <div className="flex items-start justify-between gap-4 mb-4">
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-2 mb-2">
              {email.is_demo && (
                <span className="badge bg-purple-100 text-purple-700">DEMO</span>
              )}
              <span className={`badge ${categoryColor(email.status)}`}>
                {email.status}
              </span>
            </div>
            <h1 className="text-xl font-bold text-slate-900 mb-2">
              {email.subject}
            </h1>
            <div className="flex items-center gap-3 text-sm text-slate-500">
              <div className="flex items-center gap-2">
                <div className="w-8 h-8 rounded-full bg-brand-100 flex items-center justify-center">
                  <Mail size={14} className="text-brand-600" />
                </div>
                <div>
                  <p className="font-medium text-slate-700">
                    {email.sender_name || email.sender_email}
                  </p>
                  <p className="text-xs">{email.sender_email}</p>
                </div>
              </div>
              <span className="text-slate-300">→</span>
              <p className="text-xs">{email.recipient_email}</p>
              <span className="text-xs ml-auto">
                {formatDateTime(email.received_at)}
              </span>
            </div>
          </div>
        </div>

        {/* AI Classification */}
        {cls && (
          <div className="bg-slate-50 rounded-lg p-4 border border-slate-200">
            <div className="flex items-center gap-2 mb-3">
              <Sparkles size={16} className="text-brand-500" />
              <span className="text-sm font-semibold text-slate-700">
                AI Analysis
              </span>
              {cls.is_manual_override && (
                <span className="badge bg-amber-100 text-amber-700">
                  Manually adjusted
                </span>
              )}
            </div>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-3">
              <div>
                <label className="text-xs text-slate-500">Category</label>
                <select
                  value={cls.category}
                  onChange={(e) =>
                    handleClassificationChange("category", e.target.value)
                  }
                  className={`input mt-0.5 text-xs font-medium cursor-pointer ${categoryColor(cls.category)}`}
                >
                  {CATEGORIES.map((c) => (
                    <option key={c} value={c}>
                      {c}
                    </option>
                  ))}
                </select>
              </div>
              <div>
                <label className="text-xs text-slate-500">Urgency</label>
                <select
                  value={cls.urgency}
                  onChange={(e) =>
                    handleClassificationChange("urgency", e.target.value)
                  }
                  className="input mt-0.5 text-xs font-medium cursor-pointer"
                >
                  {URGENCIES.map((u) => (
                    <option key={u} value={u}>
                      {u.charAt(0).toUpperCase() + u.slice(1)}
                    </option>
                  ))}
                </select>
              </div>
              <div>
                <label className="text-xs text-slate-500">Confidence</label>
                <div className="mt-0.5 flex items-center gap-2">
                  <div className="flex-1 bg-slate-200 rounded-full h-2 overflow-hidden">
                    <div
                      className="bg-brand-500 h-full rounded-full"
                      style={{ width: `${cls.confidence * 100}%` }}
                    />
                  </div>
                  <span className="text-xs font-medium text-slate-600">
                    {confidenceLabel(cls.confidence)}
                  </span>
                </div>
              </div>
              <div>
                <label className="text-xs text-slate-500">Needs Response</label>
                <div className="mt-0.5">
                  {cls.needs_response ? (
                    <Badge className="bg-blue-100 text-blue-700">
                      <AlertCircle size={11} /> Yes
                    </Badge>
                  ) : (
                    <Badge className="bg-slate-100 text-slate-500">No</Badge>
                  )}
                </div>
              </div>
            </div>
            {cls.explanation && (
              <p className="text-xs text-slate-500 italic">"{cls.explanation}"</p>
            )}
          </div>
        )}

        {/* Actions */}
        <div className="flex flex-wrap gap-2 mt-4">
          {email.status !== "responded" && (
            <button
              onClick={handleMarkResponded}
              className="btn-secondary text-sm"
            >
              <CheckCircle2 size={14} /> Mark as Responded
            </button>
          )}
          <button
            onClick={() => setShowFollowUpForm(!showFollowUpForm)}
            className="btn-secondary text-sm"
          >
            <Clock size={14} /> Create Follow-up
          </button>
        </div>

        {/* Follow-up form */}
        {showFollowUpForm && (
          <div className="mt-4 p-4 bg-amber-50 rounded-lg border border-amber-200 space-y-3">
            <h4 className="text-sm font-semibold text-slate-700">
              Create Follow-up Reminder
            </h4>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              <div>
                <label className="label">Reminder Date & Time</label>
                <input
                  type="datetime-local"
                  value={followUpDate}
                  onChange={(e) => setFollowUpDate(e.target.value)}
                  className="input"
                />
              </div>
              <div>
                <label className="label">Note (optional)</label>
                <input
                  type="text"
                  value={followUpNote}
                  onChange={(e) => setFollowUpNote(e.target.value)}
                  placeholder="e.g. Check if they replied"
                  className="input"
                />
              </div>
            </div>
            <div className="flex gap-2">
              <button onClick={handleCreateFollowUp} className="btn-primary text-sm">
                Create Reminder
              </button>
              <button
                onClick={() => setShowFollowUpForm(false)}
                className="btn-secondary text-sm"
              >
                Cancel
              </button>
            </div>
          </div>
        )}
      </div>

      {/* Email body */}
      <div className="card">
        <h3 className="font-semibold text-slate-900 mb-3">Message</h3>
        <div className="prose prose-sm max-w-none">
          <pre className="whitespace-pre-wrap font-sans text-sm text-slate-700 leading-relaxed">
            {email.body_text || "No content available."}
          </pre>
        </div>
      </div>

      {/* Thread */}
      {email.thread.length > 0 && (
        <div className="card">
          <button
            onClick={() => setShowThread(!showThread)}
            className="flex items-center justify-between w-full"
          >
            <h3 className="font-semibold text-slate-900 flex items-center gap-2">
              <MessageSquare size={18} />
              Conversation Thread ({email.thread.length})
            </h3>
            {showThread ? <ChevronUp size={18} /> : <ChevronDown size={18} />}
          </button>
          {showThread && (
            <div className="mt-4 space-y-3">
              {email.thread.map((t) => (
                <Link
                  key={t.id}
                  to={`/emails/${t.id}`}
                  className="block p-3 rounded-lg bg-slate-50 hover:bg-slate-100 transition-colors"
                >
                  <div className="flex items-center gap-2 mb-1">
                    <div
                      className={`w-2 h-2 rounded-full ${
                        t.classification
                          ? urgencyDot(t.classification.urgency)
                          : "bg-slate-300"
                      }`}
                    />
                    <span className="text-sm font-medium text-slate-700">
                      {t.sender_name || t.sender_email}
                    </span>
                    <span className="text-xs text-slate-400 ml-auto">
                      {formatDateTime(t.received_at)}
                    </span>
                  </div>
                  <p className="text-sm text-slate-600 truncate">{t.subject}</p>
                </Link>
              ))}
            </div>
          )}
        </div>
      )}

      {/* AI Reply Suggestions */}
      <div className="card">
        <div className="flex items-center justify-between mb-4">
          <h3 className="font-semibold text-slate-900 flex items-center gap-2">
            <Sparkles size={18} className="text-brand-500" />
            AI Reply Suggestions
          </h3>
        </div>

        {/* Generate buttons */}
        <div className="flex flex-wrap gap-2 mb-4">
          {(["professional", "friendly", "concise"] as ReplyTone[]).map((tone) => (
            <button
              key={tone}
              onClick={() => handleGenerateReply(tone)}
              disabled={generatingTone !== null}
              className="btn-secondary text-sm capitalize"
            >
              {generatingTone === tone ? (
                <RefreshCw size={14} className="animate-spin" />
              ) : (
                <Sparkles size={14} />
              )}
              {tone}
            </button>
          ))}
        </div>

        {/* Replies */}
        {email.replies.length === 0 ? (
          <p className="text-sm text-slate-400 py-4 text-center">
            Click a tone above to generate an AI reply suggestion.
          </p>
        ) : (
          <div className="space-y-3">
            {email.replies.map((reply) => (
              <div
                key={reply.id}
                className={`rounded-lg border p-4 ${
                  reply.status === "discarded"
                    ? "border-slate-200 bg-slate-50 opacity-60"
                    : "border-brand-200 bg-brand-50/30"
                }`}
              >
                <div className="flex items-center justify-between mb-2">
                  <div className="flex items-center gap-2">
                    <span className="badge bg-brand-100 text-brand-700 capitalize">
                      {reply.tone}
                    </span>
                    <span className="badge bg-slate-100 text-slate-500">
                      {reply.status}
                    </span>
                  </div>
                  <span className="text-xs text-slate-400">
                    {formatDateTime(reply.created_at)}
                  </span>
                </div>

                {editingReply === reply.id ? (
                  <div className="space-y-2">
                    <textarea
                      value={editContent}
                      onChange={(e) => setEditContent(e.target.value)}
                      rows={8}
                      className="input font-mono text-sm"
                    />
                    <div className="flex gap-2">
                      <button
                        onClick={() => handleSaveEdit(reply.id)}
                        className="btn-primary text-sm"
                      >
                        Save
                      </button>
                      <button
                        onClick={() => setEditingReply(null)}
                        className="btn-secondary text-sm"
                      >
                        Cancel
                      </button>
                    </div>
                  </div>
                ) : (
                  <>
                    <pre className="whitespace-pre-wrap font-sans text-sm text-slate-700 leading-relaxed mb-3">
                      {reply.content}
                    </pre>
                    {reply.status !== "discarded" && (
                      <div className="flex flex-wrap gap-2">
                        <button
                          onClick={() => {
                            setEditingReply(reply.id);
                            setEditContent(reply.content);
                          }}
                          className="btn-ghost text-xs"
                        >
                          Edit
                        </button>
                        <button
                          onClick={() => handleCopy(reply.content)}
                          className="btn-ghost text-xs"
                        >
                          <Copy size={12} /> Copy
                        </button>
                        <button
                          onClick={() => setShowSendConfirm(reply.id)}
                          className="btn-primary text-xs"
                        >
                          <Send size={12} /> Send
                        </button>
                        <button
                          onClick={() => handleDiscard(reply.id)}
                          className="btn-ghost text-xs text-red-500 hover:bg-red-50"
                        >
                          <Trash2 size={12} /> Discard
                        </button>
                      </div>
                    )}
                  </>
                )}
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Send confirmation dialog */}
      <ConfirmDialog
        open={showSendConfirm !== null}
        title="Send this reply?"
        message="This will send the reply via email and mark the email as responded. This action cannot be undone."
        confirmLabel="Send Reply"
        danger
        onConfirm={() => showSendConfirm && handleSend(showSendConfirm)}
        onCancel={() => setShowSendConfirm(null)}
      />
    </div>
  );
}
