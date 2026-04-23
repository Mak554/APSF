"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { BookOpen, Award, PlayCircle, CheckCircle, Video, UserCircle, Loader2 } from "lucide-react";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

type UserProfile = {
  user_id: string;
  email: string;
  full_name: string;
  department: string;
  risk_tier: string;
};

type TrainingAssignment = {
  assignment_id: string;
  module_id: string;
  module_title: string;
  reason: string;
  is_mandatory: boolean;
  is_completed: boolean;
};

export default function TrainingHub() {
  const [activeTab, setActiveTab] = useState("all");
  const [users, setUsers] = useState<UserProfile[]>([]);
  const [selectedUserId, setSelectedUserId] = useState<string>("");
  const [assignments, setAssignments] = useState<TrainingAssignment[]>([]);
  const [loadingUsers, setLoadingUsers] = useState(true);
  const [loadingModules, setLoadingModules] = useState(false);

  // 1. Fetch users on mount
  useEffect(() => {
    const fetchUsers = async () => {
      try {
        const res = await fetch(`${API_URL}/users/`);
        if (res.ok) {
          const data = await res.json();
          setUsers(data);
          if (data.length > 0) {
            setSelectedUserId(data[0].user_id);
          }
        }
      } catch (err) {
        console.error("Could not fetch users", err);
      } finally {
        setLoadingUsers(false);
      }
    };
    fetchUsers();
  }, []);

  // 2. Fetch assignments when selected user changes
  useEffect(() => {
    if (!selectedUserId) return;

    const fetchAssignments = async () => {
      setLoadingModules(true);
      try {
        const res = await fetch(`${API_URL}/atm/training-assignments/${selectedUserId}`);
        if (res.ok) {
          const data = await res.json();
          setAssignments(data);
        }
      } catch (err) {
        console.error("Could not fetch training assignments", err);
      } finally {
        setLoadingModules(false);
      }
    };
    fetchAssignments();
  }, [selectedUserId]);

  const handleComplete = async (assignment_id: string) => {
    try {
      const res = await fetch(`${API_URL}/atm/complete-training/${assignment_id}`, {
        method: "POST",
      });
      if (res.ok) {
        setAssignments(prev =>
          prev.map(a => a.assignment_id === assignment_id ? { ...a, is_completed: true } : a)
        );
      }
    } catch (err) {
      console.error("Failed to complete module", err);
    }
  };

  const selectedUser = users.find(u => u.user_id === selectedUserId);
  const pendingCount = assignments.filter(a => !a.is_completed).length;
  const completedCount = assignments.filter(a => a.is_completed).length;
  const progressRatio = assignments.length > 0 ? Math.round((completedCount / assignments.length) * 100) : 0;

  const filteredAssignments = assignments.filter(a => {
    if (activeTab === "all") return true;
    if (activeTab === "pending") return !a.is_completed;
    if (activeTab === "completed") return a.is_completed;
    return true;
  });

  return (
    <div style={{ minHeight: "100vh", background: "#0a0e1a", color: "#e2e8f0", fontFamily: "Segoe UI, sans-serif" }}>
      {/* Header */}
      <header style={{ borderBottom: "1px solid rgba(255,255,255,0.06)", padding: "14px 32px", display: "flex", alignItems: "center", justifyContent: "space-between", background: "rgba(255,255,255,0.02)" }}>
        <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
          <div style={{ width: 36, height: 36, background: "rgba(168,85,247,0.15)", borderRadius: 10, display: "flex", alignItems: "center", justifyContent: "center", color: "#c084fc" }}>
            <BookOpen className="w-5 h-5" />
          </div>
          <div>
            <div style={{ fontWeight: 700, fontSize: 16, color: "#fff" }}>Academy & Training</div>
            <div style={{ fontSize: 11, color: "#64748b" }}>APSF Employee Security Awareness</div>
          </div>
        </div>
        
        {/* User Selector Dropdown */}
        {!loadingUsers && users.length > 0 && (
          <div style={{ display: "flex", alignItems: "center", gap: 10, background: "rgba(255,255,255,0.05)", padding: "6px 12px", borderRadius: 12, border: "1px solid rgba(255,255,255,0.1)" }}>
            <UserCircle className="w-5 h-5 text-slate-400" />
            <select
              value={selectedUserId}
              onChange={(e) => setSelectedUserId(e.target.value)}
              style={{ background: "transparent", color: "#fff", border: "none", outline: "none", fontSize: 14, cursor: "pointer" }}
            >
              {users.map(u => (
                <option key={u.user_id} value={u.user_id} style={{ color: "#000" }}>
                  {u.full_name} ({u.department})
                </option>
              ))}
            </select>
          </div>
        )}

        <div style={{ display: "flex", gap: 10, alignItems: "center" }}>
          <Link href="/" style={{ fontSize: 13, color: "#94a3b8", textDecoration: "none" }}>← Back to Dashboard</Link>
        </div>
      </header>

      <div style={{ maxWidth: 1000, margin: "0 auto", padding: "40px 32px" }}>
        {/* Welcome Section */}
        <div style={{ background: "linear-gradient(135deg, rgba(59,130,246,0.1) 0%, rgba(168,85,247,0.1) 100%)", borderRadius: 16, padding: 32, border: "1px solid rgba(255,255,255,0.05)", marginBottom: 40 }}>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
            <div>
              <h1 style={{ fontSize: 24, fontWeight: 700, color: "#fff", marginBottom: 8, display: "flex", alignItems: "center", gap: 10 }}>
                Welcome back, {selectedUser ? selectedUser.full_name : "Employee"} <Award className="w-6 h-6 text-yellow-400" />
              </h1>
              <p style={{ color: "#94a3b8", fontSize: 14, maxWidth: 600, lineHeight: 1.5 }}>
                Your Risk Tier is currently <strong style={{ color: selectedUser?.risk_tier === "High" ? "#f87171" : selectedUser?.risk_tier === "Medium" ? "#fbbf24" : "#4ade80" }}>{selectedUser?.risk_tier || "..."}</strong>. You have <strong style={{ color: pendingCount > 0 ? "#fbbf24" : "#4ade80" }}>{pendingCount} pending modules</strong>. Complete them to maintain your department's compliance rating and protect the organization.
              </p>
            </div>
            <div style={{ textAlign: "center", background: "rgba(255,255,255,0.03)", padding: "16px 24px", borderRadius: 12, border: "1px solid rgba(255,255,255,0.05)" }}>
              <div style={{ fontSize: 32, fontWeight: 700, color: progressRatio === 100 ? "#4ade80" : "#fff" }}>{progressRatio}%</div>
              <div style={{ fontSize: 11, color: "#64748b", textTransform: "uppercase", letterSpacing: 1 }}>Completed</div>
            </div>
          </div>
        </div>

        {/* Tabs */}
        <div style={{ display: "flex", gap: 12, marginBottom: 24, borderBottom: "1px solid rgba(255,255,255,0.05)", paddingBottom: 16 }}>
          {[
            { id: "all", label: "All Modules" },
            { id: "pending", label: "Pending Tasks" },
            { id: "completed", label: "Completed" },
          ].map(tab => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              style={{
                background: activeTab === tab.id ? "rgba(59,130,246,0.1)" : "transparent",
                color: activeTab === tab.id ? "#60a5fa" : "#94a3b8",
                border: "none",
                padding: "8px 16px",
                borderRadius: 20,
                fontSize: 13,
                fontWeight: 600,
                cursor: "pointer",
                transition: "all 0.2s"
              }}
            >
              {tab.label}
            </button>
          ))}
        </div>

        {/* Course Grid */}
        {loadingModules && (
          <div style={{ textAlign: "center", padding: 40 }}>
            <Loader2 className="w-8 h-8 text-blue-500 animate-spin mx-auto mb-4" />
            <p style={{ color: "#64748b" }}>Loading your personalized training...</p>
          </div>
        )}

        {!loadingModules && assignments.length === 0 && (
          <div style={{ textAlign: "center", padding: "60px 20px", background: "rgba(255,255,255,0.02)", borderRadius: 16, border: "1px dashed rgba(255,255,255,0.1)" }}>
            <Award className="w-12 h-12 text-green-500 mx-auto mb-4 opacity-50" />
            <h3 style={{ fontSize: 18, color: "#fff", marginBottom: 8 }}>You're all caught up!</h3>
            <p style={{ color: "#94a3b8" }}>You currently have no training assignments assigned by the ATM.</p>
          </div>
        )}

        {!loadingModules && assignments.length > 0 && (
          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(300px, 1fr))", gap: 20 }}>
            {filteredAssignments.map((module) => (
              <div key={module.assignment_id} style={{
                background: "rgba(255,255,255,0.02)",
                border: `1px solid ${module.is_completed ? "rgba(34,197,94,0.2)" : "rgba(255,255,255,0.05)"}`,
                borderRadius: 16,
                overflow: "hidden",
                transition: "transform 0.2s",
                display: "flex",
                flexDirection: "column"
              }}>
                <div style={{ height: 120, background: "rgba(255,255,255,0.02)", display: "flex", alignItems: "center", justifyContent: "center", color: "rgba(255,255,255,0.1)", position: "relative" }}>
                  <Video className="w-12 h-12" />
                  {module.is_mandatory && !module.is_completed && (
                    <div style={{ position: "absolute", top: 10, right: 10, background: "rgba(239,68,68,0.2)", color: "#f87171", padding: "4px 8px", borderRadius: 6, fontSize: 11, fontWeight: "bold", border: "1px solid rgba(239,68,68,0.3)" }}>
                      MANDATORY
                    </div>
                  )}
                </div>
                <div style={{ padding: 20, flex: 1, display: "flex", flexDirection: "column" }}>
                  <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: 12 }}>
                    <div style={{ display: "flex", alignItems: "center", gap: 8, color: "#94a3b8", fontSize: 11 }}>
                      <span style={{ background: "rgba(255,255,255,0.05)", padding: "2px 8px", borderRadius: 4 }}>Security Module</span>
                    </div>
                    {module.is_completed ? (
                      <CheckCircle className="w-5 h-5 text-green-500" />
                    ) : (
                      <PlayCircle className="w-5 h-5 text-blue-500" />
                    )}
                  </div>
                  <h3 style={{ fontSize: 15, fontWeight: 600, color: "#fff", marginBottom: 6 }}>{module.module_title}</h3>
                  <p style={{ fontSize: 12, color: "#64748b", margin: "10px 0", flex: 1 }}>{module.reason}</p>
                  
                  <button 
                    onClick={() => !module.is_completed && handleComplete(module.assignment_id)}
                    disabled={module.is_completed}
                    style={{
                      width: "100%",
                      marginTop: 20,
                      padding: "10px",
                      background: module.is_completed ? "rgba(34,197,94,0.1)" : "linear-gradient(135deg, rgba(59,130,246,0.2), rgba(37,99,235,0.2))",
                      color: module.is_completed ? "#4ade80" : "#60a5fa",
                      border: module.is_completed ? "none" : "1px solid rgba(59,130,246,0.3)",
                      borderRadius: 8,
                      fontSize: 13,
                      fontWeight: 600,
                      cursor: module.is_completed ? "default" : "pointer",
                      transition: "all 0.2s"
                    }}>
                    {module.is_completed ? "Completed!" : "Complete Module"}
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}

      </div>
    </div>
  );
}
