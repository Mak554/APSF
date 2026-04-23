"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { ShieldAlert, Users, Mail, Zap, ChevronDown, Plus, Trash2 } from "lucide-react";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8009";

type Step = 1 | 2 | 3;

export default function NewCampaignPage() {
  const router = useRouter();
  const [step, setStep] = useState<Step>(1);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<null | { campaign_id: string; name: string }>(null);

  const [form, setForm] = useState({
    name: "",
    phishing_type: "Credential_Harvest",
    difficulty: "Medium",
    email_template_id: "tpl-it-medium",
    subject: "⚠️ Urgent: Your Password Expires in 24 Hours",
    sender_name: "IT Security Team",
    sender_email: "security@company.sa",
    urgency_level: 3,
    target_emails: [""],
  });

  const update = (field: string, value: unknown) =>
    setForm((p) => ({ ...p, [field]: value }));

  const handleSubmit = async () => {
    setLoading(true);
    try {
      // 1. Create / fetch target users
      const userIds: string[] = [];
      for (const email of form.target_emails.filter(Boolean)) {
        const res = await fetch(`${API_URL}/users/`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ email, full_name: email.split("@")[0], department: "General" }),
        });
        if (res.ok) {
          const u = await res.json();
          userIds.push(u.user_id);
        }
      }

      // 2. Create campaign
      const camRes = await fetch(`${API_URL}/campaigns/`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          name: form.name,
          phishing_type: form.phishing_type,
          email_template_id: form.email_template_id,
          subject: form.subject,
          sender_name: form.sender_name,
          sender_email: form.sender_email,
          urgency_level: form.urgency_level,
          difficulty: form.difficulty,
          target_user_ids: userIds,
        }),
      });
      const campaign = await camRes.json();
      setResult({ campaign_id: campaign.campaign_id, name: campaign.name });
      setStep(3);
    } catch {
      alert("Could not reach backend. Make sure the FastAPI server is running.");
    } finally {
      setLoading(false);
    }
  };

  const TEMPLATE_TYPES = [
    { id: "it", label: "IT Security", icon: "🛡️" },
    { id: "hr", label: "Human Resources", icon: "📋" },
    { id: "ceo", label: "CEO / Executive", icon: "👑" },
  ];

  const DIFFICULTIES = ["Easy", "Medium", "Hard"];

  const getTemplateId = (type: string, diff: string) => `tpl-${type}-${diff.toLowerCase()}`;

  const [selectedType, setSelectedType] = useState("it");

  const handleTypeDiffChange = (type: string, diff: string) => {
    const tid = getTemplateId(type, diff);
    setSelectedType(type);
    update("difficulty", diff);
    update("email_template_id", tid);
    
    // Auto-update subject/sender based on type
    if (type === "it") {
      update("subject", diff === "Hard" ? "Security Alert: Mandatory Policy Update NX-SEC-2025" : "Urgent: Your Password Expires in 24 Hours");
      update("sender_name", "IT Security Team");
      update("sender_email", "security@company.sa");
      update("phishing_type", "Credential_Harvest");
    } else if (type === "hr") {
      update("subject", diff === "Hard" ? "Action Required: 2025 GOSI & Health Insurance Re-verification" : "Important: Annual Benefits Enrollment Closing Soon");
      update("sender_name", "HR Department");
      update("sender_email", "hr@company.sa");
      update("phishing_type", "Link_Only");
    } else {
      update("subject", diff === "Hard" ? "PRIVATE: Strategic Acquisition 'Project Falcon' - Urgent Wire Authorization" : "Confidential: Urgent Wire Transfer Required");
      update("sender_name", "Mohammed Al-CEO");
      update("sender_email", "m.alghamdi@company.sa");
      update("phishing_type", "Urgency");
    }
  };

  return (
    <div className="min-h-screen p-8" style={{ background: "var(--bg-primary)" }}>
      <div className="max-w-2xl mx-auto">
        {/* Header */}
        <div className="flex items-center gap-3 mb-8">
          <a href="/" className="text-slate-500 hover:text-white transition-colors text-sm">← Dashboard</a>
          <span className="text-slate-700">/</span>
          <span className="text-sm text-white">New Campaign</span>
        </div>

        <h1 className="text-2xl font-bold text-white mb-2">Create Phishing Campaign</h1>
        <p className="text-slate-400 text-sm mb-8">Configure and launch a simulated phishing campaign.</p>

        {/* Steps */}
        <div className="flex items-center gap-2 mb-8">
          {[1, 2, 3].map((s) => (
            <div key={s} className="flex items-center gap-2">
              <div className={`w-7 h-7 rounded-full flex items-center justify-center text-xs font-bold ${
                step >= s ? "bg-blue-500 text-white" : "bg-white/5 text-slate-500"}`}>
                {s}
              </div>
              {s < 3 && <div className={`h-px w-12 ${step > s ? "bg-blue-500" : "bg-white/5"}`} />}
            </div>
          ))}
          <div className="ml-2 text-sm text-slate-400">
            {step === 1 ? "Campaign Details" : step === 2 ? "Target Users" : "Launched!"}
          </div>
        </div>

        {step === 1 && (
          <div className="glass-card p-8 space-y-5">
            <div>
              <label className="text-xs text-slate-400 block mb-1.5">Campaign Name</label>
              <input
                value={form.name}
                onChange={(e) => update("name", e.target.value)}
                placeholder="e.g. Q1 Phishing Test"
                className="w-full bg-white/5 border border-white/10 rounded-lg px-4 py-2.5 text-white placeholder:text-slate-600 focus:outline-none focus:border-blue-500 text-sm"
              />
            </div>

            <div>
              <label className="text-xs text-slate-400 block mb-3">Attack Type & Difficulty</label>
              
              {/* Type Selection */}
              <div className="grid grid-cols-3 gap-3 mb-4">
                {TEMPLATE_TYPES.map((t) => (
                  <button
                    key={t.id}
                    onClick={() => handleTypeDiffChange(t.id, form.difficulty)}
                    className={`flex flex-col items-center gap-2 p-3 rounded-xl border transition-all ${
                      selectedType === t.id
                        ? "border-blue-500 bg-blue-500/10 text-white"
                        : "border-white/5 bg-white/2 text-slate-400 hover:border-white/10"
                    }`}
                  >
                    <span className="text-xl">{t.icon}</span>
                    <span className="text-xs font-medium">{t.label}</span>
                  </button>
                ))}
              </div>

              {/* Difficulty Selection */}
              <div className="flex bg-white/5 p-1 rounded-xl gap-1">
                {DIFFICULTIES.map((d) => (
                  <button
                    key={d}
                    onClick={() => handleTypeDiffChange(selectedType, d)}
                    className={`flex-1 py-2 text-xs font-bold rounded-lg transition-all ${
                      form.difficulty === d
                        ? "bg-blue-500 text-white shadow-lg"
                        : "text-slate-500 hover:text-slate-300"
                    }`}
                  >
                    {d}
                  </button>
                ))}
              </div>
              
              <div className="mt-4 p-4 rounded-xl bg-blue-500/5 border border-blue-500/10">
                <p className="text-xs text-blue-400 font-medium mb-1">Reality Level: {form.difficulty}</p>
                <p className="text-[11px] text-slate-400 leading-relaxed">
                  {form.difficulty === "Easy" && "Obvious red flags: spelling errors, suspicious links, and generic greetings."}
                  {form.difficulty === "Medium" && "Professional tone with company branding and personalized employee names."}
                  {form.difficulty === "Hard" && "High-fidelity spear phishing: perfect grammar, authoritative tone, and specific corporate context."}
                </p>
              </div>
            </div>

            <div>
              <label className="text-xs text-slate-400 block mb-1.5">Urgency Level: {form.urgency_level}/5</label>
              <input
                type="range" min={1} max={5}
                value={form.urgency_level}
                onChange={(e) => update("urgency_level", Number(e.target.value))}
                className="w-full accent-blue-500"
              />
              <div className="flex justify-between text-xs text-slate-600 mt-1">
                <span>Low</span><span>Extreme</span>
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="text-xs text-slate-400 block mb-1.5">Sender Name</label>
                <input
                  value={form.sender_name}
                  onChange={(e) => update("sender_name", e.target.value)}
                  className="w-full bg-white/5 border border-white/10 rounded-lg px-3 py-2 text-white text-sm focus:outline-none focus:border-blue-500"
                />
              </div>
              <div>
                <label className="text-xs text-slate-400 block mb-1.5">Sender Email</label>
                <input
                  value={form.sender_email}
                  onChange={(e) => update("sender_email", e.target.value)}
                  className="w-full bg-white/5 border border-white/10 rounded-lg px-3 py-2 text-white text-sm focus:outline-none focus:border-blue-500"
                />
              </div>
            </div>

            <button
              onClick={() => setStep(2)}
              disabled={!form.name}
              className="btn-primary w-full disabled:opacity-40"
            >
              Next: Add Target Users →
            </button>
          </div>
        )}

        {step === 2 && (
          <div className="glass-card p-8 space-y-5">
            <div className="flex items-center gap-2 mb-2">
              <Users className="w-4 h-4 text-blue-400" />
              <h2 className="text-sm font-semibold text-white">Target Employees</h2>
            </div>
            <p className="text-xs text-slate-400">Add email addresses of employees to include in this simulation.</p>

            <div className="space-y-2">
              {form.target_emails.map((email, i) => (
                <div key={i} className="flex gap-2">
                  <input
                    type="email"
                    value={email}
                    onChange={(e) => {
                      const arr = [...form.target_emails];
                      arr[i] = e.target.value;
                      update("target_emails", arr);
                    }}
                    placeholder="employee@company.sa"
                    className="flex-1 bg-white/5 border border-white/10 rounded-lg px-4 py-2.5 text-white placeholder:text-slate-600 focus:outline-none focus:border-blue-500 text-sm"
                  />
                  {form.target_emails.length > 1 && (
                    <button
                      onClick={() => update("target_emails", form.target_emails.filter((_, j) => j !== i))}
                      className="p-2 glass-card rounded-lg text-slate-500 hover:text-red-400"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  )}
                </div>
              ))}
            </div>

            <button
              onClick={() => update("target_emails", [...form.target_emails, ""])}
              className="flex items-center gap-2 text-sm text-blue-400 hover:text-blue-300"
            >
              <Plus className="w-4 h-4" /> Add another email
            </button>

            <div className="flex gap-3 pt-2">
              <button onClick={() => setStep(1)} className="glass-card px-6 py-3 text-slate-300 font-medium rounded-xl text-sm">
                ← Back
              </button>
              <button
                onClick={handleSubmit}
                disabled={loading || !form.target_emails.some(Boolean)}
                className="btn-primary flex-1 disabled:opacity-40"
              >
                {loading ? "Creating Campaign…" : "🚀 Create Campaign"}
              </button>
            </div>
          </div>
        )}

        {step === 3 && result && (
          <div className="glass-card p-8 text-center space-y-5">
            <div className="w-20 h-20 bg-green-500/10 border-2 border-green-500/30 rounded-full flex items-center justify-center mx-auto">
              <Zap className="w-10 h-10 text-green-400" />
            </div>
            <div>
              <h2 className="text-2xl font-bold text-white">Campaign Created!</h2>
              <p className="text-slate-400 text-sm mt-2">
                &ldquo;{result.name}&rdquo; is ready. Launch it from the dashboard to send emails.
              </p>
            </div>
            <div className="bg-white/3 rounded-xl p-4 text-left text-xs text-slate-400 space-y-1">
              <div>Campaign ID: <span className="text-white font-mono">{result.campaign_id}</span></div>
            </div>
            <div className="flex gap-3">
              <button onClick={() => router.push("/")} className="btn-primary flex-1">
                ← Go to Dashboard
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
