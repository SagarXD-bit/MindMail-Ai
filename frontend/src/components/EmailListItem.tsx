import { Link } from "react-router-dom";
import { Reply, Clock, AlertCircle } from "lucide-react";
import type { EmailBrief } from "../types";
import {
  formatRelative,
  urgencyDot,
  categoryColor,
  statusColor,
} from "../utils/helpers";

export function EmailListItem({ email }: { email: EmailBrief }) {
  const cls = email.classification;
  const isUnread = email.status === "unread";

  return (
    <Link
      to={`/emails/${email.id}`}
      className={`block p-4 rounded-xl border transition-all hover:shadow-md hover:border-brand-300 ${
        isUnread
          ? "bg-white border-slate-200"
          : "bg-slate-50/50 border-slate-200"
      }`}
    >
      <div className="flex items-start gap-3">
        {/* Urgency indicator */}
        <div className="flex flex-col items-center gap-2 pt-1">
          <div
            className={`w-2.5 h-2.5 rounded-full ${
              cls ? urgencyDot(cls.urgency) : "bg-slate-300"
            }`}
          />
        </div>

        {/* Content */}
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 mb-1">
            <span
              className={`text-sm truncate ${
                isUnread ? "font-semibold text-slate-900" : "text-slate-600"
              }`}
            >
              {email.sender_name || email.sender_email}
            </span>
            {email.is_demo && (
              <span className="badge bg-purple-100 text-purple-700 text-[10px]">
                DEMO
              </span>
            )}
            {email.has_followup && (
              <Clock size={13} className="text-amber-500 flex-shrink-0" />
            )}
            {email.has_replies && (
              <Reply size={13} className="text-blue-500 flex-shrink-0" />
            )}
            <span className="text-xs text-slate-400 ml-auto flex-shrink-0">
              {formatRelative(email.received_at)}
            </span>
          </div>

          <h3
            className={`text-sm mb-1 truncate ${
              isUnread ? "font-semibold text-slate-900" : "text-slate-700"
            }`}
          >
            {email.subject}
          </h3>

          <p className="text-xs text-slate-500 line-clamp-1 mb-2">
            {email.preview || "No preview available"}
          </p>

          {/* Badges */}
          <div className="flex items-center gap-2 flex-wrap">
            {cls && (
              <>
                <span className={`badge ${categoryColor(cls.category)}`}>
                  {cls.category}
                </span>
                <span
                  className={`badge border ${
                    cls.urgency === "critical"
                      ? "bg-red-100 text-red-700 border-red-200"
                      : cls.urgency === "high"
                      ? "bg-orange-100 text-orange-700 border-orange-200"
                      : cls.urgency === "medium"
                      ? "bg-yellow-100 text-yellow-700 border-yellow-200"
                      : "bg-green-100 text-green-700 border-green-200"
                  }`}
                >
                  {cls.urgency}
                </span>
                {cls.needs_response && (
                  <span className="badge bg-blue-50 text-blue-600">
                    <AlertCircle size={11} /> Needs response
                  </span>
                )}
              </>
            )}
            <span className={`badge ${statusColor(email.status)} ml-auto`}>
              {email.status}
            </span>
          </div>
        </div>
      </div>
    </Link>
  );
}
