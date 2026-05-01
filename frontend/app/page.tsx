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
    { campaign_id: "c1", name: "Q1 - IT Password Reset Lure", status: "running", emails_sent: 12, clicks: 8, submissions: 4, reports: 3, target_count: 12 },
    { campaign_id: "c2", name: "Q1 - CEO Wire Transfer Spear Phish", status: "completed", emails_sent: 12, clicks: 6, submissions: 4, reports: 2, target_count: 12 },
    { campaign_id: "c3", name: "Q3 - Month 3 Adaptive Retest", status: "draft", emails_sent: 0, clicks: 0, submissions: 0, reports: 0, target_count: 12 },
  ],
};

// ─── SVG Icons (Tailwind Colored) ─────────────────────────────────────────────
const Icons = {
  Users: () => <svg className="w-5 h-5 text-blue-400" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" /></svg>,
  Shield: () => <svg className="w-5 h-5 text-purple-400" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" /></svg>,
  TrendDown: () => <svg className="w-5 h-5 text-cyan-400" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 17h8m0 0V9m0 8l-8-8-4 4-6-6" /></svg>,
  Alert: () => <svg className="w-5 h-5 text-red-400" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" /></svg>,
  Refresh: ({ spinning }: { spinning?: boolean }) => <svg className={`w-4 h-4 ${spinning ? 'animate-spin' : ''}`} fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" /></svg>,
  Plus: () => <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6v6m0 0v6m0-6h6m-6 0H6" /></svg>,
  Academy: () => <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 14l9-5-9-5-9 5 9 5z" /><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 14l6.16-3.422a12.083 12.083 0 01.665 6.479A11.952 11.952 0 0012 20.055a11.952 11.952 0 00-6.824-2.998 12.078 12.078 0 01.665-6.479L12 14z" /><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 14l9-5-9-5-9 5 9 5zm0 0l6.16-3.422a12.083 12.083 0 01.665 6.479A11.952 11.952 0 0012 20.055a11.952 11.952 0 00-6.824-2.998 12.078 12.078 0 01.665-6.479L12 14zm-4 6v-7.5l4-2.222" /></svg>
};

// ─── Risk Badge ───────────────────────────────────────────────────────────────
function RiskBadge({ tier }: { tier: string }) {
  const styles: Record<string, string> = {
    High:   "bg-red-500/10 text-red-400 border-red-500/20",
    Medium: "bg-amber-500/10 text-amber-400 border-amber-500/20",
    Low:    "bg-green-500/10 text-green-400 border-green-500/20",
    New:    "bg-slate-500/10 text-slate-400 border-slate-500/20",
  };
  return (
    <span className={`text-[10px] uppercase tracking-wider font-bold px-2.5 py-1 rounded-full border ${styles[tier] || styles["New"]}`}>
      {tier}
    </span>
  );
}

// ─── Status Badge ─────────────────────────────────────────────────────────────
function StatusBadge({ status }: { status: string }) {
  const styles: Record<string, string> = {
    running:   "bg-blue-500/10 text-blue-400 border-blue-500/20",
    completed: "bg-green-500/10 text-green-400 border-green-500/20",
    draft:     "bg-slate-500/10 text-slate-400 border-slate-500/20",
  };
  const normalized = status.toLowerCase();
  return (
    <span className={`text-[10px] uppercase tracking-wider font-bold px-2.5 py-1 rounded-full border ${styles[normalized] || styles["draft"]}`}>
      {status}
    </span>
  );
}

// ─── Charts (loaded dynamically to avoid SSR issues) ─────────────────────────
function RiskDonut({ data }: { data: Record<string, number> }) {
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    if (!canvasRef.current) return;
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    let chart: any = null;
    let isMounted = true;

    import("chart.js/auto").then((mod) => {
      if (!isMounted || !canvasRef.current) return;
      const ChartJS = mod.default;
      
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
            hoverOffset: 4
          }],
        },
        options: {
          cutout: '75%',
          plugins: { legend: { position: 'right', labels: { color: "#94a3b8", usePointStyle: true, padding: 20, font: { family: "'Inter', sans-serif" } } } },
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
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    let chart: any = null;
    let isMounted = true;

    import("chart.js/auto").then((mod) => {
      if (!isMounted || !canvasRef.current) return;
      const ChartJS = mod.default;
      
      const existingChart = ChartJS.getChart(canvasRef.current);
      if (existingChart) existingChart.destroy();

      // Create a gradient for the bars
      const ctx = canvasRef.current.getContext('2d');
      let gradient: string | CanvasGradient = "rgba(59,130,246,0.7)";
      if (ctx) {
        gradient = ctx.createLinearGradient(0, 0, 0, 300);
        gradient.addColorStop(0, "rgba(59,130,246,0.9)");
        gradient.addColorStop(1, "rgba(29,78,216,0.4)");
      }

      chart = new ChartJS(canvasRef.current, {
        type: "bar",
        data: {
          labels: campaigns.map((c) => c.name.length > 15 ? c.name.slice(0, 15) + "…" : c.name),
          datasets: [{
            label: "Click Rate (%)",
            data: campaigns.map((c) => c.click_rate),
            backgroundColor: gradient,
            borderRadius: 6,
            barPercentage: 0.6
          }],
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: { legend: { display: false } },
          scales: {
            x: { ticks: { color: "#64748b", font: { family: "'Inter', sans-serif", size: 11 } }, grid: { display: false } },
            y: { ticks: { color: "#64748b", font: { family: "'Inter', sans-serif", size: 11 } }, grid: { color: "rgba(255,255,255,0.05)" }, border: { display: false } },
          },
        },
      });
    });
    
    return () => { 
      isMounted = false;
      if (chart) chart.destroy(); 
    };
  }, [campaigns]);

  return <div className="h-[220px]"><canvas ref={canvasRef} /></div>;
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
    <div className="min-h-screen bg-slate-950 text-slate-200 font-sans selection:bg-blue-500/30">
      
      {/* Background Glow Effects */}
      <div className="fixed top-0 inset-x-0 h-[500px] bg-gradient-to-b from-blue-900/20 to-transparent pointer-events-none -z-10" />
      <div className="fixed top-[-20%] left-[-10%] w-[50%] h-[50%] rounded-full bg-blue-600/10 blur-[120px] pointer-events-none -z-10" />
      <div className="fixed top-[20%] right-[-10%] w-[40%] h-[40%] rounded-full bg-purple-600/10 blur-[120px] pointer-events-none -z-10" />

      {/* Header */}
      <header className="sticky top-0 z-50 backdrop-blur-xl bg-slate-950/60 border-b border-white/5 px-8 py-4 flex items-center justify-between">
        <div className="flex items-center gap-4 group cursor-pointer">
          <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-xl flex items-center justify-center text-xl shadow-lg shadow-blue-500/20 group-hover:shadow-blue-500/40 transition-all duration-300">
            🛡️
          </div>
          <div>
            <h1 className="font-bold text-lg text-white tracking-tight">NexaCore <span className="text-blue-400 font-medium">APSF</span></h1>
            <p className="text-[11px] text-slate-400 font-medium tracking-wide uppercase">Adaptive Phishing Simulation</p>
          </div>
        </div>
        <div className="flex items-center gap-4">
          {isDemo && (
            <span className="animate-pulse text-[11px] font-bold text-amber-400 bg-amber-500/10 border border-amber-500/20 px-3 py-1.5 rounded-full flex items-center gap-1.5">
              <span className="w-1.5 h-1.5 rounded-full bg-amber-400" />
              DEMO MODE
            </span>
          )}
          {resetMsg && (
            <span className={`text-[11px] font-bold px-3 py-1.5 rounded-full border flex items-center gap-1.5 ${resetMsg.startsWith("✅") ? "text-green-400 bg-green-500/10 border-green-500/20" : "text-red-400 bg-red-500/10 border-red-500/20"}`}>
              {resetMsg}
            </span>
          )}
          
          <Link href="/training" className="flex items-center gap-2 text-[13px] font-semibold text-purple-300 bg-purple-500/10 hover:bg-purple-500/20 border border-purple-500/20 px-4 py-2 rounded-xl transition-all duration-200">
            <Icons.Academy /> Training Hub
          </Link>
          
          <Link href="/campaigns/new" className="flex items-center gap-2 text-[13px] font-semibold text-white bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 px-4 py-2 rounded-xl shadow-lg shadow-blue-500/20 hover:shadow-blue-500/40 transition-all duration-200">
            <Icons.Plus /> New Campaign
          </Link>

          <div className="h-6 w-px bg-white/10 mx-1" />
          
          <button onClick={fetchStats} className="p-2.5 text-slate-400 hover:text-white bg-white/5 hover:bg-white/10 border border-white/5 rounded-xl transition-all duration-200">
            <Icons.Refresh />
          </button>
          
          <button
            onClick={resetDb}
            disabled={resetting}
            className={`flex items-center gap-2 px-4 py-2 text-[13px] font-semibold rounded-xl border transition-all duration-200 ${
              resetting ? "bg-red-500/5 border-red-500/10 text-slate-500 cursor-not-allowed" : "bg-red-500/10 hover:bg-red-500/20 border-red-500/20 text-red-400"
            }`}
          >
            <Icons.Refresh spinning={resetting} />
            {resetting ? "Resetting…" : "Reset Data"}
          </button>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-8 py-8 animate-fade-in">
        
        {/* KPI Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          {[
            { icon: <Icons.Users />, label: "Total Employees", value: loading ? "…" : s?.total_users ?? 0, trend: "+12% this month", color: "from-blue-500/20 to-blue-500/5" },
            { icon: <Icons.Shield />, label: "Campaigns Run", value: loading ? "…" : s?.total_campaigns ?? 0, trend: "2 active now", color: "from-purple-500/20 to-purple-500/5" },
            { icon: <Icons.TrendDown />, label: "Overall Click Rate", value: loading ? "…" : `${s?.overall_click_rate ?? 0}%`, trend: "-3.2% vs last month", color: "from-cyan-500/20 to-cyan-500/5" },
            { icon: <Icons.Alert />, label: "High Risk Users", value: loading ? "…" : s?.risk_distribution["High"] ?? 0, trend: "Requires training", color: "from-red-500/20 to-red-500/5" },
          ].map((k, i) => (
            <div key={i} className="group relative bg-slate-900/50 backdrop-blur-md border border-white/5 hover:border-white/10 rounded-2xl p-6 overflow-hidden transition-all duration-300 hover:-translate-y-1 hover:shadow-xl hover:shadow-black/20">
              <div className={`absolute top-0 right-0 w-32 h-32 bg-gradient-to-bl ${k.color} rounded-bl-full opacity-50 -z-10 group-hover:scale-110 transition-transform duration-500`} />
              <div className="flex items-center gap-3 mb-4">
                <div className="bg-slate-950/50 p-2.5 rounded-xl border border-white/5 shadow-inner">
                  {k.icon}
                </div>
                <h3 className="text-sm font-medium text-slate-400">{k.label}</h3>
              </div>
              <div className="text-3xl font-bold text-white mb-2">{k.value}</div>
              <div className="text-xs font-medium text-slate-500">{k.trend}</div>
            </div>
          ))}
        </div>

        {/* Charts Section */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
          {/* Donut Chart */}
          <div className="bg-slate-900/50 backdrop-blur-md border border-white/5 rounded-2xl p-6 lg:col-span-1 shadow-lg shadow-black/10">
            <div className="flex items-center justify-between mb-6">
              <h3 className="text-sm font-bold text-slate-300 uppercase tracking-wider">Risk Distribution</h3>
              <div className="w-8 h-8 rounded-full bg-slate-800 flex items-center justify-center border border-white/5 text-slate-400">📊</div>
            </div>
            <div className="h-[220px] flex items-center justify-center relative">
              {s ? <RiskDonut data={s.risk_distribution} /> : <div className="w-32 h-32 rounded-full border-4 border-slate-800 border-t-blue-500 animate-spin" />}
              {s && (
                <div className="absolute inset-0 flex flex-col items-center justify-center pointer-events-none">
                  <span className="text-2xl font-bold text-white">{s.total_users}</span>
                  <span className="text-[10px] text-slate-500 font-bold uppercase tracking-widest mt-1">Users</span>
                </div>
              )}
            </div>
          </div>

          {/* Bar Chart */}
          <div className="bg-slate-900/50 backdrop-blur-md border border-white/5 rounded-2xl p-6 lg:col-span-2 shadow-lg shadow-black/10">
             <div className="flex items-center justify-between mb-6">
              <h3 className="text-sm font-bold text-slate-300 uppercase tracking-wider">Campaign Performance (Click Rate)</h3>
              <div className="text-xs font-semibold text-blue-400 bg-blue-500/10 px-3 py-1 rounded-full border border-blue-500/20">Last 30 Days</div>
            </div>
            {s ? <CampaignBar campaigns={s.campaign_click_rates} /> : (
              <div className="h-[220px] flex items-end justify-between gap-4 pb-4">
                {[1,2,3,4,5].map((_, idx) => <div key={idx} className="w-full bg-slate-800/50 rounded-t-lg animate-pulse" style={{ height: `${Math.random() * 60 + 20}%` }} />)}
              </div>
            )}
          </div>
        </div>

        {/* Data Tables Section */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-12">
          
          {/* Top Risk Users */}
          <div className="bg-slate-900/50 backdrop-blur-md border border-white/5 rounded-2xl p-6 lg:col-span-2 shadow-lg shadow-black/10 flex flex-col">
            <div className="flex items-center justify-between mb-6">
              <div>
                <h3 className="text-sm font-bold text-slate-300 uppercase tracking-wider flex items-center gap-2">
                  <span className="w-2 h-2 rounded-full bg-red-500 animate-pulse" />
                  Top Risk Users
                </h3>
                <p className="text-xs text-slate-500 mt-1">Employees with highest calculated P(Fail)</p>
              </div>
              <button className="text-xs font-semibold text-slate-400 hover:text-white transition-colors">View All &rarr;</button>
            </div>
            
            <div className="overflow-x-auto">
              <table className="w-full text-left border-collapse">
                <thead>
                  <tr className="border-b border-white/5 text-[11px] font-bold text-slate-500 uppercase tracking-wider">
                    <th className="pb-3 pl-2">Employee</th>
                    <th className="pb-3">Department</th>
                    <th className="pb-3">Risk Tier</th>
                    <th className="pb-3 text-right">P(Fail)</th>
                    <th className="pb-3 text-center">F/S</th>
                  </tr>
                </thead>
                <tbody className="text-sm divide-y divide-white/5">
                  {(s?.top_risk_users ?? []).map((u, i) => (
                    <tr key={u.user_id} className="hover:bg-white/[0.02] transition-colors group">
                      <td className="py-3 pl-2">
                        <div className="font-semibold text-slate-200">{u.full_name}</div>
                        <div className="text-[11px] text-slate-500 font-mono mt-0.5">{u.email}</div>
                      </td>
                      <td className="py-3 text-slate-400 font-medium">{u.department}</td>
                      <td className="py-3"><RiskBadge tier={u.risk_tier} /></td>
                      <td className="py-3 text-right">
                        <span className={`font-mono font-bold ${u.p_fail >= 0.7 ? "text-red-400" : u.p_fail >= 0.4 ? "text-amber-400" : "text-green-400"}`}>
                          {(u.p_fail * 100).toFixed(1)}%
                        </span>
                      </td>
                      <td className="py-3 text-center">
                        <span className="text-red-400 font-bold">{u.total_failures}</span>
                        <span className="text-slate-600 mx-1">/</span>
                        <span className="text-slate-400">{u.total_simulations}</span>
                      </td>
                    </tr>
                  ))}
                  {(!s?.top_risk_users || s.top_risk_users.length === 0) && (
                    <tr><td colSpan={5} className="py-8 text-center text-slate-500 text-sm">No risk data available</td></tr>
                  )}
                </tbody>
              </table>
            </div>
          </div>

          {/* Recent Campaigns List */}
          <div className="bg-slate-900/50 backdrop-blur-md border border-white/5 rounded-2xl p-6 lg:col-span-1 shadow-lg shadow-black/10 flex flex-col">
            <div className="flex items-center justify-between mb-6">
              <div>
                <h3 className="text-sm font-bold text-slate-300 uppercase tracking-wider">Recent Activity</h3>
                <p className="text-xs text-slate-500 mt-1">Latest simulation campaigns</p>
              </div>
            </div>
            
            <div className="flex flex-col gap-3">
              {(s?.recent_campaigns ?? []).map((c) => (
                <div key={c.campaign_id} className="group p-4 rounded-xl bg-white/[0.02] border border-white/5 hover:border-white/10 hover:bg-white/[0.04] transition-all cursor-pointer">
                  <div className="flex justify-between items-start mb-2">
                    <h4 className="font-semibold text-sm text-slate-200 line-clamp-1 pr-4">{c.name}</h4>
                    <StatusBadge status={c.status} />
                  </div>
                  
                  <div className="grid grid-cols-3 gap-2 mt-3 pt-3 border-t border-white/5">
                    <div className="flex flex-col">
                      <span className="text-[10px] text-slate-500 uppercase font-bold">Sent</span>
                      <span className="text-sm font-medium text-slate-300">{c.emails_sent}/{c.target_count}</span>
                    </div>
                    <div className="flex flex-col">
                      <span className="text-[10px] text-slate-500 uppercase font-bold">Clicks</span>
                      <span className="text-sm font-bold text-amber-400">{c.clicks}</span>
                    </div>
                    <div className="flex flex-col">
                      <span className="text-[10px] text-slate-500 uppercase font-bold">Reports</span>
                      <span className="text-sm font-bold text-green-400">{c.reports}</span>
                    </div>
                  </div>
                </div>
              ))}
              {(!s?.recent_campaigns || s.recent_campaigns.length === 0) && (
                <div className="flex-1 flex flex-col items-center justify-center py-8 text-center border-2 border-dashed border-white/5 rounded-xl">
                  <span className="text-2xl mb-2 opacity-50">📫</span>
                  <span className="text-sm text-slate-400">No recent campaigns</span>
                </div>
              )}
            </div>
            
            <Link href="/campaigns" className="mt-auto pt-6 text-center text-xs font-semibold text-blue-400 hover:text-blue-300 transition-colors">
              View All Campaigns &rarr;
            </Link>
          </div>

        </div>
      </main>
    </div>
  );
}
