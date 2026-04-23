"use client";
import { useState, useEffect, useRef } from "react";
import { useParams } from "next/navigation";
import { 
  ShieldAlert, BookOpen, CheckCircle, ArrowRight, Lock, Eye, EyeOff, X, 
  AlertTriangle, User, Bell, ChevronDown, Wifi, FileText, Download, Briefcase, Building
} from "lucide-react";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8009";

type Phase = "portal" | "training";

// ─── Portal configs per template ──────────────────────────────────────────────
const PORTALS: Record<string, any> = {
  // IT Scenarios
  "tpl-it-easy": { type: "it-easy", revealWho: "IT Help Desk" },
  "tpl-it-medium": { type: "it-medium", revealWho: "IT Security Team" },
  "tpl-it-hard": { type: "it-hard", revealWho: "IT Security Department" },
  // HR Scenarios
  "tpl-hr-easy": { type: "hr-easy", revealWho: "HR Boss" },
  "tpl-hr-medium": { type: "hr-medium", revealWho: "HR Department" },
  "tpl-hr-hard": { type: "hr-hard", revealWho: "HR Compliance Team" },
  // CEO Scenarios
  "tpl-ceo-easy": { type: "ceo-easy", revealWho: "The CEO" },
  "tpl-ceo-medium": { type: "ceo-medium", revealWho: "CEO / Executive Office" },
  "tpl-ceo-hard": { type: "ceo-hard", revealWho: "The CEO & Board of Directors" },
  
  // Aliases for backward compatibility
  "tpl-001": { type: "it-medium", revealWho: "IT Security Team" },
  "tpl-002": { type: "hr-medium", revealWho: "HR Department" },
  "tpl-003": { type: "ceo-medium", revealWho: "CEO / Executive Office" },
};

const DEFAULT_PORTAL = PORTALS["tpl-it-medium"];

export default function LandingPage() {
  const params = useParams();
  const campaignId = params.campaign_id as string;
  const userId = params.user_id as string;

  const [phase, setPhase] = useState<Phase>("portal");
  const [portalKey, setPortalKey] = useState("tpl-it-medium");
  
  // Shared form state
  const [credential, setCredential] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [showModal, setShowModal] = useState(false);
  const clickLogged = useRef(false);
  
  // Extra fields for HR / CEO portals
  const [employeeId, setEmployeeId] = useState("");
  const [dob, setDob] = useState("");
  const [nationalId, setNationalId] = useState("");
  const [authCode, setAuthCode] = useState("");
  const [pin, setPin] = useState("");

  useEffect(() => {
    const searchParams = new URLSearchParams(window.location.search);
    const previewTpl = searchParams.get("template");
    if (previewTpl && PORTALS[previewTpl]) {
      setPortalKey(previewTpl);
      return;
    }
    if (!campaignId || campaignId === "preview") return;
    fetch(`${API_URL}/campaigns/${campaignId}`)
      .then(r => r.json())
      .then(data => { if (data?.email_template_id) setPortalKey(data.email_template_id); })
      .catch(() => {});
  }, [campaignId]);

  useEffect(() => {
    if (campaignId && userId && campaignId !== "preview" && !clickLogged.current) {
      clickLogged.current = true;
      fetch(`${API_URL}/track/click/${campaignId}/${userId}`).catch(() => {});
    }
  }, [campaignId, userId]);

  const portal = PORTALS[portalKey] ?? DEFAULT_PORTAL;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitting(true);
    const extra = portalKey.includes("hr")
      ? { employee_id: employeeId, date_of_birth: dob, national_id: nationalId }
      : portalKey.includes("ceo")
      ? { employee_id: employeeId, auth_code: authCode, pin_entered: !!pin }
      : {};
    
    if (campaignId !== "preview") {
      await fetch(`${API_URL}/track/submit/${campaignId}/${userId}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ submitted_data: { credential_entered: !!credential, password_entered: !!password, ...extra } }),
      }).catch(() => {});
    }
    
    await new Promise(r => setTimeout(r, 900));
    setSubmitting(false);
    setShowModal(true);
  };

  const formProps = {
    portal, credential, setCredential, password, setPassword,
    showPassword, setShowPassword, submitting, handleSubmit,
    employeeId, setEmployeeId, dob, setDob, nationalId, setNationalId,
    authCode, setAuthCode, pin, setPin, portalKey
  };

  if (phase === "training") return <TrainingPhase />;

  return (
    <>
      {showModal && <PhishedModal portal={portal} onClose={() => { setShowModal(false); setPhase("training"); }} />}
      
      {portal.type === "it-easy" && <ITEasyLayout {...formProps} />}
      {portal.type === "hr-easy" && <HREasyLayout {...formProps} />}
      {portal.type === "ceo-easy" && <CEOEasyLayout {...formProps} />}
      
      {portal.type === "it-medium" && <ITMediumLayout {...formProps} />}
      {portal.type === "hr-medium" && <HRMediumLayout {...formProps} />}
      {portal.type === "ceo-medium" && <CEOMediumLayout {...formProps} />}
      
      {portal.type === "it-hard" && <ITHardLayout {...formProps} />}
      {portal.type === "hr-hard" && <HRHardLayout {...formProps} />}
      {portal.type === "ceo-hard" && <CEOHardLayout {...formProps} />}
    </>
  );
}

// ============================================================================
// EASY DESIGNS
// ============================================================================

function ITEasyLayout({ credential, setCredential, password, setPassword, submitting, handleSubmit }: any) {
  const scamStyle: React.CSSProperties = { fontFamily: '"Comic Sans MS", "Chalkboard SE", cursive' };
  return (
    <div style={{ ...scamStyle, minHeight: "100vh", background: "linear-gradient(135deg, #FFFF00 0%, #FF6600 50%, #FF0000 100%)", display: "flex", alignItems: "center", justifyContent: "center", padding: "16px" }}>
      <style>{`
        @keyframes blink { 0%,100%{opacity:1} 50%{opacity:0} }
        @keyframes shake { 0%,100%{transform:rotate(0deg)} 25%{transform:rotate(-2deg)} 75%{transform:rotate(2deg)} }
        @keyframes scrollLeft { 0% { transform: translateX(100%); } 100% { transform: translateX(-100%); } }
        .blink-btn { animation: blink 0.8s step-start infinite; }
        .shake-icon { animation: shake 0.5s infinite; display:inline-block; }
        .fake-marquee { color: #FF0000; background: #FFFFFF; font-size: 11px; font-weight: bold; white-space: nowrap; overflow: hidden; display: block; padding: 2px; }
        .fake-marquee span { display: inline-block; animation: scrollLeft 8s linear infinite; width: 100%; }
      `}</style>
      <div style={{ width: "100%", maxWidth: "480px", background: "#ffffff", border: "6px solid #FF0000", boxShadow: "8px 8px 0px #000000" }}>
        <div style={{ background: "#0000FF", padding: "12px", textAlign: "center", borderBottom: "4px solid #FF0000" }}>
          <div style={{ fontSize: "28px" }} className="shake-icon">⚠️</div>
          <h1 style={{ margin: "4px 0", fontSize: "20px", color: "#FFFF00", fontWeight: 900, textTransform: "uppercase" }}>!! IT Support WebMail !!</h1>
          <div className="fake-marquee">
            <span>URGENT SECURTY NOTICE --- YOUR ACOUNT NEEDS VERIFYICATION --- ACT NOW!!!</span>
          </div>
        </div>
        <div style={{ padding: "20px" }}>
          <div style={{ background: "#FF0000", color: "#FFFFFF", padding: "10px", marginBottom: "16px", textAlign: "center", border: "3px solid #000000" }}>
            <p style={{ margin: 0, fontSize: "14px", fontWeight: "bold", lineHeight: "1.5" }}>
              ⚠️ WARNNING!! Your acount has been SUSPENED due to suspecious activty!!<br />
              <span style={{ fontSize: "12px" }}>Pease verfy ur identity IMMEDITELY or lose acess FOREVER!!!</span>
            </p>
          </div>
          <form onSubmit={handleSubmit}>
            <div style={{ marginBottom: "10px" }}>
              <label style={{ display: "block", fontSize: "12px", color: "#0000FF", fontWeight: "bold", marginBottom: "4px" }}>📧 Email (REQIURED!!):</label>
              <input type="email" value={credential} onChange={e => setCredential(e.target.value)} required style={{ width: "100%", padding: "8px", border: "3px solid #FF0000" }} />
            </div>
            <div style={{ marginBottom: "16px" }}>
              <label style={{ display: "block", fontSize: "12px", color: "#0000FF", fontWeight: "bold", marginBottom: "4px" }}>🔑 Pasword (REQIURED!!):</label>
              <input type="password" value={password} onChange={e => setPassword(e.target.value)} required style={{ width: "100%", padding: "8px", border: "3px solid #FF0000" }} />
            </div>
            <button type="submit" disabled={submitting} className={submitting ? "" : "blink-btn"} style={{ width: "100%", padding: "16px", background: "#00CC00", color: "#FFFFFF", border: "4px solid #000000", fontSize: "18px", fontWeight: 900, cursor: "pointer" }}>
              {submitting ? "⏳ PLEESE WATE..." : "👉👉 CLICK HERE NOW TO VERFY!!! 👈👈"}
            </button>
          </form>
        </div>
      </div>
    </div>
  );
}

function HREasyLayout({ credential, setCredential, password, setPassword, submitting, handleSubmit }: any) {
  // Looks like a terribly fake Google Form / Survey
  return (
    <div style={{ minHeight: "100vh", background: "#f0ebf8", fontFamily: "Arial, sans-serif", padding: "20px" }}>
      <div style={{ maxWidth: "640px", margin: "40px auto", background: "#fff", borderRadius: "8px", border: "1px solid #d4c5f9", borderTop: "10px solid #673ab7", padding: "30px", boxShadow: "0 2px 4px rgba(0,0,0,0.1)" }}>
        <h1 style={{ fontSize: "32px", margin: "0 0 10px 0", color: "#202124" }}>Employee Benefit Update Form</h1>
        <p style={{ color: "#70757a", fontSize: "14px", margin: "0 0 20px 0" }}>* Required</p>
        <div style={{ background: "#f8f9fa", padding: "15px", borderRadius: "8px", marginBottom: "20px", borderLeft: "4px solid #ea4335" }}>
          <p style={{ margin: 0, color: "#202124", fontSize: "14px" }}>Dear Employee, please enter your login to view your new salary and benefits for 2025.</p>
        </div>
        <form onSubmit={handleSubmit}>
          <div style={{ marginBottom: "25px", padding: "20px", background: "#fff", border: "1px solid #dadce0", borderRadius: "8px" }}>
            <label style={{ display: "block", fontSize: "16px", color: "#202124", marginBottom: "15px" }}>Email address <span style={{color: "#d93025"}}>*</span></label>
            <input type="email" value={credential} onChange={e => setCredential(e.target.value)} required placeholder="Your answer" style={{ width: "50%", border: "none", borderBottom: "1px solid #d1d5db", padding: "8px 0", outline: "none", fontSize: "14px" }} />
          </div>
          <div style={{ marginBottom: "25px", padding: "20px", background: "#fff", border: "1px solid #dadce0", borderRadius: "8px" }}>
            <label style={{ display: "block", fontSize: "16px", color: "#202124", marginBottom: "15px" }}>Account Password <span style={{color: "#d93025"}}>*</span></label>
            <input type="password" value={password} onChange={e => setPassword(e.target.value)} required placeholder="Your answer" style={{ width: "50%", border: "none", borderBottom: "1px solid #d1d5db", padding: "8px 0", outline: "none", fontSize: "14px" }} />
          </div>
          <button type="submit" disabled={submitting} style={{ background: "#673ab7", color: "#fff", border: "none", padding: "10px 24px", borderRadius: "4px", fontSize: "14px", fontWeight: "bold", cursor: "pointer" }}>
            {submitting ? "Submitting..." : "Submit"}
          </button>
        </form>
      </div>
    </div>
  );
}

function CEOEasyLayout({ credential, setCredential, password, setPassword, submitting, handleSubmit }: any) {
  // Looks like a sketchy generic file hosting page (WeTransfer/Dropbox rip-off)
  return (
    <div style={{ minHeight: "100vh", background: "#f9fafb", display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", fontFamily: "sans-serif" }}>
      <div style={{ textAlign: "center", marginBottom: "30px" }}>
        <h1 style={{ color: "#2563eb", fontSize: "40px", margin: 0, fontWeight: 900 }}>FileShare<span style={{color: "#f59e0b"}}>PRO</span></h1>
        <p style={{ color: "#6b7280" }}>The fastest way to send big files.</p>
      </div>
      <div style={{ width: "400px", background: "#fff", borderRadius: "12px", boxShadow: "0 10px 25px rgba(0,0,0,0.05)", padding: "30px", border: "1px solid #e5e7eb" }}>
        <div style={{ display: "flex", alignItems: "center", gap: "15px", marginBottom: "20px", paddingBottom: "20px", borderBottom: "1px solid #f3f4f6" }}>
          <div style={{ background: "#eff6ff", padding: "12px", borderRadius: "12px" }}>
            <Download className="w-8 h-8 text-blue-600" />
          </div>
          <div>
            <h3 style={{ margin: 0, color: "#111827", fontSize: "16px" }}>Q3_Financial_Review.pdf</h3>
            <p style={{ margin: 0, color: "#6b7280", fontSize: "13px" }}>2.4 MB • Sent by The CEO</p>
          </div>
        </div>
        <form onSubmit={handleSubmit} style={{ display: "flex", flexDirection: "column", gap: "15px" }}>
          <p style={{ margin: 0, color: "#ef4444", fontSize: "13px", fontWeight: "bold" }}>This file is protected. Login to download.</p>
          <input type="email" value={credential} onChange={e => setCredential(e.target.value)} required placeholder="Email Address" style={{ padding: "12px", borderRadius: "6px", border: "1px solid #d1d5db", background: "#f9fafb" }} />
          <input type="password" value={password} onChange={e => setPassword(e.target.value)} required placeholder="Password" style={{ padding: "12px", borderRadius: "6px", border: "1px solid #d1d5db", background: "#f9fafb" }} />
          <button type="submit" disabled={submitting} style={{ background: "#2563eb", color: "#fff", padding: "14px", borderRadius: "6px", border: "none", fontWeight: "bold", cursor: "pointer", fontSize: "16px" }}>
            {submitting ? "Processing..." : "Download File"}
          </button>
        </form>
      </div>
    </div>
  );
}


// ============================================================================
// MEDIUM DESIGNS
// ============================================================================

function ITMediumLayout({ credential, setCredential, password, setPassword, showPassword, setShowPassword, submitting, handleSubmit }: any) {
  // Generic standard corporate portal (Microsoft 365 style)
  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-slate-50 font-sans p-4">
      <div className="w-full max-w-[440px] bg-white border border-slate-200 shadow-xl rounded-lg overflow-hidden">
        <div className="px-8 pt-8 pb-6">
          <div className="flex items-center gap-2 mb-6">
            <div className="w-8 h-8 bg-blue-600 rounded flex items-center justify-center"><Building className="w-5 h-5 text-white" /></div>
            <span className="text-xl font-semibold text-slate-800">NexaCore Systems</span>
          </div>
          <h2 className="text-2xl font-semibold text-slate-800 mb-2">Sign In</h2>
          <p className="text-sm text-slate-600 mb-6">to access Corporate Intranet and Services</p>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <input type="email" value={credential} onChange={e => setCredential(e.target.value)} required placeholder="someone@nexacore.sa" 
                className="w-full px-3 py-2 border border-slate-300 rounded focus:outline-none focus:border-blue-600 focus:ring-1 focus:ring-blue-600" />
            </div>
            <div className="relative">
              <input type={showPassword ? "text" : "password"} value={password} onChange={e => setPassword(e.target.value)} required placeholder="Password" 
                className="w-full px-3 py-2 border border-slate-300 rounded focus:outline-none focus:border-blue-600 focus:ring-1 focus:ring-blue-600" />
            </div>
            <p className="text-xs text-blue-600 hover:underline cursor-pointer">Forgot my password</p>
            <div className="pt-2 flex justify-end">
              <button type="submit" disabled={submitting} className="bg-blue-600 hover:bg-blue-700 text-white px-8 py-2 rounded font-medium transition-colors">
                {submitting ? "Signing in..." : "Next"}
              </button>
            </div>
          </form>
        </div>
        <div className="bg-slate-100 px-8 py-4 border-t border-slate-200 flex items-center gap-3">
          <Lock className="w-4 h-4 text-slate-500" />
          <span className="text-xs text-slate-500">Sign-in options</span>
        </div>
      </div>
      <div className="mt-8 flex gap-4 text-xs text-slate-500">
        <span>Terms of use</span>
        <span>Privacy & cookies</span>
      </div>
    </div>
  );
}

function HRMediumLayout({ credential, setCredential, password, setPassword, submitting, handleSubmit }: any) {
  // Workday / HR Dashboard Style
  return (
    <div className="min-h-screen bg-slate-100 flex flex-col font-sans">
      <nav className="bg-white border-b border-slate-200 h-14 flex items-center px-6 justify-between shrink-0">
        <div className="flex items-center gap-2">
          <Briefcase className="w-6 h-6 text-blue-700" />
          <span className="text-lg font-bold text-blue-900 tracking-tight">PeopleFirst</span>
        </div>
      </nav>
      <div className="flex-1 flex items-center justify-center p-6">
        <div className="w-full max-w-4xl bg-white rounded-2xl shadow-lg border border-slate-200 flex overflow-hidden min-h-[500px]">
          {/* Left panel - Info */}
          <div className="w-1/2 bg-blue-50 p-10 flex flex-col justify-between hidden md:flex">
            <div>
              <h2 className="text-2xl font-bold text-blue-900 mb-4">Annual Benefits Enrollment</h2>
              <p className="text-slate-600 text-sm leading-relaxed mb-6">
                Welcome to the PeopleFirst employee portal. It's time to review and update your benefits for the upcoming year. Ensure all dependent information is correct to avoid coverage drops.
              </p>
              <div className="space-y-4">
                <div className="flex items-start gap-3">
                  <CheckCircle className="w-5 h-5 text-green-600 shrink-0" />
                  <p className="text-sm text-slate-700">Health & Dental Insurance</p>
                </div>
                <div className="flex items-start gap-3">
                  <CheckCircle className="w-5 h-5 text-green-600 shrink-0" />
                  <p className="text-sm text-slate-700">Retirement Contributions</p>
                </div>
                <div className="flex items-start gap-3">
                  <CheckCircle className="w-5 h-5 text-green-600 shrink-0" />
                  <p className="text-sm text-slate-700">Tax Withholding Adjustments</p>
                </div>
              </div>
            </div>
            <p className="text-xs text-slate-400">© 2025 PeopleFirst HR Solutions</p>
          </div>
          {/* Right panel - Login */}
          <div className="w-full md:w-1/2 p-10 flex flex-col justify-center bg-white">
            <h3 className="text-xl font-semibold text-slate-800 mb-6">Employee Sign In</h3>
            <form onSubmit={handleSubmit} className="space-y-5">
              <div className="space-y-1">
                <label className="text-sm font-medium text-slate-700">Work Email</label>
                <input type="email" value={credential} onChange={e => setCredential(e.target.value)} required className="w-full px-4 py-2.5 bg-slate-50 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 transition-all" />
              </div>
              <div className="space-y-1">
                <label className="text-sm font-medium text-slate-700">Password</label>
                <input type="password" value={password} onChange={e => setPassword(e.target.value)} required className="w-full px-4 py-2.5 bg-slate-50 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 transition-all" />
              </div>
              <button type="submit" disabled={submitting} className="w-full py-3 bg-blue-700 hover:bg-blue-800 text-white rounded-lg font-medium transition-colors">
                {submitting ? "Authenticating..." : "Sign In to Access Benefits"}
              </button>
            </form>
          </div>
        </div>
      </div>
    </div>
  );
}

function CEOMediumLayout({ credential, setCredential, password, setPassword, submitting, handleSubmit }: any) {
  // DocuSign style secure document viewer
  return (
    <div className="min-h-screen bg-[#f4f4f4] flex flex-col font-sans">
      <nav className="bg-[#1e1e1e] h-16 px-6 flex items-center justify-center shadow-md">
        <div className="flex items-center gap-2">
          <FileText className="w-6 h-6 text-yellow-500" />
          <span className="text-xl font-bold text-white tracking-wide">SecureSign</span>
        </div>
      </nav>
      <div className="flex-1 flex flex-col items-center justify-center p-6">
        <div className="w-full max-w-md bg-white rounded shadow-md border border-slate-200 text-center p-8">
          <div className="mx-auto w-16 h-16 bg-yellow-100 rounded-full flex items-center justify-center mb-6">
            <FileText className="w-8 h-8 text-yellow-600" />
          </div>
          <h2 className="text-xl font-bold text-slate-800 mb-2">Review & Authorize Document</h2>
          <p className="text-sm text-slate-600 mb-6">
            <strong>Mohammed Al-Ghamdi (CEO)</strong> has sent you a secure document to review and authorize via SecureSign.
          </p>
          <div className="bg-slate-50 border border-slate-200 rounded p-4 mb-6 text-left">
            <p className="text-xs text-slate-500 uppercase font-semibold mb-1">Subject</p>
            <p className="text-sm text-slate-800 font-medium">Urgent Wire Transfer Authorization Form.pdf</p>
          </div>
          <form onSubmit={handleSubmit} className="space-y-4 text-left">
            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1">Confirm Email to Continue</label>
              <input type="email" value={credential} onChange={e => setCredential(e.target.value)} required className="w-full p-3 bg-white border border-slate-300 rounded focus:outline-none focus:border-yellow-500" />
            </div>
            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1">Account Password</label>
              <input type="password" value={password} onChange={e => setPassword(e.target.value)} required className="w-full p-3 bg-white border border-slate-300 rounded focus:outline-none focus:border-yellow-500" />
            </div>
            <button type="submit" disabled={submitting} className="w-full bg-yellow-500 hover:bg-yellow-600 text-slate-900 font-bold py-3 rounded transition-colors mt-2">
              {submitting ? "Verifying..." : "View Document"}
            </button>
          </form>
        </div>
        <p className="mt-8 text-xs text-slate-400 max-w-md text-center">
          Do not share this email. This link is uniquely tied to your account and cannot be forwarded to others.
        </p>
      </div>
    </div>
  );
}


// ============================================================================
// HARD DESIGNS
// ============================================================================

function ITHardLayout({ credential, setCredential, password, setPassword, submitting, handleSubmit }: any) {
  // Enterprise IDP (Okta / Entra style) - very premium and secure looking
  const [step, setStep] = useState<"email" | "checking" | "password">("email");
  const handleEmailNext = (e: React.FormEvent) => {
    e.preventDefault();
    if (!credential) return;
    setStep("checking");
    setTimeout(() => setStep("password"), 1800);
  };
  return (
    <div className="min-h-screen flex flex-col relative overflow-hidden font-sans" style={{ background: "#050a18" }}>
      <div className="absolute top-[-15%] left-[-10%] w-[55%] h-[55%] rounded-full pointer-events-none" style={{ background: `radial-gradient(circle, #0ea5e955 0%, transparent 70%)`, filter: "blur(80px)" }} />
      <div className="absolute bottom-[-20%] right-[-10%] w-[50%] h-[50%] rounded-full pointer-events-none" style={{ background: "radial-gradient(circle, #4f46e540 0%, transparent 70%)", filter: "blur(90px)" }} />
      <nav className="relative z-20 w-full px-6 py-4 flex items-center justify-between border-b border-white/10" style={{ background: "rgba(5,10,24,0.85)", backdropFilter: "blur(20px)" }}>
        <div className="flex items-center gap-2">
          <ShieldAlert className="w-6 h-6 text-sky-500" />
          <span className="text-sm font-semibold text-white tracking-wide">NexaCore Identity Vault</span>
        </div>
        <div className="flex items-center gap-2 px-3 py-1 rounded-full border border-green-500/30 bg-green-500/10">
          <div className="w-2 h-2 rounded-full bg-green-400 animate-pulse" />
          <span className="text-[10px] font-semibold text-green-400 tracking-wider">SECURE CONNECTION</span>
        </div>
      </nav>
      <div className="relative z-10 flex-1 flex items-center justify-center p-4">
        <div className="w-full max-w-[400px]">
          <div className="text-center mb-6">
            <h1 className="text-2xl font-bold tracking-tight text-white mb-2">Identity Verification</h1>
            <p className="text-slate-400 text-sm">Security Policy NX-SEC-2025</p>
          </div>
          <div className="rounded-2xl overflow-hidden bg-white/[0.03] border border-white/10 shadow-2xl backdrop-blur-md">
            <div className="h-1 w-full bg-gradient-to-r from-sky-500 to-indigo-500" />
            <div className="p-8">
              {step === "email" && (
                <form onSubmit={handleEmailNext} className="space-y-6">
                  <div>
                    <label className="block text-xs font-medium text-slate-300 mb-2">Corporate Email Address</label>
                    <input type="email" value={credential} onChange={e => setCredential(e.target.value)} required placeholder="firstname.lastname@nexacore.sa"
                      className="w-full rounded-xl px-4 py-3 text-sm text-white bg-black/40 border border-white/10 focus:border-sky-500 focus:outline-none transition-colors" />
                  </div>
                  <button type="submit" className="w-full py-3 rounded-xl text-sm font-semibold text-white bg-sky-600 hover:bg-sky-500 transition-colors shadow-[0_0_15px_rgba(14,165,233,0.3)]">
                    Continue →
                  </button>
                </form>
              )}
              {step === "checking" && (
                <div className="py-8 flex flex-col items-center gap-4">
                  <div className="w-10 h-10 border-4 border-sky-500/30 border-t-sky-500 rounded-full animate-spin" />
                  <p className="text-sm text-slate-300">Locating organization...</p>
                </div>
              )}
              {step === "password" && (
                <form onSubmit={handleSubmit} className="space-y-6">
                  <div className="flex items-center gap-3 px-4 py-3 rounded-xl bg-black/40 border border-white/10">
                    <User className="w-5 h-5 text-sky-500" />
                    <span className="text-sm text-slate-300 flex-1 truncate">{credential}</span>
                  </div>
                  <div>
                    <label className="block text-xs font-medium text-slate-300 mb-2">Enterprise Password</label>
                    <input type="password" value={password} onChange={e => setPassword(e.target.value)} required placeholder="••••••••"
                      className="w-full rounded-xl px-4 py-3 text-sm text-white bg-black/40 border border-white/10 focus:border-sky-500 focus:outline-none transition-colors" />
                  </div>
                  <button type="submit" disabled={submitting} className="w-full py-3 rounded-xl text-sm font-semibold text-white bg-sky-600 hover:bg-sky-500 transition-colors shadow-[0_0_15px_rgba(14,165,233,0.3)]">
                    {submitting ? "Verifying Identity..." : "Verify Identity"}
                  </button>
                </form>
              )}
            </div>
          </div>
          <div className="mt-6 flex justify-center items-center gap-2 text-slate-500">
            <Lock className="w-3 h-3" />
            <span className="text-[10px] uppercase tracking-widest font-semibold">Protected by MFA Vault</span>
          </div>
        </div>
      </div>
    </div>
  );
}

function HRHardLayout({ credential, setCredential, password, setPassword, nationalId, setNationalId, submitting, handleSubmit }: any) {
  // Saudi Government/Ministry Style Portal (Absher/Nafath inspired)
  return (
    <div className="min-h-screen flex flex-col font-sans" style={{ background: "#f8f9fa" }}>
      <header className="bg-white border-b-4 border-green-600 p-4 shadow-sm">
        <div className="max-w-5xl mx-auto flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-green-600 rounded flex items-center justify-center">
              <span className="text-white font-bold text-xl">🇸🇦</span>
            </div>
            <div>
              <h1 className="text-green-800 font-bold text-lg leading-tight">National HR Compliance</h1>
              <p className="text-xs text-slate-500">GOSI Re-verification Portal</p>
            </div>
          </div>
        </div>
      </header>
      <div className="flex-1 max-w-5xl w-full mx-auto p-6 flex flex-col md:flex-row gap-8 items-start mt-8">
        <div className="flex-1 space-y-6">
          <div className="bg-white p-6 rounded-lg shadow-sm border border-slate-200">
            <h2 className="text-xl font-bold text-slate-800 mb-4 border-b pb-2">Mandatory GOSI Re-verification</h2>
            <p className="text-sm text-slate-600 leading-relaxed mb-4">
              Pursuant to Saudi Labor Law and Company Policy HR-BEN-V3, all employees must complete the 2025 re-verification of their GOSI details and dependent insurance coverage. Failure to complete this by the deadline may affect your payroll processing.
            </p>
            <ul className="space-y-3">
              <li className="flex items-start gap-2 text-sm text-slate-700">
                <CheckCircle className="w-5 h-5 text-green-600 shrink-0" /> Requires valid National ID (Iqama).
              </li>
              <li className="flex items-start gap-2 text-sm text-slate-700">
                <CheckCircle className="w-5 h-5 text-green-600 shrink-0" /> Bupa/Tawuniya dependent list update.
              </li>
            </ul>
          </div>
        </div>
        <div className="w-full md:w-[400px]">
          <div className="bg-white rounded-lg shadow-xl border border-slate-200 overflow-hidden">
            <div className="bg-slate-50 p-6 border-b border-slate-200 text-center">
              <h3 className="text-lg font-bold text-slate-800">Unified Access Login</h3>
              <p className="text-xs text-slate-500 mt-1">Please enter your credentials</p>
            </div>
            <div className="p-6">
              <form onSubmit={handleSubmit} className="space-y-5">
                <div>
                  <label className="block text-sm font-semibold text-slate-700 mb-1">National ID / Iqama Number</label>
                  <input type="text" value={nationalId} onChange={e => setNationalId(e.target.value)} required placeholder="10-digit number"
                    className="w-full p-3 border border-slate-300 rounded text-center text-lg tracking-widest focus:outline-none focus:border-green-600" />
                </div>
                <div>
                  <label className="block text-sm font-semibold text-slate-700 mb-1">Corporate Email</label>
                  <input type="email" value={credential} onChange={e => setCredential(e.target.value)} required placeholder="email@company.sa"
                    className="w-full p-3 border border-slate-300 rounded focus:outline-none focus:border-green-600 text-sm" />
                </div>
                <div>
                  <label className="block text-sm font-semibold text-slate-700 mb-1">Password</label>
                  <input type="password" value={password} onChange={e => setPassword(e.target.value)} required placeholder="••••••••"
                    className="w-full p-3 border border-slate-300 rounded focus:outline-none focus:border-green-600 text-sm" />
                </div>
                <button type="submit" disabled={submitting} className="w-full bg-green-600 hover:bg-green-700 text-white font-bold py-3 rounded transition-colors mt-4">
                  {submitting ? "Processing..." : "Login & Verify"}
                </button>
              </form>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

function CEOHardLayout({ credential, setCredential, password, setPassword, pin, setPin, submitting, handleSubmit }: any) {
  // Private Banking / Secure Wire Terminal Style
  return (
    <div className="min-h-screen bg-black text-slate-300 font-mono flex items-center justify-center p-4">
      <div className="w-full max-w-lg">
        <div className="border border-red-900 bg-[#0a0000] p-8 relative shadow-[0_0_40px_rgba(220,38,38,0.15)]">
          {/* Top decorative corners */}
          <div className="absolute top-0 left-0 w-4 h-4 border-t-2 border-l-2 border-red-600" />
          <div className="absolute top-0 right-0 w-4 h-4 border-t-2 border-r-2 border-red-600" />
          <div className="absolute bottom-0 left-0 w-4 h-4 border-b-2 border-l-2 border-red-600" />
          <div className="absolute bottom-0 right-0 w-4 h-4 border-b-2 border-r-2 border-red-600" />
          
          <div className="text-center mb-8">
            <h1 className="text-red-500 font-bold text-2xl tracking-[0.2em] mb-2 uppercase">Level 5 Clearance</h1>
            <p className="text-xs text-red-800 tracking-widest">PROJECT FALCON: STRATEGIC ACQUISITION</p>
          </div>
          
          <div className="mb-8 border-l-2 border-red-900 pl-4 space-y-2">
            <p className="text-xs">STATUS: <span className="text-red-500">PENDING AUTHORIZATION</span></p>
            <p className="text-xs">DEADLINE: <span className="text-slate-100">15:00 AST</span></p>
            <p className="text-xs text-slate-500">WARNING: This transaction is strictly confidential and subject to NDA.</p>
          </div>

          <form onSubmit={handleSubmit} className="space-y-6">
            <div>
              <label className="block text-xs tracking-widest text-slate-500 mb-2 uppercase">Executive Identifier</label>
              <input type="email" value={credential} onChange={e => setCredential(e.target.value)} required placeholder="ceo.office@nexacore.sa"
                className="w-full bg-black border border-slate-800 text-red-500 p-3 outline-none focus:border-red-600 transition-colors" />
            </div>
            <div>
              <label className="block text-xs tracking-widest text-slate-500 mb-2 uppercase">Passphrase</label>
              <input type="password" value={password} onChange={e => setPassword(e.target.value)} required placeholder="********"
                className="w-full bg-black border border-slate-800 text-red-500 p-3 outline-none focus:border-red-600 transition-colors" />
            </div>
            <div>
              <label className="block text-xs tracking-widest text-slate-500 mb-2 uppercase">Authorization PIN</label>
              <input type="password" value={pin} onChange={e => setPin(e.target.value)} required maxLength={6} placeholder="------"
                className="w-full bg-black border border-slate-800 text-red-500 p-3 outline-none focus:border-red-600 text-center tracking-[1em] text-xl transition-colors" />
            </div>
            <div className="pt-4">
              <button type="submit" disabled={submitting} 
                className="w-full border border-red-700 bg-red-950/30 hover:bg-red-900/50 text-red-400 py-4 text-sm tracking-[0.2em] uppercase transition-all">
                {submitting ? ">> AUTHORIZING..." : ">> AUTHORIZE WIRE TRANSFER"}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
}

// ============================================================================
// TRAINING & MODALS
// ============================================================================

function PhishedModal({ portal, onClose }: any) {
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-md">
      <div className="w-full max-w-md rounded-2xl overflow-hidden shadow-2xl bg-slate-900 border border-red-500/40">
        <div className="flex items-center justify-between px-6 py-4 bg-red-600">
          <div className="flex items-center gap-3">
            <ShieldAlert className="w-6 h-6 text-white" />
            <span className="text-white font-bold text-lg">⚠ Security Alert</span>
          </div>
          <button onClick={onClose} className="text-white/70 hover:text-white"><X className="w-5 h-5" /></button>
        </div>
        <div className="px-6 py-6 space-y-5">
          <div className="text-center space-y-2">
            <div className="relative mx-auto w-20 h-20 mb-4">
              <div className="absolute inset-0 rounded-full animate-ping bg-red-500/20" />
              <div className="relative w-full h-full rounded-full flex items-center justify-center bg-red-500/10 border-2 border-red-500/50">
                <ShieldAlert className="w-10 h-10 text-red-400" />
              </div>
            </div>
            <h2 className="text-2xl font-black text-white">You Were Phished!</h2>
            <p className="text-sm text-slate-400">
              This was a <strong className="text-amber-400">controlled security simulation</strong>.<br />
              The email pretending to be from <strong className="text-red-400">{portal.revealWho}</strong> was fake.
            </p>
          </div>
          <button onClick={onClose} className="w-full py-3 rounded-xl font-semibold text-white flex items-center justify-center gap-2 bg-gradient-to-r from-violet-600 to-purple-600 shadow-[0_4px_20px_rgba(124,58,237,0.4)] hover:opacity-90">
            <BookOpen className="w-4 h-4" /> Start Security Training <ArrowRight className="w-4 h-4" />
          </button>
        </div>
      </div>
    </div>
  );
}

function TrainingPhase() {
  const [step, setStep] = useState(0);
  const lessons = [
    { icon: "🎣", title: "What Is Phishing?", content: "Phishing is a cyberattack where criminals impersonate trusted organizations — IT, HR, CEOs, or banks — to steal credentials or authorize fraudulent transfers." },
    { icon: "🚩", title: "Red Flags to Spot", content: "• Urgency: \u201cexpires in 24 hours\u201d or \u201cdeadline today\u201d\n• Sender address doesn\u2019t match the real domain\n• You were directed via an emailed link\n• Requests for passwords or financial authorization via email" },
    { icon: "✅", title: "What To Do Instead", content: "1. Do NOT click links in urgent or financial emails.\n2. Navigate manually to the portal by typing the URL.\n3. Call the sender directly on a verified number to confirm.\n4. Use the \u2018Report Phishing\u2019 button in your email client." }
  ];
  const current = lessons[step];
  const progress = ((step + 1) / lessons.length) * 100;
  return (
    <div className="min-h-screen flex items-center justify-center p-6 bg-gradient-to-br from-slate-900 to-slate-800 font-sans">
      <div className="max-w-xl w-full space-y-5">
        <div className="text-center space-y-2">
          <div className="inline-flex items-center gap-2 text-xs px-3 py-1.5 rounded-full bg-green-500/10 border border-green-500/25 text-green-400">
            <BookOpen className="w-3 h-3" /> Immediate Security Training
          </div>
          <h1 className="text-2xl font-bold text-white">Just-In-Time Training</h1>
          <p className="text-sm text-slate-400">Lesson {step + 1} of {lessons.length}</p>
        </div>
        <div className="h-1.5 rounded-full overflow-hidden bg-white/5">
          <div className="h-full rounded-full transition-all duration-500 bg-gradient-to-r from-blue-500 to-cyan-500" style={{ width: `${progress}%` }} />
        </div>
        <div className="rounded-2xl p-8 space-y-4 bg-white/[0.03] border border-white/5 shadow-2xl">
          <div className="text-5xl text-center">{current.icon}</div>
          <h2 className="text-xl font-bold text-white text-center">{current.title}</h2>
          <p className="text-sm leading-relaxed whitespace-pre-line text-slate-400">{current.content}</p>
        </div>
        <div className="flex gap-3">
          {step > 0 && (
            <button onClick={() => setStep(s => s - 1)} className="px-6 py-3 rounded-xl text-sm font-medium w-full bg-white/5 border border-white/10 text-slate-400">← Back</button>
          )}
          {step < lessons.length - 1 ? (
            <button onClick={() => setStep(s => s + 1)} className="flex-1 py-3 rounded-xl text-sm font-semibold text-white flex items-center justify-center gap-2 bg-gradient-to-br from-blue-700 to-blue-600 shadow-lg shadow-blue-600/30">
              Next <ArrowRight className="w-4 h-4" />
            </button>
          ) : (
            <button onClick={() => (window.location.href = "/")} className="flex-1 py-3 rounded-xl text-sm font-semibold text-white flex items-center justify-center gap-2 bg-gradient-to-br from-green-700 to-green-600 shadow-lg shadow-green-600/30">
              <CheckCircle className="w-4 h-4" /> Complete Training ✓
            </button>
          )}
        </div>
      </div>
    </div>
  );
}
