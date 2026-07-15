// frontend/src/components/ChatContainer.tsx
"use client";

import { useState } from "react";
import { 
  MessageSquare, 
  Send, 
  Mic, 
  FileDown, 
  Sparkles, 
  X, 
  Languages, 
  Eye, 
  Maximize2,
  ChevronUp
} from "lucide-react";

interface ChatContainerProps {
  demoMode: boolean;
}

export default function ChatContainer({ demoMode }: ChatContainerProps) {
  const [isOpen, setIsOpen] = useState(false);
  const [language, setLanguage] = useState<"EN" | "KN">("EN");
  const [messages, setMessages] = useState<Array<{ sender: "user" | "bot"; text: string; sql?: string; confidence?: number; citations?: string[] }>>([
    { 
      sender: "bot", 
      text: "Good day, Inspector. I am KSP Investigative Copilot. How can I assist you with the crime database today?",
    }
  ]);
  const [inputVal, setInputVal] = useState("");

  const handleSend = async () => {
    if (!inputVal.trim()) return;
    const userText = inputVal;
    setInputVal("");

    // Add user message
    setMessages(prev => [...prev, { sender: "user", text: userText }]);

    try {
      const response = await fetch("http://localhost:8000/api/v1/chat/message", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: userText, session_id: "", demo_mode: demoMode })
      });
      if (!response.body) throw new Error("No response body");
      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let done = false;
      let botMessage = { sender: "bot", text: "", sql: "", confidence: 0, citations: [] };

      while (!done) {
        const { value, done: readerDone } = await reader.read();
        done = readerDone;
        if (value) {
          const chunk = decoder.decode(value, { stream: true });
          const lines = chunk.split("\n").filter(line => line.startsWith("data:"));
          for (const line of lines) {
            const jsonStr = line.replace(/^data:\s*/, "");
            const data = JSON.parse(jsonStr);
            if (data.event === "message_chunk") {
              botMessage.text += data.text;
              setMessages(prev => [...prev, { ...botMessage }]);
            } else if (data.event === "metadata") {
              botMessage.sql = data.sql_executed || "";
              botMessage.citations = data.citations || [];
              botMessage.confidence = data.confidence_score || 0;
              setMessages(prev => [...prev, { ...botMessage }]);
            } else if (data.event === "error") {
              setMessages(prev => [...prev, { sender: "bot", text: `Error: ${data.text}` }]);
            }
          }
        }
      }
    } catch (e) {
      console.error(e);
      setMessages(prev => [...prev, { sender: "bot", text: "Failed to connect to backend chat service." }]);
    }
  };

  return (
    <div className="fixed bottom-6 right-6 z-40 flex flex-col items-end">
      
      {/* Floating Trigger button when closed */}
      {!isOpen && (
        <button
          onClick={() => setIsOpen(true)}
          className="flex items-center gap-2 bg-blue-600 hover:bg-blue-500 text-white px-4 py-3 rounded-full shadow-lg hover:shadow-blue-500/20 border border-blue-400/40 hover:scale-105 transition-all duration-300 cursor-pointer group"
        >
          <MessageSquare size={20} className="group-hover:rotate-12 transition-transform" />
          <span className="text-xs font-semibold tracking-wide">Conversational Assistant</span>
        </button>
      )}

      {/* Floating Copilot Window when open */}
      {isOpen && (
        <div className="glass-panel w-96 md:w-[450px] h-[550px] rounded-2xl shadow-2xl shadow-black/80 flex flex-col justify-between overflow-hidden animate-in slide-in-from-bottom-12 fade-in duration-200">
          
          {/* Header */}
          <div className="bg-white/[0.03] border-b border-police-border/40 p-4 flex items-center justify-between">
            <div className="flex items-center gap-2">
              <div className="bg-blue-600/20 p-1.5 rounded-lg border border-blue-500/30 text-blue-500">
                <Sparkles size={16} className="animate-pulse" />
              </div>
              <div>
                <h3 className="text-xs font-bold font-display text-gray-200">KSP Investigative Copilot</h3>
                <span className="text-[9px] text-emerald-500 flex items-center gap-1">
                  <span className="w-1.5 h-1.5 bg-emerald-500 rounded-full animate-ping"></span>
                  Language Engine Ready
                </span>
              </div>
            </div>
            
            {/* Header controls (PDF, Language, Close) */}
            <div className="flex items-center gap-2">
              <button 
                onClick={() => setLanguage(language === "EN" ? "KN" : "EN")}
                className="p-1.5 rounded-lg hover:bg-white/5 text-gray-400 hover:text-blue-400 border border-transparent hover:border-police-border/20 transition-all cursor-pointer flex items-center gap-1 text-[10px] font-bold"
                title="Toggle Language (Kannada/English)"
              >
                <Languages size={14} />
                <span>{language}</span>
              </button>
              
              <button 
                className="p-1.5 rounded-lg hover:bg-white/5 text-gray-400 hover:text-blue-400 border border-transparent hover:border-police-border/20 transition-all cursor-pointer"
                title="Export chat history as PDF"
              >
                <FileDown size={14} />
              </button>
              
              <button 
                onClick={() => setIsOpen(false)}
                className="p-1.5 rounded-lg hover:bg-red-500/10 text-gray-400 hover:text-red-400 border border-transparent hover:border-red-500/20 transition-all cursor-pointer"
              >
                <X size={14} />
              </button>
            </div>
          </div>

          {/* Chat Feed Messages */}
          <div className="flex-1 overflow-y-auto p-4 space-y-4">
            {messages.map((msg, index) => (
              <div 
                key={index} 
                className={`flex flex-col ${msg.sender === "user" ? "items-end" : "items-start"}`}
              >
                <div 
                  className={`max-w-[85%] rounded-2xl p-3 text-xs leading-relaxed ${
                    msg.sender === "user" 
                      ? "bg-blue-600/30 text-blue-200 border border-blue-500/40 rounded-br-none" 
                      : "bg-white/5 text-gray-200 border border-police-border/30 rounded-bl-none"
                  }`}
                >
                  {msg.text}

                  {/* Explainability Block (SQL query executed) */}
                  {msg.sql && (
                    <div className="mt-3 pt-2 border-t border-police-border/30 space-y-1.5">
                      <div className="flex items-center gap-1.5 text-[9px] text-blue-400 font-bold uppercase tracking-wider">
                        <Eye size={10} />
                        <span>Live Explainability Path</span>
                      </div>
                      <pre className="text-[9px] font-mono bg-black/40 p-2 rounded border border-white/5 overflow-x-auto text-gray-400">
                        {msg.sql}
                      </pre>
                      <div className="flex items-center justify-between text-[9px] text-gray-500">
                        <span>Confidence Score: {((msg.confidence || 0.9) * 100).toFixed(0)}%</span>
                        {msg.citations && <span>Citations: {msg.citations.join(", ")}</span>}
                      </div>
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>

          {/* Quick Action Suggestions */}
          {messages.length === 1 && (
            <div className="px-4 py-2 flex flex-wrap gap-2">
              <button 
                onClick={() => setInputVal("Find theft cases in Kalasipalya during 2026")}
                className="text-[10px] bg-white/5 hover:bg-white/10 text-gray-400 hover:text-gray-200 px-2.5 py-1 rounded-full border border-police-border/40 transition-all cursor-pointer"
              >
                "Burglary cases in Kalasipalya"
              </button>
              <button 
                onClick={() => setInputVal("Find repeat offenders linked to case 103")}
                className="text-[10px] bg-white/5 hover:bg-white/10 text-gray-400 hover:text-gray-200 px-2.5 py-1 rounded-full border border-police-border/40 transition-all cursor-pointer"
              >
                "Repeat offenders linked to case 103"
              </button>
            </div>
          )}

          {/* Input Panel */}
          <div className="p-4 border-t border-police-border/40 bg-white/[0.01] flex items-center gap-2">
            <button className="p-2 rounded-xl hover:bg-white/5 text-gray-400 hover:text-blue-400 border border-transparent hover:border-police-border/30 transition-all cursor-pointer">
              <Mic size={16} />
            </button>
            
            <input
              type="text"
              placeholder={language === "EN" ? "Ask a question about FIRs, accused..." : "ಎಫ್ಐಆರ್ ಬಗ್ಗೆ ಪ್ರಶ್ನೆ ಕೇಳಿ..."}
              value={inputVal}
              onChange={(e) => setInputVal(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && handleSend()}
              className="flex-1 bg-transparent text-xs text-gray-200 outline-none placeholder-gray-500"
            />
            
            <button 
              onClick={handleSend}
              className="p-2 bg-blue-600 hover:bg-blue-500 text-white rounded-xl border border-blue-400/30 transition-all cursor-pointer"
            >
              <Send size={14} />
            </button>
          </div>

        </div>
      )}

    </div>
  );
}
