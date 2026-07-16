// frontend/src/components/Header.tsx
"use client";

import { Search, Bell, ShieldCheck, Database, GitBranch, ShieldAlert, Download } from "lucide-react";

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

interface HeaderProps {
  demoMode: boolean;
  setDemoMode: (val: boolean) => void;
  onSearchClick: () => void;
  user: { email: string; role: string; station_id: number } | null;
  onLogout: () => void;
}

export default function Header({ demoMode, setDemoMode, onSearchClick, user }: HeaderProps) {
  const handleDownloadPDF = async () => {
    try {
      const token = localStorage.getItem("token");
      const res = await fetch(`${API_URL}/api/v1/reports/pdf`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          ...(token ? { Authorization: `Bearer ${token}` } : {}),
        },
        body: JSON.stringify({ include_kpis: true, include_recent_cases: true, include_risk_profiles: true }),
      });
      if (!res.ok) {
        const msg = await res.text();
        alert(`Report error: ${msg}`);
        return;
      }
      const blob = await res.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `KSP_Intel_Report_${new Date().toISOString().slice(0, 10)}.pdf`;
      a.click();
      window.URL.revokeObjectURL(url);
    } catch {
      alert("Could not connect to report service.");
    }
  };

  const canDownloadReport = ["Investigator", "Analyst", "Supervisor"].includes(user?.role ?? "");

  return (
    <header className="h-16 border-b border-police-border/40 px-5 flex items-center justify-between sticky top-0 bg-police-bg/90 backdrop-blur-md z-30">

      {/* Left: Search */}
      <button
        onClick={onSearchClick}
        className="flex items-center gap-3 w-80 text-left px-4 py-2 bg-white/5 border border-police-border/50 rounded-xl text-gray-500 hover:text-gray-300 hover:bg-white/10 transition-all cursor-pointer"
      >
        <Search size={14} />
        <span className="text-xs flex-1">Search cases, suspects, FIRs…</span>
        <span className="text-[10px] font-mono bg-white/10 px-1.5 py-0.5 rounded border border-white/10 shrink-0">⌘K</span>
      </button>

      {/* Right: Indicators + Controls */}
      <div className="flex items-center gap-4">

        {/* DB health indicators */}
        <div className="hidden md:flex items-center gap-3 text-[11px] text-gray-500">
          <span className="flex items-center gap-1.5" title="PostgreSQL">
            <Database size={13} className="text-emerald-500" />
            <span>PostGIS</span>
          </span>
          <span className="flex items-center gap-1.5" title="Neo4j">
            <GitBranch size={13} className="text-emerald-500" />
            <span>Neo4j</span>
          </span>
        </div>

        <div className="h-4 w-px bg-police-border/40 hidden md:block" />

        {/* Demo Mode toggle */}
        <div className="flex items-center gap-2 bg-white/5 px-3 py-1.5 rounded-xl border border-police-border/40">
          {demoMode
            ? <ShieldAlert size={13} className="text-amber-400 animate-pulse" />
            : <ShieldCheck size={13} className="text-blue-400" />
          }
          <span className="text-[11px] font-semibold text-gray-400 hidden sm:inline">
            {demoMode ? "Demo Masking ON" : "Full Data Mode"}
          </span>
          <button
            onClick={() => setDemoMode(!demoMode)}
            className={`relative inline-flex h-4 w-8 shrink-0 rounded-full border-2 border-transparent transition-colors ${
              demoMode ? "bg-amber-600" : "bg-gray-700"
            } cursor-pointer`}
          >
            <span className={`inline-block h-3 w-3 rounded-full bg-white shadow transition-transform ${
              demoMode ? "translate-x-4" : "translate-x-0"
            }`} />
          </button>
        </div>

        {/* Notification bell */}
        <button className="relative p-2 rounded-xl hover:bg-white/5 text-gray-500 hover:text-gray-200 border border-transparent hover:border-police-border/30 transition-all cursor-pointer">
          <Bell size={16} />
          <span className="absolute top-1.5 right-1.5 w-1.5 h-1.5 bg-blue-500 rounded-full" />
        </button>

        {/* User badge */}
        <div className="hidden lg:flex flex-col items-end text-right">
          <span className="text-[11px] font-semibold text-gray-300 leading-tight">{user?.email ?? "officer@ksp.gov.in"}</span>
          <span className="text-[9px] text-gray-500">Stn {user?.station_id ?? "—"} · {user?.role ?? "Officer"}</span>
        </div>

        {/* PDF download — role-gated */}
        {canDownloadReport && (
          <button
            onClick={handleDownloadPDF}
            title="Download PDF Intelligence Report"
            className="p-2 rounded-xl hover:bg-green-500/10 text-gray-500 hover:text-green-400 border border-transparent hover:border-green-500/20 transition-all cursor-pointer"
          >
            <Download size={16} />
          </button>
        )}
      </div>
    </header>
  );
}
