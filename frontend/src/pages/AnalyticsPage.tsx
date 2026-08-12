import {
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from "recharts";
import {
  Mail,
  Clock,
  CheckCircle2,
  AlertTriangle,
  TrendingUp,
  Sparkles,
  Zap,
  Timer,
  Target,
} from "lucide-react";
import { useAnalytics } from "../hooks/queries";
import {
  StatCard,
  LoadingCard,
  ErrorState,
  EmptyState,
} from "../components/ui";
import { categoryColor } from "../utils/helpers";

// Color palette for charts

export function AnalyticsPage() {
  const { data: analytics, isLoading, isError, refetch } = useAnalytics();

  if (isLoading) {
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

  if (isError || !analytics) {
    return (
      <ErrorState
        message="Couldn't load analytics data."
        onRetry={() => refetch()}
      />
    );
  }

  if (analytics.total_emails === 0) {
    return (
      <EmptyState
        icon={BarChart as any}
        title="No analytics yet"
        description="Sync your emails to generate insights and analytics."
      />
    );
  }

  const categoryData = Object.entries(analytics.emails_by_category)
    .map(([name, value]) => ({ name, value }))
    .sort((a, b) => b.value - a.value);

  const urgencyData = Object.entries(analytics.emails_by_urgency).map(
    ([name, value]) => ({
      name: name.charAt(0).toUpperCase() + name.slice(1),
      value,
      fill:
        name === "critical"
          ? "#dc2626"
          : name === "high"
          ? "#ea580c"
          : name === "medium"
          ? "#ca8a04"
          : "#16a34a",
    })
  );

  const trendData = analytics.recent_trend.map((d) => ({
    ...d,
    date: new Date(d.date).toLocaleDateString("en-US", {
      month: "short",
      day: "numeric",
    }),
  }));

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-slate-900">Analytics</h1>
        <p className="text-sm text-slate-500">
          Response metrics, email insights, and AI performance
        </p>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard
          label="Total Emails"
          value={analytics.total_emails}
          icon={Mail}
          color="brand"
        />
        <StatCard
          label="Pending Responses"
          value={analytics.pending_responses}
          icon={Clock}
          color="amber"
        />
        <StatCard
          label="Response Rate"
          value={`${analytics.response_rate}%`}
          icon={Target}
          color="green"
        />
        <StatCard
          label="Avg Response Time"
          value={
            analytics.avg_response_time_hours
              ? `${analytics.avg_response_time_hours}h`
              : "—"
          }
          icon={Timer}
          color="blue"
        />
      </div>

      {/* Second row KPIs */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard
          label="Emails Requiring Response"
          value={analytics.emails_requiring_response}
          icon={AlertTriangle}
          color="orange"
        />
        <StatCard
          label="Emails Responded"
          value={analytics.emails_responded_to}
          icon={CheckCircle2}
          color="green"
        />
        <StatCard
          label="Follow-ups Completed"
          value={analytics.follow_ups_completed}
          icon={CheckCircle2}
          color="violet"
        />
        <StatCard
          label="Overdue Follow-ups"
          value={analytics.follow_ups_overdue}
          icon={Zap}
          color="red"
        />
      </div>

      {/* Trend Chart */}
      {trendData.length > 0 && (
        <div className="card">
          <h3 className="font-semibold text-slate-900 mb-4 flex items-center gap-2">
            <TrendingUp size={18} className="text-brand-500" />
            Email Volume Trend (Last 14 Days)
          </h3>
          <ResponsiveContainer width="100%" height={250}>
            <LineChart data={trendData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
              <XAxis dataKey="date" tick={{ fontSize: 12 }} />
              <YAxis allowDecimals={false} tick={{ fontSize: 12 }} />
              <Tooltip />
              <Line
                type="monotone"
                dataKey="count"
                stroke="#6366f1"
                strokeWidth={2}
                dot={{ r: 4 }}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
      )}

      {/* Category + Urgency charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Category distribution */}
        <div className="card">
          <h3 className="font-semibold text-slate-900 mb-4">
            Emails by Category
          </h3>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={categoryData} layout="vertical">
              <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
              <XAxis type="number" tick={{ fontSize: 12 }} />
              <YAxis
                type="category"
                dataKey="name"
                tick={{ fontSize: 11 }}
                width={120}
              />
              <Tooltip />
              <Bar dataKey="value" fill="#6366f1" radius={[0, 4, 4, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* Urgency distribution */}
        <div className="card">
          <h3 className="font-semibold text-slate-900 mb-4">
            Emails by Urgency
          </h3>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={urgencyData}
                cx="50%"
                cy="50%"
                outerRadius={100}
                dataKey="value"
                nameKey="name"
                label={(entry: any) => `${entry.name}: ${entry.value}`}
              >
                {urgencyData.map((entry, i) => (
                  <Cell key={i} fill={entry.fill} />
                ))}
              </Pie>
              <Tooltip />
              <Legend />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* AI Performance */}
      <div className="card">
        <h3 className="font-semibold text-slate-900 mb-4 flex items-center gap-2">
          <Sparkles size={18} className="text-brand-500" />
          AI Performance Metrics
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="bg-slate-50 rounded-lg p-4 text-center">
            <div className="text-3xl font-bold text-brand-600 mb-1">
              {analytics.ai_accuracy}%
            </div>
            <p className="text-sm text-slate-500">Categorization Accuracy</p>
            <p className="text-xs text-slate-400 mt-1">
              Based on user corrections
            </p>
          </div>
          <div className="bg-slate-50 rounded-lg p-4 text-center">
            <div className="text-3xl font-bold text-blue-600 mb-1">
              {analytics.reply_suggestions_generated}
            </div>
            <p className="text-sm text-slate-500">Replies Generated</p>
          </div>
          <div className="bg-slate-50 rounded-lg p-4 text-center">
            <div className="text-3xl font-bold text-green-600 mb-1">
              {analytics.reply_suggestions_used}
            </div>
            <p className="text-sm text-slate-500">Replies Used / Sent</p>
          </div>
        </div>
      </div>

      {/* Category breakdown table */}
      <div className="card">
        <h3 className="font-semibold text-slate-900 mb-4">
          Detailed Category Breakdown
        </h3>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-slate-200">
                <th className="text-left py-2 px-3 font-medium text-slate-600">
                  Category
                </th>
                <th className="text-right py-2 px-3 font-medium text-slate-600">
                  Count
                </th>
                <th className="text-right py-2 px-3 font-medium text-slate-600">
                  Percentage
                </th>
                <th className="py-2 px-3">Distribution</th>
              </tr>
            </thead>
            <tbody>
              {categoryData.map((cat) => {
                const pct = analytics.total_emails
                  ? Math.round((cat.value / analytics.total_emails) * 100)
                  : 0;
                return (
                  <tr
                    key={cat.name}
                    className="border-b border-slate-100 hover:bg-slate-50"
                  >
                    <td className="py-2 px-3">
                      <span className={`badge ${categoryColor(cat.name)}`}>
                        {cat.name}
                      </span>
                    </td>
                    <td className="text-right py-2 px-3 font-medium text-slate-700">
                      {cat.value}
                    </td>
                    <td className="text-right py-2 px-3 text-slate-500">
                      {pct}%
                    </td>
                    <td className="py-2 px-3">
                      <div className="w-full bg-slate-200 rounded-full h-2 overflow-hidden">
                        <div
                          className="bg-brand-500 h-full rounded-full"
                          style={{ width: `${pct}%` }}
                        />
                      </div>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
