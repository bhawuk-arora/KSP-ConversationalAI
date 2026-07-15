// frontend/src/app/page.tsx
"use client";

import { useState, useEffect } from "react";
import Sidebar from "@/components/Sidebar";
import Header from "@/components/Header";
import ScenarioSimulator from "@/components/ScenarioSimulator";
import CommandPalette from "@/components/CommandPalette";
import ChatContainer from "@/components/ChatContainer";
import NetworkGraph from "@/components/NetworkGraph";
import GisMap from "@/components/GisMap";

import { 
  TrendingUp, 
  ShieldAlert, 
  Users, 
  Clock, 
  MapPin, 
  Calendar, 
  UserPlus, 
  CheckCircle,
  Activity,
  AlertTriangle,
  MessageSquare
} from "lucide-react";

export default function Home() {
  const [token, setToken] = useState<string | null>(null);
  const [user, setUser] = useState<{ email: string, role: string, station_id: number } | null>(null);
  const [emailInput, setEmailInput] = useState("");
  const [passwordInput, setPasswordInput] = useState("");
  const [errorMsg, setErrorMsg] = useState("");
  const [isMounted, setIsMounted] = useState(false);

  const [currentTab, setCurrentTab] = useState("dashboard");
  const [demoMode, setDemoMode] = useState(true);
  const [searchOpen, setSearchOpen] = useState(false);

  // Authenticate token status on mount
  useEffect(() => {
    setIsMounted(true);
    const storedToken = localStorage.getItem("token");
    if (storedToken) {
      setToken(storedToken);
      try {
        const payload = JSON.parse(window.atob(storedToken.split(".")[1]));
        setUser({
          email: payload.sub,
          role: payload.role,
          station_id: payload.station_id
        });
      } catch (e) {
        localStorage.removeItem("token");
      }
    }
  }, []);

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setErrorMsg("");
    try {
      const formData = new URLSearchParams();
      formData.append("username", emailInput);
      formData.append("password", passwordInput);
      
      const res = await fetch("http://localhost:8000/api/v1/auth/token", {
        method: "POST",
        headers: { "Content-Type": "application/x-www-form-urlencoded" },
        body: formData
      });
      
      if (res.ok) {
        const data = await res.json();
        localStorage.setItem("token", data.access_token);
        setToken(data.access_token);
        
        const payload = JSON.parse(window.atob(data.access_token.split(".")[1]));
        setUser({
          email: payload.sub,
          role: payload.role,
          station_id: payload.station_id
        });
      } else {
        setErrorMsg("Authentication failed. Check your KSP email/password.");
      }
    } catch (err) {
      setErrorMsg("Cannot connect to KSP backend API. Make sure it is running.");
    }
  };

  const handleLogout = () => {
    localStorage.removeItem("token");
    setToken(null);
    setUser(null);
    setEmailInput("");
    setPasswordInput("");
  };

  // Sample analytics data reflecting real KSP contexts
  const kpis = [
    { label: "Total Cases (Q2 2026)", value: "2,042", change: "+5.4%", isAlert: false, icon: TrendingUp },
    { label: "Heinous Offences", value: "142", change: "+12% spike", isAlert: true, icon: ShieldAlert },
    { label: "Repeat Suspects", value: "394", change: "42 active networks", isAlert: false, icon: Users },
    { label: "Pending Case Files", value: "842", change: "82% in-progress", isAlert: false, icon: Clock }
  ];

  const emergingSpikes = [
    { district: "Bengaluru Urban", station: "Kalasipalya", crime: "House Breaking By Night", index: "+24%", details: "Burglary MO matches lock cutting signature." },
    { district: "Mysuru", station: "Devaraja", crime: "Attempt to Murder", index: "+18%", details: "Increase in street gang skirmishes." },
    { district: "Mangaluru", station: "Kadri", crime: "Cyber Fraud", index: "+32%", details: "OTP Phishing loops target senior citizens." }
  ];

  const suspectRiskProfiles = [
    { name: demoMode ? "<SUSPECT_A_MASKED>" : "Ravi alias Kariya", age: 31, risk: 84, primaryMO: "Lock Cutting/Burglary", status: "Arrested" },
    { name: demoMode ? "<SUSPECT_B_MASKED>" : "Ganesh alias Gani", age: 26, risk: 76, primaryMO: "Body Offences/Daggers", status: "Bailed" },
    { name: demoMode ? "<SUSPECT_C_MASKED>" : "Imran Khan", age: 24, risk: 72, primaryMO: "NDPS/Drug Peddling", status: "Arrested" }
  ];

  const recentCases = [
    { caseId: "FIR:100120257202500001", date: "2025-05-20", crimeHead: "Body Offences", status: "Chargesheeted" },
    { caseId: "FIR:100020027202600001", date: "2026-06-01", crimeHead: "Property Offences", status: "Under Investigation" },
    { caseId: "FIR:300040077202600001", date: "2026-06-10", crimeHead: "Property Offences", status: "Under Investigation" }
  ];

  // Render glassmorphism Login card if not authenticated
  if (isMounted && !token) {
    return (
      <div className="flex h-screen w-screen items-center justify-center bg-police-bg overflow-hidden relative">
        <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-blue-500/10 rounded-full blur-3xl" />
        <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-emerald-500/5 rounded-full blur-3xl" />

        <div className="glass-panel w-full max-w-md p-8 rounded-3xl space-y-6 z-10 border border-police-border/40 shadow-2xl">
          <div className="text-center space-y-2">
            <h1 className="text-2xl font-bold font-display text-gray-100 tracking-wide">Karnataka State Police</h1>
            <p className="text-xs text-gray-500 uppercase tracking-widest">Crime Intelligence Hub</p>
          </div>

          <form onSubmit={handleLogin} className="space-y-4">
            <div className="space-y-1">
              <label className="text-[10px] uppercase font-bold tracking-wider text-gray-400">Clearance Email</label>
              <input
                type="email"
                value={emailInput}
                onChange={(e) => setEmailInput(e.target.value)}
                placeholder="io@ksp.gov.in"
                required
                className="w-full bg-white/5 border border-police-border/60 rounded-xl px-4 py-2.5 text-xs text-gray-200 focus:outline-none focus:border-blue-500 transition-all"
              />
            </div>

            <div className="space-y-1">
              <label className="text-[10px] uppercase font-bold tracking-wider text-gray-400">Security Password</label>
              <input
                type="password"
                value={passwordInput}
                onChange={(e) => setPasswordInput(e.target.value)}
                placeholder="••••••••"
                required
                className="w-full bg-white/5 border border-police-border/60 rounded-xl px-4 py-2.5 text-xs text-gray-200 focus:outline-none focus:border-blue-500 transition-all"
              />
            </div>

            {errorMsg && (
              <p className="text-[10px] text-red-500 font-semibold">{errorMsg}</p>
            )}

            <button
              type="submit"
              className="w-full bg-blue-600 hover:bg-blue-700 text-white font-semibold py-2.5 rounded-xl text-xs tracking-wider uppercase transition-all shadow-lg hover:shadow-blue-500/20 cursor-pointer"
            >
              Sign In Clearances
            </button>
          </form>

          <div className="border-t border-police-border/30 pt-4 text-center">
            <span className="text-[9px] text-gray-500 uppercase tracking-wide">Official SCRB Access Only</span>
          </div>
        </div>
      </div>
    );
  }

  // Render fully populated dashboard if authenticated
  return (
    <div className="flex h-screen w-screen overflow-hidden bg-police-bg">
      {/* Collapsible Left Sidebar */}
      <Sidebar currentTab={currentTab} setCurrentTab={setCurrentTab} user={user} onLogout={handleLogout} />

      {/* Main content viewport */}
      <div className="flex-1 flex flex-col min-w-0">
        <Header 
          demoMode={demoMode} 
          setDemoMode={setDemoMode} 
          onSearchClick={() => setSearchOpen(true)} 
          user={user}
          onLogout={handleLogout}
        />

        <main className="flex-1 overflow-y-auto p-6 space-y-6">
          
          {/* TAB 1: Core Dashboard View */}
          {currentTab === "dashboard" && (
            <>
              {/* Header Titles */}
              <div className="space-y-1">
                <h1 className="text-2xl font-bold font-display text-gray-100">State Crime Intelligence Hub</h1>
                <p className="text-xs text-gray-500">Karnataka State Crime Records Bureau (SCRB) | Analytical Overview</p>
              </div>

              {/* KPI Cards Grid */}
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
                {kpis.map((kpi, idx) => {
                  const Icon = kpi.icon;
                  return (
                    <div key={idx} className="glass-panel glass-panel-hover p-4 rounded-2xl flex items-center justify-between">
                      <div className="space-y-1">
                        <span className="text-[10px] text-gray-500 font-medium">{kpi.label}</span>
                        <p className="text-xl font-bold font-display text-gray-100">{kpi.value}</p>
                        <span className={`text-[10px] font-semibold flex items-center gap-1 ${
                          kpi.isAlert ? "text-red-500" : "text-emerald-500"
                        }`}>
                          {kpi.change}
                        </span>
                      </div>
                      <div className={`p-3 rounded-xl border ${
                        kpi.isAlert 
                          ? "bg-red-500/10 border-red-500/20 text-red-500" 
                          : "bg-blue-500/10 border-blue-500/20 text-blue-500"
                      }`}>
                        <Icon size={20} />
                      </div>
                    </div>
                  );
                })}
              </div>

              {/* Dashboard Content Grid */}
              <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                
                {/* Column 1: Emerging Spikes (Pulse alerts) */}
                <div className="glass-panel p-5 rounded-2xl space-y-4">
                  <div className="flex items-center gap-2 border-b border-police-border/40 pb-3">
                    <Activity className="text-blue-500" size={16} />
                    <h3 className="text-xs font-bold font-display uppercase tracking-wider text-gray-200">Emerging Regional Spikes</h3>
                  </div>

                  <div className="space-y-3">
                    {emergingSpikes.map((spike, idx) => (
                      <div key={idx} className="p-3 bg-white/[0.02] border border-police-border/40 rounded-xl flex items-start gap-3">
                        <div className="bg-red-500/10 border border-red-500/30 p-2 rounded-lg text-red-500 shrink-0 mt-0.5 animate-pulse">
                          <AlertTriangle size={14} />
                        </div>
                        <div className="min-w-0 space-y-1">
                          <div className="flex items-center justify-between">
                            <span className="text-[10px] font-bold text-gray-300">{spike.district} - {spike.station}</span>
                            <span className="text-[9px] font-bold text-red-500 bg-red-500/10 px-1.5 py-0.5 rounded">{spike.index}</span>
                          </div>
                          <p className="text-xs font-semibold text-gray-200">{spike.crime}</p>
                          <p className="text-[10px] text-gray-500">{spike.details}</p>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Column 2: Recent Cases and Statuses */}
                <div className="glass-panel p-5 rounded-2xl space-y-4">
                  <div className="flex items-center gap-2 border-b border-police-border/40 pb-3">
                    <CheckCircle className="text-blue-500" size={16} />
                    <h3 className="text-xs font-bold font-display uppercase tracking-wider text-gray-200">Recent Investigations</h3>
                  </div>

                  <div className="space-y-3">
                    {recentCases.map((c, idx) => (
                      <div key={idx} className="p-3 bg-white/[0.02] border border-police-border/40 rounded-xl flex items-center justify-between">
                        <div className="space-y-1 min-w-0">
                          <p className="text-xs font-semibold text-gray-200 truncate">{c.caseId}</p>
                          <div className="flex items-center gap-2 text-[9px] text-gray-500">
                            <span className="flex items-center gap-0.5"><Calendar size={10} /> {c.date}</span>
                            <span>•</span>
                            <span>{c.crimeHead}</span>
                          </div>
                        </div>
                        <span className={`text-[9px] font-bold px-2 py-0.5 rounded-full border ${
                          c.status === "Chargesheeted" 
                            ? "bg-emerald-500/10 border-emerald-500/20 text-emerald-400" 
                            : "bg-blue-500/10 border-blue-500/20 text-blue-400"
                        }`}>
                          {c.status}
                        </span>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Column 3: Habitual Offender Profiling (Risk list) */}
                <div className="glass-panel p-5 rounded-2xl space-y-4">
                  <div className="flex items-center gap-2 border-b border-police-border/40 pb-3">
                    <UserPlus className="text-blue-500" size={16} />
                    <h3 className="text-xs font-bold font-display uppercase tracking-wider text-gray-200">Habitual Offender Risk</h3>
                  </div>

                  <div className="space-y-3">
                    {suspectRiskProfiles.map((p, idx) => (
                      <div key={idx} className="p-3 bg-white/[0.02] border border-police-border/40 rounded-xl flex items-center justify-between">
                        <div className="space-y-1">
                          <p className="text-xs font-bold text-gray-200">{p.name}</p>
                          <p className="text-[10px] text-gray-500">MO: {p.primaryMO}</p>
                        </div>
                        <div className="flex items-center gap-3">
                          <div className="text-right">
                            <span className="text-[9px] text-gray-500 block">Risk Index</span>
                            <span className={`text-xs font-bold font-display ${
                              p.risk > 80 ? "text-red-500" : "text-amber-500"
                            }`}>{p.risk}%</span>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

              </div>
            </>
          )}

          {/* TAB 2: AI Copilot Assistant Placeholder (Or trigger drawer) */}
          {currentTab === "copilot" && (
            <div className="h-full flex flex-col items-center justify-center py-20 space-y-4">
              <div className="bg-blue-600/10 border border-blue-500/20 p-6 rounded-2xl text-blue-500">
                <MessageSquare size={48} />
              </div>
              <h2 className="text-lg font-bold font-display text-gray-200">Conversational AI Assistant</h2>
              <p className="text-xs text-gray-500 text-center max-w-md leading-relaxed">
                Click the floating blue button on the bottom right of the screen at any time to open the Conversational Copilot and interact with the database.
              </p>
            </div>
          )}

          {/* TAB 3: Suspect Relationship Network */}
          {currentTab === "network" && (
            <NetworkGraph />
          )}

          {/* TAB 4: GIS Hotspot Map */}
          {currentTab === "map" && (
            <GisMap />
          )}

          {/* TAB 5: Scenario Simulation */}
          {currentTab === "simulation" && (
            <ScenarioSimulator />
          )}

        </main>
      </div>

      {/* Floating Conversational AI drawer */}
      <ChatContainer demoMode={demoMode} />

      {/* Command Palette (Ctrl+K Modal) */}
      <CommandPalette 
        isOpen={searchOpen} 
        setIsOpen={setSearchOpen} 
        setTab={setCurrentTab} 
      />
    </div>
  );
}
