# UI/UX Design System Document

This document outlines the visual language, typography, color tokens, and interface principles for the KSP Crime Intelligence Platform. It targets a premium, dark-mode government workspace resembling an enterprise dashboard.

---

## 1. Design Tokens

### 1.1 Color Palette (Dark Theme / Glassmorphism)

| Token | CSS HSL Value | Sample Use |
| :--- | :--- | :--- |
| **Background (Deep Space)** | `hsl(224, 71%, 4%)` | App background |
| **Surface (Glass Base)** | `hsla(224, 71%, 8%, 0.45)` | Card backgrounds (with backdrop-filter) |
| **Primary (KSP Police Blue)** | `hsl(217, 91%, 60%)` | Interactive actions, active state |
| **Secondary (Muted Indigo)** | `hsl(230, 58%, 75%)` | Subtext, secondary details |
| **Accent / Active (Emerald)** | `hsl(142, 70%, 45%)` | Low risk, solved cases, normal status |
| **Warning (Amber)** | `hsl(38, 92%, 50%)` | Medium risk, ongoing investigations |
| **Danger (Pulse Red)** | `hsl(346, 84%, 50%)` | Heinous crimes, high-risk forecasting, alerts |
| **Border (Muted Slate)** | `hsla(220, 20%, 20%, 0.6)` | Card borders, dividers |

### 1.2 Typography
- **Primary Sans-Serif Font**: **Inter** (via Google Fonts) - used for body copy, numbers, and dense data layouts due to high legibility.
- **Display/Header Font**: **Outfit** - used for titles, page headings, and metric counters to give a clean, premium modern feel.
- **Font Sizes**:
  - `h1`: 2.25rem (36px) | Bold
  - `h2`: 1.5rem (24px) | Semi-Bold
  - `h3`: 1.25rem (20px) | Medium
  - `body`: 0.875rem (14px) | Regular
  - `caption`: 0.75rem (12px) | Regular / Muted

---

## 2. Layout & UI Framework

### 2.1 Glassmorphism & Cards
All container cards implement a distinct frosted-glass effect to convey high technical sophistication:
- **Tailwind Class Blueprint**: 
  `bg-[#0c1020]/45 backdrop-blur-md border border-[#232a42]/60 rounded-xl shadow-lg shadow-[#02040a]/50`
- **Hover Micro-Animations**:
  Scale on hover (`scale-[1.01]`), transition duration (`duration-300`), border color shifting (`hover:border-blue-500/50`).

### 2.2 Global Dashboard Layout
- **Sidebar**: Fixed thin navigation panel (collapsible) containing system status metrics and icon links.
- **Main View**: Grid-based workspace. Layout structures adjust between 3 columns for analysts (interactive map, trend charts, list) and 2 columns for investigators (conversational chatbot + map/graph visualization).
- **Command Palette**: Triggered by `Ctrl+K`. Floating glass modal allowing instant search of Case IDs, Accused Names, or navigation triggers.

---

## 3. Interactive Visualization Guidelines

### 3.1 Geospatial Maps (Leaflet / MapLibre)
- **Map Base Tile**: Dark matter vector tiles (e.g. CartoDB Dark Matter) to avoid blinding the user and to make hotspots stand out.
- **Hotspot Heatmap**: Dynamic canvas layer overlaying coordinate density. Grid clusters use radial gradients shifting from green (low density) to pulsing red-yellow (high-density hotspots).
- **Geofences**: High-risk crime zones bounded by semi-transparent red polygons (`fillColor: '#ef4444', fillOpacity: 0.15, color: '#ef4444'`).

### 3.2 Relational Networks (React Flow)
- **Suspect Nodes**: Dark-slate rounded capsules containing suspect avatar placeholder, name, and risk score indicator.
- **Case Nodes**: Circular icons color-coded by the Crime Major Head category.
- **Edges (Links)**:
  - Phone call linkages: Thin solid blue lines with directional arrows. Thickness correlates to call frequency.
  - Financial linkages: Green dashed lines labeled with transaction amounts.
- **Layouting**: Force-directed layout engine (via `d3-force`) to automatically organize clusters, pulling connected suspects together and separating independent entities.

### 3.3 Analytics Charts (Apache ECharts)
- Global dark theme configuration matching the background colors.
- Tooltips designed with absolute backdrop blur.
- Smooth transitions enabled during data filter changes or district drill-downs.
