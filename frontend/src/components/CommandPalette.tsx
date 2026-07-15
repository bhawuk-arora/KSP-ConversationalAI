// frontend/src/components/CommandPalette.tsx
"use client";

import { useEffect, useState, useRef } from "react";
import { Search, FileText, User, Navigation, Shield, CornerDownLeft } from "lucide-react";

interface CommandPaletteProps {
  isOpen: boolean;
  setIsOpen: (val: boolean) => void;
  setTab: (tab: string) => void;
}

export default function CommandPalette({ isOpen, setIsOpen, setTab }: CommandPaletteProps) {
  const [searchQuery, setSearchQuery] = useState("");
  const inputRef = useRef<HTMLInputElement>(null);

  // Monitor global Ctrl+K keystrokes
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === "k") {
        e.preventDefault();
        setIsOpen(!isOpen);
      }
      if (e.key === "Escape") {
        setIsOpen(false);
      }
    };
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [isOpen, setIsOpen]);

  // Focus input when modal opens
  useEffect(() => {
    if (isOpen && inputRef.current) {
      inputRef.current.focus();
    }
  }, [isOpen]);

  if (!isOpen) return null;

  const mockResults = [
    { type: "case", icon: FileText, label: "FIR:100120257202500001", sub: "Section 302 - Crimes Against Body (Kalasipalya)" },
    { type: "case", icon: FileText, label: "FIR:100020027202600001", sub: "Section 380 - Housebreaking Theft (Vidhana Soudha)" },
    { type: "suspect", icon: User, label: "Ravi alias Kariya", sub: "Habitual Offender | Theft | Risk Score: 84" },
    { type: "suspect", icon: User, label: "Yahvi Mannan", sub: "Accused | Murder | Kalasipalya Case" },
    { type: "nav", icon: Navigation, label: "Navigate: Network Graph", sub: "View criminal relationship maps", target: "network" },
    { type: "nav", icon: Navigation, label: "Navigate: Hotspot Map", sub: "View spatiotemporal maps", target: "map" }
  ];

  const filteredResults = mockResults.filter(item => 
    item.label.toLowerCase().includes(searchQuery.toLowerCase()) ||
    item.sub.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const handleItemClick = (item: typeof mockResults[0]) => {
    if (item.type === "nav" && item.target) {
      setTab(item.target);
    }
    setIsOpen(false);
    setSearchQuery("");
  };

  return (
    <div className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-start justify-center pt-24">
      {/* Click outside to close */}
      <div className="absolute inset-0" onClick={() => setIsOpen(false)}></div>
      
      {/* Floating Glass Panel Search Box */}
      <div className="glass-panel w-full max-w-2xl rounded-2xl shadow-2xl shadow-black/80 overflow-hidden relative z-10 scale-[0.98] animate-in fade-in zoom-in-95 duration-150">
        
        {/* Search Input */}
        <div className="flex items-center gap-3 px-4 py-4 border-b border-police-border/40">
          <Search className="text-gray-400 shrink-0" size={18} />
          <input
            ref={inputRef}
            type="text"
            placeholder="Type a case ID, suspect name, or navigation command..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full bg-transparent text-sm text-gray-200 outline-none placeholder-gray-500"
          />
        </div>

        {/* Results List */}
        <div className="max-h-96 overflow-y-auto p-2 space-y-1">
          {filteredResults.length > 0 ? (
            filteredResults.map((item, idx) => {
              const Icon = item.icon;
              return (
                <button
                  key={idx}
                  onClick={() => handleItemClick(item)}
                  className="w-full text-left flex items-center justify-between p-3 rounded-xl hover:bg-white/5 border border-transparent hover:border-police-border/30 transition-all cursor-pointer group"
                >
                  <div className="flex items-center gap-3 min-w-0">
                    <div className="p-2 rounded-lg bg-white/5 border border-police-border/40 text-gray-400 group-hover:text-blue-400 group-hover:border-blue-500/20 transition-all">
                      <Icon size={16} />
                    </div>
                    <div className="min-w-0">
                      <p className="text-xs font-semibold text-gray-200 truncate">{item.label}</p>
                      <p className="text-[10px] text-gray-500 truncate">{item.sub}</p>
                    </div>
                  </div>
                  <div className="opacity-0 group-hover:opacity-100 flex items-center gap-1.5 text-[9px] text-blue-400 font-medium transition-all">
                    <span>Select</span>
                    <CornerDownLeft size={10} />
                  </div>
                </button>
              );
            })
          ) : (
            <div className="py-8 text-center text-xs text-gray-500">
              No matching cases, suspects, or commands found.
            </div>
          )}
        </div>

        {/* Footer shortcuts */}
        <div className="bg-white/[0.02] border-t border-police-border/30 px-4 py-2.5 flex items-center justify-between text-[10px] text-gray-500">
          <div className="flex items-center gap-4">
            <span className="flex items-center gap-1"><kbd className="bg-white/10 px-1 rounded font-mono">↑↓</kbd> Navigate</span>
            <span className="flex items-center gap-1"><kbd className="bg-white/10 px-1 rounded font-mono">Enter</kbd> Select</span>
          </div>
          <span className="flex items-center gap-1"><kbd className="bg-white/10 px-1 rounded font-mono">ESC</kbd> Close</span>
        </div>

      </div>
    </div>
  );
}
