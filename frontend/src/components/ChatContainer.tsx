// frontend/src/components/ChatContainer.tsx
"use client";

import { useState, useRef, useEffect } from "react";
import {
  MessageSquare,
  Send,
  FileDown,
  Sparkles,
  X,
  Languages,
  Eye,
  ChevronRight,
  Loader2,
  Bot,
} from "lucide-react";

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

type Message = {
  sender: "user" | "bot";
  text: string;
  sql?: string;
  confidence?: number;
  citations?: string[];
  timestamp: Date;
};

interface ChatContainerProps {
  demoMode: boolean;
  user?: { email: string; role: string; station_id: number } | null;
}

const QUICK_PROMPTS = [
  "Show theft cases in Bengaluru Urban 2026",
  "Who are the repeat offenders with 3+ cases?",
  "List body offence cases under investigation",
  "Which stations have the highest crime index?",
];

function TypingIndicator() {
  return (
    <div className="flex items-end gap-2">
      <div className="bg-blue-600/20 border border-blue-500/20 p-1.5 rounded-lg text-blue-400">
        <Bot size={12} />
      </div>
      <div className="bg-white/5 border border-police-border/30 rounded-2xl rounded-bl-none px-4 py-3 flex items-center gap-1.5">
        <span className="w-1.5 h-1.5 bg-gray-400 rounded-full animate-bounce [animation-delay:0ms]" />
        <span className="w-1.5 h-1.5 bg-gray-400 rounded-full animate-bounce [animation-delay:150ms]" />
        <span className="w-1.5 h-1.5 bg-gray-400 rounded-full animate-bounce [animation-delay:300ms]" />
      </div>
    </div>
  );
}

function formatTime(d: Date) {
  return d.toLocaleTimeString("en-IN", { hour: "2-digit", minute: "2-digit", hour12: true });
}

export default function ChatContainer({ demoMode, user }: ChatContainerProps) {
  const [isOpen, setIsOpen] = useState(false);
  const [language, setLanguage] = useState<"EN" | "KN">("EN");
  const [messages, setMessages] = useState<Message[]>([
    {
      sender: "bot",
      text: `Good day${user?.role ? `, ${user.role}` : ""}. I am the KSP Investigative Copilot — your AI assistant for querying crime records, suspect profiles, and case intelligence. How can I help?`,
      timestamp: new Date(),
    },
  ]);
  const [inputVal, setInputVal] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  const bottomRef = useRef<HTMLDivElement>(null);

  // Auto-scroll on every new message
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isLoading]);

  const handleSend = async () => {
    if (!inputVal.trim() || isLoading) return;
    const userText = inputVal;
    setInputVal("");
    setIsLoading(true);

    const userMsg: Message = { sender: "user", text: userText, timestamp: new Date() };
    setMessages(prev => [...prev, userMsg]);

    try {
      const token = localStorage.getItem("token");
      const response = await fetch(`${API_URL}/api/v1/chat/message`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          ...(token ? { Authorization: `Bearer ${token}` } : {}),
        },
        body: JSON.stringify({ message: userText, session_id: crypto.randomUUID(), demo_mode: demoMode }),
      });

      if (!response.body) throw new Error("No response body");

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let done = false;
      let botMsg: Message = { sender: "bot", text: "", timestamp: new Date() };
      let started = false;

      while (!done) {
        const { value, done: readerDone } = await reader.read();
        done = readerDone;
        if (!value) continue;

        const chunk = decoder.decode(value, { stream: true });
        const lines = chunk.split("\n").filter(l => l.startsWith("data:"));

        for (const line of lines) {
          try {
            const data = JSON.parse(line.replace(/^data:\s*/, ""));

            if (data.event === "message_chunk") {
              botMsg.text += data.text;
              setIsLoading(false);
              if (!started) {
                started = true;
                setMessages(prev => [...prev, { ...botMsg }]);
              } else {
                setMessages(prev => {
                  const updated = [...prev];
                  updated[updated.length - 1] = { ...botMsg };
                  return updated;
                });
              }
            } else if (data.event === "metadata") {
              botMsg.sql = data.sql_executed || "";
              botMsg.citations = data.citations || [];
              botMsg.confidence = data.confidence_score || 0;
              setMessages(prev => {
                const updated = [...prev];
                updated[updated.length - 1] = { ...botMsg };
                return updated;
              });
            } else if (data.event === "error") {
              setIsLoading(false);
              setMessages(prev => [
                ...prev,
                { sender: "bot" as const, text: `⚠️ ${data.text}`, timestamp: new Date() },
              ]);
            }
          } catch {
            // skip malformed SSE line
          }
        }
      }
    } catch {
      setMessages(prev => [
        ...prev,
        { sender: "bot", text: "Could not reach the backend chat service. Please ensure the API is running.", timestamp: new Date() },
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleExportPDF = async () => {
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
      if (!res.ok) { alert("You may not have permission to generate reports."); return; }
      const blob = await res.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `KSP_Report_${new Date().toISOString().slice(0, 10)}.pdf`;
      a.click();
      window.URL.revokeObjectURL(url);
    } catch {
      alert("Report download failed.");
    }
  };

  return (
    <div className="fixed bottom-6 right-6 z-40 flex flex-col items-end gap-2">

      {/* Floating trigger */}
      {!isOpen && (
        <button
          onClick={() => setIsOpen(true)}
          className="flex items-center gap-2.5 bg-blue-600 hover:bg-blue-500 text-white pl-4 pr-5 py-3 rounded-full shadow-xl shadow-blue-900/40 border border-blue-400/30 hover:scale-[1.03] active:scale-[0.98] transition-all duration-200 cursor-pointer group"
        >
          <MessageSquare size={18} className="group-hover:rotate-6 transition-transform" />
          <span className="text-sm font-semibold tracking-wide">Copilot</span>
          <ChevronRight size={14} className="opacity-60" />
        </button>
      )}

      {/* Chat window */}
      {isOpen && (
        <div className="glass-panel w-[440px] h-[580px] rounded-2xl shadow-2xl shadow-black/60 flex flex-col overflow-hidden border border-police-border/50">

          {/* Header */}
          <div className="shrink-0 px-4 py-3 border-b border-police-border/40 bg-white/[0.02] flex items-center justify-between">
            <div className="flex items-center gap-2.5">
              <div className="bg-blue-600/20 p-1.5 rounded-lg border border-blue-500/30 text-blue-400">
                <Sparkles size={14} className="animate-pulse" />
              </div>
              <div>
                <h3 className="text-xs font-bold text-gray-200 tracking-wide">KSP Investigative Copilot</h3>
                <span className="text-[9px] text-emerald-500 flex items-center gap-1">
                  <span className="w-1.5 h-1.5 bg-emerald-500 rounded-full animate-ping" />
                  Connected · {demoMode ? "Demo Mode ON" : "Full Data Mode"}
                </span>
              </div>
            </div>

            <div className="flex items-center gap-1">
              {/* Language toggle */}
              <button
                onClick={() => setLanguage(l => l === "EN" ? "KN" : "EN")}
                title="Toggle language"
                className="flex items-center gap-1 px-2 py-1 rounded-lg text-[10px] font-bold text-gray-400 hover:text-blue-400 hover:bg-white/5 border border-transparent hover:border-police-border/30 transition-all cursor-pointer"
              >
                <Languages size={12} />
                {language}
              </button>

              {/* Export PDF */}
              <button
                onClick={handleExportPDF}
                title="Download PDF report"
                className="p-1.5 rounded-lg text-gray-400 hover:text-green-400 hover:bg-green-500/10 border border-transparent hover:border-green-500/20 transition-all cursor-pointer"
              >
                <FileDown size={14} />
              </button>

              {/* Close */}
              <button
                onClick={() => setIsOpen(false)}
                className="p-1.5 rounded-lg text-gray-400 hover:text-red-400 hover:bg-red-500/10 border border-transparent hover:border-red-500/20 transition-all cursor-pointer"
              >
                <X size={14} />
              </button>
            </div>
          </div>

          {/* Message feed */}
          <div className="flex-1 overflow-y-auto px-4 py-4 space-y-4 scrollbar-thin scrollbar-thumb-white/10">
            {messages.map((msg, i) => (
              <div key={i} className={`flex flex-col gap-1 ${msg.sender === "user" ? "items-end" : "items-start"}`}>
                <div
                  className={`max-w-[88%] rounded-2xl px-3.5 py-2.5 text-[12px] leading-relaxed ${
                    msg.sender === "user"
                      ? "bg-blue-600/25 text-blue-100 border border-blue-500/30 rounded-br-sm"
                      : "bg-white/[0.05] text-gray-200 border border-police-border/30 rounded-bl-sm"
                  }`}
                >
                  {msg.text}

                  {/* Explainability block */}
                  {msg.sql && (
                    <div className="mt-3 pt-2.5 border-t border-white/10 space-y-2">
                      <div className="flex items-center gap-1 text-[9px] text-blue-400 font-bold uppercase tracking-wider">
                        <Eye size={9} />
                        <span>SQL Executed</span>
                      </div>
                      <pre className="text-[9px] font-mono bg-black/50 p-2 rounded-lg border border-white/5 overflow-x-auto text-gray-400 whitespace-pre-wrap">
                        {msg.sql}
                      </pre>
                      <div className="flex items-center justify-between text-[9px] text-gray-500">
                        <span>Confidence: <span className="text-emerald-400 font-semibold">{((msg.confidence ?? 0.9) * 100).toFixed(0)}%</span></span>
                        {msg.citations?.length ? (
                          <span>Sources: {msg.citations.slice(0, 2).join(", ")}</span>
                        ) : null}
                      </div>
                    </div>
                  )}
                </div>
                <span className="text-[9px] text-gray-600 px-1">{formatTime(msg.timestamp)}</span>
              </div>
            ))}

            {isLoading && <TypingIndicator />}
            <div ref={bottomRef} />
          </div>

          {/* Quick prompts — shown only at start */}
          {messages.length === 1 && !isLoading && (
            <div className="shrink-0 px-4 pb-2 flex flex-wrap gap-1.5">
              {QUICK_PROMPTS.map(p => (
                <button
                  key={p}
                  onClick={() => { setInputVal(p); }}
                  className="text-[10px] bg-white/5 hover:bg-white/10 text-gray-400 hover:text-gray-200 px-2.5 py-1 rounded-full border border-police-border/30 transition-all cursor-pointer"
                >
                  {p}
                </button>
              ))}
            </div>
          )}

          {/* Input bar */}
          <div className="shrink-0 px-3 py-3 border-t border-police-border/40 bg-white/[0.01] flex items-center gap-2">
            <input
              type="text"
              placeholder={language === "EN" ? "Ask about FIRs, suspects, trends…" : "ಎಫ್ಐಆರ್, ಆರೋಪಿಗಳ ಬಗ್ಗೆ ಕೇಳಿ…"}
              value={inputVal}
              onChange={e => setInputVal(e.target.value)}
              onKeyDown={e => e.key === "Enter" && handleSend()}
              disabled={isLoading}
              className="flex-1 bg-white/5 border border-police-border/40 rounded-xl px-3 py-2 text-xs text-gray-200 placeholder-gray-600 outline-none focus:border-blue-500/50 transition-all disabled:opacity-50"
            />
            <button
              onClick={handleSend}
              disabled={isLoading || !inputVal.trim()}
              className="p-2.5 bg-blue-600 hover:bg-blue-500 disabled:bg-gray-700 disabled:cursor-not-allowed text-white rounded-xl border border-blue-400/30 transition-all cursor-pointer flex items-center justify-center"
            >
              {isLoading
                ? <Loader2 size={14} className="animate-spin" />
                : <Send size={14} />
              }
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
