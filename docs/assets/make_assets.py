import os

ASSETS_DIR = r"docs/assets"
os.makedirs(ASSETS_DIR, exist_ok=True)

def write_svg(filename, content):
    path = os.path.join(ASSETS_DIR, filename)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content.strip() + "\n")
    print(f"Generated: {path} ({len(content)} bytes)")

# ==============================================================================
# 1. HERO BANNER SVG (1200 x 480)
# ==============================================================================
HERO_BANNER_SVG = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 480" width="100%" height="100%">
  <defs>
    <linearGradient id="h-bg" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#060911"/>
      <stop offset="50%" stop-color="#0c1427"/>
      <stop offset="100%" stop-color="#050812"/>
    </linearGradient>

    <radialGradient id="h-glow-cyan" cx="18%" cy="50%" r="45%">
      <stop offset="0%" stop-color="#38bdf8" stop-opacity="0.18"/>
      <stop offset="100%" stop-color="#38bdf8" stop-opacity="0"/>
    </radialGradient>
    <radialGradient id="h-glow-emerald" cx="82%" cy="50%" r="45%">
      <stop offset="0%" stop-color="#10b981" stop-opacity="0.18"/>
      <stop offset="100%" stop-color="#10b981" stop-opacity="0"/>
    </radialGradient>
    <radialGradient id="h-glow-amber" cx="50%" cy="85%" r="35%">
      <stop offset="0%" stop-color="#f59e0b" stop-opacity="0.16"/>
      <stop offset="100%" stop-color="#f59e0b" stop-opacity="0"/>
    </radialGradient>
    <radialGradient id="h-glow-purple" cx="50%" cy="45%" r="40%">
      <stop offset="0%" stop-color="#a855f7" stop-opacity="0.22"/>
      <stop offset="100%" stop-color="#a855f7" stop-opacity="0"/>
    </radialGradient>

    <linearGradient id="h-card-cam" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#0c2340"/>
      <stop offset="100%" stop-color="#081426"/>
    </linearGradient>
    <linearGradient id="h-card-lidar" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#062e24"/>
      <stop offset="100%" stop-color="#051c17"/>
    </linearGradient>
    <linearGradient id="h-card-imu" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#332205"/>
      <stop offset="100%" stop-color="#1c1303"/>
    </linearGradient>
    <linearGradient id="h-card-fusion" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#2a124d"/>
      <stop offset="100%" stop-color="#150a2b"/>
    </linearGradient>

    <linearGradient id="h-neon-cyan" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="#38bdf8"/>
      <stop offset="100%" stop-color="#0284c7"/>
    </linearGradient>
    <linearGradient id="h-neon-emerald" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="#34d399"/>
      <stop offset="100%" stop-color="#059669"/>
    </linearGradient>
    <linearGradient id="h-neon-amber" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="#fbbf24"/>
      <stop offset="100%" stop-color="#d97706"/>
    </linearGradient>
    <linearGradient id="h-neon-purple" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="#c084fc"/>
      <stop offset="100%" stop-color="#9333ea"/>
    </linearGradient>

    <filter id="h-shadow" x="-10%" y="-10%" width="120%" height="120%">
      <feDropShadow dx="0" dy="8" stdDeviation="12" flood-color="#000000" flood-opacity="0.65"/>
    </filter>
    <filter id="h-glow-c" x="-20%" y="-20%" width="140%" height="140%">
      <feGaussianBlur stdDeviation="4" result="blur"/>
      <feComposite in="SourceGraphic" in2="blur" operator="over"/>
    </filter>
    <filter id="h-glow-e" x="-20%" y="-20%" width="140%" height="140%">
      <feGaussianBlur stdDeviation="4" result="blur"/>
      <feComposite in="SourceGraphic" in2="blur" operator="over"/>
    </filter>
    <filter id="h-glow-p" x="-20%" y="-20%" width="140%" height="140%">
      <feGaussianBlur stdDeviation="6" result="blur"/>
      <feComposite in="SourceGraphic" in2="blur" operator="over"/>
    </filter>

    <pattern id="h-grid" width="40" height="40" patternUnits="userSpaceOnUse">
      <path d="M 40 0 L 0 0 0 40" fill="none" stroke="#1e293b" stroke-width="0.75" stroke-opacity="0.45"/>
    </pattern>
  </defs>

  <style>
    .h-title { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; font-weight: 800; letter-spacing: -0.5px; }
    .h-subtitle { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; font-weight: 400; fill: #94a3b8; }
    .h-mono { font-family: 'SF Mono', Monaco, Consolas, 'Liberation Mono', monospace; }
    .h-hud { font-family: 'SF Mono', Monaco, Consolas, monospace; font-size: 10px; fill: #64748b; letter-spacing: 1.5px; }
    .h-card-head { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; font-weight: 700; font-size: 15px; }
    .h-card-text { font-family: 'SF Mono', Monaco, Consolas, monospace; font-size: 11px; fill: #94a3b8; }
    .h-metric { font-family: 'SF Mono', Monaco, Consolas, monospace; font-weight: 700; font-size: 16px; }

    @keyframes h-pulse-flow {
      0% { stroke-dashoffset: 80; }
      100% { stroke-dashoffset: 0; }
    }
    @keyframes h-ping {
      0% { r: 4px; opacity: 0.9; }
      100% { r: 18px; opacity: 0; }
    }
    .h-flow { stroke-dasharray: 6 6; animation: h-pulse-flow 2s linear infinite; }
    .h-ping-circ { animation: h-ping 2s cubic-bezier(0, 0, 0.2, 1) infinite; }
  </style>

  <!-- Background Base -->
  <rect width="1200" height="480" fill="url(#h-bg)"/>
  <rect width="1200" height="480" fill="url(#h-grid)"/>

  <!-- Glow Sprites -->
  <rect width="1200" height="480" fill="url(#h-glow-cyan)"/>
  <rect width="1200" height="480" fill="url(#h-glow-emerald)"/>
  <rect width="1200" height="480" fill="url(#h-glow-amber)"/>
  <rect width="1200" height="480" fill="url(#h-glow-purple)"/>

  <!-- Top Status Bar -->
  <g transform="translate(60, 36)">
    <line x1="0" y1="0" x2="1080" y2="0" stroke="#1e293b" stroke-width="1"/>
    
    <!-- Left Tag -->
    <rect x="0" y="-12" width="220" height="24" rx="4" fill="#0f172a" stroke="#38bdf8" stroke-width="1"/>
    <circle cx="14" cy="0" r="4" fill="#38bdf8" filter="url(#h-glow-c)"/>
    <text x="28" y="4" class="h-mono" font-size="10" font-weight="600" fill="#38bdf8" letter-spacing="1">RESEARCH PROTOCOL v1.0</text>

    <!-- Right Tag -->
    <rect x="860" y="-12" width="220" height="24" rx="4" fill="#0f172a" stroke="#10b981" stroke-width="1"/>
    <circle cx="876" cy="0" r="4" fill="#10b981" filter="url(#h-glow-e)"/>
    <text x="890" y="4" class="h-mono" font-size="10" font-weight="600" fill="#10b981" letter-spacing="1">CARLA 0.9.16 • 20 HZ SYNC</text>
  </g>

  <!-- Main Hero Titles -->
  <g transform="translate(600, 96)" text-anchor="middle">
    <text y="0" class="h-title" font-size="27" fill="#f8fafc">
      IMU-Assisted Temporal Reliability-Aware Sensor Fusion
    </text>
    <text y="30" class="h-title" font-size="21" fill="#38bdf8" filter="url(#h-glow-c)">
      Robust Multimodal Autonomous-Driving Perception
    </text>
    <text y="58" class="h-subtitle" font-size="13.5">
      Closed-loop perception dynamically balancing RGB Camera, 64-Beam LiDAR, and 6-DoF IMU under continuous environmental degradation
    </text>
  </g>

  <!-- Animated Signal Connectors -->
  <g fill="none" stroke-width="2">
    <!-- Camera to Fusion Core -->
    <path d="M 285 285 C 380 285, 410 285, 465 285" stroke="#38bdf8" stroke-opacity="0.75" class="h-flow"/>
    <!-- LiDAR to Fusion Core -->
    <path d="M 915 285 C 820 285, 790 285, 735 285" stroke="#34d399" stroke-opacity="0.75" class="h-flow"/>
    <!-- IMU to Fusion Core -->
    <path d="M 600 395 L 600 365" stroke="#fbbf24" stroke-opacity="0.8" class="h-flow"/>
    <!-- Cross-Modal Arc -->
    <path d="M 285 235 C 450 170, 750 170, 915 235" stroke="#8b5cf6" stroke-width="1.5" stroke-dasharray="4 4" stroke-opacity="0.45"/>
  </g>

  <!-- SENSOR CARD 1: CAMERA (LEFT) -->
  <g transform="translate(70, 205)" filter="url(#h-shadow)">
    <rect width="215" height="160" rx="10" fill="url(#h-card-cam)" stroke="url(#h-neon-cyan)" stroke-width="1.5"/>
    <rect x="0" y="0" width="215" height="3" fill="#38bdf8" rx="1.5"/>
    
    <g transform="translate(16, 22)">
      <circle cx="12" cy="10" r="14" fill="#0284c7" fill-opacity="0.2"/>
      <path d="M 6 5 L 18 5 L 20 8 L 22 8 C 23.1 8 24 8.9 24 10 L 24 18 C 24 19.1 23.1 20 22 20 L 2 20 C 0.9 20 0 19.1 0 18 L 0 10 C 0 8.9 0.9 8 2 8 L 4 8 Z M 12 17 C 14.2 17 16 15.2 16 13 C 16 10.8 14.2 9 12 9 C 9.8 9 8 10.8 8 13 C 8 15.2 9.8 17 12 17 Z" fill="#38bdf8"/>
      <text x="32" y="15" class="h-card-head" fill="#38bdf8">RGB CAMERA</text>
    </g>

    <text x="16" y="65" class="h-hud">STREAM METRICS</text>
    <text x="16" y="83" class="h-card-text">800 × 600 px • 90° FOV</text>
    <text x="16" y="101" class="h-card-text">YOLOv8 2D Semantics</text>
    <text x="16" y="119" class="h-card-text">Laplacian Sharpness (ψ)</text>

    <rect x="16" y="132" width="183" height="18" rx="4" fill="#091a2e"/>
    <circle cx="27" cy="141" r="3.5" fill="#38bdf8"/>
    <text x="38" y="145" class="h-mono" font-size="9.5" fill="#38bdf8" font-weight="600">R_cam: 0.01 – 0.99</text>
  </g>

  <!-- SENSOR CARD 2: LIDAR (RIGHT) -->
  <g transform="translate(915, 205)" filter="url(#h-shadow)">
    <rect width="215" height="160" rx="10" fill="url(#h-card-lidar)" stroke="url(#h-neon-emerald)" stroke-width="1.5"/>
    <rect x="0" y="0" width="215" height="3" fill="#34d399" rx="1.5"/>

    <g transform="translate(16, 22)">
      <circle cx="12" cy="10" r="14" fill="#059669" fill-opacity="0.2"/>
      <path d="M 12 2 C 6.5 2 2 6.5 2 12 L 5 12 C 5 8.1 8.1 5 12 5 Z M 12 8 C 9.8 8 8 9.8 8 12 L 10 12 C 10 10.9 10.9 10 12 10 Z M 12 14 C 10.9 14 10 13.1 10 12 L 14 12 C 14 13.1 13.1 14 12 14 Z M 19 12 C 19 8.1 15.9 5 12 5 L 12 2 C 17.5 2 22 6.5 22 12 Z" fill="#34d399"/>
      <text x="32" y="15" class="h-card-head" fill="#34d399">64-BEAM LiDAR</text>
    </g>

    <text x="16" y="65" class="h-hud">STREAM METRICS</text>
    <text x="16" y="83" class="h-card-text">64 Channels • 20 Hz Spin</text>
    <text x="16" y="101" class="h-card-text">RANSAC Ground Removal</text>
    <text x="16" y="119" class="h-card-text">Euclidean DBSCAN 3D</text>

    <rect x="16" y="132" width="183" height="18" rx="4" fill="#04221a"/>
    <circle cx="27" cy="141" r="3.5" fill="#34d399"/>
    <text x="38" y="145" class="h-mono" font-size="9.5" fill="#34d399" font-weight="600">R_lidar: 1/d Calibrated</text>
  </g>

  <!-- SENSOR CARD 3: IMU (BOTTOM CENTER) -->
  <g transform="translate(470, 385)" filter="url(#h-shadow)">
    <rect width="260" height="80" rx="8" fill="url(#h-card-imu)" stroke="url(#h-neon-amber)" stroke-width="1.5"/>
    <rect x="0" y="0" width="260" height="3" fill="#fbbf24" rx="1.5"/>

    <g transform="translate(16, 18)">
      <circle cx="10" cy="8" r="12" fill="#d97706" fill-opacity="0.2"/>
      <path d="M 10 0 L 13 6 L 20 7 L 15 12 L 16 19 L 10 16 L 4 19 L 5 12 L 0 7 L 7 6 Z" fill="#fbbf24" transform="scale(0.8)"/>
      <text x="28" y="12" class="h-card-head" fill="#fbbf24">6-DoF IMU TELEMETRY</text>
    </g>

    <text x="16" y="48" class="h-card-text">Gravity Isolation: a_lin = [fx, fy, fz - 9.81]</text>
    <text x="16" y="66" class="h-card-text">SE(3) Point-Cloud Warping: p(t-1 → t)</text>
  </g>

  <!-- CENTRAL FUSION ENGINE CARD -->
  <g transform="translate(465, 185)" filter="url(#h-shadow)">
    <rect width="270" height="180" rx="12" fill="url(#h-card-fusion)" stroke="url(#h-neon-purple)" stroke-width="2"/>
    <rect x="0" y="0" width="270" height="4" fill="#c084fc" rx="2"/>

    <g transform="translate(135, 38)">
      <circle cx="0" cy="0" r="26" fill="#9333ea" fill-opacity="0.22" filter="url(#h-glow-p)"/>
      <circle cx="0" cy="0" r="15" fill="#7e22ce" stroke="#c084fc" stroke-width="1.5"/>
      <circle cx="0" cy="0" r="5" fill="#f8fafc"/>
      <circle cx="0" cy="0" r="16" fill="none" stroke="#a855f7" stroke-width="1.5" class="h-ping-circ"/>
    </g>

    <text x="135" y="80" text-anchor="middle" class="h-card-head" fill="#e9d5ff" font-size="16">ADAPTIVE FUSION</text>
    <text x="135" y="98" text-anchor="middle" class="h-mono" font-size="10" font-weight="600" fill="#c084fc" letter-spacing="1">DYNAMIC RELIABILITY CORE</text>

    <!-- Verified Metric Callouts -->
    <g transform="translate(16, 114)">
      <rect width="112" height="50" rx="6" fill="#1b0c36" stroke="#9333ea" stroke-width="0.75"/>
      <text x="8" y="16" class="h-hud">MAE REDUCTION</text>
      <text x="8" y="38" class="h-metric" fill="#34d399">-7.88%</text>

      <rect x="126" width="112" height="50" rx="6" fill="#1b0c36" stroke="#9333ea" stroke-width="0.75"/>
      <text x="134" y="16" class="h-hud">JITTER REDUCTION</text>
      <text x="134" y="38" class="h-metric" fill="#38bdf8">-39.48%</text>
    </g>
  </g>

  <!-- Bottom Legend -->
  <g transform="translate(600, 470)" text-anchor="middle">
    <text class="h-card-text" fill="#64748b" font-size="10.5">
      w_cam(t) + w_lidar(t) = 1.0  •  α = 0.65 Hysteresis Filter  •  Δt = 0.05s Synchronous Step  •  min_hits ≥ 2 Temporal Gate
    </text>
  </g>
</svg>"""

write_svg("hero-banner.svg", HERO_BANNER_SVG)

# ==============================================================================
# 2. DATA FLOW SVG (1100 x 220)
# ==============================================================================
DATA_FLOW_SVG = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1100 220" width="100%" height="100%">
  <defs>
    <linearGradient id="df-bg" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#070b14"/>
      <stop offset="100%" stop-color="#0d1527"/>
    </linearGradient>
    <linearGradient id="df-card" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%" stop-color="#141e33"/>
      <stop offset="100%" stop-color="#0b1220"/>
    </linearGradient>
    <filter id="df-glow" x="-20%" y="-20%" width="140%" height="140%">
      <feDropShadow dx="0" dy="4" stdDeviation="6" flood-color="#000000" flood-opacity="0.5"/>
    </filter>
  </defs>

  <style>
    .df-title { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; font-size: 11px; font-weight: 700; fill: #f8fafc; }
    .df-sub { font-family: 'SF Mono', Monaco, monospace; font-size: 9px; fill: #94a3b8; }
    .df-step { font-family: 'SF Mono', Monaco, monospace; font-size: 8.5px; font-weight: 600; fill: #38bdf8; }
  </style>

  <rect width="1100" height="220" rx="8" fill="url(#df-bg)" stroke="#1e293b" stroke-width="1"/>

  <text x="40" y="32" font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif" font-size="13" font-weight="700" fill="#f8fafc">
    END-TO-END PERCEPTION DATA FLOW PIPELINE
  </text>
  <text x="40" y="48" font-family="'SF Mono', Monaco, monospace" font-size="10" fill="#64748b">
    Sequential execution loop operating at 20 Hz synchronous lockstep (Δt = 0.05 s) in CARLA 0.9.16
  </text>

  <!-- Stage 1: Acquisition -->
  <g transform="translate(40, 75)" filter="url(#df-glow)">
    <rect width="140" height="110" rx="6" fill="url(#df-card)" stroke="#38bdf8" stroke-width="1.2"/>
    <rect x="0" y="0" width="140" height="3" fill="#38bdf8" rx="1.5"/>
    <text x="12" y="20" class="df-step">STAGE 01</text>
    <text x="12" y="38" class="df-title">Synchronous Sense</text>
    <text x="12" y="56" class="df-sub">• RGB Camera (800x600)</text>
    <text x="12" y="72" class="df-sub">• 64-Beam LiDAR (20Hz)</text>
    <text x="12" y="88" class="df-sub">• 6-DoF IMU Telemetry</text>
  </g>
  <path d="M 185 130 L 210 130" stroke="#38bdf8" stroke-width="1.5" stroke-dasharray="3 3"/>
  <polygon points="212,130 205,126 205,134" fill="#38bdf8"/>

  <!-- Stage 2: Single Modality -->
  <g transform="translate(215, 75)" filter="url(#df-glow)">
    <rect width="140" height="110" rx="6" fill="url(#df-card)" stroke="#34d399" stroke-width="1.2"/>
    <rect x="0" y="0" width="140" height="3" fill="#34d399" rx="1.5"/>
    <text x="12" y="20" class="df-step" fill="#34d399">STAGE 02</text>
    <text x="12" y="38" class="df-title">Unimodal Extract</text>
    <text x="12" y="56" class="df-sub">• YOLOv8 2D BBoxes</text>
    <text x="12" y="72" class="df-sub">• RANSAC Ground Cut</text>
    <text x="12" y="88" class="df-sub">• DBSCAN 3D Clusters</text>
  </g>
  <path d="M 360 130 L 385 130" stroke="#34d399" stroke-width="1.5" stroke-dasharray="3 3"/>
  <polygon points="387,130 380,126 380,134" fill="#34d399"/>

  <!-- Stage 3: IMU Warping -->
  <g transform="translate(390, 75)" filter="url(#df-glow)">
    <rect width="140" height="110" rx="6" fill="url(#df-card)" stroke="#fbbf24" stroke-width="1.2"/>
    <rect x="0" y="0" width="140" height="3" fill="#fbbf24" rx="1.5"/>
    <text x="12" y="20" class="df-step" fill="#fbbf24">STAGE 03</text>
    <text x="12" y="38" class="df-title">IMU SE(3) Warping</text>
    <text x="12" y="56" class="df-sub">• Gravity a_lin extract</text>
    <text x="12" y="72" class="df-sub">• ΔR in SO(3) integrate</text>
    <text x="12" y="88" class="df-sub">• Warps p(t-1 → t)</text>
  </g>
  <path d="M 535 130 L 560 130" stroke="#fbbf24" stroke-width="1.5" stroke-dasharray="3 3"/>
  <polygon points="562,130 555,126 555,134" fill="#fbbf24"/>

  <!-- Stage 4: Spatial & Temporal -->
  <g transform="translate(565, 75)" filter="url(#df-glow)">
    <rect width="140" height="110" rx="6" fill="url(#df-card)" stroke="#818cf8" stroke-width="1.2"/>
    <rect x="0" y="0" width="140" height="3" fill="#818cf8" rx="1.5"/>
    <text x="12" y="20" class="df-step" fill="#818cf8">STAGE 04</text>
    <text x="12" y="38" class="df-title">Cross-Modal &amp; Track</text>
    <text x="12" y="56" class="df-sub">• 3D-to-2D via Matrix K</text>
    <text x="12" y="72" class="df-sub">• Hungarian IoU Match</text>
    <text x="12" y="88" class="df-sub">• Kalman min_hits ≥ 2</text>
  </g>
  <path d="M 710 130 L 735 130" stroke="#818cf8" stroke-width="1.5" stroke-dasharray="3 3"/>
  <polygon points="737,130 730,126 730,134" fill="#818cf8"/>

  <!-- Stage 5: Reliability -->
  <g transform="translate(740, 75)" filter="url(#df-glow)">
    <rect width="140" height="110" rx="6" fill="url(#df-card)" stroke="#c084fc" stroke-width="1.2"/>
    <rect x="0" y="0" width="140" height="3" fill="#c084fc" rx="1.5"/>
    <text x="12" y="20" class="df-step" fill="#c084fc">STAGE 05</text>
    <text x="12" y="38" class="df-title">Reliability Engine</text>
    <text x="12" y="56" class="df-sub">• Laplacian Sharpness</text>
    <text x="12" y="72" class="df-sub">• Range Density (1/d)</text>
    <text x="12" y="88" class="df-sub">• Agitation Penalty</text>
  </g>
  <path d="M 885 130 L 910 130" stroke="#c084fc" stroke-width="1.5" stroke-dasharray="3 3"/>
  <polygon points="912,130 905,126 905,134" fill="#c084fc"/>

  <!-- Stage 6: Adaptive Fusion Output -->
  <g transform="translate(915, 75)" filter="url(#df-glow)">
    <rect width="145" height="110" rx="6" fill="url(#df-card)" stroke="#f43f5e" stroke-width="1.5"/>
    <rect x="0" y="0" width="145" height="3" fill="#f43f5e" rx="1.5"/>
    <text x="12" y="20" class="df-step" fill="#f43f5e">STAGE 06</text>
    <text x="12" y="38" class="df-title">Adaptive Fusion</text>
    <text x="12" y="56" class="df-sub">• Hysteresis α = 0.65</text>
    <text x="12" y="72" class="df-sub">• Health &amp; Trend Deriv</text>
    <text x="12" y="88" class="df-sub" font-weight="700" fill="#f8fafc">→ Fused 3D Obstacles</text>
  </g>
</svg>"""

write_svg("data-flow.svg", DATA_FLOW_SVG)

# ==============================================================================
# 3. SENSOR SCENE SVG (1050 x 480)
# ==============================================================================
SENSOR_SCENE_SVG = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1050 480" width="100%" height="100%">
  <defs>
    <linearGradient id="sc-bg" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#070b14"/>
      <stop offset="100%" stop-color="#0b1222"/>
    </linearGradient>
    <linearGradient id="sc-card" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%" stop-color="#111c33"/>
      <stop offset="100%" stop-color="#0b1324"/>
    </linearGradient>
    <pattern id="sc-road-grid" width="40" height="25" patternUnits="userSpaceOnUse">
      <path d="M 40 0 L 0 0 0 25" fill="none" stroke="#1e293b" stroke-width="0.8" stroke-opacity="0.6"/>
    </pattern>
    <radialGradient id="sc-cam-cone" cx="15%" cy="50%" r="80%">
      <stop offset="0%" stop-color="#38bdf8" stop-opacity="0.3"/>
      <stop offset="100%" stop-color="#38bdf8" stop-opacity="0.02"/>
    </radialGradient>
    <radialGradient id="sc-lidar-rings" cx="50%" cy="50%" r="50%">
      <stop offset="0%" stop-color="#10b981" stop-opacity="0.25"/>
      <stop offset="100%" stop-color="#10b981" stop-opacity="0"/>
    </radialGradient>
  </defs>

  <style>
    .sc-title { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; font-size: 13px; font-weight: 700; fill: #f8fafc; }
    .sc-sub { font-family: 'SF Mono', Monaco, monospace; font-size: 10px; fill: #94a3b8; }
    .sc-legend-title { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; font-size: 11px; font-weight: 700; }
    .sc-legend-desc { font-family: 'SF Mono', Monaco, monospace; font-size: 9.5px; fill: #94a3b8; }
  </style>

  <rect width="1050" height="480" rx="8" fill="url(#sc-bg)" stroke="#1e293b" stroke-width="1"/>

  <!-- Top Title Bar -->
  <text x="40" y="32" class="sc-title">EGO-VEHICLE MULTIMODAL PERCEPTION FIELD &amp; EXTRINSICS</text>
  <text x="40" y="48" class="sc-sub">CARLA Unreal Engine Left-Handed Coordinate Frame (+X Forward, +Y Right, +Z Up)</text>

  <!-- Left: Perspective 3D Perception Scene (620 wide) -->
  <g transform="translate(40, 75)">
    <!-- Ground / Road plane -->
    <polygon points="0,320 180,90 440,90 620,320" fill="#080f1e" stroke="#1e293b" stroke-width="1"/>
    
    <!-- Perspective Grid lines -->
    <line x1="180" y1="90" x2="0" y2="320" stroke="#1e293b" stroke-width="0.8"/>
    <line x1="245" y1="90" x2="155" y2="320" stroke="#1e293b" stroke-width="0.8"/>
    <line x1="310" y1="90" x2="310" y2="320" stroke="#334155" stroke-dasharray="8 6" stroke-width="1.5"/>
    <line x1="375" y1="90" x2="465" y2="320" stroke="#1e293b" stroke-width="0.8"/>
    <line x1="440" y1="90" x2="620" y2="320" stroke="#1e293b" stroke-width="0.8"/>

    <line x1="140" y1="140" x2="480" y2="140" stroke="#1e293b" stroke-width="0.8"/>
    <line x1="90" y1="200" x2="530" y2="200" stroke="#1e293b" stroke-width="0.8"/>
    <line x1="40" y1="260" x2="580" y2="260" stroke="#1e293b" stroke-width="0.8"/>

    <!-- LiDAR Concentric Scan Rings (Emerald) -->
    <ellipse cx="310" cy="285" rx="140" ry="35" fill="none" stroke="#10b981" stroke-width="1" stroke-opacity="0.4" stroke-dasharray="4 4"/>
    <ellipse cx="310" cy="285" rx="220" ry="55" fill="none" stroke="#10b981" stroke-width="1" stroke-opacity="0.3" stroke-dasharray="6 4"/>
    <ellipse cx="310" cy="285" rx="290" ry="75" fill="none" stroke="#10b981" stroke-width="1" stroke-opacity="0.2" stroke-dasharray="8 4"/>

    <!-- Camera FOV Frustum (Cyan Cone 90°) -->
    <polygon points="310,270 120,90 500,90" fill="url(#sc-cam-cone)" stroke="#38bdf8" stroke-width="1.5" stroke-opacity="0.7"/>
    <line x1="310" y1="270" x2="120" y2="90" stroke="#38bdf8" stroke-width="1.2" stroke-dasharray="4 2"/>
    <line x1="310" y1="270" x2="500" y2="90" stroke="#38bdf8" stroke-width="1.2" stroke-dasharray="4 2"/>
    <text x="310" y="105" text-anchor="middle" font-family="'SF Mono', Monaco, monospace" font-size="9" fill="#38bdf8" font-weight="600">CAMERA FOV: 90°</text>

    <!-- Detected Target Obstacle at Range d = 18m -->
    <g transform="translate(350, 150)">
      <!-- 3D Bounding Box (LiDAR DBSCAN) -->
      <polygon points="0,35 25,25 65,25 40,35" fill="#042e20" stroke="#34d399" stroke-width="1.2"/>
      <polygon points="0,35 40,35 40,75 0,75" fill="#053e2c" stroke="#34d399" stroke-width="1.2"/>
      <polygon points="40,35 65,25 65,65 40,75" fill="#03261a" stroke="#34d399" stroke-width="1.2"/>
      
      <!-- 2D Projected Bounding Box (Camera YOLOv8) -->
      <rect x="-4" y="20" width="73" height="58" rx="2" fill="none" stroke="#38bdf8" stroke-width="1.5" stroke-dasharray="3 2"/>
      <rect x="-4" y="8" width="60" height="12" rx="2" fill="#0369a1"/>
      <text x="-1" y="17" font-family="'SF Mono', Monaco, monospace" font-size="7.5" fill="#f8fafc" font-weight="700">VEHICLE 0.94</text>
      
      <!-- Spatial IoU Indicator -->
      <text x="75" y="48" font-family="'SF Mono', Monaco, monospace" font-size="8" fill="#c084fc">IoU: 0.82</text>
      <line x1="40" y1="48" x2="72" y2="48" stroke="#c084fc" stroke-width="1"/>
    </g>

    <!-- Ego Vehicle Body (Center Bottom) -->
    <g transform="translate(270, 260)">
      <!-- Vehicle Chassis Base -->
      <rect x="0" y="10" width="80" height="40" rx="8" fill="#1e293b" stroke="#475569" stroke-width="1.5"/>
      <rect x="15" y="0" width="50" height="30" rx="5" fill="#0f172a" stroke="#38bdf8" stroke-width="1"/>
      
      <!-- Sensor Mounting Nodes on Ego -->
      <!-- Camera Node: [1.5, 0.0, 2.4] -->
      <circle cx="40" cy="5" r="4.5" fill="#38bdf8"/>
      <text x="40" y="-3" text-anchor="middle" font-family="'SF Mono', Monaco, monospace" font-size="7.5" fill="#38bdf8" font-weight="700">CAM [1.5, 0, 2.4]</text>

      <!-- LiDAR Node: [0.0, 0.0, 2.5] -->
      <circle cx="40" cy="18" r="4.5" fill="#34d399"/>
      <text x="95" y="22" font-family="'SF Mono', Monaco, monospace" font-size="7.5" fill="#34d399" font-weight="700">LiDAR [0, 0, 2.5]</text>
      <line x1="45" y1="18" x2="90" y2="18" stroke="#34d399" stroke-width="0.8"/>

      <!-- IMU Node: [0.0, 0.0, 2.0] -->
      <circle cx="40" cy="32" r="4" fill="#fbbf24"/>
      <text x="-35" y="35" font-family="'SF Mono', Monaco, monospace" font-size="7.5" fill="#fbbf24" font-weight="700">IMU [0, 0, 2.0]</text>
      <line x1="35" y1="32" x2="-5" y2="32" stroke="#fbbf24" stroke-width="0.8"/>

      <!-- 6-DoF Axis Triad -->
      <g transform="translate(40, 32)">
        <line x1="0" y1="0" x2="0" y2="-18" stroke="#fbbf24" stroke-width="1.5"/>
        <polygon points="0,-20 -3,-15 3,-15" fill="#fbbf24"/>
        <line x1="0" y1="0" x2="18" y2="0" stroke="#ef4444" stroke-width="1.5"/>
        <polygon points="20,0 15,-3 15,3" fill="#ef4444"/>
      </g>
    </g>
  </g>

  <!-- Right: Sensor Specifications & Extrinsics Cards (340 wide) -->
  <g transform="translate(680, 75)">
    <!-- Card 1: Camera -->
    <g transform="translate(0, 0)">
      <rect width="330" height="95" rx="6" fill="url(#sc-card)" stroke="#38bdf8" stroke-width="1"/>
      <rect x="0" y="0" width="4" height="95" fill="#38bdf8" rx="2"/>
      <circle cx="22" cy="20" r="6" fill="#0284c7"/>
      <text x="36" y="24" class="sc-legend-title" fill="#38bdf8">RGB CAMERA SPECIFICATION</text>
      <text x="16" y="44" class="sc-legend-desc">• Mounting: p_cam = [1.5, 0.0, 2.4] m</text>
      <text x="16" y="58" class="sc-legend-desc">• Intrinsics: fx = fy = 400.0 px, cx=400, cy=300</text>
      <text x="16" y="72" class="sc-legend-desc">• Resolution: 800 × 600 px, FOV: 90°</text>
      <text x="16" y="86" class="sc-legend-desc">• Model: YOLOv8 2D Semantics + Laplacian Sharpness</text>
    </g>

    <!-- Card 2: LiDAR -->
    <g transform="translate(0, 110)">
      <rect width="330" height="95" rx="6" fill="url(#sc-card)" stroke="#34d399" stroke-width="1"/>
      <rect x="0" y="0" width="4" height="95" fill="#34d399" rx="2"/>
      <circle cx="22" cy="20" r="6" fill="#059669"/>
      <text x="36" y="24" class="sc-legend-title" fill="#34d399">64-BEAM LiDAR SPECIFICATION</text>
      <text x="16" y="44" class="sc-legend-desc">• Mounting: p_lidar = [0.0, 0.0, 2.5] m</text>
      <text x="16" y="58" class="sc-legend-desc">• Extrinsic Translation: t = [1.5, 0.0, -0.1] m</text>
      <text x="16" y="72" class="sc-legend-desc">• 64 Channels, 20 Hz, ~3000 points/frame</text>
      <text x="16" y="86" class="sc-legend-desc">• Processing: RANSAC Ground Cut + DBSCAN 3D</text>
    </g>

    <!-- Card 3: IMU -->
    <g transform="translate(0, 220)">
      <rect width="330" height="95" rx="6" fill="url(#sc-card)" stroke="#fbbf24" stroke-width="1"/>
      <rect x="0" y="0" width="4" height="95" fill="#fbbf24" rx="2"/>
      <circle cx="22" cy="20" r="6" fill="#d97706"/>
      <text x="36" y="24" class="sc-legend-title" fill="#fbbf24">6-DoF IMU TELEMETRY SPECIFICATION</text>
      <text x="16" y="44" class="sc-legend-desc">• Mounting: p_imu = [0.0, 0.0, 2.0] m</text>
      <text x="16" y="58" class="sc-legend-desc">• Gravity Removal: a_linear = [fx, fy, fz - 9.81]</text>
      <text x="16" y="72" class="sc-legend-desc">• SO(3) Rotation + SE(3) Rigid Transformation</text>
      <text x="16" y="86" class="sc-legend-desc">• Vehicle Motion State Classification (6 States)</text>
    </g>
  </g>
</svg>"""

write_svg("sensor-scene.svg", SENSOR_SCENE_SVG)

# ==============================================================================
# 4. IMU MOTION COMPENSATION SVG (1100 x 500)
# ==============================================================================
IMU_MOTION_SVG = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1100 500" width="100%" height="100%">
  <defs>
    <linearGradient id="imu-bg" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#060a13"/>
      <stop offset="100%" stop-color="#0a1224"/>
    </linearGradient>
    <linearGradient id="imu-box" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%" stop-color="#121d36"/>
      <stop offset="100%" stop-color="#0b1324"/>
    </linearGradient>
  </defs>

  <style>
    .imu-title { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; font-size: 13px; font-weight: 700; fill: #f8fafc; }
    .imu-sub { font-family: 'SF Mono', Monaco, monospace; font-size: 10px; fill: #94a3b8; }
    .imu-math { font-family: 'SF Mono', Monaco, monospace; font-size: 11px; fill: #fbbf24; font-weight: 600; }
    .imu-desc { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; font-size: 11px; fill: #cbd5e1; }
    .imu-num { font-family: 'SF Mono', Monaco, monospace; font-size: 14px; font-weight: 700; }
  </style>

  <rect width="1100" height="500" rx="8" fill="url(#imu-bg)" stroke="#1e293b" stroke-width="1"/>

  <text x="40" y="32" class="imu-title">IMU EGO-MOTION COMPENSATION &amp; SE(3) POINT-CLOUD WARPING</text>
  <text x="40" y="48" class="imu-sub">Rigid-body kinematic integration over Δt = 50 ms eliminating inter-frame spatial smearing</text>

  <!-- Left: Mathematical Formulation & Kinematics (500 wide) -->
  <g transform="translate(40, 75)">
    <!-- Step 1: Specific Force Decomposition -->
    <rect width="490" height="115" rx="6" fill="url(#imu-box)" stroke="#fbbf24" stroke-width="1"/>
    <rect x="0" y="0" width="4" height="115" fill="#fbbf24" rx="2"/>
    <text x="16" y="24" class="imu-title" fill="#fbbf24">1. Specific Force Decomposition &amp; Gravity Removal</text>
    <text x="16" y="48" class="imu-math">f_measured = a_linear - g,  g = [0, 0, -9.81]^T m/s²</text>
    <text x="16" y="70" class="imu-math">a_linear = [fx,  fy,  fz - 9.81]^T m/s²</text>
    <text x="16" y="94" class="imu-desc">Recovers true vehicle acceleration by subtracting downward gravity vector in CARLA frame.</text>

    <!-- Step 2: SO(3) and SE(3) Formation -->
    <g transform="translate(0, 130)">
      <rect width="490" height="125" rx="6" fill="url(#imu-box)" stroke="#fbbf24" stroke-width="1"/>
      <rect x="0" y="0" width="4" height="125" fill="#fbbf24" rx="2"/>
      <text x="16" y="24" class="imu-title" fill="#fbbf24">2. Rigid-Body Transformation Matrix T_ego ∈ SE(3)</text>
      <text x="16" y="48" class="imu-math">ΔR = R_z(ω_z Δt) · R_y(ω_y Δt) · R_x(ω_x Δt) ∈ SO(3)</text>
      <text x="16" y="70" class="imu-math">Δt = v_{k-1} Δt + 0.5 a_linear (Δt)²</text>
      <text x="16" y="92" class="imu-math">T_ego = [ ΔR  Δt ;  0^T  1 ] ∈ SE(3)</text>
      <text x="16" y="112" class="imu-desc">Integrates high-rate gyroscope and linear acceleration over Δt = 0.05 s.</text>
    </g>

    <!-- Step 3: Point Cloud Warping Equation -->
    <g transform="translate(0, 270)">
      <rect width="490" height="110" rx="6" fill="url(#imu-box)" stroke="#38bdf8" stroke-width="1"/>
      <rect x="0" y="0" width="4" height="110" fill="#38bdf8" rx="2"/>
      <text x="16" y="24" class="imu-title" fill="#38bdf8">3. Inter-Frame Point-Cloud Warping (t-1 → t)</text>
      <text x="16" y="52" class="imu-math" fill="#38bdf8">p_{t-1 → t} = ΔR^T (p_{t-1} - Δt)</text>
      <text x="16" y="80" class="imu-desc">Transforms previous LiDAR returns into current vehicle coordinate frame, aligning dynamic historical scans with incoming observations.</text>
    </g>
  </g>

  <!-- Right: Visual Comparison & Benchmark Proof (500 wide) -->
  <g transform="translate(560, 75)">
    <!-- Diagram: Uncompensated vs Compensated Visual -->
    <rect width="500" height="235" rx="6" fill="#081022" stroke="#1e293b" stroke-width="1"/>
    <text x="20" y="26" class="imu-title">POINT-CLOUD SPATIAL REGISTRATION COMPARISON</text>

    <!-- Left Box: Uncompensated -->
    <g transform="translate(20, 45)">
      <rect width="215" height="170" rx="4" fill="#0c162d" stroke="#ef4444" stroke-width="1"/>
      <text x="12" y="20" font-family="'SF Mono', Monaco, monospace" font-size="9.5" fill="#f87171" font-weight="700">RAW (UNCOMPENSATED)</text>
      
      <!-- Ghosting points -->
      <!-- Frame t-1 points (red ghosted) -->
      <circle cx="80" cy="70" r="3" fill="#ef4444" fill-opacity="0.8"/>
      <circle cx="95" cy="65" r="3" fill="#ef4444" fill-opacity="0.8"/>
      <circle cx="110" cy="72" r="3" fill="#ef4444" fill-opacity="0.8"/>
      <circle cx="125" cy="80" r="3" fill="#ef4444" fill-opacity="0.8"/>
      <circle cx="90" cy="90" r="3" fill="#ef4444" fill-opacity="0.8"/>
      <circle cx="105" cy="85" r="3" fill="#ef4444" fill-opacity="0.8"/>

      <!-- Frame t points (white actual) -->
      <circle cx="95" cy="90" r="3" fill="#f8fafc"/>
      <circle cx="110" cy="85" r="3" fill="#f8fafc"/>
      <circle cx="125" cy="92" r="3" fill="#f8fafc"/>
      <circle cx="140" cy="100" r="3" fill="#f8fafc"/>
      <circle cx="105" cy="110" r="3" fill="#f8fafc"/>
      <circle cx="120" cy="105" r="3" fill="#f8fafc"/>

      <!-- Error Vectors -->
      <line x1="80" y1="70" x2="95" y2="90" stroke="#ef4444" stroke-width="1.2" stroke-dasharray="2 2"/>
      <line x1="95" y1="65" x2="110" y2="85" stroke="#ef4444" stroke-width="1.2" stroke-dasharray="2 2"/>
      <line x1="110" y1="72" x2="125" y2="92" stroke="#ef4444" stroke-width="1.2" stroke-dasharray="2 2"/>

      <text x="12" y="145" class="imu-sub" fill="#f87171">MAE = 0.0964 m</text>
      <text x="12" y="158" class="imu-sub" fill="#f87171">Jitter = 0.8426 m</text>
    </g>

    <!-- Right Box: IMU-Compensated -->
    <g transform="translate(265, 45)">
      <rect width="215" height="170" rx="4" fill="#0c162d" stroke="#34d399" stroke-width="1.2"/>
      <text x="12" y="20" font-family="'SF Mono', Monaco, monospace" font-size="9.5" fill="#34d399" font-weight="700">IMU-WARPED SE(3)</text>

      <!-- Perfectly aligned points -->
      <circle cx="95" cy="90" r="4.5" fill="none" stroke="#38bdf8" stroke-width="1.5"/>
      <circle cx="95" cy="90" r="2.5" fill="#34d399"/>

      <circle cx="110" cy="85" r="4.5" fill="none" stroke="#38bdf8" stroke-width="1.5"/>
      <circle cx="110" cy="85" r="2.5" fill="#34d399"/>

      <circle cx="125" cy="92" r="4.5" fill="none" stroke="#38bdf8" stroke-width="1.5"/>
      <circle cx="125" cy="92" r="2.5" fill="#34d399"/>

      <circle cx="140" cy="100" r="4.5" fill="none" stroke="#38bdf8" stroke-width="1.5"/>
      <circle cx="140" cy="100" r="2.5" fill="#34d399"/>

      <circle cx="105" cy="110" r="4.5" fill="none" stroke="#38bdf8" stroke-width="1.5"/>
      <circle cx="105" cy="110" r="2.5" fill="#34d399"/>

      <circle cx="120" cy="105" r="4.5" fill="none" stroke="#38bdf8" stroke-width="1.5"/>
      <circle cx="120" cy="105" r="2.5" fill="#34d399"/>

      <text x="12" y="145" class="imu-sub" fill="#34d399">MAE = 0.0888 m (-7.88%)</text>
      <text x="12" y="158" class="imu-sub" fill="#34d399">Jitter = 0.5099 m (-39.48%)</text>
    </g>

    <!-- Bottom 4 Quantitative Verification Cards -->
    <g transform="translate(0, 250)">
      <!-- Metric 1: MAE -->
      <rect width="118" height="130" rx="6" fill="url(#imu-box)" stroke="#1e293b" stroke-width="1"/>
      <text x="10" y="22" class="imu-sub">REGISTRATION MAE</text>
      <text x="10" y="46" class="imu-sub" fill="#94a3b8">Raw: 0.0964 m</text>
      <text x="10" y="66" class="imu-sub" fill="#f8fafc">IMU: 0.0888 m</text>
      <text x="10" y="100" class="imu-num" fill="#34d399">-7.88%</text>
      <text x="10" y="116" font-family="'SF Mono', Monaco, monospace" font-size="8.5" fill="#64748b">ERROR CUT</text>

      <!-- Metric 2: MSE -->
      <g transform="translate(127, 0)">
        <rect width="118" height="130" rx="6" fill="url(#imu-box)" stroke="#1e293b" stroke-width="1"/>
        <text x="10" y="22" class="imu-sub">REGISTRATION MSE</text>
        <text x="10" y="46" class="imu-sub" fill="#94a3b8">Raw: 0.0383 m²</text>
        <text x="10" y="66" class="imu-sub" fill="#f8fafc">IMU: 0.0315 m²</text>
        <text x="10" y="100" class="imu-num" fill="#34d399">-17.75%</text>
        <text x="10" y="116" font-family="'SF Mono', Monaco, monospace" font-size="8.5" fill="#64748b">ERROR CUT</text>
      </g>

      <!-- Metric 3: Peak Error -->
      <g transform="translate(254, 0)">
        <rect width="118" height="130" rx="6" fill="url(#imu-box)" stroke="#1e293b" stroke-width="1"/>
        <text x="10" y="22" class="imu-sub">PEAK CORRECTION</text>
        <text x="10" y="46" class="imu-sub" fill="#94a3b8">Raw: 0.4280 m²</text>
        <text x="10" y="66" class="imu-sub" fill="#f8fafc">IMU: 0.2810 m²</text>
        <text x="10" y="100" class="imu-num" fill="#38bdf8">-34.35%</text>
        <text x="10" y="116" font-family="'SF Mono', Monaco, monospace" font-size="8.5" fill="#64748b">PEAK DROP</text>
      </g>

      <!-- Metric 4: Jitter -->
      <g transform="translate(381, 0)">
        <rect width="118" height="130" rx="6" fill="url(#imu-box)" stroke="#1e293b" stroke-width="1"/>
        <text x="10" y="22" class="imu-sub">DISPLACEMENT JITTER</text>
        <text x="10" y="46" class="imu-sub" fill="#94a3b8">Raw: 0.8426 m</text>
        <text x="10" y="66" class="imu-sub" fill="#f8fafc">IMU: 0.5099 m</text>
        <text x="10" y="100" class="imu-num" fill="#c084fc">-39.48%</text>
        <text x="10" y="116" font-family="'SF Mono', Monaco, monospace" font-size="8.5" fill="#64748b">SMOOTHER</text>
      </g>
    </g>
  </g>
</svg>"""

write_svg("imu-motion-compensation.svg", IMU_MOTION_SVG)

# ==============================================================================
# 5. SPATIAL ASSOCIATION SVG (1080 x 460)
# ==============================================================================
SPATIAL_ASSOC_SVG = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1080 460" width="100%" height="100%">
  <defs>
    <linearGradient id="sa-bg" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#060911"/>
      <stop offset="100%" stop-color="#0a1223"/>
    </linearGradient>
    <linearGradient id="sa-card" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%" stop-color="#111c34"/>
      <stop offset="100%" stop-color="#0b1220"/>
    </linearGradient>
  </defs>

  <style>
    .sa-title { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; font-size: 13px; font-weight: 700; fill: #f8fafc; }
    .sa-sub { font-family: 'SF Mono', Monaco, monospace; font-size: 10px; fill: #94a3b8; }
    .sa-step { font-family: 'SF Mono', Monaco, monospace; font-size: 9px; font-weight: 600; }
    .sa-body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; font-size: 10.5px; fill: #cbd5e1; }
    .sa-math { font-family: 'SF Mono', Monaco, monospace; font-size: 10px; fill: #fbbf24; }
  </style>

  <rect width="1080" height="460" rx="8" fill="url(#sa-bg)" stroke="#1e293b" stroke-width="1"/>

  <text x="40" y="32" class="sa-title">CROSS-MODAL SPATIAL ASSOCIATION PIPELINE</text>
  <text x="40" y="48" class="sa-sub">3D LiDAR Cluster Projection via Pinhole Calibration Matrix K &amp; Hungarian 2D IoU Matching</text>

  <!-- 4 Step Pipeline Architecture -->
  <!-- Step 1: 3D LiDAR Cluster -->
  <g transform="translate(40, 75)">
    <rect width="220" height="340" rx="6" fill="url(#sa-card)" stroke="#34d399" stroke-width="1"/>
    <rect x="0" y="0" width="220" height="3" fill="#34d399" rx="1.5"/>
    <text x="16" y="24" class="sa-step" fill="#34d399">STEP 01: 3D EXTRACTION</text>
    <text x="16" y="44" class="sa-title">LiDAR 3D Cluster</text>
    
    <!-- 3D BBox Illustration -->
    <g transform="translate(40, 65)">
      <polygon points="20,20 60,10 120,10 80,20" fill="#042e20" stroke="#34d399" stroke-width="1"/>
      <polygon points="20,20 80,20 80,70 20,70" fill="#053e2c" stroke="#34d399" stroke-width="1"/>
      <polygon points="80,20 120,10 120,60 80,70" fill="#03261a" stroke="#34d399" stroke-width="1"/>
      <!-- 8 vertices -->
      <circle cx="20" cy="20" r="3" fill="#34d399"/>
      <circle cx="60" cy="10" r="3" fill="#34d399"/>
      <circle cx="120" cy="10" r="3" fill="#34d399"/>
      <circle cx="80" cy="20" r="3" fill="#34d399"/>
      <circle cx="20" cy="70" r="3" fill="#34d399"/>
      <circle cx="80" cy="70" r="3" fill="#34d399"/>
      <circle cx="120" cy="60" r="3" fill="#34d399"/>
    </g>

    <text x="16" y="170" class="sa-body">• RANSAC extracts ground</text>
    <text x="16" y="188" class="sa-body">• DBSCAN forms 3D clusters</text>
    <text x="16" y="206" class="sa-body">• Computes 8 corner vertices:</text>
    <text x="24" y="226" class="sa-math">p_k ∈ R³, k = 1..8</text>
    <text x="16" y="254" class="sa-body">• 3D Centroid (x, y, z)</text>
    <text x="16" y="272" class="sa-body">• Volume (dx, dy, dz)</text>
  </g>

  <!-- Arrow 1 to 2 -->
  <path d="M 270 245 L 295 245" stroke="#34d399" stroke-width="1.5" stroke-dasharray="3 3"/>
  <polygon points="298,245 291,241 291,249" fill="#34d399"/>

  <!-- Step 2: Perspective Projection K -->
  <g transform="translate(305, 75)">
    <rect width="220" height="340" rx="6" fill="url(#sa-card)" stroke="#fbbf24" stroke-width="1"/>
    <rect x="0" y="0" width="220" height="3" fill="#fbbf24" rx="1.5"/>
    <text x="16" y="24" class="sa-step" fill="#fbbf24">STEP 02: PROJECTION K</text>
    <text x="16" y="44" class="sa-title">Optical Perspective</text>

    <!-- Calibration Equation Box -->
    <g transform="translate(14, 65)">
      <rect width="192" height="85" rx="4" fill="#181305" stroke="#d97706" stroke-width="0.8"/>
      <text x="10" y="20" class="sa-math">K = [ 400.0   0.0  400.0 ]</text>
      <text x="10" y="38" class="sa-math">    [   0.0 400.0  300.0 ]</text>
      <text x="10" y="56" class="sa-math">    [   0.0   0.0    1.0 ]</text>
      <text x="10" y="74" class="sa-math" fill="#38bdf8">u_k = π( K · [ R_opt p_k + t ] )</text>
    </g>

    <text x="16" y="180" class="sa-body">• Basis transform to optical frame:</text>
    <text x="24" y="200" class="sa-math">[X_opt, Y_opt, Z_opt]^T</text>
    <text x="16" y="228" class="sa-body">• Computes 2D image envelope:</text>
    <text x="24" y="250" class="sa-math" fill="#38bdf8">B_proj = [min u, min v,</text>
    <text x="80" y="268" class="sa-math" fill="#38bdf8">max u, max v]</text>
    <text x="16" y="298" class="sa-body">• Filters frustum boundary</text>
  </g>

  <!-- Arrow 2 to 3 -->
  <path d="M 535 245 L 560 245" stroke="#fbbf24" stroke-width="1.5" stroke-dasharray="3 3"/>
  <polygon points="563,245 556,241 556,249" fill="#fbbf24"/>

  <!-- Step 3: 2D IoU Spatial Overlap -->
  <g transform="translate(570, 75)">
    <rect width="220" height="340" rx="6" fill="url(#sa-card)" stroke="#38bdf8" stroke-width="1"/>
    <rect x="0" y="0" width="220" height="3" fill="#38bdf8" rx="1.5"/>
    <text x="16" y="24" class="sa-step" fill="#38bdf8">STEP 03: 2D OVERLAP</text>
    <text x="16" y="44" class="sa-title">IoU Intersection</text>

    <!-- Visual of two overlapping boxes -->
    <g transform="translate(30, 65)">
      <!-- Projected Box (Green/dashed) -->
      <rect x="15" y="10" width="100" height="70" rx="3" fill="#042e20" fill-opacity="0.4" stroke="#34d399" stroke-width="1.5" stroke-dasharray="4 2"/>
      <text x="20" y="25" font-family="'SF Mono', Monaco, monospace" font-size="8" fill="#34d399">B_proj (LiDAR)</text>

      <!-- YOLOv8 Box (Cyan/solid) -->
      <rect x="45" y="25" width="95" height="70" rx="3" fill="#0c2340" fill-opacity="0.4" stroke="#38bdf8" stroke-width="1.5"/>
      <text x="65" y="85" font-family="'SF Mono', Monaco, monospace" font-size="8" fill="#38bdf8">B_cam (YOLO)</text>

      <!-- Overlap hatch area -->
      <rect x="45" y="25" width="70" height="55" fill="#8b5cf6" fill-opacity="0.35"/>
    </g>

    <text x="16" y="180" class="sa-body">• YOLOv8 outputs 2D box B_cam</text>
    <text x="16" y="202" class="sa-body">• Formulates IoU formula:</text>
    <text x="24" y="226" class="sa-math">IoU = Area(B_cam ∩ B_proj) /</text>
    <text x="65" y="244" class="sa-math">     Area(B_cam ∪ B_proj)</text>
    <text x="16" y="276" class="sa-body">• Cost matrix: C_ij = 1 - IoU_ij</text>
    <text x="16" y="296" class="sa-body">• Min overlap threshold = 0.10</text>
  </g>

  <!-- Arrow 3 to 4 -->
  <path d="M 800 245 L 825 245" stroke="#38bdf8" stroke-width="1.5" stroke-dasharray="3 3"/>
  <polygon points="828,245 821,241 821,249" fill="#38bdf8"/>

  <!-- Step 4: Hungarian Matching Output -->
  <g transform="translate(835, 75)">
    <rect width="205" height="340" rx="6" fill="url(#sa-card)" stroke="#c084fc" stroke-width="1.5"/>
    <rect x="0" y="0" width="205" height="3" fill="#c084fc" rx="1.5"/>
    <text x="16" y="24" class="sa-step" fill="#c084fc">STEP 04: ASSIGNMENT</text>
    <text x="16" y="44" class="sa-title">Hungarian Match</text>

    <!-- Match table visual -->
    <g transform="translate(14, 65)">
      <rect width="177" height="85" rx="4" fill="#1b0c36" stroke="#9333ea" stroke-width="0.8"/>
      <text x="10" y="20" font-family="'SF Mono', Monaco, monospace" font-size="8.5" fill="#c084fc" font-weight="700">OPTIMAL BIPARTITE MAP</text>
      <text x="10" y="40" class="sa-math" fill="#34d399">Cam_0 ↔ LiDAR_1 (0.84)</text>
      <text x="10" y="58" class="sa-math" fill="#34d399">Cam_1 ↔ LiDAR_0 (0.76)</text>
      <text x="10" y="76" class="sa-math" fill="#f43f5e">Cam_2 → Unmatched (FP)</text>
    </g>

    <text x="16" y="180" class="sa-body">• O(N³) Kuhn-Munkres solver</text>
    <text x="16" y="200" class="sa-body">• Associated pairs form fused</text>
    <text x="16" y="218" class="sa-body">  3D-2D object tracklets</text>
    <text x="16" y="246" class="sa-body">• Unmatched LiDAR →</text>
    <text x="24" y="264" class="sa-sub" fill="#34d399">LiDAR-only candidate</text>
    <text x="16" y="286" class="sa-body">• Unmatched Camera →</text>
    <text x="24" y="304" class="sa-sub" fill="#38bdf8">Camera-only candidate</text>
  </g>
</svg>"""

write_svg("spatial-association.svg", SPATIAL_ASSOC_SVG)

# ==============================================================================
# 6. TEMPORAL TRACKING SVG (1080 x 460)
# ==============================================================================
TEMPORAL_TRACKING_SVG = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1080 460" width="100%" height="100%">
  <defs>
    <linearGradient id="tt-bg" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#060912"/>
      <stop offset="100%" stop-color="#091122"/>
    </linearGradient>
    <linearGradient id="tt-box" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%" stop-color="#121b30"/>
      <stop offset="100%" stop-color="#0b1220"/>
    </linearGradient>
  </defs>

  <style>
    .tt-title { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; font-size: 13px; font-weight: 700; fill: #f8fafc; }
    .tt-sub { font-family: 'SF Mono', Monaco, monospace; font-size: 10px; fill: #94a3b8; }
    .tt-head { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; font-size: 11.5px; font-weight: 700; }
    .tt-body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; font-size: 10px; fill: #cbd5e1; }
    .tt-math { font-family: 'SF Mono', Monaco, monospace; font-size: 9.5px; fill: #818cf8; }
    .tt-stat { font-family: 'SF Mono', Monaco, monospace; font-size: 15px; font-weight: 700; }
  </style>

  <rect width="1080" height="460" rx="8" fill="url(#tt-bg)" stroke="#1e293b" stroke-width="1"/>

  <text x="40" y="32" class="tt-title">TEMPORAL MULTI-FRAME GATING &amp; IMU-WARPED KALMAN TRACKING</text>
  <text x="40" y="48" class="tt-sub">6-DoF State Estimation with Empirical Confirmation Gate (min_hits ≥ 2) Suppressing Spurious False Alarms</text>

  <!-- Left: Kalman Filter Lifecycle & Equations (500 wide) -->
  <g transform="translate(40, 75)">
    <!-- Stage 1: State Vector & Propagation -->
    <rect width="480" height="110" rx="6" fill="url(#tt-box)" stroke="#818cf8" stroke-width="1"/>
    <rect x="0" y="0" width="4" height="110" fill="#818cf8" rx="2"/>
    <text x="16" y="24" class="tt-head" fill="#818cf8">1. 6-DoF State Representation &amp; IMU Motion Propagation</text>
    <text x="16" y="46" class="tt-math">State Vector: x_t = [ x,  y,  z,  v_x,  v_y,  v_z ]^T ∈ R⁶</text>
    <text x="16" y="66" class="tt-math">Ego Warping: x_{t|t-1} = T_{ego, t}^{-1} · x_{t-1|t-1}</text>
    <text x="16" y="90" class="tt-body">Propagates existing tracklet centroids using inter-frame rigid transformation before measurement update.</text>

    <!-- Stage 2: Prediction & Update Cycle -->
    <g transform="translate(0, 125)">
      <rect width="480" height="110" rx="6" fill="url(#tt-box)" stroke="#818cf8" stroke-width="1"/>
      <rect x="0" y="0" width="4" height="110" fill="#818cf8" rx="2"/>
      <text x="16" y="24" class="tt-head" fill="#818cf8">2. Discrete Kalman Prediction &amp; Covariance Update</text>
      <text x="16" y="46" class="tt-math">Prediction: x̂_k = F x̂_{k-1},  P̂_k = F P_{k-1} F^T + Q</text>
      <text x="16" y="66" class="tt-math">Kalman Gain: K_k = P̂_k H^T ( H P̂_k H^T + R )⁻¹</text>
      <text x="16" y="88" class="tt-math">State Update: x̂_k = x̂_k + K_k ( z_k - H x̂_k ),  P_k = ( I - K_k H ) P̂_k</text>
    </g>

    <!-- Stage 3: Persistence Ratio -->
    <g transform="translate(0, 250)">
      <rect width="480" height="90" rx="6" fill="url(#tt-box)" stroke="#c084fc" stroke-width="1"/>
      <rect x="0" y="0" width="4" height="90" fill="#c084fc" rx="2"/>
      <text x="16" y="24" class="tt-head" fill="#c084fc">3. Tracklet Persistence Metric</text>
      <text x="16" y="48" class="tt-math" fill="#c084fc">τ_temp = hits / age ∈ (0, 1.0]</text>
      <text x="16" y="72" class="tt-body">Rewards temporally consistent obstacles. Transient single-frame detections have low persistence and are penalized.</text>
    </g>
  </g>

  <!-- Right: Confirmation Gate State Machine & Visual (500 wide) -->
  <g transform="translate(550, 75)">
    <rect width="490" height="340" rx="6" fill="#081022" stroke="#1e293b" stroke-width="1"/>
    <text x="20" y="26" class="tt-title">TRACKLET CONFIRMATION GATE STATE MACHINE</text>

    <!-- State 1: Tentative (hits = 1) -->
    <g transform="translate(20, 50)">
      <rect width="130" height="120" rx="6" fill="#1b1528" stroke="#f43f5e" stroke-width="1.2"/>
      <circle cx="20" cy="22" r="6" fill="#e11d48"/>
      <text x="32" y="26" font-family="'SF Mono', Monaco, monospace" font-size="9" fill="#f43f5e" font-weight="700">TENTATIVE</text>
      <text x="12" y="48" class="tt-body" fill="#f87171">• hits = 1</text>
      <text x="12" y="66" class="tt-body">• First observation</text>
      <rect x="10" y="80" width="110" height="26" rx="4" fill="#360a16"/>
      <text x="18" y="97" font-family="'SF Mono', Monaco, monospace" font-size="8" fill="#fca5a5" font-weight="700">OUTPUT: BLOCKED</text>
    </g>

    <!-- Arrow Tentative to Confirmed -->
    <path d="M 155 110 L 195 110" stroke="#34d399" stroke-width="2"/>
    <polygon points="198,110 190,105 190,115" fill="#34d399"/>
    <text x="156" y="100" font-family="'SF Mono', Monaco, monospace" font-size="7.5" fill="#34d399">hits ≥ 2</text>

    <!-- State 2: Confirmed (hits >= 2) -->
    <g transform="translate(200, 50)">
      <rect width="145" height="120" rx="6" fill="#062e24" stroke="#34d399" stroke-width="1.5"/>
      <circle cx="20" cy="22" r="6" fill="#059669"/>
      <text x="32" y="26" font-family="'SF Mono', Monaco, monospace" font-size="9" fill="#34d399" font-weight="700">CONFIRMED</text>
      <text x="12" y="48" class="tt-body" fill="#34d399">• hits ≥ 2</text>
      <text x="12" y="66" class="tt-body">• Confirmed obstacle</text>
      <rect x="10" y="80" width="125" height="26" rx="4" fill="#043d2c"/>
      <text x="16" y="97" font-family="'SF Mono', Monaco, monospace" font-size="8" fill="#a7f3d0" font-weight="700">OUTPUT: EMITTED</text>
    </g>

    <!-- Arrow Confirmed to Coasting -->
    <path d="M 350 110 L 375 110" stroke="#fbbf24" stroke-width="1.5" stroke-dasharray="3 3"/>
    <polygon points="378,110 371,106 371,114" fill="#fbbf24"/>
    <text x="352" y="100" font-family="'SF Mono', Monaco, monospace" font-size="7" fill="#fbbf24">missed</text>

    <!-- State 3: Coasting -->
    <g transform="translate(380, 50)">
      <rect width="95" height="120" rx="6" fill="#261c06" stroke="#fbbf24" stroke-width="1"/>
      <circle cx="16" cy="22" r="5" fill="#d97706"/>
      <text x="26" y="25" font-family="'SF Mono', Monaco, monospace" font-size="8" fill="#fbbf24" font-weight="700">COASTING</text>
      <text x="8" y="48" class="tt-body" fill="#fde047">• missed ≤ 3</text>
      <text x="8" y="66" class="tt-body">• Kalman pred</text>
      <rect x="6" y="80" width="83" height="26" rx="4" fill="#382806"/>
      <text x="12" y="97" font-family="'SF Mono', Monaco, monospace" font-size="7.5" fill="#fef08a">MAINTAINED</text>
    </g>

    <!-- Bottom Statistical Callout -->
    <g transform="translate(20, 195)">
      <rect width="455" height="125" rx="6" fill="#0e172a" stroke="#334155" stroke-width="1"/>
      <text x="16" y="24" class="tt-head" fill="#f8fafc">EMPIRICAL VALIDATION RESULT</text>
      
      <g transform="translate(16, 40)">
        <text x="0" y="16" class="tt-sub">DISPLACEMENT JITTER REDUCTION</text>
        <text x="0" y="44" class="tt-stat" fill="#38bdf8">0.8426 m → 0.5099 m (-39.48%)</text>
        <text x="0" y="64" class="tt-body">IMU motion-warped tracklet propagation stabilizes 3D positions across high-speed maneuvers.</text>
      </g>
    </g>
  </g>
</svg>"""

write_svg("temporal-tracking.svg", TEMPORAL_TRACKING_SVG)

# ==============================================================================
# 7. RELIABILITY ENGINE SVG (1150 x 580)
# ==============================================================================
RELIABILITY_ENGINE_SVG = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1150 580" width="100%" height="100%">
  <defs>
    <linearGradient id="re-bg" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#060912"/>
      <stop offset="100%" stop-color="#0b1326"/>
    </linearGradient>
    <linearGradient id="re-cam-card" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%" stop-color="#0c2340"/>
      <stop offset="100%" stop-color="#081426"/>
    </linearGradient>
    <linearGradient id="re-lidar-card" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%" stop-color="#062e24"/>
      <stop offset="100%" stop-color="#051c17"/>
    </linearGradient>
  </defs>

  <style>
    .re-title { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; font-size: 13px; font-weight: 700; fill: #f8fafc; }
    .re-sub { font-family: 'SF Mono', Monaco, monospace; font-size: 10px; fill: #94a3b8; }
    .re-head { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; font-size: 11.5px; font-weight: 700; }
    .re-body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; font-size: 10px; fill: #cbd5e1; }
    .re-math { font-family: 'SF Mono', Monaco, monospace; font-size: 10px; font-weight: 600; }
  </style>

  <rect width="1150" height="580" rx="8" fill="url(#re-bg)" stroke="#1e293b" stroke-width="1"/>

  <text x="40" y="32" class="re-title">PHYSICAL RELIABILITY ESTIMATION &amp; ADAPTIVE WEIGHTING ENGINE</text>
  <text x="40" y="48" class="re-sub">Multi-Criteria Physical Indicator Modeling, Operational Health Classification, and Exponential Hysteresis Stabilization</text>

  <!-- Parallel Pipeline 1: Camera Reliability (Left, 520 wide) -->
  <g transform="translate(40, 75)">
    <rect width="520" height="235" rx="8" fill="url(#re-cam-card)" stroke="#38bdf8" stroke-width="1.2"/>
    <rect x="0" y="0" width="520" height="3" fill="#38bdf8" rx="1.5"/>

    <text x="20" y="24" class="re-head" fill="#38bdf8">CAMERA PHYSICAL RELIABILITY FORMULATION (R_cam ∈ [0.01, 0.99])</text>
    
    <g transform="translate(16, 38)">
      <rect width="488" height="40" rx="4" fill="#08182b" stroke="#0284c7" stroke-width="0.8"/>
      <text x="12" y="24" class="re-math" fill="#38bdf8">R_cam = c_det · ψ_visual · ψ_range · ψ_motion · τ_temp</text>
    </g>

    <g transform="translate(20, 95)">
      <text x="0" y="16" class="re-body" font-weight="700" fill="#f8fafc">• Visual Quality (ψ_visual = 0.5 ψ_sharp + 0.5 ψ_illum):</text>
      <text x="14" y="32" class="re-sub">Modified Laplacian variance (optical blur) + luminance deviation from nominal 128.</text>

      <text x="0" y="56" class="re-body" font-weight="700" fill="#f8fafc">• Optical Range Decay Penalty (ψ_range):</text>
      <text x="14" y="72" class="re-math" fill="#38bdf8">ψ_range = exp( -d / 45 )</text>

      <text x="0" y="96" class="re-body" font-weight="700" fill="#f8fafc">• IMU Vehicle Agitation Penalty (ψ_motion):</text>
      <text x="14" y="112" class="re-math" fill="#38bdf8">ψ_motion = exp( -0.08 · ( ||a_linear|| + 5 ||ω|| ) )</text>
    </g>
  </g>

  <!-- Parallel Pipeline 2: LiDAR Reliability (Right, 520 wide) -->
  <g transform="translate(590, 75)">
    <rect width="520" height="235" rx="8" fill="url(#re-lidar-card)" stroke="#34d399" stroke-width="1.2"/>
    <rect x="0" y="0" width="520" height="3" fill="#34d399" rx="1.5"/>

    <text x="20" y="24" class="re-head" fill="#34d399">LiDAR PHYSICAL RELIABILITY FORMULATION (R_lidar ∈ [0.01, 0.99])</text>

    <g transform="translate(16, 38)">
      <rect width="488" height="40" rx="4" fill="#042018" stroke="#059669" stroke-width="0.8"/>
      <text x="12" y="24" class="re-math" fill="#34d399">R_lidar = ( 0.50 γ_geom + 0.50 ρ_density ) · ψ_health · τ_temp</text>
    </g>

    <g transform="translate(20, 95)">
      <text x="0" y="16" class="re-body" font-weight="700" fill="#f8fafc">• Range-Normalized Point Density Model (ρ_density):</text>
      <text x="14" y="32" class="re-math" fill="#34d399">ρ_density = min( 1.0, N_cluster / ( 400 / (d + 1) ) )</text>
      <text x="14" y="48" class="re-sub">Calibrates point count against physical 1/d laser beam divergence.</text>

      <text x="0" y="72" class="re-body" font-weight="700" fill="#f8fafc">• Geometric Consistency Factor (γ_geom):</text>
      <text x="14" y="88" class="re-sub">3D bounding box aspect ratio and spatial cluster compactness.</text>

      <text x="0" y="112" class="re-body" font-weight="700" fill="#f8fafc">• Sensor Hardware Health Indicator (ψ_health):</text>
      <text x="14" y="128" class="re-sub">Monitors beam return completeness and backscatter spray noise.</text>
    </g>
  </g>

  <!-- Lower Section: Health States (Left) & Weight Hysteresis (Right) -->
  <!-- Operational Health Classification (Left, 520 wide) -->
  <g transform="translate(40, 330)">
    <rect width="520" height="225" rx="8" fill="#0a1224" stroke="#1e293b" stroke-width="1"/>
    <text x="20" y="24" class="re-head" fill="#f8fafc">DYNAMIC SENSOR HEALTH CLASSIFICATION &amp; DERIVATIVE TRENDS</text>

    <!-- 4 Health Status Bars -->
    <g transform="translate(20, 42)">
      <!-- HEALTHY -->
      <rect width="112" height="65" rx="4" fill="#062e24" stroke="#34d399" stroke-width="1"/>
      <circle cx="16" cy="18" r="4" fill="#34d399"/>
      <text x="26" y="21" font-family="'SF Mono', Monaco, monospace" font-size="8.5" fill="#34d399" font-weight="700">HEALTHY</text>
      <text x="12" y="40" class="re-math" fill="#34d399">R ≥ 0.70</text>
      <text x="12" y="54" class="re-sub">Nominal modal state</text>

      <!-- DEGRADED -->
      <g transform="translate(122, 0)">
        <rect width="112" height="65" rx="4" fill="#08233a" stroke="#38bdf8" stroke-width="1"/>
        <circle cx="16" cy="18" r="4" fill="#38bdf8"/>
        <text x="26" y="21" font-family="'SF Mono', Monaco, monospace" font-size="8.5" fill="#38bdf8" font-weight="700">DEGRADED</text>
        <text x="12" y="40" class="re-math" fill="#38bdf8">0.40 ≤ R &lt; 0.70</text>
        <text x="12" y="54" class="re-sub">Down-weighted</text>
      </g>

      <!-- SEVERELY DEGRADED -->
      <g transform="translate(244, 0)">
        <rect width="115" height="65" rx="4" fill="#2b1b05" stroke="#fbbf24" stroke-width="1"/>
        <circle cx="16" cy="18" r="4" fill="#fbbf24"/>
        <text x="26" y="21" font-family="'SF Mono', Monaco, monospace" font-size="8" fill="#fbbf24" font-weight="700">SEV_DEGRADED</text>
        <text x="12" y="40" class="re-math" fill="#fbbf24">0.15 ≤ R &lt; 0.40</text>
        <text x="12" y="54" class="re-sub">Heavy penalty</text>
      </g>

      <!-- FAILED -->
      <g transform="translate(369, 0)">
        <rect width="110" height="65" rx="4" fill="#2b0a14" stroke="#f43f5e" stroke-width="1"/>
        <circle cx="16" cy="18" r="4" fill="#f43f5e"/>
        <text x="26" y="21" font-family="'SF Mono', Monaco, monospace" font-size="8.5" fill="#f43f5e" font-weight="700">FAILED</text>
        <text x="12" y="40" class="re-math" fill="#f43f5e">R &lt; 0.15</text>
        <text x="12" y="54" class="re-sub">Zero-weighted</text>
      </g>
    </g>

    <!-- Derivative Trend Derivatives -->
    <g transform="translate(20, 125)">
      <rect width="480" height="85" rx="4" fill="#111c33" stroke="#334155" stroke-width="0.8"/>
      <text x="12" y="18" class="re-sub" font-weight="700" fill="#f8fafc">RELIABILITY TIME DERIVATIVE: dR / dt = ( R_t - R_{t-1} ) / Δt</text>
      <text x="12" y="36" class="re-math" fill="#f43f5e">• Rapidly Degrading: dR/dt &lt; -0.40 s⁻¹ (Imminent failure alert)</text>
      <text x="12" y="52" class="re-math" fill="#fbbf24">• Degrading: -0.40 ≤ dR/dt &lt; -0.05 s⁻¹  |  • Stable: |dR/dt| ≤ 0.05 s⁻¹</text>
      <text x="12" y="68" class="re-math" fill="#34d399">• Improving / Recovering: dR/dt &gt; +0.05 s⁻¹ (Controlled restitution)</text>
    </g>
  </g>

  <!-- Weight Generation & Hysteresis Smoothing (Right, 520 wide) -->
  <g transform="translate(590, 330)">
    <rect width="520" height="225" rx="8" fill="#150a2b" stroke="#9333ea" stroke-width="1.2"/>
    <text x="20" y="24" class="re-head" fill="#c084fc">EXPONENTIAL HYSTERESIS WEIGHT SMOOTHING (α = 0.65)</text>

    <g transform="translate(20, 42)">
      <rect width="480" height="65" rx="4" fill="#240f47" stroke="#a855f7" stroke-width="0.8"/>
      <text x="12" y="22" class="re-math" fill="#e9d5ff">w_cam,smooth(t) = 0.65 · w_cam,raw(t) + 0.35 · w_cam,smooth(t - Δt)</text>
      <text x="12" y="42" class="re-math" fill="#e9d5ff">w_lidar,smooth(t) = 0.65 · w_lidar,raw(t) + 0.35 · w_lidar,smooth(t - Δt)</text>
      <text x="12" y="58" class="re-math" fill="#34d399">Normalized Output: w_cam(t) + w_lidar(t) = 1.0</text>
    </g>

    <!-- Visual Chatter Comparison -->
    <g transform="translate(20, 125)">
      <!-- Without Hysteresis (Chatter) -->
      <rect width="235" height="85" rx="4" fill="#1c1130" stroke="#ef4444" stroke-width="0.8"/>
      <text x="10" y="16" font-family="'SF Mono', Monaco, monospace" font-size="8" fill="#f87171" font-weight="700">WITHOUT HYSTERESIS (RAW)</text>
      <path d="M 15 45 L 35 70 L 55 25 L 75 75 L 95 30 L 115 65 L 135 25 L 155 70 L 175 35 L 195 65 L 220 45" fill="none" stroke="#ef4444" stroke-width="1.5"/>
      <text x="10" y="78" class="re-sub" fill="#fca5a5">High-frequency weight jitter</text>

      <!-- With Hysteresis (Smooth) -->
      <g transform="translate(245, 0)">
        <rect width="235" height="85" rx="4" fill="#1c1130" stroke="#34d399" stroke-width="0.8"/>
        <text x="10" y="16" font-family="'SF Mono', Monaco, monospace" font-size="8" fill="#34d399" font-weight="700">WITH HYSTERESIS (α = 0.65)</text>
        <path d="M 15 45 C 50 45, 70 70, 115 70 C 160 70, 180 35, 220 35" fill="none" stroke="#34d399" stroke-width="2"/>
        <text x="10" y="78" class="re-sub" fill="#a7f3d0">Stable exponential transitions</text>
      </g>
    </g>
  </g>
</svg>"""

write_svg("reliability-engine.svg", RELIABILITY_ENGINE_SVG)

# ==============================================================================
# 8. CONTINUOUS DEGRADATION TIMELINE SVG (1180 x 480)
# ==============================================================================
DEGRADATION_TIMELINE_SVG = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1180 480" width="100%" height="100%">
  <defs>
    <linearGradient id="dt-bg" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#060911"/>
      <stop offset="100%" stop-color="#0a1224"/>
    </linearGradient>
  </defs>

  <style>
    .dt-title { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; font-size: 13px; font-weight: 700; fill: #f8fafc; }
    .dt-sub { font-family: 'SF Mono', Monaco, monospace; font-size: 10px; fill: #94a3b8; }
    .dt-phase { font-family: 'SF Mono', Monaco, monospace; font-size: 8.5px; font-weight: 700; }
    .dt-name { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; font-size: 10px; font-weight: 700; fill: #f8fafc; }
    .dt-detail { font-family: 'SF Mono', Monaco, monospace; font-size: 8px; fill: #94a3b8; }
  </style>

  <rect width="1180" height="480" rx="8" fill="url(#dt-bg)" stroke="#1e293b" stroke-width="1"/>

  <text x="40" y="32" class="dt-title">CONTINUOUS TIME-VARYING DYNAMIC DEGRADATION SCHEDULE</text>
  <text x="40" y="48" class="dt-sub">70 Synchronized Frames @ 20 Hz (Town10HD_Opt) — Progressive Environmental Regimes vs Adaptive Modal Hand-Off</text>

  <!-- Horizontal Timeline Segments (Frames 0 to 69, 1100 px total width) -->
  <g transform="translate(40, 75)">
    <!-- Time Axis Header -->
    <rect width="1100" height="24" rx="4" fill="#0f172a" stroke="#1e293b" stroke-width="1"/>
    <text x="10" y="16" font-family="'SF Mono', Monaco, monospace" font-size="9" fill="#38bdf8" font-weight="700">t = 0.0 s</text>
    <text x="240" y="16" font-family="'SF Mono', Monaco, monospace" font-size="9" fill="#94a3b8">t = 0.75 s</text>
    <text x="550" y="16" font-family="'SF Mono', Monaco, monospace" font-size="9" fill="#94a3b8">t = 1.75 s</text>
    <text x="865" y="16" font-family="'SF Mono', Monaco, monospace" font-size="9" fill="#94a3b8">t = 2.75 s</text>
    <text x="1040" y="16" font-family="'SF Mono', Monaco, monospace" font-size="9" fill="#f43f5e" font-weight="700">t = 3.5 s</text>

    <!-- Phase 1: Nominal (Frames 0-14, width: 235) -->
    <g transform="translate(0, 35)">
      <rect width="230" height="155" rx="6" fill="#062e24" stroke="#34d399" stroke-width="1.2"/>
      <rect x="0" y="0" width="230" height="3" fill="#34d399" rx="1.5"/>
      <text x="12" y="20" class="dt-phase" fill="#34d399">FRAMES 0 – 14</text>
      <text x="12" y="38" class="dt-name">Nominal Baseline</text>
      <text x="12" y="58" class="dt-detail">• Clear daylight, cruising</text>
      <text x="12" y="74" class="dt-detail">• Unimpaired visual/LiDAR</text>
      <text x="12" y="90" class="dt-detail">• F1-Score: 0.9913</text>
      <rect x="10" y="110" width="210" height="32" rx="4" fill="#032119"/>
      <text x="16" y="126" font-family="'SF Mono', Monaco, monospace" font-size="8.5" fill="#34d399" font-weight="600">Camera: HEALTHY (R=0.92)</text>
      <text x="16" y="138" font-family="'SF Mono', Monaco, monospace" font-size="8.5" fill="#34d399" font-weight="600">LiDAR: HEALTHY (R=0.95)</text>
    </g>

    <!-- Phase 2: Camera Blur Ramp (Frames 15-24, width: 155) -->
    <g transform="translate(235, 35)">
      <rect width="150" height="155" rx="6" fill="#10253d" stroke="#38bdf8" stroke-width="1.2"/>
      <rect x="0" y="0" width="150" height="3" fill="#38bdf8" rx="1.5"/>
      <text x="10" y="20" class="dt-phase" fill="#38bdf8">FRAMES 15 – 24</text>
      <text x="10" y="38" class="dt-name">Motion Blur Ramp</text>
      <text x="10" y="58" class="dt-detail">• Kernel 3×3 → 21×21</text>
      <text x="10" y="74" class="dt-detail">• Progressive dimming</text>
      <text x="10" y="90" class="dt-detail">• F1-Score: 0.9817</text>
      <rect x="8" y="110" width="134" height="32" rx="4" fill="#08182b"/>
      <text x="12" y="126" font-family="'SF Mono', Monaco, monospace" font-size="8" fill="#f87171" font-weight="600">R_cam: DEGRADED</text>
      <text x="12" y="138" font-family="'SF Mono', Monaco, monospace" font-size="8" fill="#34d399" font-weight="600">w_lidar → 0.98</text>
    </g>

    <!-- Phase 3: Camera Recovery (Frames 25-34, width: 155) -->
    <g transform="translate(390, 35)">
      <rect width="150" height="155" rx="6" fill="#0d1b33" stroke="#818cf8" stroke-width="1"/>
      <rect x="0" y="0" width="150" height="3" fill="#818cf8" rx="1.5"/>
      <text x="10" y="20" class="dt-phase" fill="#818cf8">FRAMES 25 – 34</text>
      <text x="10" y="38" class="dt-name">Camera Recovery</text>
      <text x="10" y="58" class="dt-detail">• Blur fades 21×21 → clean</text>
      <text x="10" y="74" class="dt-detail">• Illumination restored</text>
      <text x="10" y="90" class="dt-detail">• Smooth weight return</text>
      <rect x="8" y="110" width="134" height="32" rx="4" fill="#0b1324"/>
      <text x="12" y="126" font-family="'SF Mono', Monaco, monospace" font-size="8" fill="#a5b4fc" font-weight="600">Trend: IMPROVING</text>
      <text x="12" y="138" font-family="'SF Mono', Monaco, monospace" font-size="8" fill="#a5b4fc" font-weight="600">Hysteresis smooth</text>
    </g>

    <!-- Phase 4: LiDAR Dropout Ramp (Frames 35-44, width: 155) -->
    <g transform="translate(545, 35)">
      <rect width="150" height="155" rx="6" fill="#241708" stroke="#fbbf24" stroke-width="1.2"/>
      <rect x="0" y="0" width="150" height="3" fill="#fbbf24" rx="1.5"/>
      <text x="10" y="20" class="dt-phase" fill="#fbbf24">FRAMES 35 – 44</text>
      <text x="10" y="38" class="dt-name">LiDAR Attenuation</text>
      <text x="10" y="58" class="dt-detail">• 10% → 85% dropout</text>
      <text x="10" y="74" class="dt-detail">• Backscatter spray</text>
      <text x="10" y="90" class="dt-detail">• Precision: 0.4000</text>
      <rect x="8" y="110" width="134" height="32" rx="4" fill="#1f1203"/>
      <text x="12" y="126" font-family="'SF Mono', Monaco, monospace" font-size="8" fill="#f87171" font-weight="600">R_lidar: SEV_DEGRADED</text>
      <text x="12" y="138" font-family="'SF Mono', Monaco, monospace" font-size="8" fill="#38bdf8" font-weight="600">w_cam → 0.95</text>
    </g>

    <!-- Phase 5: LiDAR Recovery (Frames 45-54, width: 155) -->
    <g transform="translate(700, 35)">
      <rect width="150" height="155" rx="6" fill="#08231c" stroke="#34d399" stroke-width="1"/>
      <rect x="0" y="0" width="150" height="3" fill="#34d399" rx="1.5"/>
      <text x="10" y="20" class="dt-phase" fill="#34d399">FRAMES 45 – 54</text>
      <text x="10" y="38" class="dt-name">LiDAR Recovery</text>
      <text x="10" y="58" class="dt-detail">• Beam return restores</text>
      <text x="10" y="74" class="dt-detail">• Spray clears out</text>
      <text x="10" y="90" class="dt-detail">• Density recalibrated</text>
      <rect x="8" y="110" width="134" height="32" rx="4" fill="#041a14"/>
      <text x="12" y="126" font-family="'SF Mono', Monaco, monospace" font-size="8" fill="#34d399" font-weight="600">Density → nominal</text>
      <text x="12" y="138" font-family="'SF Mono', Monaco, monospace" font-size="8" fill="#34d399" font-weight="600">Weights rebalanced</text>
    </g>

    <!-- Phase 6: Tunnel Plunge (Frames 55-59, width: 80) -->
    <g transform="translate(855, 35)">
      <rect width="75" height="155" rx="6" fill="#240711" stroke="#f43f5e" stroke-width="1.2"/>
      <rect x="0" y="0" width="75" height="3" fill="#f43f5e" rx="1.5"/>
      <text x="6" y="20" class="dt-phase" fill="#f43f5e" font-size="7.5">55 – 59</text>
      <text x="6" y="36" class="dt-name" font-size="9">Darkness</text>
      <text x="6" y="56" class="dt-detail" font-size="7.5">• 0.10x illum</text>
      <text x="6" y="70" class="dt-detail" font-size="7.5">• Tunnel drop</text>
      <rect x="5" y="110" width="65" height="32" rx="3" fill="#1a040b"/>
      <text x="7" y="124" font-family="'SF Mono', Monaco, monospace" font-size="7" fill="#f87171" font-weight="700">R_cam &lt; 0.15</text>
      <text x="7" y="136" font-family="'SF Mono', Monaco, monospace" font-size="7" fill="#34d399">LiDAR solo</text>
    </g>

    <!-- Phase 7: Maneuver (Frames 60-64, width: 80) -->
    <g transform="translate(935, 35)">
      <rect width="75" height="155" rx="6" fill="#241708" stroke="#fbbf24" stroke-width="1"/>
      <rect x="0" y="0" width="75" height="3" fill="#fbbf24" rx="1.5"/>
      <text x="6" y="20" class="dt-phase" fill="#fbbf24" font-size="7.5">60 – 64</text>
      <text x="6" y="36" class="dt-name" font-size="9">Agitation</text>
      <text x="6" y="56" class="dt-detail" font-size="7.5">• ω_z &gt; 15°/s</text>
      <text x="6" y="70" class="dt-detail" font-size="7.5">• a_x &lt; -2 m/s²</text>
      <rect x="5" y="110" width="65" height="32" rx="3" fill="#1a1003"/>
      <text x="7" y="124" font-family="'SF Mono', Monaco, monospace" font-size="7" fill="#fbbf24" font-weight="700">IMU penalty</text>
      <text x="7" y="136" font-family="'SF Mono', Monaco, monospace" font-size="7" fill="#fbbf24">Warp active</text>
    </g>

    <!-- Phase 8: Dual Degradation (Frames 65-69, width: 85) -->
    <g transform="translate(1015, 35)">
      <rect width="85" height="155" rx="6" fill="#260920" stroke="#c084fc" stroke-width="1.2"/>
      <rect x="0" y="0" width="85" height="3" fill="#c084fc" rx="1.5"/>
      <text x="6" y="20" class="dt-phase" fill="#c084fc" font-size="7.5">65 – 69</text>
      <text x="6" y="36" class="dt-name" font-size="9">Dual Fail</text>
      <text x="6" y="56" class="dt-detail" font-size="7.5">• 17x17 blur</text>
      <text x="6" y="70" class="dt-detail" font-size="7.5">• 70% dropout</text>
      <rect x="5" y="110" width="75" height="32" rx="3" fill="#1b0617"/>
      <text x="7" y="124" font-family="'SF Mono', Monaco, monospace" font-size="7" fill="#c084fc" font-weight="700">c → 0.0773</text>
      <text x="7" y="136" font-family="'SF Mono', Monaco, monospace" font-size="7" fill="#f43f5e">Alert trigger</text>
    </g>

    <!-- Bottom Continuous Area: Adaptive Weights Stream Profile -->
    <g transform="translate(0, 205)">
      <rect width="1100" height="180" rx="6" fill="#0b1325" stroke="#1e293b" stroke-width="1"/>
      <text x="20" y="24" class="dt-name">DYNAMIC MODALITY WEIGHT PROFILE (w_cam vs w_lidar) ACROSS SEQUENCE</text>

      <!-- Graph Axis -->
      <line x1="40" y1="145" x2="1080" y2="145" stroke="#334155" stroke-width="1"/>
      <line x1="40" y1="45" x2="1080" y2="45" stroke="#1e293b" stroke-width="0.8" stroke-dasharray="4 4"/>
      <line x1="40" y1="95" x2="1080" y2="95" stroke="#1e293b" stroke-width="0.8" stroke-dasharray="4 4"/>
      <text x="15" y="50" class="dt-detail">1.0</text>
      <text x="15" y="100" class="dt-detail">0.5</text>
      <text x="15" y="148" class="dt-detail">0.0</text>

      <!-- w_cam curve (Cyan) -->
      <path d="M 40 95 L 235 95 C 270 95, 290 140, 390 140 C 440 140, 480 95, 545 95 C 570 95, 600 50, 695 50 C 740 50, 780 95, 855 95 C 870 95, 885 142, 935 142 C 960 142, 980 95, 1015 95 C 1030 95, 1050 95, 1080 95" fill="none" stroke="#38bdf8" stroke-width="2.5"/>

      <!-- w_lidar curve (Emerald) -->
      <path d="M 40 95 L 235 95 C 270 95, 290 50, 390 50 C 440 50, 480 95, 545 95 C 570 95, 600 140, 695 140 C 740 140, 780 95, 855 95 C 870 95, 885 48, 935 48 C 960 48, 980 95, 1015 95 C 1030 95, 1050 95, 1080 95" fill="none" stroke="#34d399" stroke-width="2.5"/>

      <!-- Legend -->
      <g transform="translate(800, 16)">
        <line x1="0" y1="6" x2="25" y2="6" stroke="#38bdf8" stroke-width="2.5"/>
        <text x="32" y="10" class="dt-detail" fill="#38bdf8" font-weight="700">w_cam (Camera Weight)</text>
        <line x1="150" y1="6" x2="175" y2="6" stroke="#34d399" stroke-width="2.5"/>
        <text x="182" y="10" class="dt-detail" fill="#34d399" font-weight="700">w_lidar (LiDAR Weight)</text>
      </g>
    </g>
  </g>
</svg>"""

write_svg("continuous-degradation-timeline.svg", DEGRADATION_TIMELINE_SVG)

# ==============================================================================
# 9. FAIL-SAFE LOGIC SVG (1050 x 440)
# ==============================================================================
FAIL_SAFE_LOGIC_SVG = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1050 440" width="100%" height="100%">
  <defs>
    <linearGradient id="fs-bg" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#060912"/>
      <stop offset="100%" stop-color="#0b1222"/>
    </linearGradient>
    <linearGradient id="fs-card" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%" stop-color="#121d33"/>
      <stop offset="100%" stop-color="#0b1322"/>
    </linearGradient>
  </defs>

  <style>
    .fs-title { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; font-size: 13px; font-weight: 700; fill: #f8fafc; }
    .fs-sub { font-family: 'SF Mono', Monaco, monospace; font-size: 10px; fill: #94a3b8; }
    .fs-card-head { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; font-size: 12px; font-weight: 700; }
    .fs-body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; font-size: 10.5px; fill: #cbd5e1; }
    .fs-math { font-family: 'SF Mono', Monaco, monospace; font-size: 10px; font-weight: 600; }
  </style>

  <rect width="1050" height="440" rx="8" fill="url(#fs-bg)" stroke="#1e293b" stroke-width="1"/>

  <text x="40" y="32" class="fs-title">FAIL-SAFE FUSION DECISION MATRIX &amp; MODAL DEGRADATION LOGIC</text>
  <text x="40" y="48" class="fs-sub">Dynamic Hand-Off Guarantees System Robustness Without Hallucinating Confidence When Both Modalities Suffer</text>

  <!-- 4 Scenario Cards Grid (2x2) -->
  <g transform="translate(40, 75)">
    <!-- Quadrant 1: Both Healthy -->
    <g transform="translate(0, 0)">
      <rect width="470" height="155" rx="6" fill="url(#fs-card)" stroke="#34d399" stroke-width="1.2"/>
      <rect x="0" y="0" width="4" height="155" fill="#34d399" rx="2"/>
      <text x="16" y="24" class="fs-card-head" fill="#34d399">STATE 1: NOMINAL DUAL-STREAM OPERATION</text>
      <text x="16" y="44" class="fs-sub">Camera HEALTHY (R ≥ 0.70)  •  LiDAR HEALTHY (R ≥ 0.70)</text>
      <text x="16" y="70" class="fs-body">• Both modalities exhibit high visual sharpness and dense 3D geometry.</text>
      <text x="16" y="88" class="fs-body">• Evidential fusion combines mutual confidence masses.</text>
      <text x="16" y="106" class="fs-body">• Fused weights maintain balanced distribution:</text>
      <text x="24" y="130" class="fs-math" fill="#34d399">w_cam ≈ 0.50,  w_lidar ≈ 0.50  →  F1: 0.9852, Loc Error: 0.0137 m</text>
    </g>

    <!-- Quadrant 2: Camera Degraded / Outage -->
    <g transform="translate(500, 0)">
      <rect width="470" height="155" rx="6" fill="url(#fs-card)" stroke="#38bdf8" stroke-width="1.2"/>
      <rect x="0" y="0" width="4" height="155" fill="#38bdf8" rx="2"/>
      <text x="16" y="24" class="fs-card-head" fill="#38bdf8">STATE 2: CAMERA MOTION BLUR / TUNNEL BLACKOUT</text>
      <text x="16" y="44" class="fs-sub">Camera FAILED (R &lt; 0.15)  •  LiDAR HEALTHY (R ≥ 0.70)</text>
      <text x="16" y="70" class="fs-body">• Severe visual degradation detected via Laplacian variance / luminance.</text>
      <text x="16" y="88" class="fs-body">• Hysteresis smoothly collapses camera weight toward minimum threshold.</text>
      <text x="16" y="106" class="fs-body">• LiDAR retains full responsibility without perception interruption:</text>
      <text x="24" y="130" class="fs-math" fill="#38bdf8">w_lidar → 0.99,  w_cam → 0.01  →  F1 Remains: 0.9853 (Clean Pass)</text>
    </g>

    <!-- Quadrant 3: LiDAR Attenuation / Rain -->
    <g transform="translate(0, 175)">
      <rect width="470" height="155" rx="6" fill="url(#fs-card)" stroke="#fbbf24" stroke-width="1.2"/>
      <rect x="0" y="0" width="4" height="155" fill="#fbbf24" rx="2"/>
      <text x="16" y="24" class="fs-card-head" fill="#fbbf24">STATE 3: LiDAR 85% DROPOUT &amp; BACKSCATTER SPRAY</text>
      <text x="16" y="44" class="fs-sub">Camera HEALTHY (R ≥ 0.70)  •  LiDAR SEV_DEGRADED (0.15 ≤ R &lt; 0.40)</text>
      <text x="16" y="70" class="fs-body">• Rain/fog pulse attenuation collapses cluster return density below 1/d curve.</text>
      <text x="16" y="88" class="fs-body">• Adaptive density gating suppresses noisy sparse cluster candidates.</text>
      <text x="16" y="106" class="fs-body">• Camera semantics preserve obstacle localization:</text>
      <text x="24" y="130" class="fs-math" fill="#fbbf24">Precision: 0.4000 (vs 0.0241 Fixed Late Fusion — 16.6x Cleaner)</text>
    </g>

    <!-- Quadrant 4: Dual Modality Degradation -->
    <g transform="translate(500, 175)">
      <rect width="470" height="155" rx="6" fill="url(#fs-card)" stroke="#f43f5e" stroke-width="1.2"/>
      <rect x="0" y="0" width="4" height="155" fill="#f43f5e" rx="2"/>
      <text x="16" y="24" class="fs-card-head" fill="#f43f5e">STATE 4: DUAL SENSOR SEVERE FAILURE (FAIL-SAFE)</text>
      <text x="16" y="44" class="fs-sub">Camera FAILED (R &lt; 0.15)  •  LiDAR FAILED (R &lt; 0.15)</text>
      <text x="16" y="70" class="fs-body">• Both visual stream and point cloud are critically compromised.</text>
      <text x="16" y="88" class="fs-body">• System DOES NOT hallucinate false confidence (Fixed fusion falsely outputs 0.2338).</text>
      <text x="16" y="106" class="fs-body">• Automatically depresses fused confidence to signal vehicle safety stop:</text>
      <text x="24" y="130" class="fs-math" fill="#f43f5e">Fused Confidence: 0.0673 – 0.0773  →  SAFETY INTERVENTION TRIGGERED</text>
    </g>
  </g>
</svg>"""

write_svg("fail-safe-logic.svg", FAIL_SAFE_LOGIC_SVG)

# ==============================================================================
# 10. ARCHITECTURE PIPELINE SVG (1200 x 920)
# ==============================================================================
ARCH_PIPELINE_SVG = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 920" width="100%" height="100%">
  <defs>
    <linearGradient id="ap-bg" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#060911"/>
      <stop offset="50%" stop-color="#0a1224"/>
      <stop offset="100%" stop-color="#050812"/>
    </linearGradient>

    <linearGradient id="ap-cam" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%" stop-color="#0c2545"/>
      <stop offset="100%" stop-color="#081526"/>
    </linearGradient>
    <linearGradient id="ap-lidar" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%" stop-color="#063328"/>
      <stop offset="100%" stop-color="#041a14"/>
    </linearGradient>
    <linearGradient id="ap-imu" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%" stop-color="#382506"/>
      <stop offset="100%" stop-color="#1c1303"/>
    </linearGradient>
    <linearGradient id="ap-core" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%" stop-color="#241042"/>
      <stop offset="100%" stop-color="#120824"/>
    </linearGradient>

    <filter id="ap-shadow" x="-10%" y="-10%" width="120%" height="120%">
      <feDropShadow dx="0" dy="6" stdDeviation="8" flood-color="#000000" flood-opacity="0.5"/>
    </filter>
  </defs>

  <style>
    .ap-title { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; font-size: 14px; font-weight: 700; fill: #f8fafc; }
    .ap-sub { font-family: 'SF Mono', Monaco, monospace; font-size: 10px; fill: #94a3b8; }
    .ap-card-head { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; font-size: 12px; font-weight: 700; }
    .ap-body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; font-size: 10.5px; fill: #cbd5e1; }
    .ap-mono { font-family: 'SF Mono', Monaco, monospace; font-size: 9.5px; }
  </style>

  <rect width="1200" height="920" fill="url(#ap-bg)"/>

  <!-- Top Title -->
  <g transform="translate(60, 35)">
    <text x="0" y="0" class="ap-title">DETAILED SYSTEM ARCHITECTURE &amp; DATA PROCESSING PIPELINE</text>
    <text x="0" y="18" class="ap-sub">Synchronous lockstep execution in CARLA 0.9.16 at 20 Hz (Δt = 0.05 s) across perception, tracking, and reliability layers</text>
  </g>

  <!-- ================= LEVEL 1: SIMULATOR SOURCE ================= -->
  <g transform="translate(60, 80)" filter="url(#ap-shadow)">
    <rect width="1080" height="48" rx="6" fill="#0f172a" stroke="#334155" stroke-width="1.2"/>
    <circle cx="25" cy="24" r="6" fill="#10b981"/>
    <text x="42" y="28" font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif" font-size="12" font-weight="700" fill="#f8fafc">
      CARLA 0.9.16 SYNCHRONOUS SIMULATOR RUNTIME (20 Hz, Fixed Delta t = 0.05 s)
    </text>
    <text x="820" y="28" class="ap-mono" fill="#10b981">MAP: Town10HD_Opt • LOCKSTEP FIFO</text>
  </g>

  <!-- Downward Connectors from Simulator -->
  <path d="M 230 128 L 230 160" stroke="#38bdf8" stroke-width="1.8"/>
  <polygon points="230,163 226,155 234,155" fill="#38bdf8"/>

  <path d="M 600 128 L 600 160" stroke="#34d399" stroke-width="1.8"/>
  <polygon points="600,163 596,155 604,155" fill="#34d399"/>

  <path d="M 970 128 L 970 160" stroke="#fbbf24" stroke-width="1.8"/>
  <polygon points="970,163 966,155 974,155" fill="#fbbf24"/>

  <!-- ================= LEVEL 2: 3 SENSOR MODALITY BRANCHES ================= -->
  <!-- Branch 1: RGB Camera -->
  <g transform="translate(60, 165)" filter="url(#ap-shadow)">
    <rect width="330" height="155" rx="8" fill="url(#ap-cam)" stroke="#38bdf8" stroke-width="1.2"/>
    <rect x="0" y="0" width="330" height="3" fill="#38bdf8" rx="1.5"/>
    <text x="16" y="24" class="ap-card-head" fill="#38bdf8">📷 RGB CAMERA PERCEPTION BRANCH</text>
    <text x="16" y="42" class="ap-mono" fill="#94a3b8">800 × 600 px • FOV 90° • p_cam = [1.5, 0, 2.4] m</text>
    
    <text x="16" y="66" class="ap-body" font-weight="700" fill="#f8fafc">• 2D Semantics: Ultralytics YOLOv8 (yolov8n.pt)</text>
    <text x="26" y="82" class="ap-sub">Outputs: Class labels, Bounding Boxes B_cam, Conf c_det</text>
    
    <text x="16" y="104" class="ap-body" font-weight="700" fill="#f8fafc">• Optical Quality Extractor:</text>
    <text x="26" y="120" class="ap-sub">Modified Laplacian Variance (Sharpness ψ_sharp)</text>
    <text x="26" y="136" class="ap-sub">Mean Luminance Deviation (Illumination ψ_illum)</text>
  </g>

  <!-- Branch 2: 64-Beam LiDAR -->
  <g transform="translate(435, 165)" filter="url(#ap-shadow)">
    <rect width="330" height="155" rx="8" fill="url(#ap-lidar)" stroke="#34d399" stroke-width="1.2"/>
    <rect x="0" y="0" width="330" height="3" fill="#34d399" rx="1.5"/>
    <text x="16" y="24" class="ap-card-head" fill="#34d399">📡 64-BEAM LiDAR GEOMETRY BRANCH</text>
    <text x="16" y="42" class="ap-mono" fill="#94a3b8">64 Channels • 20 Hz • p_lidar = [0, 0, 2.5] m</text>

    <text x="16" y="66" class="ap-body" font-weight="700" fill="#f8fafc">• Point Cloud Preprocessing &amp; ROI Filter</text>
    <text x="26" y="82" class="ap-sub">~3000 points/frame, range 50m, Open3D pipeline</text>

    <text x="16" y="104" class="ap-body" font-weight="700" fill="#f8fafc">• RANSAC Ground Removal &amp; DBSCAN 3D:</text>
    <text x="26" y="120" class="ap-sub">Separates drivable ground plane (distance_thresh=0.2m)</text>
    <text x="26" y="136" class="ap-sub">Euclidean clustering → 3D Bounding Boxes &amp; 8 Vertices</text>
  </g>

  <!-- Branch 3: 6-DoF IMU -->
  <g transform="translate(810, 165)" filter="url(#ap-shadow)">
    <rect width="330" height="155" rx="8" fill="url(#ap-imu)" stroke="#fbbf24" stroke-width="1.2"/>
    <rect x="0" y="0" width="330" height="3" fill="#fbbf24" rx="1.5"/>
    <text x="16" y="24" class="ap-card-head" fill="#fbbf24">🧭 6-DoF IMU KINEMATICS BRANCH</text>
    <text x="16" y="42" class="ap-mono" fill="#94a3b8">Specific Force + Gyro • p_imu = [0, 0, 2.0] m</text>

    <text x="16" y="66" class="ap-body" font-weight="700" fill="#f8fafc">• Specific Force Gravity Removal:</text>
    <text x="26" y="82" class="ap-mono" fill="#fbbf24">a_linear = [fx, fy, fz - 9.81]^T m/s²</text>

    <text x="16" y="104" class="ap-body" font-weight="700" fill="#f8fafc">• Inter-Frame Kinematic Integration:</text>
    <text x="26" y="120" class="ap-mono" fill="#fbbf24">ΔR ∈ SO(3),  Δt = v Δt + 0.5 a (Δt)²</text>
    <text x="26" y="136" class="ap-sub">Builds Rigid Transform T_ego ∈ SE(3)</text>
  </g>

  <!-- Connectors from Branches to Association Layer -->
  <path d="M 225 320 L 225 370 L 360 370 L 360 395" stroke="#38bdf8" stroke-width="1.8" fill="none"/>
  <polygon points="360,398 356,390 364,390" fill="#38bdf8"/>

  <path d="M 600 320 L 600 395" stroke="#34d399" stroke-width="1.8" fill="none"/>
  <polygon points="600,398 596,390 604,390" fill="#34d399"/>

  <!-- IMU branch bypass to Temporal Tracker and Motion Compensator -->
  <path d="M 975 320 L 975 565 L 755 565 L 755 595" stroke="#fbbf24" stroke-width="1.8" fill="none"/>
  <polygon points="755,598 751,590 759,590" fill="#fbbf24"/>

  <!-- ================= LEVEL 3: SPATIAL CROSS-MODAL ASSOCIATION ================= -->
  <g transform="translate(180, 400)" filter="url(#ap-shadow)">
    <rect width="840" height="120" rx="8" fill="#101935" stroke="#818cf8" stroke-width="1.5"/>
    <rect x="0" y="0" width="840" height="3" fill="#818cf8" rx="1.5"/>
    
    <text x="20" y="24" class="ap-card-head" fill="#818cf8">🔗 SPATIAL CROSS-MODAL ASSOCIATION LAYER</text>
    <text x="20" y="42" class="ap-mono" fill="#c7d2fe">3D-to-2D Optical Projection (Matrix K) + Hungarian 2D Bounding Box IoU Matching</text>

    <g transform="translate(20, 56)">
      <rect width="380" height="50" rx="4" fill="#152142"/>
      <text x="10" y="18" class="ap-mono" fill="#818cf8">Projection: u_k = π( K · [ R_opt p_k + t_opt ] )</text>
      <text x="10" y="36" class="ap-sub">Projects 8 corner vertices to image envelope B_proj</text>
    </g>

    <g transform="translate(420, 56)">
      <rect width="400" height="50" rx="4" fill="#152142"/>
      <text x="10" y="18" class="ap-mono" fill="#34d399">Hungarian Assignment: C_ij = 1 - IoU(B_cam, B_proj)</text>
      <text x="10" y="36" class="ap-sub">Assigns optimal cross-modal pairs (min overlap = 0.10)</text>
    </g>
  </g>

  <!-- Connector from Spatial to Temporal Layer -->
  <path d="M 500 520 L 500 595" stroke="#818cf8" stroke-width="1.8"/>
  <polygon points="500,598 496,590 504,590" fill="#818cf8"/>

  <!-- ================= LEVEL 4: TEMPORAL TRACKING & RELIABILITY ================= -->
  <g transform="translate(60, 600)" filter="url(#ap-shadow)">
    <rect width="1080" height="155" rx="8" fill="url(#ap-core)" stroke="#c084fc" stroke-width="1.5"/>
    <rect x="0" y="0" width="1080" height="3" fill="#c084fc" rx="1.5"/>

    <text x="20" y="24" class="ap-card-head" fill="#e9d5ff">🧠 TEMPORAL GATING &amp; DYNAMIC RELIABILITY ESTIMATOR</text>
    <text x="20" y="42" class="ap-mono" fill="#c084fc">IMU-Warped Kalman Tracklets (min_hits ≥ 2) + Multi-Criteria Sensor Health Engine</text>

    <!-- Sub-Block 1: Temporal Kalman Tracker -->
    <g transform="translate(20, 55)">
      <rect width="330" height="85" rx="6" fill="#1a0b33" stroke="#9333ea" stroke-width="0.8"/>
      <text x="12" y="20" class="ap-mono" fill="#c084fc" font-weight="700">IMU-WARPED KALMAN TRACKER</text>
      <text x="12" y="38" class="ap-sub">• Warps tracklet centroids via T_ego</text>
      <text x="12" y="54" class="ap-sub">• Enforces min_hits ≥ 2 (eliminates false alarms)</text>
      <text x="12" y="70" class="ap-mono" fill="#34d399">• Jitter Cut: -39.48% (0.84m → 0.51m)</text>
    </g>

    <!-- Sub-Block 2: Camera Reliability -->
    <g transform="translate(370, 55)">
      <rect width="330" height="85" rx="6" fill="#0c1b36" stroke="#38bdf8" stroke-width="0.8"/>
      <text x="12" y="20" class="ap-mono" fill="#38bdf8" font-weight="700">CAMERA RELIABILITY (R_cam)</text>
      <text x="12" y="38" class="ap-mono" font-size="8.5" fill="#38bdf8">c_det · ψ_vis · ψ_rng · ψ_mot · τ_temp</text>
      <text x="12" y="54" class="ap-sub">• Lapl Sharpness + Illum Deviation</text>
      <text x="12" y="70" class="ap-sub">• Range exp(-d/45) + Agitation penalty</text>
    </g>

    <!-- Sub-Block 3: LiDAR Reliability -->
    <g transform="translate(720, 55)">
      <rect width="340" height="85" rx="6" fill="#06241c" stroke="#34d399" stroke-width="0.8"/>
      <text x="12" y="20" class="ap-mono" fill="#34d399" font-weight="700">LiDAR RELIABILITY (R_lidar)</text>
      <text x="12" y="38" class="ap-mono" font-size="8.5" fill="#34d399">(0.50 γ_geom + 0.50 ρ_dens) · ψ_hlth · τ</text>
      <text x="12" y="54" class="ap-sub">• Range-Calibrated Density: 1/d Model</text>
      <text x="12" y="70" class="ap-sub">• Compactness + Spray Noise Resistance</text>
    </g>
  </g>

  <!-- Connector from Temporal/Reliability to Adaptive Fusion -->
  <path d="M 600 755 L 600 790" stroke="#c084fc" stroke-width="2"/>
  <polygon points="600,793 596,785 604,785" fill="#c084fc"/>

  <!-- ================= LEVEL 5: ADAPTIVE FUSION OUTPUT ================= -->
  <g transform="translate(60, 795)" filter="url(#ap-shadow)">
    <rect width="1080" height="95" rx="8" fill="#190a33" stroke="#f43f5e" stroke-width="1.8"/>
    <rect x="0" y="0" width="1080" height="3" fill="#f43f5e" rx="1.5"/>

    <text x="20" y="24" class="ap-card-head" fill="#f8fafc">⚖ RELIABILITY-AWARE ADAPTIVE FUSION ENGINE &amp; CALIBRATED OUTPUT</text>
    
    <g transform="translate(20, 36)">
      <text x="0" y="18" class="ap-mono" fill="#f43f5e">• Exponential Hysteresis Weight Smoothing: α = 0.65 (Prevents high-frequency switching chatter)</text>
      <text x="0" y="34" class="ap-mono" fill="#34d399">• Health States: HEALTHY (≥0.70), DEGRADED (0.40..0.70), SEV_DEGRADED (0.15..0.40), FAILED (&lt;0.15)</text>
      <text x="0" y="50" class="ap-mono" fill="#38bdf8">• Dynamic Trend Derivatives: dR/dt (Anticipates impending dropouts)  •  Normalized Weights: w_cam + w_lidar = 1.0</text>
    </g>

    <rect x="830" y="20" width="230" height="60" rx="6" fill="#2d081f" stroke="#f43f5e" stroke-width="1.2"/>
    <text x="845" y="42" font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif" font-size="11" font-weight="700" fill="#f8fafc">CALIBRATED 3D OBSTACLES</text>
    <text x="845" y="62" class="ap-mono" fill="#f43f5e">MAE: 0.0888m • F1: 0.9852</text>
  </g>
</svg>"""

write_svg("architecture-pipeline.svg", ARCH_PIPELINE_SVG)

print("All 10 SVG diagrams generated successfully!")


