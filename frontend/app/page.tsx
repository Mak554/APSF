"use client";

import { useState, useEffect, useRef } from "react";
import Link from "next/link";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8009";

// ─── Types ────────────────────────────────────────────────────────────────────
type DashboardStats = {
  total_users: number;
  total_campaigns: number;
  overall_click_rate: number;
  risk_distribution: Record<string, number>;
  top_risk_users: UserProfile[];
  recent_campaigns: Campaign[];
  campaign_click_rates: CampaignRate[];
};

type UserProfile = {
  user_id: string; email: string; full_name: string; department: string;
  risk_tier: string; p_fail: number; total_simulations: number;
  total_failures: number; total_reports: number;
};

type Campaign = {
  campaign_id: string; name: string; status: string; emails_sent: number;
  clicks: number; submissions: number; reports: number; target_count: number;
};

type CampaignRate = {
  name: string; click_rate: number; emails_sent: number;
  clicks: number; reports: number;
};

// ─── Demo Data ────────────────────────────────────────────────────────────────
const DEMO_STATS: DashboardStats = {
  total_users: 47,
  total_campaigns: 6,
  overall_click_rate: 22.4,
  risk_distribution: { High: 8, Medium: 14, Low: 22, New: 3 },
  campaign_click_rates: [
    { name: "Q1 Password Reset", click_rate: 34.2, emails_sent: 47, clicks: 16, reports: 5 },
    { name: "CEO Wire Transfer", click_rate: 28.7, emails_sent: 47, clicks: 13, reports: 8 },
    { name: "HR Benefits Q2", click_rate: 19.1, emails_sent: 47, clicks: 9, reports: 12 },
    { name: "Month-3 Retest", click_rate: 8.5, emails_sent: 47, clicks: 4, reports: 22 },
  ],
  top_risk_users: [
    { user_id: "1", email: "a.alkhateeb@company.sa", full_name: "Ahmad Alkhateeb", department: "Finance", risk_tier: "High", p_fail: 0.91, total_simulations: 4, total_failures: 4, total_reports: 0 },
    { user_id: "2", email: "j.alharbi@company.sa", full_name: "Jassim Alharbi", department: "Finance", risk_tier: "High", p_fail: 0.85, total_simulations: 4, total_failures: 4, total_reports: 0 },
    { user_id: "3", email: "f.ali@company.sa", full_name: "Fatimah Ali", department: "HR", risk_tier: "Medium", p_fail: 0.61, total_simulations: 3, total_failures: 2, total_reports: 0 },
    { user_id: "4", email: "n.hassan@company.sa", full_name: "Nora Hassan", department: "IT Security", risk_tier: "Low", p_fail: 0.12, total_simulations: 4, total_failures: 0, total_reports: 3 },
  ],
  recent_campaigns: [
    { campaign_id: "c1", name: "Q1 - IT Password Reset Lure", status: "draft", emails_sent: 0, clicks: 8, submissions: 4, reports: 3, target_count: 12 },
    { campaign_id: "c2", name: "Q1 - CEO Wire Transfer Spear Phish", status: "draft", emails_sent: 0, clicks: 6, submissions: 4, reports: 2, target_count: 12 },
    { campaign_id: "c3", name: "Q3 - Month 3 Adaptive Retest", status: "draft", emails_sent: 0, clicks: 1, submissions: 0, reports: 5, target_count: 12 },
  ],
};

// ─── Risk Badge ───────────────────────────────────────────────────────────────
function RiskBadge({ tier }: { tier: string }) {
  const styles: Record<string, React.CSSProperties> = {
    High:   { background: "rgba(239,68,68,0.15)",   color: "#f87171", border: "1px solid rgba(239,68,68,0.3)" },
    Medium: { background: "rgba(245,158,11,0.15)",  color: "#fbbf24", border: "1px solid rgba(245,158,11,0.3)" },
    Low:    { background: "rgba(34,197,94,0.15)",   color: "#4ade80", border: "1px solid rgba(34,197,94,0.3)" },
    New:    { background: "rgba(100,116,139,0.15)", color: "#94a3b8", border: "1px solid rgba(100,116,139,0.3)" },
  };
  return (
    <span style={{ ...styles[tier] || styles["New"], fontSize: 11, padding: "2px 8px", borderRadius: 20, fontWeight: 600 }}>
      {tier}
    </span>
  );
}

// ─── Charts (loaded dynamically to avoid SSR issues) ─────────────────────────
function RiskDonut({ data }: { data: Record<string, number> }) {
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    if (!canvasRef.current) return;
    let chart: any = null;
    let isMounted = true;

    import("chart.js/auto").then((mod) => {
      if (!isMounted || !canvasRef.current) return;
      const ChartJS = mod.default;
      
      // Destroy any existing chart on this canvas to prevent "already in use" errors
      const existingChart = ChartJS.getChart(canvasRef.current);
      if (existingChart) existingChart.destroy();

      chart = new ChartJS(canvasRef.current, {
        type: "doughnut",
        data: {
          labels: ["High Risk", "Medium Risk", "Low Risk", "New"],
          datasets: [{
            data: [data.High || 0, data.Medium || 0, data.Low || 0, data.New || 0],
            backgroundColor: ["#ef4444", "#f59e0b", "#22c55e", "#64748b"],
            borderWidth: 0,
          }],
        },
        options: {
          plugins: { legend: { labels: { color: "#94a3b8", boxWidth: 12 } } },
        },
      });
    });
    
    return () => { 
      isMounted = false;
      if (chart) chart.destroy(); 
    };
  }, [data]);

  return <canvas ref={canvasRef} />;
}

function CampaignBar({ campaigns }: { campaigns: CampaignRate[] }) {
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    if (!canvasRef.current || !campaigns.length) return;
    let chart: any = null;
    let isMounted = true;

    import("chart.js/auto").then((mod) => {
      if (!isMounted || !canvasRef.current) return;
      const ChartJS = mod.default;
      
      const existingChart = ChartJS.getChart(canvasRef.current);
      if (existingChart) existingChart.destroy();

      chart = new ChartJS(canvasRef.current, {
        type: "bar",
        data: {
          labels: campaigns.map((c) => c.name.length > 18 ? c.name.slice(0, 18) + "…" : c.name),
          datasets: [{
            label: "Click Rate (%)",
            data: campaigns.map((c) => c.click_rate),
            backgroundColor: "rgba(59,130,246,0.7)",
            borderRadius: 8,
          }],
        },
        options: {
          responsive: true,
          plugins: { legend: { display: false } },
          scales: {
            x: { ticks: { color: "#64748b" }, grid: { color: "rgba(255,255,255,0.05)" } },
            y: { ticks: { color: "#64748b" }, grid: { color: "rgba(255,255,255,0.05)" } },
          },
        },
      });
    });
    
    return () => { 
      isMounted = false;
      if (chart) chart.destroy(); 
    };
  }, [campaigns]);

  return <canvas ref={canvasRef} />;
}

// ─── Main Dashboard ───────────────────────────────────────────────────────────
export default function DashboardPage() {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [isDemo, setIsDemo] = useState(false);
  const [resetting, setResetting] = useState(false);
  const [resetMsg, setResetMsg] = useState<string | null>(null);

  const fetchStats = async () => {
    setLoading(true);
    try {
      const res = await fetch(`${API_URL}/dashboard/stats`);
      if (!res.ok) throw new Error();
      setStats(await res.json());
      setIsDemo(false);
    } catch {
      setStats(DEMO_STATS);
      setIsDemo(true);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchStats(); }, []);

  const resetDb = async () => {
    if (!confirm("Reset the database? This will wipe all campaigns and re-seed the 3 target employees.")) return;
    setResetting(true);
    setResetMsg(null);
    try {
      const res = await fetch(`${API_URL}/admin/reset`, { method: "POST" });
      const data = await res.json();
      setResetMsg(`✅ ${data.message}`);
      await fetchStats();
    } catch {
      setResetMsg("❌ Reset failed — is the backend online?");
    } finally {
      setResetting(false);
      setTimeout(() => setResetMsg(null), 4000);
    }
  };

  const s = stats;

  return (
    <div style={{ minHeight: "100vh", background: "#0a0e1a", color: "#e2e8f0", fontFamily: "Segoe UI, sans-serif" }}>

      {/* Header */}
      <header style={{ borderBottom: "1px solid rgba(255,255,255,0.06)", padding: "14px 32px", display: "flex", alignItems: "center", justifyContent: "space-between" }}>
        <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
          <div style={{ width: 36, height: 36, background: "rgba(59,130,246,0.15)", borderRadius: 10, display: "flex", alignItems: "center", justifyContent: "center", fontSize: 18 }}>🛡️</div>
          <div>
            <div style={{ fontWeight: 700, fontSize: 16, color: "#fff" }}>APSF Admin Dashboard</div>
            <div style={{ fontSize: 11, color: "#64748b" }}>Adaptive Phishing Simulation Framework</div>
          </div>
        </div>
        <div style={{ display: "flex", gap: 10, alignItems: "center" }}>
          {isDemo && (
            <span style={{ fontSize: 11, color: "#fbbf24", background: "rgba(245,158,11,0.1)", border: "1px solid rgba(245,158,11,0.2)", padding: "3px 10px", borderRadius: 20 }}>
              ⚠ Demo Mode – Backend Offline
            </span>
          )}
          {resetMsg && (
            <span style={{ fontSize: 11, color: resetMsg.startsWith("✅") ? "#4ade80" : "#f87171", background: resetMsg.startsWith("✅") ? "rgba(34,197,94,0.1)" : "rgba(239,68,68,0.1)", border: `1px solid ${resetMsg.startsWith("✅") ? "rgba(34,197,94,0.3)" : "rgba(239,68,68,0.3)"}`, padding: "3px 12px", borderRadius: 20 }}>
              {resetMsg}
            </span>
          )}
          <Link href="/training" style={{ background: "rgba(168,85,247,0.1)", color: "#c084fc", border: "1px solid rgba(168,85,247,0.3)", padding: "8px 18px", borderRadius: 10, fontSize: 13, fontWeight: 600, textDecoration: "none", transition: "all 0.2s" }}>
            🎓 Academy
          </Link>
          <Link href="/campaigns/new" style={{ background: "linear-gradient(135deg, #3b82f6, #1d4ed8)", color: "#fff", padding: "8px 18px", borderRadius: 10, fontSize: 13, fontWeight: 600, textDecoration: "none" }}>
            + New Campaign
          </Link>
          <button onClick={fetchStats} title="Refresh" style={{ background: "rgba(255,255,255,0.05)", border: "1px solid rgba(255,255,255,0.08)", color: "#94a3b8", padding: "8px 12px", borderRadius: 10, cursor: "pointer", fontSize: 14 }}>↻</button>
          <button
            id="reset-db-btn"
            onClick={resetDb}
            disabled={resetting}
            title="Wipe DB and re-seed the 3 target employees"
            style={{
              background: resetting ? "rgba(239,68,68,0.05)" : "rgba(239,68,68,0.12)",
              border: "1px solid rgba(239,68,68,0.35)",
              color: resetting ? "#94a3b8" : "#f87171",
              padding: "8px 14px",
              borderRadius: 10,
              cursor: resetting ? "not-allowed" : "pointer",
              fontSize: 13,
              fontWeight: 600,
              display: "flex",
              alignItems: "center",
              gap: 6,
              transition: "all 0.2s",
            }}
          >
            {resetting ? (
              <><span style={{ display: "inline-block", animation: "spin 1s linear infinite" }}>⟳</span> Resetting…</>
            ) : (
              <>⟳ Reset DB</>
            )}
          </button>
        </div>
      </header>

      <div style={{ maxWidth: 1280, margin: "0 auto", padding: "32px 32px" }}>

        {/* KPI Cards */}
        <div style={{ display: "grid", gridTemplateColumns: "repeat(4, 1fr)", gap: 16, marginBottom: 28 }}>
          {[
            { icon: "👥", label: "Total Employees",    value: loading ? "…" : s?.total_users ?? 0,                   color: "#3b82f6" },
            { icon: "🎯", label: "Campaigns Run",       value: loading ? "…" : s?.total_campaigns ?? 0,               color: "#a855f7" },
            { icon: "📉", label: "Overall Click Rate",  value: loading ? "…" : `${s?.overall_click_rate ?? 0}%`,      color: "#06b6d4" },
            { icon: "🚨", label: "High Risk Users",     value: loading ? "…" : s?.risk_distribution["High"] ?? 0,     color: "#ef4444" },
          ].map((k) => (
            <div key={k.label} style={{ background: "rgba(255,255,255,0.03)", border: "1px solid rgba(255,255,255,0.07)", borderRadius: 16, padding: "20px 22px" }}>
              <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 10 }}>
                <div style={{ background: `${k.color}22`, borderRadius: 8, padding: "6px 8px", fontSize: 16 }}>{k.icon}</div>
                <span style={{ fontSize: 12, color: "#94a3b8" }}>{k.label}</span>
              </div>
              <div style={{ fontSize: 30, fontWeight: 700, color: "#fff" }}>{k.value}</div>
            </div>
          ))}
        </div>

        {/* Charts */}
        <div style={{ display: "grid", gridTemplateColumns: "1fr 2fr", gap: 20, marginBottom: 28 }}>
          <div style={{ background: "rgba(255,255,255,0.03)", border: "1px solid rgba(255,255,255,0.07)", borderRadius: 16, padding: 24 }}>
            <div style={{ fontSize: 13, fontWeight: 600, color: "#cbd5e1", marginBottom: 16 }}>📊 Risk Distribution</div>
            {s ? <RiskDonut data={s.risk_distribution} /> : <div style={{ height: 160, background: "rgba(255,255,255,0.05)", borderRadius: 10 }} />}
          </div>
          <div style={{ background: "rgba(255,255,255,0.03)", border: "1px solid rgba(255,255,255,0.07)", borderRadius: 16, padding: 24 }}>
            <div style={{ fontSize: 13, fontWeight: 600, color: "#cbd5e1", marginBottom: 16 }}>📈 Campaign Click Rates</div>
            {s ? <CampaignBar campaigns={s.campaign_click_rates} /> : <div style={{ height: 160, background: "rgba(255,255,255,0.05)", borderRadius: 10 }} />}
          </div>
        </div>

        {/* Risk Users Table */}
        <div style={{ background: "rgba(255,255,255,0.03)", border: "1px solid rgba(255,255,255,0.07)", borderRadius: 16, padding: 24, marginBottom: 24 }}>
          <div style={{ fontSize: 13, fontWeight: 600, color: "#cbd5e1", marginBottom: 16 }}>🚨 Top Risk Users</div>
          <table style={{ width: "100%", borderCollapse: "collapse", fontSize: 13 }}>
            <thead>
              <tr style={{ color: "#64748b", borderBottom: "1px solid rgba(255,255,255,0.06)" }}>
                {["Employee", "Department", "Risk Tier", "P(Fail)", "Simulations", "Failures", "Reports"].map((h) => (
                  <th key={h} style={{ textAlign: "left", paddingBottom: 10, fontWeight: 500 }}>{h}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {(s?.top_risk_users ?? []).map((u) => (
                <tr key={u.user_id} style={{ borderBottom: "1px solid rgba(255,255,255,0.04)" }}>
                  <td style={{ padding: "11px 0", color: "#fff", fontWeight: 500 }}>{u.full_name}</td>
                  <td style={{ color: "#94a3b8" }}>{u.department}</td>
                  <td><RiskBadge tier={u.risk_tier} /></td>
                  <td style={{ color: u.p_fail >= 0.7 ? "#f87171" : u.p_fail >= 0.4 ? "#fbbf24" : "#4ade80", fontWeight: 600 }}>
                    {(u.p_fail * 100).toFixed(1)}%
                  </td>
                  <td style={{ color: "#94a3b8" }}>{u.total_simulations}</td>
                  <td style={{ color: "#f87171" }}>{u.total_failures}</td>
                  <td style={{ color: "#4ade80" }}>{u.total_reports}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {/* Recent Campaigns */}
        <div style={{ background: "rgba(255,255,255,0.03)", border: "1px solid rgba(255,255,255,0.07)", borderRadius: 16, padding: 24 }}>
          <div style={{ fontSize: 13, fontWeight: 600, color: "#cbd5e1", marginBottom: 16 }}>🕐 Recent Campaigns</div>
          <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
            {(s?.recent_campaigns ?? []).map((c) => (
              <div key={c.campaign_id} style={{ display: "flex", justifyContent: "space-between", alignItems: "center", background: "rgba(255,255,255,0.02)", borderRadius: 12, padding: "14px 18px", border: "1px solid rgba(255,255,255,0.05)" }}>
                <div>
                  <div style={{ color: "#fff", fontWeight: 500 }}>{c.name}</div>
                  <div style={{ fontSize: 11, color: "#64748b", marginTop: 3 }}>
                    {c.clicks} clicks · {c.submissions} submissions · {c.reports} reports
                  </div>
                </div>
                <span style={{
                  fontSize: 11, padding: "3px 10px", borderRadius: 20,
                  background: c.status === "running" ? "rgba(59,130,246,0.15)" : c.status === "completed" ? "rgba(34,197,94,0.15)" : "rgba(100,116,139,0.15)",
                  color: c.status === "running" ? "#60a5fa" : c.status === "completed" ? "#4ade80" : "#94a3b8",
                }}>
                  {c.status}
                </span>
              </div>
            ))}
          </div>
        </div>

      </div>
    </div>
  );
}
