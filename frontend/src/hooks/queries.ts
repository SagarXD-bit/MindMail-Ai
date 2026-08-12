// React Query hooks for data fetching and mutations

import {
  useQuery,
  useMutation,
  useQueryClient,
} from "@tanstack/react-query";
import {
  getEmails,
  getEmail,
  getFollowUps,
  getAnalytics,
  getAccounts,
  getSettings,
  checkHealth,
  syncEmails,
  type EmailQuery,
} from "../api/endpoints";

// Query keys
export const qk = {
  emails: (q?: EmailQuery) => ["emails", q] as const,
  email: (id: number) => ["email", id] as const,
  followUps: (status?: string) => ["follow-ups", status] as const,
  analytics: ["analytics"] as const,
  accounts: ["accounts"] as const,
  settings: ["settings"] as const,
  health: ["health"] as const,
};

// ---- Queries ----
export function useEmails(query: EmailQuery = {}) {
  return useQuery({
    queryKey: qk.emails(query),
    queryFn: () => getEmails(query),
    staleTime: 10_000,
  });
}

export function useEmail(id: number | null) {
  return useQuery({
    queryKey: qk.email(id!),
    queryFn: () => getEmail(id!),
    enabled: !!id,
  });
}

export function useFollowUps(status?: string) {
  return useQuery({
    queryKey: qk.followUps(status),
    queryFn: () => getFollowUps(status),
  });
}

export function useAnalytics() {
  return useQuery({
    queryKey: qk.analytics,
    queryFn: getAnalytics,
  });
}

export function useAccounts() {
  return useQuery({
    queryKey: qk.accounts,
    queryFn: getAccounts,
  });
}

export function useSettings() {
  return useQuery({
    queryKey: qk.settings,
    queryFn: getSettings,
  });
}

export function useHealth() {
  return useQuery({
    queryKey: qk.health,
    queryFn: checkHealth,
    refetchInterval: 60_000,
  });
}

// ---- Mutations ----
export function useSyncEmails() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (forceDemo: boolean = false) => syncEmails(forceDemo),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["emails"] });
      qc.invalidateQueries({ queryKey: qk.analytics });
      qc.invalidateQueries({ queryKey: qk.accounts });
    },
  });
}

export function useInvalidateAll() {
  const qc = useQueryClient();
  return () => {
    qc.invalidateQueries({ queryKey: ["emails"] });
    qc.invalidateQueries({ queryKey: qk.analytics });
    qc.invalidateQueries({ queryKey: qk.followUps() });
  };
}
