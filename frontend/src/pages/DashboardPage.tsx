import { Link } from "react-router-dom";
import {
  Mail,
  AlertTriangle,
  Clock,
  CheckCircle2,
  TrendingUp,
  ArrowRight,
  Zap,
} from "lucide-react";
import {
  PieChart,
  Pie,
  Cell,
  ResponsiveContainer,
  Tooltip,
} from "recharts";
import { useAnalytics, useEmails, useFollowUps } from "../hooks/queries";
import {
  StatCard,
  LoadingCard,
  ErrorState,
  EmptyState,
} from "../components/ui";
import { EmailListItem } from "../components/EmailListItem";
import { categoryColor } from "../utils/helpers";

const PIE_COLORS = [
  "#6366f1", "#ec4899", "#06b6d4", "#10b981", "#f59e0b",
  "#8b5cf6", "#6366f1", "#14b8a6", "#64748b", "#ef4444", "#9ca3af",
];

export function DashboardPage() {
  const { data: analytics, isLoading: aLoading, isError: aError } = useAnalytics();
  const { data: emailsData, isLoading: eLoading } = useEmails({
    page_size: 5,
    sort: "newest",
  });
  const { data: upcomingFollowUps } = useFollowUps("upcoming");
  const { data: urgentEmails } = useEmails({
    urgency: "critical",
    page_size: 3,
  });

  if (aLoading || eLoading) {
    return (
      <div className="space-y-6">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <LoadingCard />
          <LoadingCard />
          <LoadingCard />
          <LoadingCard />
        </div>
        <LoadingCard />
      </div>
    );
  }

  if (aError) {
    return (
      <ErrorState
        message="Couldn't load analytics data."
        onRetry={() => window.location.reload()}
      />
    );
  }

  const categoryData = analytics
    ? Object.entries(analytics.emails_by_category).map(([name, value]) => ({
        name,
        value,
      }))
    : [];

  const recentEmails = emailsData?.emails || [];
  const urgent = urgentEmails?.emails || [];

  return (
    <div className="space-y-6">
      {/* Page header */}
      <div className="flex items-center justify-between flex-wrap gap-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">Dashboard</h1>
          <p className="text-sm text-slate-500">
            Overview of your email activity and AI insights
          </p>
        </div>
        <div className="flex gap-2">
          <Link to="/inbox?urgency=critical" className="btn-secondary">
            <Zap size={16} /> Urgent
          </Link>
          <Link to="/inbox" className="btn-primary">
            <Mail size={16} /> View Inbox
          </Link>
        </div>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard
          label="Total Emails"
          value={analytics?.total_emails ?? 0}
          icon={Mail}
          color="brand"
        />
        <StatCard
          label="Urgent / Critical"
          value={
            (analytics?.emails_by_urgency?.critical || 0)
          }
          icon={AlertTriangle}
          color="red"
          subtitle={`${analytics?.pending_responses ?? 0} pending responses`}
        />
        <StatCard
          label="Pending Replies"
          value={analytics?.pending_responses ?? 0}
          icon={Clock}
          color="amber"
        />
        <StatCard
          label="Responded"
          value={analytics?.emails_responded_to ?? 0}
          icon={CheckCircle2}
          color="green"
          subtitle={`${analytics?.response_rate ?? 0}% response rate`}
        />
      </div>

      {/* Charts + Quick Info */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Category distribution */}
        <div className="card lg:col-span-1">
          <h3 className="font-semibold text-slate-900 mb-4">Category Distribution</h3>
          {categoryData.length > 0 ? (
            <ResponsiveContainer width="100%" height={250}>
              <PieChart>
                <Pie
                  data={categoryData}
                  cx="50%"
                  cy="50%"
                  outerRadius={80}
                  innerRadius={40}
                  dataKey="value"
                  nameKey="name"
                >
                  {categoryData.map((_, i) => (
                    <Cell key={i} fill={PIE_COLORS[i % PIE_COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          ) : (
            <p className="text-sm text-slate-400 py-12 text-center">
              No data yet. Sync your emails to see insights.
            </p>
          )}
          <div className="mt-3 flex flex-wrap gap-1.5">
            {categoryData.slice(0, 6).map((cat) => (
              <span
                key={cat.name}
                className={`badge ${categoryColor(cat.name)}`}
              >
                {cat.name}: {cat.value}
              </span>
            ))}
          </div>
        </div>

        {/* Upcoming follow-ups */}
        <div className="card lg:col-span-2">
          <div className="flex items-center justify-between mb-4">
            <h3 className="font-semibold text-slate-900">Upcoming Follow-ups</h3>
            <Link
              to="/follow-ups"
              className="text-sm text-brand-600 hover:text-brand-700 flex items-center gap-1"
            >
              View all <ArrowRight size={14} />
            </Link>
          </div>
          {(upcomingFollowUps || []).length > 0 ? (
            <div className="space-y-2">
              {upcomingFollowUps!.slice(0, 4).map((fu) => (
                <Link
                  key={fu.id}
                  to={`/emails/${fu.email_id}`}
                  className="flex items-center gap-3 p-3 rounded-lg hover:bg-slate-50 transition-colors"
                >
                  <div className="w-10 h-10 rounded-lg bg-amber-50 flex items-center justify-center flex-shrink-0">
                    <Clock className="text-amber-500" size={18} />
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium text-slate-900 truncate">
                      {fu.email?.subject}
                    </p>
                    <p className="text-xs text-slate-500">
                      Due: {new Date(fu.reminder_at).toLocaleString()}
                      {fu.note && ` • ${fu.note}`}
                    </p>
                  </div>
                </Link>
              ))}
            </div>
          ) : (
            <EmptyState
              icon={Clock}
              title="No upcoming follow-ups"
              description="Create follow-up reminders to stay on top of important emails."
            />
          )}
        </div>
      </div>

      {/* Urgent emails + Recent emails */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Urgent */}
        <div>
          <div className="flex items-center justify-between mb-3">
            <h3 className="font-semibold text-slate-900 flex items-center gap-2">
              <AlertTriangle size={18} className="text-red-500" />
              Urgent Emails
            </h3>
            <Link
              to="/inbox?urgency=critical"
              className="text-sm text-brand-600 hover:text-brand-700 flex items-center gap-1"
            >
              View all <ArrowRight size={14} />
            </Link>
          </div>
          {urgent.length > 0 ? (
            <div className="space-y-2">
              {urgent.map((e) => (
                <EmailListItem key={e.id} email={e} />
              ))}
            </div>
          ) : (
            <div className="card text-center py-8">
              <p className="text-sm text-slate-400">No urgent emails 🎉</p>
            </div>
          )}
        </div>

        {/* Recent */}
        <div>
          <div className="flex items-center justify-between mb-3">
            <h3 className="font-semibold text-slate-900 flex items-center gap-2">
              <TrendingUp size={18} className="text-brand-500" />
              Recent Emails
            </h3>
            <Link
              to="/inbox"
              className="text-sm text-brand-600 hover:text-brand-700 flex items-center gap-1"
            >
              View all <ArrowRight size={14} />
            </Link>
          </div>
          {recentEmails.length > 0 ? (
            <div className="space-y-2">
              {recentEmails.map((e) => (
                <EmailListItem key={e.id} email={e} />
              ))}
            </div>
          ) : (
            <div className="card text-center py-8">
              <p className="text-sm text-slate-400">No emails yet. Sync to load.</p>
            </div>
          )}
        </div>
      </div>

      {/* AI Metrics */}
      {analytics && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="card flex items-center gap-4">
            <div className="w-12 h-12 rounded-xl bg-violet-50 flex items-center justify-center">
              <TrendingUp className="text-violet-600" size={22} />
            </div>
            <div>
              <p className="text-2xl font-bold text-slate-900">
                {analytics.ai_accuracy}%
              </p>
              <p className="text-sm text-slate-500">AI Categorization Accuracy</p>
            </div>
          </div>
          <div className="card flex items-center gap-4">
            <div className="w-12 h-12 rounded-xl bg-blue-50 flex items-center justify-center">
              <Mail className="text-blue-600" size={22} />
            </div>
            <div>
              <p className="text-2xl font-bold text-slate-900">
                {analytics.reply_suggestions_generated}
              </p>
              <p className="text-sm text-slate-500">Reply Suggestions Generated</p>
            </div>
          </div>
          <div className="card flex items-center gap-4">
            <div className="w-12 h-12 rounded-xl bg-green-50 flex items-center justify-center">
              <CheckCircle2 className="text-green-600" size={22} />
            </div>
            <div>
              <p className="text-2xl font-bold text-slate-900">
                {analytics.follow_ups_completed}
              </p>
              <p className="text-sm text-slate-500">Follow-ups Completed</p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
