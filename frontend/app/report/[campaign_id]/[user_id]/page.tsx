"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { ShieldCheck, Loader2 } from "lucide-react";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export default function ReportPhishingPage() {
  const params = useParams();
  const campaign_id = params.campaign_id as string;
  const user_id = params.user_id as string;

  const [status, setStatus] = useState<"loading" | "success" | "error">("loading");

  useEffect(() => {
    if (!campaign_id || !user_id) {
      setStatus("error");
      return;
    }

    const reportEmail = async () => {
      try {
        const res = await fetch(`${API_URL}/track/report/${campaign_id}/${user_id}`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
        });

        if (res.ok) {
          setStatus("success");
        } else {
          setStatus("error");
        }
      } catch (err) {
        setStatus("error");
      }
    };

    reportEmail();
  }, [campaign_id, user_id]);

  return (
    <div style={{ minHeight: "100vh", background: "#0a0e1a", color: "#e2e8f0", fontFamily: "Segoe UI, sans-serif", display: "flex", alignItems: "center", justifyContent: "center" }}>
      <div style={{ background: "rgba(255,255,255,0.03)", border: "1px solid rgba(255,255,255,0.07)", borderRadius: 16, padding: "40px", textAlign: "center", maxWidth: "480px", width: "90%" }}>
        
        {status === "loading" && (
          <div style={{ display: "flex", flexDirection: "column", alignItems: "center", gap: 16 }}>
            <Loader2 className="w-12 h-12 text-blue-500 animate-spin" />
            <h2 style={{ fontSize: 22, fontWeight: 700, color: "#fff" }}>Logging Report...</h2>
            <p style={{ color: "#94a3b8" }}>Please wait while we log this as positive behavior.</p>
          </div>
        )}

        {status === "success" && (
          <div style={{ display: "flex", flexDirection: "column", alignItems: "center", gap: 16 }}>
            <div style={{ background: "rgba(34,197,94,0.15)", borderRadius: "50%", padding: 20 }}>
              <ShieldCheck className="w-16 h-16 text-green-500" />
            </div>
            <h2 style={{ fontSize: 24, fontWeight: 700, color: "#fff" }}>Great Catch!</h2>
            <p style={{ color: "#94a3b8", lineHeight: 1.6 }}>
              Thank you for reporting this email. You correctly identified a simulated phishing attack. Your positive behavior has been recorded and will positively impact your Risk Score.
            </p>
            <p style={{ color: "#64748b", fontSize: 13, marginTop: 10 }}>
              You may now close this tab.
            </p>
          </div>
        )}

        {status === "error" && (
          <div style={{ display: "flex", flexDirection: "column", alignItems: "center", gap: 16 }}>
            <div style={{ background: "rgba(239,68,68,0.15)", borderRadius: "50%", padding: 20, fontSize: 32 }}>
              ❌
            </div>
            <h2 style={{ fontSize: 24, fontWeight: 700, color: "#fff" }}>Something went wrong</h2>
            <p style={{ color: "#94a3b8", lineHeight: 1.6 }}>
              We could not log this report. The campaign might have ended or the link is invalid. Please contact the IT department if this persists.
            </p>
          </div>
        )}

      </div>
    </div>
  );
}
