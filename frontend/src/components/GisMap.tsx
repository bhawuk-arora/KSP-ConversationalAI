// frontend/src/components/GisMap.tsx
"use client";

import { useEffect, useRef, useState } from "react";
import { MapPin, ShieldAlert, Sparkles, Layout } from "lucide-react";

interface Hotspot {
  id: number;
  crime_no: string;
  latitude: number;
  longitude: number;
  date: string;
  major_head_id: number;
}

export default function GisMap() {
  const mapContainerRef = useRef<HTMLDivElement>(null);
  const [mapLoaded, setMapLoaded] = useState(false);
  const [selectedHotspot, setSelectedHotspot] = useState<Hotspot | null>(null);

  // Sample seed hotspots for Bengaluru Urban (Kalasipalya & neighboring sectors)
  const mockHotspots: Hotspot[] = [
    { id: 1, crime_no: "KSP/2026/00102", latitude: 12.9631, longitude: 77.5724, date: "2026-05-20", major_head_id: 2 }, // Kalasipalya (Theft)
    { id: 2, crime_no: "KSP/2026/00143", latitude: 12.9731, longitude: 77.5824, date: "2026-06-01", major_head_id: 1 }, // Chickpet (Body offence)
    { id: 3, crime_no: "KSP/2026/00189", latitude: 12.9531, longitude: 77.5624, date: "2026-06-15", major_head_id: 3 }, // Upparpet (NDPS)
    { id: 4, crime_no: "KSP/2026/00204", latitude: 12.9691, longitude: 77.5904, date: "2026-06-25", major_head_id: 2 }  // Majestic (Burglary)
  ];

  useEffect(() => {
    // 1. Dynamic check to ensure Leaflet runs only on browser clients (avoids SSR errors)
    if (typeof window === "undefined" || !mapContainerRef.current) return;

    // 2. Load Leaflet CDN script & styles dynamically
    const linkId = "leaflet-css";
    const scriptId = "leaflet-js";

    if (!document.getElementById(linkId)) {
      const link = document.createElement("link");
      link.id = linkId;
      link.rel = "stylesheet";
      link.href = "https://unpkg.com/leaflet@1.9.4/dist/leaflet.css";
      document.head.appendChild(link);
    }

    const initMap = () => {
      const L = (window as any).L;
      if (!L || !mapContainerRef.current) return;

      // Initialize map centered around Central Bengaluru
      const map = L.map(mapContainerRef.current, {
        zoomControl: false,
        attributionControl: false
      }).setView([12.9631, 77.5724], 14);

      // Add dark-theme mapped tile layer (OpenStreetMap styled with CSS filter overrides)
      L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
        maxZoom: 19
      }).addTo(map);

      // Add zoom control at bottom right
      L.control.zoom({ position: "bottomright" }).addTo(map);

      // Apply Dark Mode inversion filters directly to Leaflet map tiles
      const mapEl = mapContainerRef.current;
      const tilePane = mapEl.querySelector(".leaflet-tile-pane");
      if (tilePane) {
        (tilePane as HTMLElement).style.filter = "invert(92%) hue-rotate(190deg) brightness(85%) contrast(110%)";
      }

      // Add pulsing alert overlay markers for hotspots
      mockHotspots.forEach((spot) => {
        // Create custom HTML pulsing div marker
        const pulsingIcon = L.divIcon({
          className: "custom-pulsing-icon",
          html: `<div class="w-4 h-4 bg-red-500 rounded-full border-2 border-white animate-ping absolute opacity-75"></div>
                 <div class="w-3.5 h-3.5 bg-red-600 rounded-full border border-white relative z-10"></div>`,
          iconSize: [16, 16],
          iconAnchor: [8, 8]
        });

        const marker = L.marker([spot.latitude, spot.longitude], { icon: pulsingIcon }).addTo(map);
        
        // Link click callback
        marker.on("click", () => {
          setSelectedHotspot(spot);
          map.setView([spot.latitude, spot.longitude], 15);
        });
      });

      setSelectedHotspot(mockHotspots[0]);
      setMapLoaded(true);
    };

    if (!document.getElementById(scriptId)) {
      const script = document.createElement("script");
      script.id = scriptId;
      script.src = "https://unpkg.com/leaflet@1.9.4/dist/leaflet.js";
      script.onload = initMap;
      document.body.appendChild(script);
    } else {
      // Script already loaded, initialize directly
      // Allow DOM repaint to register container ref
      setTimeout(initMap, 200);
    }

    return () => {
      // Cleanup map references if needed
    };
  }, []);

  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 h-[600px]">
      
      {/* Left: Map Container canvas */}
      <div className="lg:col-span-2 glass-panel rounded-2xl p-4 flex flex-col justify-between relative overflow-hidden">
        
        {/* Map overlay dashboard labels */}
        <div className="flex items-center justify-between z-10 absolute top-6 left-6 right-6">
          <div className="flex items-center gap-2 bg-police-bg/80 backdrop-blur border border-police-border/40 px-3 py-1.5 rounded-xl shadow-lg">
            <MapPin className="text-red-500 animate-bounce" size={16} />
            <span className="text-[10px] font-bold font-display uppercase tracking-wider text-gray-200">
              Live Hotspot Plotter (Bengaluru)
            </span>
          </div>
          
          <div className="bg-police-bg/80 backdrop-blur border border-police-border/40 px-3 py-1.5 rounded-xl text-[9px] text-gray-400 shadow-lg flex items-center gap-1.5">
            <span className="w-1.5 h-1.5 bg-red-500 rounded-full animate-ping"></span>
            <span>Spatiotemporal Scan Active</span>
          </div>
        </div>

        {/* Leaflet DOM Anchor */}
        <div 
          ref={mapContainerRef} 
          className="flex-1 w-full h-full rounded-xl z-0" 
          style={{ minHeight: "450px" }}
        />

        {/* Loader status */}
        {!mapLoaded && (
          <div className="absolute inset-0 bg-police-bg/90 backdrop-blur-sm z-20 flex items-center justify-center text-xs text-gray-500 gap-2">
            <span className="w-1.5 h-1.5 bg-blue-500 rounded-full animate-ping"></span>
            Loading GIS Tile Engine...
          </div>
        )}

      </div>

      {/* Right: Inspection GIS Detail Panel */}
      <div className="glass-panel rounded-2xl p-5 flex flex-col justify-between">
        {selectedHotspot ? (
          <div className="space-y-4">
            <div className="flex items-start justify-between border-b border-police-border/40 pb-3">
              <div>
                <span className="text-[9px] uppercase tracking-wider font-bold text-red-400 font-mono">
                  GIS Hotspot Scanner
                </span>
                <h4 className="text-sm font-bold font-display text-gray-200">KSP Crime Incident</h4>
              </div>
              <span className="bg-red-500/10 text-red-500 border border-red-500/20 text-[9px] font-bold px-2 py-0.5 rounded uppercase">
                Active Spike
              </span>
            </div>

            {/* Hotspot details specs */}
            <div className="space-y-4 text-xs">
              <div className="flex items-center justify-between bg-white/5 p-2.5 rounded-lg border border-police-border/20">
                <span className="text-gray-500">Case FIR ID</span>
                <span className="text-gray-200 font-mono font-bold">{selectedHotspot.crime_no}</span>
              </div>
              
              <div className="grid grid-cols-2 gap-3">
                <div className="bg-white/5 p-2 rounded-lg border border-police-border/20">
                  <span className="text-gray-500 text-[10px] block">Latitude</span>
                  <span className="text-gray-200 font-medium">{selectedHotspot.latitude}</span>
                </div>
                <div className="bg-white/5 p-2 rounded-lg border border-police-border/20">
                  <span className="text-gray-500 text-[10px] block">Longitude</span>
                  <span className="text-gray-200 font-medium">{selectedHotspot.longitude}</span>
                </div>
              </div>

              <div className="space-y-1">
                <span className="text-[10px] text-gray-500 block">Crime Category ID</span>
                <p className="text-gray-300 font-medium">
                  {selectedHotspot.major_head_id === 2 
                    ? "Property Offence (Burglary)" 
                    : selectedHotspot.major_head_id === 1 
                      ? "Offence Against Person (Body)" 
                      : "Narcotics Offence (NDPS)"}
                </p>
              </div>

              <div className="space-y-1">
                <span className="text-[10px] text-gray-500 block">Registered Date</span>
                <p className="text-gray-300 font-medium">{selectedHotspot.date}</p>
              </div>
            </div>
          </div>
        ) : (
          <div className="flex-1 flex flex-col items-center justify-center text-center space-y-2 text-gray-500">
            <Layout size={24} />
            <p className="text-xs">Click on any map marker to inspect spatiotemporal cluster details</p>
          </div>
        )}

        {/* Map control widgets */}
        <div className="border-t border-police-border/20 pt-4 mt-4 space-y-2">
          <div className="flex items-center gap-2 text-[10px] text-gray-400">
            <ShieldAlert size={12} className="text-red-400" />
            <span>Spatiotemporal Prediction</span>
          </div>
          
          <div className="bg-white/5 p-3 rounded-xl border border-police-border/40 flex items-start gap-3">
            <Sparkles size={16} className="text-amber-500 shrink-0 mt-0.5 animate-pulse" />
            <div className="min-w-0">
              <span className="text-[10px] font-bold text-gray-200 block">Kalasipalya Spike Prediction</span>
              <p className="text-[9px] text-gray-500 leading-relaxed">
                Predicitive modeling scans indicate a 74% likelihood of repeat burglary incidents within a 200m radius of Kalasipalya limit between 22:00 and 04:00 hours.
              </p>
            </div>
          </div>
        </div>

      </div>

    </div>
  );
}
