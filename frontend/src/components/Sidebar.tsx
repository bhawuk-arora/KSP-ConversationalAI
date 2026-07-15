// frontend/src/components/Sidebar.tsx
"use client";

import { useState } from "react";
import { 
  Shield, 
  LayoutDashboard, 
  MessageSquareCode, 
  Network, 
  Map, 
  Settings, 
  ChevronLeft, 
  ChevronRight, 
  LogOut, 
  UserRound 
} from "lucide-react";

interface SidebarProps {
  currentTab: string;
  setCurrentTab: (tab: string) => void;
}

export default function Sidebar({ currentTab, setCurrentTab }: SidebarProps) {
  const [isCollapsed, setIsCollapsed] = useState(false);

  const navItems = [
    { id: "dashboard", label: "Dashboard", icon: LayoutDashboard },
    { id: "copilot", label: "AI Assistant", icon: MessageSquareCode },
    { id: "network", label: "Network Graph", icon: Network },
    { id: "map", label: "Hotspot Map", icon: Map },
  ];

  return (
    <aside 
      className={`glass-panel border-y-0 border-l-0 flex flex-col justify-between transition-all duration-300 ${
        isCollapsed ? "w-16" : "w-64"
      } h-screen sticky top-0`}
    >
      {/* Upper Segment: Branding & Navigation */}
      <div>
        {/* Branding header */}
        <div className="h-16 flex items-center justify-between px-4 border-b border-police-border/40">
          <div className="flex items-center gap-3 overflow-hidden">
            <div className="bg-blue-600/20 p-2 rounded-lg border border-blue-500/30 text-blue-500">
              <Shield className="h-5 w-5" />
            </div>
            {!isCollapsed && (
              <span className="font-display font-bold text-lg tracking-wider bg-gradient-to-r from-blue-400 to-indigo-200 bg-clip-text text-transparent">
                KSP INTEL
              </span>
            )}
          </div>
          <button 
            onClick={() => setIsCollapsed(!isCollapsed)}
            className="hover:bg-blue-900/20 text-gray-400 hover:text-blue-400 p-1.5 rounded-lg border border-transparent hover:border-blue-500/20 transition-all cursor-pointer"
          >
            {isCollapsed ? <ChevronRight size={16} /> : <ChevronLeft size={16} />}
          </button>
        </div>

        {/* Navigation list */}
        <nav className="p-3 space-y-1">
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = currentTab === item.id;
            return (
              <button
                key={item.id}
                onClick={() => setCurrentTab(item.id)}
                className={`w-full flex items-center gap-3 p-3 rounded-xl transition-all duration-200 cursor-pointer ${
                  isActive 
                    ? "bg-blue-600/20 text-blue-400 border border-blue-500/40 shadow-inner" 
                    : "text-gray-400 hover:text-gray-200 hover:bg-white/5 border border-transparent"
                }`}
              >
                <Icon size={18} className="shrink-0" />
                {!isCollapsed && <span className="text-sm font-medium">{item.label}</span>}
              </button>
            );
          })}
        </nav>
      </div>

      {/* Lower Segment: User Profile Card & Options */}
      <div className="border-t border-police-border/40 p-3 space-y-2">
        <div className={`flex items-center gap-3 p-2 rounded-xl bg-white/5 border border-police-border/30 overflow-hidden ${
          isCollapsed ? "justify-center px-1" : ""
        }`}>
          <div className="bg-gray-700/50 p-2 rounded-lg border border-gray-600/30 text-gray-300 shrink-0">
            <UserRound className="h-4 w-4" />
          </div>
          {!isCollapsed && (
            <div className="min-w-0">
              <p className="text-xs font-semibold text-gray-200 truncate">Insp. Siddaraju</p>
              <p className="text-[10px] text-gray-500 truncate">KGID: 00395 | Station 1002</p>
            </div>
          )}
        </div>
        
        <button 
          className={`w-full flex items-center gap-3 p-2.5 rounded-xl text-gray-500 hover:text-red-400 hover:bg-red-500/10 border border-transparent hover:border-red-500/20 transition-all cursor-pointer ${
            isCollapsed ? "justify-center" : ""
          }`}
        >
          <LogOut size={16} className="shrink-0" />
          {!isCollapsed && <span className="text-xs font-medium">Log out</span>}
        </button>
      </div>
    </aside>
  );
}
