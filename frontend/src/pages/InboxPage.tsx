import { useState, useEffect } from "react";
import { useSearchParams } from "react-router-dom";
import { Search, Filter, RefreshCw, Inbox as InboxIcon } from "lucide-react";
import { useEmails, useSyncEmails } from "../hooks/queries";
import { EmailListItem } from "../components/EmailListItem";
import {
  LoadingCard,
  EmptyState,
  ErrorState,
} from "../components/ui";
import { CATEGORIES, URGENCIES } from "../types";
import toast from "react-hot-toast";

export function InboxPage() {
  const [searchParams, setSearchParams] = useSearchParams();
  const [search, setSearch] = useState(searchParams.get("search") || "");
  const [debouncedSearch, setDebouncedSearch] = useState(search);
  const [showFilters, setShowFilters] = useState(false);
  const syncMutation = useSyncEmails();

  const filters = {
    search: debouncedSearch || undefined,
    category: searchParams.get("category") || undefined,
    urgency: searchParams.get("urgency") || undefined,
    status: searchParams.get("status") || undefined,
    follow_up: searchParams.get("follow_up") || undefined,
    sort: searchParams.get("sort") || "newest",
  };

  const { data, isLoading, isError, refetch } = useEmails({
    ...filters,
    page_size: 50,
  });

  // Debounce search
  useEffect(() => {
    const timer = setTimeout(() => setDebouncedSearch(search), 300);
    return () => clearTimeout(timer);
  }, [search]);

  const updateFilter = (key: string, value: string | null) => {
    const newParams = new URLSearchParams(searchParams);
    if (value && value !== "all") {
      newParams.set(key, value);
    } else {
      newParams.delete(key);
    }
    setSearchParams(newParams);
  };

  const handleSync = () => {
    toast.promise(syncMutation.mutateAsync(false), {
      loading: "Syncing emails...",
      success: (res) => res.message,
      error: (err) => `Sync failed: ${err.detail || err.message}`,
    });
  };

  const emails = data?.emails || [];
  const activeFilterCount = [
    filters.category,
    filters.urgency,
    filters.status,
    filters.follow_up,
  ].filter(Boolean).length;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between flex-wrap gap-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">Inbox</h1>
          <p className="text-sm text-slate-500">
            {data?.total ?? 0} {data?.total === 1 ? "email" : "emails"}
            {activeFilterCount > 0 && ` • ${activeFilterCount} filter${activeFilterCount > 1 ? "s" : ""} active`}
          </p>
        </div>
        <button
          onClick={handleSync}
          disabled={syncMutation.isPending}
          className="btn-primary"
        >
          <RefreshCw
            size={16}
            className={syncMutation.isPending ? "animate-spin" : ""}
          />
          {syncMutation.isPending ? "Syncing..." : "Sync"}
        </button>
      </div>

      {/* Search bar */}
      <div className="flex gap-2">
        <div className="relative flex-1">
          <Search
            size={18}
            className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400"
          />
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search by sender, subject, or content..."
            className="input pl-10"
          />
        </div>
        <button
          onClick={() => setShowFilters(!showFilters)}
          className={`btn-secondary ${activeFilterCount > 0 ? "ring-2 ring-brand-300" : ""}`}
        >
          <Filter size={16} />
          Filters
          {activeFilterCount > 0 && (
            <span className="badge bg-brand-600 text-white">
              {activeFilterCount}
            </span>
          )}
        </button>
        <select
          value={filters.sort}
          onChange={(e) => updateFilter("sort", e.target.value)}
          className="input w-auto"
        >
          <option value="newest">Newest</option>
          <option value="oldest">Oldest</option>
          <option value="urgency">Urgency</option>
        </select>
      </div>

      {/* Filter panel */}
      {showFilters && (
        <div className="card grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <div>
            <label className="label">Category</label>
            <select
              value={filters.category || "all"}
              onChange={(e) => updateFilter("category", e.target.value)}
              className="input"
            >
              <option value="all">All Categories</option>
              {CATEGORIES.map((c) => (
                <option key={c} value={c}>
                  {c}
                </option>
              ))}
            </select>
          </div>
          <div>
            <label className="label">Urgency</label>
            <select
              value={filters.urgency || "all"}
              onChange={(e) => updateFilter("urgency", e.target.value)}
              className="input"
            >
              <option value="all">All Urgency Levels</option>
              {URGENCIES.map((u) => (
                <option key={u} value={u}>
                  {u.charAt(0).toUpperCase() + u.slice(1)}
                </option>
              ))}
            </select>
          </div>
          <div>
            <label className="label">Status</label>
            <select
              value={filters.status || "all"}
              onChange={(e) => updateFilter("status", e.target.value)}
              className="input"
            >
              <option value="all">All Statuses</option>
              <option value="unread">Unread</option>
              <option value="read">Read</option>
              <option value="responded">Responded</option>
              <option value="archived">Archived</option>
            </select>
          </div>
          <div>
            <label className="label">Follow-up</label>
            <select
              value={filters.follow_up || "all"}
              onChange={(e) => updateFilter("follow_up", e.target.value)}
              className="input"
            >
              <option value="all">All Emails</option>
              <option value="pending">Has Pending Follow-up</option>
              <option value="completed">Follow-up Completed</option>
              <option value="none">No Follow-up</option>
            </select>
          </div>
        </div>
      )}

      {/* Email list */}
      {isLoading ? (
        <div className="space-y-3">
          <LoadingCard />
          <LoadingCard />
          <LoadingCard />
        </div>
      ) : isError ? (
        <ErrorState
          message="Couldn't load emails. Please try syncing."
          onRetry={() => refetch()}
        />
      ) : emails.length === 0 ? (
        <EmptyState
          icon={InboxIcon}
          title="No emails found"
          description={
            debouncedSearch || activeFilterCount > 0
              ? "Try adjusting your search or filters."
              : "Sync your inbox to load emails, or try demo mode."
          }
          action={
            !debouncedSearch &&
            activeFilterCount === 0 && (
              <button onClick={handleSync} className="btn-primary">
                <RefreshCw size={16} /> Sync Now
              </button>
            )
          }
        />
      ) : (
        <div className="space-y-2">
          {emails.map((email) => (
            <EmailListItem key={email.id} email={email} />
          ))}
        </div>
      )}
    </div>
  );
}
