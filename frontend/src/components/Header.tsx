// frontend/src/components/Header.tsx
"use client";

import { Search, Bell, ShieldCheck, Database, GitBranch, ShieldAlert, LogOut, Download } from "lucide-react";

interface HeaderProps {
  demoMode: boolean;
  setDemoMode: (val: boolean) => void;
  onSearchClick: () => void;
  user: { email: string, role: string, station_id: number } | null;
  onLogout: () => void;
}

export default function Header({ demoMode, setDemoMode, onSearchClick, user, onLogout }: HeaderProps) {
  return (
    <header className="h-16 border-b border-police-border/40 px-6 flex items-center justify-between sticky top-0 bg-police-bg/85 backdrop-blur-md z-30">
      {/* Left: Interactive Search Bar & Command Hint */}
      <div className="flex items-center gap-4 w-96">
        <button 
          onClick={onSearchClick}
          className="w-full flex items-center justify-between text-left px-4 py-2 bg-white/5 border border-police-border/50 rounded-xl text-gray-500 hover:text-gray-300 hover:bg-white/10 transition-all cursor-pointer"
        >
          <div className="flex items-center gap-3">
            <Search size={16} />
            <span className="text-xs">Quick search cases or suspects...</span>
          </div>
          <span className="text-[10px] font-mono bg-white/10 px-1.5 py-0.5 rounded border border-white/5">Ctrl + K</span>
        </button>
      </div>

      {/* Right: Engine health, Demo Toggle, Notifications, User Badge */}
      <div className="flex items-center gap-6">
        
        {/* System Health Indicators */}
        <div className="flex items-center gap-4 text-xs text-gray-400">
          <div className="flex items-center gap-1.5" title="PostgreSQL status">
            <Database size={14} className="text-emerald-500" />
            <span className="hidden md:inline">PostGIS</span>
          </div>
          <div className="flex items-center gap-1.5" title="Neo4j status">
            <GitBranch size={14} className="text-emerald-500" />
            <span className="hidden md:inline">Neo4j</span>
          </div>
        </div>

        <div className="h-4 w-px bg-police-border/40 hidden md:block"></div>

        {/* Citizen-Safe Demo Mode Toggle */}
        <div className="flex items-center gap-3 bg-white/5 px-3 py-1.5 rounded-xl border border-police-border/40">
          <div className="flex items-center gap-2">
            {demoMode ? (
              <ShieldAlert size={14} className="text-amber-500 animate-pulse" />
            ) : (
              <ShieldCheck size={14} className="text-blue-500" />
            )}
            <span className="text-xs font-semibold text-gray-300 hidden sm:inline">Demo Masking</span>
          </div>
          
          <button
            onClick={() => setDemoMode(!demoMode)}
            className={`relative inline-flex h-5 w-9 shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-200 ease-in-out ${
              demoMode ? "bg-amber-600" : "bg-gray-700"
            }`}
          >
            <span
              className={`pointer-events-none inline-block h-4 w-4 transform rounded-full bg-white shadow ring-0 transition duration-200 ease-in-out ${
                demoMode ? "translate-x-4" : "translate-x-0"
              }`}
            />
          </button>
        </div>

        {/* Notifications Trigger */}
        <button className="relative hover:bg-white/5 p-2 rounded-xl border border-transparent hover:border-police-border/30 text-gray-400 hover:text-gray-200 transition-all cursor-pointer">
          <Bell size={18} />
          <span className="absolute top-1 right-1 w-2 h-2 bg-blue-500 rounded-full"></span>
        </button>

        {/* Officer Clearance Badge */}
        <div className="flex items-center gap-3">
          <div className="flex flex-col items-end text-[10px] hidden lg:flex">
            <span className="font-bold text-gray-300">{user?.email || "io@ksp.gov.in"}</span>
            <span className="text-gray-500 text-[9px]">Station ID: {user?.station_id || 1002}</span>
          </div>
          <span className="text-[10px] font-bold tracking-wider uppercase bg-blue-500/20 text-blue-400 px-2 py-1 rounded-md border border-blue-500/30">
            {user?.role || "Investigator"}
          </span>
        </div>

          {/* PDF Report Download */}
          <button
            onClick={async () => {
              try {
                const res = await fetch('http://localhost:8000/api/v1/reports/pdf', {
                  method: 'POST',
                  headers: { 'Content-Type': 'application/json' },
                  body: JSON.stringify({ include_kpis: true, include_recent_cases: true, include_risk_profiles: true }),
                });
                if (!res.ok) throw new Error('Failed to generate report');
                const blob = await res.blob();
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = 'KSP_Report.pdf';
                a.click();
                window.URL.revokeObjectURL(url);
              } catch (e) {
                console.error(e);
                alert('Error downloading report');
              }
            }}
            className="hover:bg-green-500/10 p-2 rounded-xl border border-transparent hover:border-green-500/20 text-gray-400 hover:text-green-400 transition-all cursor-pointer"
            title="Download PDF report"
          >
            <Download size={16} />
          </button>
        {/* Logout Button */}
        <button 
          onClick={onLogout}
          className="hover:bg-red-500/10 p-2 rounded-xl border border-transparent hover:border-red-500/20 text-gray-400 hover:text-red-400 transition-all cursor-pointer"
          title="Sign out of system"
        >
          <LogOut size={16} />
        </button>
      </div>
    </header>
  );
}
