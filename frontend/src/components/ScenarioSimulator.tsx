// frontend/src/components/ScenarioSimulator.tsx

"use client";

import { useState } from "react";

interface Step {
  action: string;
  parameters?: Record<string, any>;
}

interface SimulationResult {
  scenario_name: string;
  outcome: string;
  details: Record<string, any>;
}

export default function ScenarioSimulator() {
  const [scenarioName, setScenarioName] = useState("");
  const [stepsJson, setStepsJson] = useState<string>("[\n  { \"action\": \"example\", \"parameters\": {} }\n]");
  const [result, setResult] = useState<SimulationResult | null>(null);
  const [error, setError] = useState<string>("");
  const [loading, setLoading] = useState(false);

  const runSimulation = async () => {
    setLoading(true);
    setError("");
    setResult(null);
    try {
      const steps: Step[] = JSON.parse(stepsJson);
      const payload = { scenario_name: scenarioName, steps };
      const token = typeof window !== "undefined" ? localStorage.getItem("token") : null;
      const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";
      const res = await fetch(`${API_URL}/api/v1/simulation/simulate`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          ...(token ? { Authorization: `Bearer ${token}` } : {}),
        },
        body: JSON.stringify(payload),
      });
      if (!res.ok) {
        const txt = await res.text();
        throw new Error(`Server error ${res.status}: ${txt}`);
      }
      const data: SimulationResult = await res.json();
      setResult(data);
    } catch (e: any) {
      setError(e.message || "Unexpected error");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="glass-panel p-6 rounded-2xl space-y-4">
      <h2 className="text-xl font-bold text-gray-100">Scenario Simulation</h2>
      <div className="space-y-2">
        <label className="block text-sm font-medium text-gray-300">Scenario Name</label>
        <input
          type="text"
          className="w-full bg-white/5 border border-police-border/40 rounded-xl px-3 py-2 text-gray-200 focus:outline-none"
          value={scenarioName}
          onChange={(e) => setScenarioName(e.target.value)}
          placeholder="Enter a name..."
        />
      </div>
      <div className="space-y-2">
        <label className="block text-sm font-medium text-gray-300">Steps (JSON array)</label>
        <textarea
          rows={6}
          className="w-full bg-white/5 border border-police-border/40 rounded-xl px-3 py-2 text-gray-200 focus:outline-none resize-none"
          value={stepsJson}
          onChange={(e) => setStepsJson(e.target.value)}
        />
      </div>
      <button
        onClick={runSimulation}
        disabled={loading}
        className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-xl transition-colors disabled:opacity-50"
      >
        {loading ? "Running…" : "Run Simulation"}
      </button>
      {error && <p className="text-sm text-red-400">{error}</p>}
      {result && (
        <div className="mt-4 p-4 bg-white/5 border border-police-border/30 rounded-xl text-gray-200">
          <h3 className="text-lg font-semibold mb-2">Result</h3>
          <pre className="whitespace-pre-wrap text-sm">{JSON.stringify(result, null, 2)}</pre>
        </div>
      )}
    </div>
  );
}
