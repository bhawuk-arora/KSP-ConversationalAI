// frontend/src/components/Sidebar.tsx
"use client";

import { useState } from "react";
import {
  Shield,
  LayoutDashboard,
  MessageSquareCode,
  Network,
  Map,
  Settings2,
  ChevronLeft,
  ChevronRight,
  LogOut,
  UserRound,
  ChevronDown,
} from "lucide-react";

interface SidebarProps {
  currentTab: string;
  setCurrentTab: (tab: string) => void;
  user: { email: string; role: string; station_id: number } | null;
  onLogout: () => void;
}

// Define all nav items with minimum role required
const ALL_NAV = [
  { id: "dashboard", label: "Dashboard",       icon: LayoutDashboard, roles: ["Constable", "Investigator", "Analyst", "Supervisor"] },
  { id: "copilot",   label: "AI Copilot",      icon: MessageSquareCode, roles: ["Constable", "Investigator", "Analyst", "Supervisor"] },
  { id: "network",   label: "Network Graph",   icon: Network,           roles: ["Investigator", "Analyst", "Supervisor"] },
  { id: "map",       label: "Hotspot Map",     icon: Map,               roles: ["Investigator", "Analyst", "Supervisor"] },
  { id: "simulation",label: "Scenario Sim",    icon: Settings2,         roles: ["Supervisor"] },
];

const ROLE_BADGE: Record<string, string> = {
  Constable:   "bg-slate-500/20 text-slate-400 border-slate-500/30",
  Investigator:"bg-blue-500/20 text-blue-400 border-blue-500/30",
  Analyst:     "bg-purple-500/20 text-purple-400 border-purple-500/30",
  Supervisor:  "bg-amber-500/20 text-amber-400 border-amber-500/30",
};

export default function Sidebar({ currentTab, setCurrentTab, user, onLogout }: SidebarProps) {
  const [isCollapsed, setIsCollapsed] = useState(false);
  const [profileOpen, setProfileOpen] = useState(false);

  const role = user?.role ?? "Constable";
  const filteredNav = ALL_NAV.filter(item => item.roles.includes(role));

  const badgeClass = ROLE_BADGE[role] ?? "bg-gray-500/20 text-gray-400 border-gray-500/30";
  const kgid = user?.email?.split("@")[0]?.toUpperCase() ?? "UNKNOWN";

  return (
    <aside
      className={`flex flex-col justify-between transition-all duration-300 ease-in-out border-r border-police-border/40 bg-police-bg/80 backdrop-blur-md ${
        isCollapsed ? "w-16" : "w-64"
      } h-screen sticky top-0`}
    >
      {/* ── Top: Logo + Nav ── */}
      <div>
        {/* Logo bar */}
        <div className="h-16 flex items-center justify-between px-3 border-b border-police-border/40">
          <div className="flex items-center gap-2.5 overflow-hidden">
            <div className="shrink-0 bg-blue-600/20 p-2 rounded-lg border border-blue-500/30 text-blue-400">
              <Shield className="h-4 w-4" />
            </div>
            {!isCollapsed && (
              <span className="font-bold text-sm tracking-widest bg-gradient-to-r from-blue-400 to-indigo-300 bg-clip-text text-transparent select-none">
                KSP INTEL
              </span>
            )}
          </div>
          <button
            onClick={() => setIsCollapsed(!isCollapsed)}
            className="p-1.5 rounded-lg text-gray-500 hover:text-blue-400 hover:bg-blue-500/10 transition-all cursor-pointer"
            title={isCollapsed ? "Expand sidebar" : "Collapse sidebar"}
          >
            {isCollapsed ? <ChevronRight size={14} /> : <ChevronLeft size={14} />}
          </button>
        </div>

        {/* Role badge — only when expanded */}
        {!isCollapsed && (
          <div className="px-3 pt-3 pb-1">
            <span className={`inline-flex items-center text-[9px] font-bold tracking-widest uppercase px-2 py-1 rounded border ${badgeClass}`}>
              {role}
            </span>
          </div>
        )}

        {/* Navigation */}
        <nav className="p-2 space-y-0.5 mt-1">
          {filteredNav.map(item => {
            const Icon = item.icon;
            const isActive = currentTab === item.id;
            return (
              <button
                key={item.id}
                onClick={() => setCurrentTab(item.id)}
                title={isCollapsed ? item.label : undefined}
                className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-medium transition-all duration-150 cursor-pointer group ${
                  isActive
                    ? "bg-blue-600/20 text-blue-400 border border-blue-500/30 shadow-sm"
                    : "text-gray-500 hover:text-gray-200 hover:bg-white/5 border border-transparent"
                } ${isCollapsed ? "justify-center" : ""}`}
              >
                <Icon size={17} className={`shrink-0 transition-transform ${isActive ? "" : "group-hover:scale-110"}`} />
                {!isCollapsed && <span>{item.label}</span>}
              </button>
            );
          })}
        </nav>
      </div>

      {/* ── Bottom: User Profile + Logout ── */}
      <div className="border-t border-police-border/40 p-2 space-y-1">
        {/* Profile card */}
        {!isCollapsed ? (
          <button
            onClick={() => setProfileOpen(!profileOpen)}
            className="w-full flex items-center gap-2.5 p-2.5 rounded-xl hover:bg-white/5 border border-transparent hover:border-police-border/30 transition-all cursor-pointer text-left"
          >
            <div className="shrink-0 bg-gray-700/60 p-2 rounded-lg border border-gray-600/40 text-gray-300">
              <UserRound className="h-3.5 w-3.5" />
            </div>
            <div className="min-w-0 flex-1">
              <p className="text-xs font-semibold text-gray-200 truncate">{user?.email ?? "Officer"}</p>
              <p className="text-[10px] text-gray-500 truncate">KGID: {kgid} · Stn {user?.station_id ?? "—"}</p>
            </div>
            <ChevronDown size={12} className={`text-gray-500 transition-transform ${profileOpen ? "rotate-180" : ""}`} />
          </button>
        ) : (
          <div className="flex justify-center py-1">
            <div className="bg-gray-700/60 p-2 rounded-lg border border-gray-600/40 text-gray-300">
              <UserRound className="h-3.5 w-3.5" />
            </div>
          </div>
        )}

        {/* Logout — always visible */}
        <button
          onClick={onLogout}
          title="Sign out"
          className={`w-full flex items-center gap-2.5 px-3 py-2 rounded-xl text-gray-500 hover:text-red-400 hover:bg-red-500/10 border border-transparent hover:border-red-500/20 transition-all cursor-pointer text-sm font-medium ${
            isCollapsed ? "justify-center" : ""
          }`}
        >
          <LogOut size={15} className="shrink-0" />
          {!isCollapsed && <span>Sign out</span>}
        </button>
      </div>
    </aside>
  );
}
