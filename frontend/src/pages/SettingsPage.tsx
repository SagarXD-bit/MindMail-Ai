import { useState } from "react";
import {
  Mail,
  Sparkles,
  Bell,
  Shield,
  CheckCircle2,
  Trash2,
  Plus,
  Server,
  Loader2,
} from "lucide-react";
import toast from "react-hot-toast";
import { useSettings, useAccounts } from "../hooks/queries";
import {
  updateSettings,
  createAccount,
  deleteAccount,
  testAccount,
} from "../api/endpoints";
import {
  LoadingCard,
} from "../components/ui";
import { ConfirmDialog } from "../components/ConfirmDialog";
import type { UserSettings } from "../types";

export function SettingsPage() {
  const { data: settings, isLoading: sLoading } = useSettings();
  const { data: accounts, isLoading: aLoading } = useAccounts();
  const [showAccountForm, setShowAccountForm] = useState(false);
  const [deleteAccountId, setDeleteAccountId] = useState<number | null>(null);
  const [saving, setSaving] = useState(false);
  const [localSettings, setLocalSettings] = useState<UserSettings | null>(null);

  // Account form state
  const [emailAddr, setEmailAddr] = useState("");
  const [imapServer, setImapServer] = useState("");
  const [imapPort, setImapPort] = useState("993");
  const [imapSsl, setImapSsl] = useState(true);
  const [smtpServer, setSmtpServer] = useState("");
  const [smtpPort, setSmtpPort] = useState("587");
  const [smtpSsl, setSmtpSsl] = useState(true);
  const [password, setPassword] = useState("");

  // Sync local settings when loaded
  if (settings && !localSettings) {
    setLocalSettings(settings);
  }

  const handleSaveSettings = async () => {
    if (!localSettings) return;
    setSaving(true);
    try {
      await updateSettings(localSettings);
      toast.success("Settings saved!");
    } catch (err: any) {
      toast.error(`Failed to save: ${err.detail || err.message}`);
    } finally {
      setSaving(false);
    }
  };

  const handleCreateAccount = async () => {
    if (!emailAddr || !imapServer || !password) {
      toast.error("Email, IMAP server, and password are required.");
      return;
    }
    try {
      await createAccount({
        email_address: emailAddr,
        imap_server: imapServer,
        imap_port: parseInt(imapPort),
        imap_ssl: imapSsl,
        smtp_server: smtpServer || undefined,
        smtp_port: smtpPort ? parseInt(smtpPort) : undefined,
        smtp_ssl: smtpSsl,
        password,
      });
      toast.success("Account connected successfully!");
      setShowAccountForm(false);
      // Reset form
      setEmailAddr("");
      setImapServer("");
      setPassword("");
      setSmtpServer("");
    } catch (err: any) {
      // The backend returns 201 with detail for connection errors
      if (err.status === 201) {
        toast.error(err.detail || "Account saved but connection failed.");
      } else {
        toast.error(err.detail || err.message);
      }
    }
  };

  const handleDeleteAccount = async () => {
    if (!deleteAccountId) return;
    try {
      await deleteAccount(deleteAccountId);
      toast.success("Account removed.");
      setDeleteAccountId(null);
    } catch (err: any) {
      toast.error(`Failed: ${err.detail || err.message}`);
    }
  };

  const handleTestAccount = async (id: number) => {
    const tid = toast.loading("Testing connection...");
    try {
      const res = await testAccount(id);
      toast.success(res.message, { id: tid });
    } catch (err: any) {
      toast.error(err.detail || err.message, { id: tid });
    }
  };

  if (sLoading || aLoading) {
    return (
      <div className="space-y-4">
        <LoadingCard />
        <LoadingCard />
      </div>
    );
  }

  return (
    <div className="space-y-6 max-w-4xl">
      <div>
        <h1 className="text-2xl font-bold text-slate-900">Settings</h1>
        <p className="text-sm text-slate-500">
          Configure your email account, AI preferences, and privacy settings
        </p>
      </div>

      {/* Email Account Configuration */}
      <div className="card">
        <div className="flex items-center gap-2 mb-4">
          <Server size={20} className="text-brand-500" />
          <h2 className="font-semibold text-slate-900">Email Account (IMAP)</h2>
        </div>

        {/* Connected accounts */}
        {accounts && accounts.length > 0 ? (
          <div className="space-y-2 mb-4">
            {accounts.map((acc) => (
              <div
                key={acc.id}
                className="flex items-center justify-between p-3 rounded-lg border border-slate-200"
              >
                <div className="flex items-center gap-3">
                  <div
                    className={`w-10 h-10 rounded-lg flex items-center justify-center ${
                      acc.status === "connected"
                        ? "bg-green-50"
                        : "bg-red-50"
                    }`}
                  >
                    <Mail
                      className={
                        acc.status === "connected"
                          ? "text-green-500"
                          : "text-red-500"
                      }
                      size={18}
                    />
                  </div>
                  <div>
                    <p className="text-sm font-medium text-slate-900">
                      {acc.email_address}
                    </p>
                    <p className="text-xs text-slate-500">
                      {acc.imap_server}:{acc.imap_port} • Status: {acc.status}
                    </p>
                  </div>
                </div>
                <div className="flex gap-2">
                  <button
                    onClick={() => handleTestAccount(acc.id)}
                    className="btn-ghost text-xs"
                  >
                    Test
                  </button>
                  <button
                    onClick={() => setDeleteAccountId(acc.id)}
                    className="btn-ghost text-xs text-red-500 hover:bg-red-50"
                  >
                    <Trash2 size={14} />
                  </button>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="text-center py-6 mb-4">
            <p className="text-sm text-slate-500">
              No email account connected. Add one to sync real emails, or use
              demo mode.
            </p>
          </div>
        )}

        {/* Add account button / form */}
        {!showAccountForm ? (
          <button
            onClick={() => setShowAccountForm(true)}
            className="btn-secondary"
          >
            <Plus size={16} /> Add Email Account
          </button>
        ) : (
          <div className="space-y-4 p-4 bg-slate-50 rounded-lg border border-slate-200">
            <h3 className="font-medium text-slate-700">Connect Email Account</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="label">Email Address</label>
                <input
                  type="email"
                  value={emailAddr}
                  onChange={(e) => setEmailAddr(e.target.value)}
                  placeholder="you@example.com"
                  className="input"
                />
              </div>
              <div>
                <label className="label">Password</label>
                <input
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="App password"
                  className="input"
                />
              </div>
              <div>
                <label className="label">IMAP Server</label>
                <input
                  type="text"
                  value={imapServer}
                  onChange={(e) => setImapServer(e.target.value)}
                  placeholder="imap.example.com"
                  className="input"
                />
              </div>
              <div>
                <label className="label">IMAP Port</label>
                <input
                  type="number"
                  value={imapPort}
                  onChange={(e) => setImapPort(e.target.value)}
                  className="input"
                />
              </div>
              <div>
                <label className="label">SMTP Server (optional)</label>
                <input
                  type="text"
                  value={smtpServer}
                  onChange={(e) => setSmtpServer(e.target.value)}
                  placeholder="smtp.example.com"
                  className="input"
                />
              </div>
              <div>
                <label className="label">SMTP Port</label>
                <input
                  type="number"
                  value={smtpPort}
                  onChange={(e) => setSmtpPort(e.target.value)}
                  className="input"
                />
              </div>
            </div>
            <div className="flex gap-4">
              <label className="flex items-center gap-2 text-sm text-slate-600">
                <input
                  type="checkbox"
                  checked={imapSsl}
                  onChange={(e) => setImapSsl(e.target.checked)}
                  className="rounded"
                />
                IMAP SSL
              </label>
              <label className="flex items-center gap-2 text-sm text-slate-600">
                <input
                  type="checkbox"
                  checked={smtpSsl}
                  onChange={(e) => setSmtpSsl(e.target.checked)}
                  className="rounded"
                />
                SMTP TLS/SSL
              </label>
            </div>
            <div className="flex gap-2">
              <button
                onClick={handleCreateAccount}
                className="btn-primary text-sm"
              >
                Connect
              </button>
              <button
                onClick={() => setShowAccountForm(false)}
                className="btn-secondary text-sm"
              >
                Cancel
              </button>
            </div>
            <p className="text-xs text-slate-400">
              🔒 Your password is encrypted before storage and never exposed in
              the API or frontend.
            </p>
          </div>
        )}
      </div>

      {/* AI Preferences */}
      {localSettings && (
        <div className="card">
          <div className="flex items-center gap-2 mb-4">
            <Sparkles size={20} className="text-brand-500" />
            <h2 className="font-semibold text-slate-900">AI Preferences</h2>
          </div>
          <div className="space-y-4">
            <div>
              <label className="label">Default Reply Tone</label>
              <select
                value={localSettings.default_reply_tone}
                onChange={(e) =>
                  setLocalSettings({
                    ...localSettings,
                    default_reply_tone: e.target.value as any,
                  })
                }
                className="input"
              >
                <option value="professional">Professional</option>
                <option value="friendly">Friendly</option>
                <option value="concise">Concise</option>
              </select>
            </div>
            <div>
              <label className="label">Categorization Aggressiveness</label>
              <select
                value={localSettings.categorization_aggressiveness}
                onChange={(e) =>
                  setLocalSettings({
                    ...localSettings,
                    categorization_aggressiveness: e.target.value,
                  })
                }
                className="input"
              >
                <option value="conservative">
                  Conservative — only confident categorizations
                </option>
                <option value="balanced">
                  Balanced — standard confidence threshold
                </option>
                <option value="aggressive">
                  Aggressive — categorize everything
                </option>
              </select>
            </div>
            <label className="flex items-center justify-between">
              <div>
                <span className="text-sm font-medium text-slate-700">
                  Automatic Categorization
                </span>
                <p className="text-xs text-slate-500">
                  Automatically categorize new emails using AI
                </p>
              </div>
              <input
                type="checkbox"
                checked={localSettings.auto_categorize}
                onChange={(e) =>
                  setLocalSettings({
                    ...localSettings,
                    auto_categorize: e.target.checked,
                  })
                }
                className="w-5 h-5 rounded"
              />
            </label>
          </div>
        </div>
      )}

      {/* Notification Settings */}
      {localSettings && (
        <div className="card">
          <div className="flex items-center gap-2 mb-4">
            <Bell size={20} className="text-brand-500" />
            <h2 className="font-semibold text-slate-900">Notifications</h2>
          </div>
          <div className="space-y-4">
            <label className="flex items-center justify-between">
              <div>
                <span className="text-sm font-medium text-slate-700">
                  Browser Notifications
                </span>
                <p className="text-xs text-slate-500">
                  Show notifications for new emails and follow-up reminders
                </p>
              </div>
              <input
                type="checkbox"
                checked={localSettings.notifications_enabled}
                onChange={(e) =>
                  setLocalSettings({
                    ...localSettings,
                    notifications_enabled: e.target.checked,
                  })
                }
                className="w-5 h-5 rounded"
              />
            </label>
            <label className="flex items-center justify-between">
              <div>
                <span className="text-sm font-medium text-slate-700">
                  Email Notifications
                </span>
                <p className="text-xs text-slate-500">
                  Receive email summaries of urgent emails and overdue follow-ups
                </p>
              </div>
              <input
                type="checkbox"
                checked={localSettings.email_notifications}
                onChange={(e) =>
                  setLocalSettings({
                    ...localSettings,
                    email_notifications: e.target.checked,
                  })
                }
                className="w-5 h-5 rounded"
              />
            </label>
          </div>
        </div>
      )}

      {/* Privacy & Security */}
      {localSettings && (
        <div className="card">
          <div className="flex items-center gap-2 mb-4">
            <Shield size={20} className="text-brand-500" />
            <h2 className="font-semibold text-slate-900">Privacy & Security</h2>
          </div>
          <div className="space-y-4">
            <label className="flex items-center justify-between">
              <div>
                <span className="text-sm font-medium text-slate-700">
                  Store Email Bodies
                </span>
                <p className="text-xs text-slate-500">
                  Save full email content for AI analysis. Disable for
                  maximum privacy (only metadata is stored).
                </p>
              </div>
              <input
                type="checkbox"
                checked={localSettings.store_email_bodies}
                onChange={(e) =>
                  setLocalSettings({
                    ...localSettings,
                    store_email_bodies: e.target.checked,
                  })
                }
                className="w-5 h-5 rounded"
              />
            </label>
            <div className="bg-slate-50 rounded-lg p-4 text-sm text-slate-600 space-y-2">
              <p className="font-medium text-slate-700">
                🔒 Your data is protected:
              </p>
              <ul className="space-y-1 text-xs text-slate-500">
                <li className="flex items-start gap-2">
                  <CheckCircle2 size={14} className="text-green-500 mt-0.5" />
                  Email passwords are encrypted at rest using Fernet encryption
                </li>
                <li className="flex items-start gap-2">
                  <CheckCircle2 size={14} className="text-green-500 mt-0.5" />
                  API keys are stored in environment variables, never in source code
                </li>
                <li className="flex items-start gap-2">
                  <CheckCircle2 size={14} className="text-green-500 mt-0.5" />
                  No reply is ever sent without your explicit confirmation
                </li>
                <li className="flex items-start gap-2">
                  <CheckCircle2 size={14} className="text-green-500 mt-0.5" />
                  Demo data is clearly marked and never mixed with real emails
                </li>
              </ul>
            </div>
          </div>
        </div>
      )}

      {/* Save button */}
      <div className="flex justify-end gap-3 sticky bottom-4">
        <button
          onClick={handleSaveSettings}
          disabled={saving}
          className="btn-primary shadow-lg"
        >
          {saving ? <Loader2 size={16} className="animate-spin" /> : <CheckCircle2 size={16} />}
          Save Settings
        </button>
      </div>

      {/* Delete account confirm */}
      <ConfirmDialog
        open={deleteAccountId !== null}
        title="Remove email account?"
        message="This will disconnect the email account and remove stored credentials. Your existing emails will be preserved."
        confirmLabel="Remove"
        danger
        onConfirm={handleDeleteAccount}
        onCancel={() => setDeleteAccountId(null)}
      />
    </div>
  );
}
