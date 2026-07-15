// frontend/src/components/NetworkGraph.tsx
"use client";

import { useState, useEffect } from "react";
import { 
  Users, 
  Search, 
  ShieldAlert, 
  HelpCircle, 
  BookOpen, 
  Layers,
  Network
} from "lucide-react";

interface Node {
  id: string;
  label: string;
  type: "accused" | "case" | "policestation";
  x?: number;
  y?: number;
}

interface Edge {
  id: string;
  source: string;
  target: string;
  label: string;
}

export default function NetworkGraph() {
  const [suspectIdInput, setSuspectIdInput] = useState("1001");
  const [nodes, setNodes] = useState<Node[]>([]);
  const [edges, setEdges] = useState<Edge[]>([]);
  const [selectedNode, setSelectedNode] = useState<Node | null>(null);
  const [hoveredNode, setHoveredNode] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  // Load target network dataset
  const fetchNetwork = (id: string) => {
    setLoading(true);
    // In a real environment, we call: fetch(`/api/v1/network/suspect/${id}`, { headers })
    // For local frontend, we provide a beautiful simulated network matching KSP DB parameters
    setTimeout(() => {
      const mockNodes: Node[] = [
        { id: "accused_1001", label: "Ravi alias Kariya", type: "accused" },
        { id: "case_202501", label: "FIR: Kalasipalya Robbery 101", type: "case" },
        { id: "case_202502", label: "FIR: Upparpet Burglary 103", type: "case" },
        { id: "accused_1002", label: "Ganesh alias Gani", type: "accused" },
        { id: "accused_1003", label: "Imran Khan", type: "accused" },
        { id: "station_10", label: "Kalasipalya Police Station", type: "policestation" },
      ];

      const mockEdges: Edge[] = [
        { id: "e1", source: "accused_1001", target: "case_202501", label: "ACCUSED_IN" },
        { id: "e2", source: "accused_1001", target: "case_202502", label: "ACCUSED_IN" },
        { id: "e3", source: "accused_1002", target: "case_202501", label: "ACCUSED_IN" },
        { id: "e4", source: "accused_1003", target: "case_202502", label: "ACCUSED_IN" },
        { id: "e5", source: "accused_1001", target: "accused_1002", label: "CO_ACCUSED_WITH" },
        { id: "e6", source: "accused_1001", target: "accused_1003", label: "CO_ACCUSED_WITH" },
        { id: "e7", source: "case_202501", target: "station_10", label: "REPORTED_AT" },
      ];

      // Distribute coordinates in concentric circles
      // Target in center
      mockNodes[0].x = 250;
      mockNodes[0].y = 220;

      // Cases in inner circle
      mockNodes[1].x = 130;
      mockNodes[1].y = 140;
      mockNodes[2].x = 370;
      mockNodes[2].y = 140;

      // Co-accused in outer circle
      mockNodes[3].x = 100;
      mockNodes[3].y = 310;
      mockNodes[4].x = 400;
      mockNodes[4].y = 310;

      // Station offset
      mockNodes[5].x = 250;
      mockNodes[5].y = 60;

      setNodes(mockNodes);
      setEdges(mockEdges);
      setSelectedNode(mockNodes[0]);
      setLoading(false);
    }, 400);
  };

  useEffect(() => {
    fetchNetwork("1001");
  }, []);

  const handleNodeClick = (node: Node) => {
    setSelectedNode(node);
  };

  // Determine if a node is connected to the hovered node
  const isRelated = (nodeId: string) => {
    if (!hoveredNode) return true;
    if (nodeId === hoveredNode) return true;
    return edges.some(
      e => 
        (e.source === hoveredNode && e.target === nodeId) ||
        (e.target === hoveredNode && e.source === nodeId)
    );
  };

  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 h-[600px]">
      
      {/* Left: SVG Canvas */}
      <div className="lg:col-span-2 glass-panel rounded-2xl p-4 flex flex-col justify-between relative overflow-hidden">
        
        {/* Graph Header Tools */}
        <div className="flex items-center justify-between z-10">
          <div className="flex items-center gap-2">
            <Network className="text-indigo-400" size={16} />
            <span className="text-xs font-bold font-display uppercase tracking-wider text-gray-200">Suspect Links Explorer</span>
          </div>
          
          {/* Search bar input */}
          <div className="flex items-center gap-2 bg-white/5 border border-police-border/40 rounded-xl px-2 py-1">
            <Search size={12} className="text-gray-500" />
            <input
              type="text"
              placeholder="Suspect ID (e.g. 1001)..."
              value={suspectIdInput}
              onChange={(e) => setSuspectIdInput(e.target.value)}
              className="bg-transparent text-[10px] text-gray-200 outline-none w-28 placeholder-gray-500"
            />
            <button 
              onClick={() => fetchNetwork(suspectIdInput)}
              className="text-[9px] bg-indigo-600/30 hover:bg-indigo-600/50 text-indigo-300 border border-indigo-500/30 px-2 py-0.5 rounded cursor-pointer transition-all"
            >
              Trace
            </button>
          </div>
        </div>

        {/* Dynamic SVG Visualizer Canvas */}
        <div className="flex-1 flex items-center justify-center relative min-h-[400px]">
          {loading ? (
            <div className="text-xs text-gray-500 flex items-center gap-2">
              <span className="w-1.5 h-1.5 bg-blue-500 rounded-full animate-ping"></span>
              Tracing relationship trails in Neo4j...
            </div>
          ) : (
            <svg 
              viewBox="0 0 500 400" 
              className="w-full max-w-[500px] h-full"
            >
              {/* Draw Edges */}
              {edges.map((edge) => {
                const sourceNode = nodes.find(n => n.id === edge.source);
                const targetNode = nodes.find(n => n.id === edge.target);
                if (!sourceNode || !targetNode) return null;
                
                const isEdgeHighlighted = hoveredNode 
                  ? (edge.source === hoveredNode || edge.target === hoveredNode) 
                  : true;
                  
                return (
                  <g key={edge.id}>
                    <line
                      x1={sourceNode.x}
                      y1={sourceNode.y}
                      x2={targetNode.x}
                      y2={targetNode.y}
                      stroke={
                        isEdgeHighlighted 
                          ? edge.label === "CO_ACCUSED_WITH" ? "rgba(239, 68, 68, 0.45)" : "rgba(59, 130, 246, 0.45)"
                          : "rgba(35, 42, 66, 0.15)"
                      }
                      strokeWidth={isEdgeHighlighted ? edge.label === "CO_ACCUSED_WITH" ? 2 : 1.5 : 0.5}
                      strokeDasharray={edge.label === "CO_ACCUSED_WITH" ? "4,4" : "0"}
                      className="transition-all duration-300"
                    />
                    
                    {/* Tiny edge labels on hover */}
                    {hoveredNode && isEdgeHighlighted && (
                      <text
                        x={((sourceNode.x || 0) + (targetNode.x || 0)) / 2}
                        y={((sourceNode.y || 0) + (targetNode.y || 0)) / 2 - 4}
                        fill="rgba(156, 163, 175, 0.7)"
                        fontSize="6"
                        textAnchor="middle"
                        className="pointer-events-none select-none font-mono"
                      >
                        {edge.label}
                      </text>
                    )}
                  </g>
                );
              })}

              {/* Draw Nodes */}
              {nodes.map((node) => {
                const isNodeRelated = isRelated(node.id);
                const isSelected = selectedNode?.id === node.id;
                
                return (
                  <g 
                    key={node.id}
                    transform={`translate(${node.x}, ${node.y})`}
                    onClick={() => handleNodeClick(node)}
                    onMouseEnter={() => setHoveredNode(node.id)}
                    onMouseLeave={() => setHoveredNode(null)}
                    className="cursor-pointer group"
                  >
                    {/* Outer hover ring */}
                    <circle
                      r={isSelected ? 18 : 15}
                      fill="transparent"
                      stroke={
                        isSelected 
                          ? "#3b82f6" 
                          : node.type === "accused" ? "#ef4444" : node.type === "case" ? "#f59e0b" : "#10b981"
                      }
                      strokeWidth={isSelected ? 2 : 0}
                      className="group-hover:stroke-blue-400 group-hover:stroke-[1.5px] transition-all duration-300"
                    />
                    
                    {/* Node Core */}
                    <circle
                      r={isSelected ? 12 : 10}
                      fill={
                        node.type === "accused" 
                          ? "rgba(239, 68, 68, 0.2)" 
                          : node.type === "case" ? "rgba(245, 158, 11, 0.2)" : "rgba(16, 185, 129, 0.2)"
                      }
                      stroke={
                        node.type === "accused" 
                          ? "rgba(239, 68, 68, 0.8)" 
                          : node.type === "case" ? "rgba(245, 158, 11, 0.8)" : "rgba(16, 185, 129, 0.8)"
                      }
                      strokeWidth={1.5}
                      opacity={isNodeRelated ? 1 : 0.25}
                      className="transition-all duration-300"
                    />

                    {/* Text Label overlay */}
                    <text
                      y={isSelected ? 26 : 22}
                      fill={isNodeRelated ? "rgba(243, 244, 246, 0.85)" : "rgba(156, 163, 175, 0.2)"}
                      fontSize="7"
                      fontWeight={isSelected ? "bold" : "normal"}
                      textAnchor="middle"
                      className="pointer-events-none select-none font-sans transition-all duration-300"
                    >
                      {node.label.length > 18 ? `${node.label.slice(0, 15)}...` : node.label}
                    </text>
                  </g>
                );
              })}
            </svg>
          )}
        </div>

        {/* Legend */}
        <div className="flex items-center gap-4 text-[9px] text-gray-500 border-t border-police-border/20 pt-2 z-10">
          <div className="flex items-center gap-1">
            <span className="w-2 h-2 rounded-full bg-red-500/20 border border-red-500/80"></span>
            <span>Suspect</span>
          </div>
          <div className="flex items-center gap-1">
            <span className="w-2 h-2 rounded-full bg-amber-500/20 border border-amber-500/80"></span>
            <span>FIR Case</span>
          </div>
          <div className="flex items-center gap-1">
            <span className="w-2 h-2 rounded-full bg-emerald-500/20 border border-emerald-500/80"></span>
            <span>Station</span>
          </div>
          <div className="flex-1"></div>
          <span>Tip: Hover nodes to highlight local subnet connections</span>
        </div>

      </div>

      {/* Right: Inspection Inspector Panel */}
      <div className="glass-panel rounded-2xl p-5 flex flex-col justify-between">
        {selectedNode ? (
          <div className="space-y-4">
            <div className="flex items-start justify-between border-b border-police-border/40 pb-3">
              <div>
                <span className="text-[9px] uppercase tracking-wider font-bold text-blue-400 font-mono">
                  Node Inspector
                </span>
                <h4 className="text-sm font-bold font-display text-gray-200">{selectedNode.label}</h4>
              </div>
              <span className={`text-[9px] font-bold px-2 py-0.5 rounded uppercase ${
                selectedNode.type === "accused" 
                  ? "bg-red-500/10 text-red-500 border border-red-500/20" 
                  : selectedNode.type === "case" 
                    ? "bg-amber-500/10 text-amber-500 border border-amber-500/20" 
                    : "bg-emerald-500/10 text-emerald-500 border border-emerald-500/20"
              }`}>
                {selectedNode.type}
              </span>
            </div>

            {/* Profile specifications */}
            <div className="space-y-3 text-xs">
              {selectedNode.type === "accused" && (
                <>
                  <div className="flex items-center justify-between bg-white/5 p-2 rounded-lg border border-police-border/20">
                    <span className="text-gray-500">Suspect Risk Factor</span>
                    <span className="text-red-500 font-bold font-display">84% High Risk</span>
                  </div>
                  <div className="space-y-1">
                    <span className="text-[10px] text-gray-500 block">Primary M.O. Signature</span>
                    <p className="text-gray-300 font-medium">House Breaking/Lock Cutting</p>
                  </div>
                  <div className="space-y-1">
                    <span className="text-[10px] text-gray-500 block">Network Involvement</span>
                    <p className="text-gray-300">Co-conspirator links traced to 2 other suspects in Kalasipalya limit.</p>
                  </div>
                </>
              )}

              {selectedNode.type === "case" && (
                <>
                  <div className="flex items-center justify-between bg-white/5 p-2 rounded-lg border border-police-border/20">
                    <span className="text-gray-500">Major Crime Head</span>
                    <span className="text-amber-500 font-bold font-display">Property Offence</span>
                  </div>
                  <div className="space-y-1">
                    <span className="text-[10px] text-gray-500 block">Offences Violations</span>
                    <p className="text-gray-300 font-medium">Section 380 - House Breaking Theft</p>
                  </div>
                  <div className="space-y-1">
                    <span className="text-[10px] text-gray-500 block">Investigation Status</span>
                    <p className="text-gray-300">Under investigation. Chargesheet pending draft.</p>
                  </div>
                </>
              )}

              {selectedNode.type === "policestation" && (
                <>
                  <div className="flex items-center justify-between bg-white/5 p-2 rounded-lg border border-police-border/20">
                    <span className="text-gray-500">Station Limit Code</span>
                    <span className="text-emerald-500 font-bold font-display">Station-1002</span>
                  </div>
                  <div className="space-y-1">
                    <span className="text-[10px] text-gray-500 block">Total Active FIRs</span>
                    <p className="text-gray-300 font-medium">1,204 Cases (Q2 2026)</p>
                  </div>
                </>
              )}
            </div>
          </div>
        ) : (
          <div className="flex-1 flex flex-col items-center justify-center text-center space-y-2 text-gray-500">
            <HelpCircle size={24} />
            <p className="text-xs">Select any node on the graph canvas to view details</p>
          </div>
        )}

        {/* Segment options */}
        <div className="border-t border-police-border/20 pt-4 mt-4 space-y-2">
          <div className="flex items-center gap-2 text-[10px] text-gray-400">
            <ShieldAlert size={12} className="text-indigo-400" />
            <span>Link Analytics Tools</span>
          </div>
          <div className="grid grid-cols-2 gap-2 text-[10px]">
            <button className="bg-white/5 hover:bg-white/10 border border-police-border/40 text-gray-300 py-2 rounded-xl transition-all cursor-pointer text-center font-semibold">
              Find Communities
            </button>
            <button className="bg-white/5 hover:bg-white/10 border border-police-border/40 text-gray-300 py-2 rounded-xl transition-all cursor-pointer text-center font-semibold">
              Shortest Path
            </button>
          </div>
        </div>

      </div>

    </div>
  );
}
