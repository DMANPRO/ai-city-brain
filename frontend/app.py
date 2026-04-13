import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import streamlit as st
import streamlit.components.v1 as components
import time, base64
from backend.orchestrator import run

st.set_page_config(
    page_title="AI City Brain",
    page_icon="●",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ─────────────────────────────── CSS ──────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Space+Mono:wght@400;700&display=swap');

:root {
    --bg:    #090e1a;
    --panel: #0e1525;
    --surf:  #131d30;
    --b1:    #1e2d45;
    --b2:    #263447;
    --acc:   #00d4aa;
    --acc2:  #00b894;
    --tx:    #e4ecf7;
    --sub:   #8fa3be;
    --faint: #3d5068;
    --red:   #f05470;
    --ylw:   #f5b731;
    --r:     4px;
}

/* Kill Streamlit chrome */
#MainMenu, footer, .stDeployButton,
[data-testid="stToolbar"],      [data-testid="stDecoration"],
[data-testid="stStatusWidget"], [data-testid="collapsedControl"],
[data-testid="stSidebar"],      header[data-testid="stHeader"],
button[aria-label*="sidebar"],  button[aria-label*="Sidebar"],
[class*="collapsedControl"],    [class*="sidebarButton"] {
    display: none !important;
}

/* Viewport containment */
html, body { overflow: hidden !important; height: 100vh !important; margin: 0; padding: 0; background: var(--bg) !important; }
.stApp    { height: 100vh !important; overflow: hidden !important; background: var(--bg) !important; font-family: 'Inter', sans-serif; color: var(--tx); }
[data-testid="stAppViewContainer"] { height: 100vh !important; overflow: hidden !important; }
section.main  { height: 100vh !important; overflow: hidden !important; padding: 0 !important; background: transparent !important; }
.block-container { height: 100vh !important; overflow: hidden !important; padding: 0 !important; max-width: 100% !important; background: transparent !important; }

/* Column row */
[data-testid="stHorizontalBlock"] { height: 100vh !important; overflow: hidden !important; gap: 0 !important; align-items: stretch !important; }

/* Both columns: full height, internal scroll, hidden scrollbar */
[data-testid="stColumn"] { height: 100vh !important; overflow: hidden !important; }
[data-testid="stColumn"] > div { height: 100% !important; overflow-y: auto !important; scrollbar-width: none !important; -ms-overflow-style: none !important; }
[data-testid="stColumn"] > div::-webkit-scrollbar { display: none !important; }

/* Left panel */
[data-testid="stHorizontalBlock"] > [data-testid="stColumn"]:first-child { background: var(--panel) !important; border-right: 1px solid var(--b1) !important; flex-shrink: 0 !important; }

/* Right panel */
[data-testid="stHorizontalBlock"] > [data-testid="stColumn"]:last-child { background: var(--bg) !important; }

/* Spacing resets */
[data-testid="stVerticalBlock"] { gap: 0 !important; }
.element-container { margin: 0 !important; padding: 0 !important; }
.stMarkdown { margin: 0 !important; }

/* Input field padding in left column */
[data-testid="stHorizontalBlock"] > [data-testid="stColumn"]:first-child .stTextInput { padding: 0 20px !important; }
[data-testid="stHorizontalBlock"] > [data-testid="stColumn"]:first-child .stButton    { padding: 8px 20px 0 20px !important; }

/* Input styles */
.stTextInput label { display: none !important; }
.stTextInput > div > div > input {
    background: var(--bg) !important; border: 1px solid var(--b1) !important;
    color: var(--tx) !important; font-family: 'Space Mono', monospace !important;
    font-size: 12px !important; border-radius: var(--r) !important;
    padding: 10px 12px !important; width: 100% !important;
    outline: none !important; caret-color: var(--acc) !important;
    transition: border-color .15s, box-shadow .15s !important;
}
.stTextInput > div > div > input:focus { border-color: var(--acc) !important; box-shadow: 0 0 0 3px rgba(0,212,170,.1) !important; }
.stTextInput > div > div > input::placeholder { color: var(--faint) !important; }

/* Button styles */
.stButton > button {
    background: var(--acc) !important; color: #060e1a !important;
    border: none !important; border-radius: var(--r) !important;
    font-family: 'Inter', sans-serif !important; font-weight: 600 !important;
    font-size: 12px !important; letter-spacing: .6px !important; text-transform: uppercase !important;
    width: 100% !important; padding: 12px 4px !important; cursor: pointer !important;
    transition: background .15s, box-shadow .15s, transform .1s !important;
}
.stButton > button:hover  { background: var(--acc2) !important; box-shadow: 0 4px 18px rgba(0,212,170,.25) !important; transform: translateY(-1px) !important; }
.stButton > button:active { transform: translateY(0) !important; }
.stButton > button *, .stButton > button p, .stButton > button span { color: #060e1a !important; font-weight: 600 !important; }

/* Hide spinner */
.stSpinner { display: none !important; }

/* iframes — always full width, no overflow */
iframe { width: 100% !important; max-width: 100% !important; border: none !important; display: block !important; overflow: hidden !important; }
[data-testid="stCustomComponentV1"] { width: 100% !important; max-width: 100% !important; overflow: hidden !important; }

/* Animations */
@keyframes pulse-dot { 0%,100%{box-shadow:0 0 0 0 rgba(0,212,170,.5)} 50%{box-shadow:0 0 0 5px rgba(0,212,170,0)} }
@keyframes spin       { to{transform:rotate(360deg)} }

/* Mobile */
@media (max-width:768px) {
    html,body,.stApp,[data-testid="stAppViewContainer"],section.main,.block-container,
    [data-testid="stHorizontalBlock"],[data-testid="stColumn"] { height:auto !important; overflow:visible !important; }
    [data-testid="stHorizontalBlock"] { flex-direction:column !important; }
    [data-testid="stHorizontalBlock"] > [data-testid="stColumn"]:first-child { width:100% !important; border-right:none !important; border-bottom:1px solid var(--b1) !important; min-height:auto !important; }
}
</style>
<script>
(function(){
    function hide(){
        ['[data-testid="collapsedControl"]','button[aria-label*="sidebar"]','[class*="collapsedControl"]']
        .forEach(s=>document.querySelectorAll(s).forEach(el=>{el.style.cssText='display:none!important;';}));
    }
    hide();
    new MutationObserver(hide).observe(document.documentElement,{childList:true,subtree:true});
})();
</script>
""", unsafe_allow_html=True)

# ── Colour maps ────────────────────────────────────────────────────────────────
COORDS = {
    "whitefield":      [12.9698,77.7499], "indiranagar":    [12.9784,77.6408],
    "koramangala":     [12.9352,77.6245], "hebbal":         [13.0354,77.5970],
    "marathahalli":    [12.9591,77.6972], "mg road":        [12.9757,77.6011],
    "electronic city": [12.8399,77.6770], "jayanagar":      [12.9308,77.5838],
    "yeshwanthpur":    [13.0280,77.5478], "hsr layout":     [12.9116,77.6389],
    "bengaluru":       [12.9716,77.5946], "bangalore":      [12.9716,77.5946],
    "bellandur":       [12.9257,77.6771], "sarjapur":       [12.9102,77.6874],
    "jp nagar":        [12.9061,77.5853], "silk board":     [12.9175,77.6237],
    "banashankari":    [12.9258,77.5461],
}
CMAP = {"critical":"#f05470","high":"#f05470","medium":"#f5b731","moderate":"#f5b731","low":"#00d4aa"}
AGENTS = [
    ("Scenario Agent",   "Parsing natural language input"),
    ("Traffic Engine",   "Fetching live flow data"),
    ("Congestion Model", "Computing congestion score"),
    ("Propagation",      "Simulating spread to zones"),
    ("Routing Engine",   "Generating optimal plan"),
    ("Explanation",      "Summarising analysis"),
]
IT = "font-family:'Inter',sans-serif;"
JM = "font-family:'Space Mono',monospace;"

# ── Helpers ────────────────────────────────────────────────────────────────────
def lp(html, pt=0, pb=0):
    return f'<div style="padding:{pt}px 24px {pb}px 24px;">{html}</div>'

def sec(label):
    return (f'<div style="{IT}font-size:10px;font-weight:600;letter-spacing:1.4px;'
            f'text-transform:uppercase;color:#3d5068;margin-bottom:12px;">{label}</div>')

def hr():
    return '<div style="height:1px;background:#1e2d45;"></div>'

def agent_log(done, active=None):
    rows = ""
    for i,(name,detail) in enumerate(AGENTS):
        if i < done:
            ic = (f'<div style="width:16px;height:16px;border-radius:50%;flex-shrink:0;'
                  f'background:#00d4aa18;border:1px solid #00d4aa50;display:flex;align-items:center;justify-content:center;">'
                  f'<div style="width:5px;height:5px;border-radius:50%;background:#00d4aa;"></div></div>')
            nc,dc = "#00d4aa","#3d5068"
        elif i == active:
            ic = (f'<div style="width:16px;height:16px;border-radius:50%;flex-shrink:0;'
                  f'border:2px solid #00d4aa;display:flex;align-items:center;justify-content:center;'
                  f'animation:spin 1s linear infinite;">'
                  f'<div style="width:4px;height:4px;border-radius:50%;background:#00d4aa;"></div></div>')
            nc,dc = "#e4ecf7","#8fa3be"
        else:
            ic = f'<div style="width:16px;height:16px;border-radius:50%;flex-shrink:0;border:1px solid #1e2d45;"></div>'
            nc,dc = "#2a3a52","#1e2d45"
        rows += (f'<div style="display:flex;align-items:center;gap:10px;padding:5px 0;">'
                 f'{ic}<div><div style="{IT}font-size:12px;font-weight:500;color:{nc};line-height:1.3;">{name}</div>'
                 f'<div style="{IT}font-size:10px;color:{dc};margin-top:1px;">{detail}</div></div></div>')
    return rows

# ── Map HTML (rendered inside iframe via components.html) ──────────────────────
def make_map(result=None):
    extra = ""
    if result:
        loc   = str(result.get("location","bengaluru")).lower().strip()
        cong  = str(result.get("congestion","medium")).lower()
        speed = result.get("avg_speed","—")
        trend = str(result.get("trend","stable")).title()
        # Try exact match, then partial
        center = COORDS.get(loc)
        if not center:
            for k,v in COORDS.items():
                if k in loc or loc in k:
                    center = v; break
        if not center:
            center = COORDS["bengaluru"]
        col   = CMAP.get(cong,"#f5b731")

        zone_js = ""
        for z in result.get("affected_zones",[]):
            if isinstance(z,dict) and "lat" in z and "lon" in z:
                zn = str(z.get("zone","Zone")).replace("-"," ").title()
                zone_js += (f'L.circle([{z["lat"]},{z["lon"]}],'
                            f'{{radius:600,color:"{col}",fillColor:"{col}",'
                            f'fillOpacity:.06,weight:1,dashArray:"4 8"}}).addTo(map)'
                            f'.bindPopup("<b>{zn}</b><br><small>Affected zone</small>");')

        loc_title = loc.replace("-"," ").title()
        extra = f"""
        var mk=L.divIcon({{
            html:'<div style="width:14px;height:14px;border-radius:50%;background:{col};border:2.5px solid rgba(255,255,255,.9);box-shadow:0 0 0 4px {col}30;"></div>',
            iconSize:[14,14],iconAnchor:[7,7],className:''
        }});
        L.marker([{center[0]},{center[1]}],{{icon:mk}}).addTo(map)
          .bindPopup('<div style="font-family:Inter,sans-serif;padding:2px 0;min-width:140px;">'
            +'<div style="font-size:13px;font-weight:600;margin-bottom:4px;">{loc_title}</div>'
            +'<div style="font-size:11px;color:#444;line-height:1.9;">'
            +'Congestion: <b style="color:{col}">{cong.upper()}</b><br>'
            +'Speed: <b>{speed} km/h</b><br>'
            +'Trend: <b>{trend}</b>'
            +'</div></div>').openPopup();
        L.circle([{center[0]},{center[1]}],{{radius:900,color:'{col}',fillColor:'{col}',fillOpacity:.05,weight:1}}).addTo(map);
        {zone_js}
        map.flyTo([{center[0]},{center[1]}],14,{{duration:1}});"""

    return f"""<!DOCTYPE html><html><head>
<meta name="viewport" content="width=device-width,initial-scale=1">
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"/>
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap" rel="stylesheet">
<style>
*{{margin:0;padding:0;box-sizing:border-box;}}html,body,#map{{width:100%;height:100%;background:#090e1a;}}
.leaflet-tile{{filter:brightness(.58) saturate(.4) hue-rotate(185deg);}}
.leaflet-popup-content-wrapper{{background:#fff;border-radius:6px;box-shadow:0 8px 24px rgba(0,0,0,.15);border:none;}}
.leaflet-popup-tip{{background:#fff;}}
.leaflet-popup-content{{margin:12px 16px;}}
.leaflet-control-zoom{{border:1px solid #1e2d45!important;border-radius:4px!important;}}
.leaflet-control-zoom a{{background:#0e1525!important;color:#8fa3be!important;border-color:#1e2d45!important;line-height:26px!important;}}
.leaflet-control-zoom a:hover{{background:#131d30!important;color:#e4ecf7!important;}}
.leaflet-control-attribution{{background:#0e152590!important;color:#3d5068!important;font-size:9px!important;}}
.leaflet-control-attribution a{{color:#3d5068!important;}}
</style></head><body>
<div id="map"></div>
<script>
var map=L.map('map').setView([12.9716,77.5946],12);
L.tileLayer('https://{{s}}.tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png',{{attribution:'© OpenStreetMap',maxZoom:19}}).addTo(map);
{extra}
window.addEventListener('resize',function(){{map.invalidateSize();}});
</script></body></html>"""

# ── Results HTML (rendered via components.html — guaranteed rendering) ─────────
def make_results(result):
    cong      = str(result.get("congestion","medium")).lower()
    location  = str(result.get("location","bengaluru")).replace("-"," ").title()
    t_str     = str(result.get("time","—"))
    speed     = result.get("avg_speed","—")
    trend     = str(result.get("trend","stable")).lower()
    delay     = result.get("estimated_delay","—")
    mode      = str(result.get("recommended_mode","—"))
    spread    = str(result.get("spread_level","—")).title()
    eff       = int(result.get("efficiency_score", 0))
    routes_l  = result.get("routes",[])
    best      = result.get("best_route",{})
    advisory  = str(result.get("travel_advisory",""))
    suggestions = result.get("suggestions",[])

    ao = result.get("agent_outputs",{})
    td = ao.get("traffic",{}); rd = ao.get("routes",{}); md = ao.get("mobility",{})

    ff        = td.get("free_flow_speed", result.get("free_flow_speed","—"))
    volume    = str(td.get("traffic_volume", result.get("traffic_volume","—"))).title()
    incidents = td.get("incident_count", result.get("incident_count",0))
    roadwork  = bool(td.get("road_work_active", result.get("road_work_active",False)))
    inc_types = td.get("incident_types", result.get("incident_types",[]))
    cong_score= td.get("congestion_score", result.get("congestion_score","—"))
    signal    = str(rd.get("signal_control",{}).get("signal_mode","—")).replace("_"," ").title()
    reroute   = rd.get("rerouting",{}).get("reroute", False)
    priority  = str(rd.get("priority","—"))
    eff_score = int(md.get("efficiency_score", eff))
    if advisory == "" and md:
        advisory = str(md.get("travel_advisory",""))
    if not suggestions and md:
        suggestions = md.get("suggestions",[])

    color  = CMAP.get(cong,"#f5b731")
    tc     = {"worsening":"#f05470","moderate":"#f5b731","stable":"#00d4aa"}.get(trend,"#00d4aa")
    sc     = f"{cong_score:.0f}" if isinstance(cong_score,(int,float)) else str(cong_score)
    ticon  = "↑" if trend=="worsening" else ("↓" if trend=="improving" else "→")
    ec     = "#00d4aa" if eff_score>70 else "#f5b731" if eff_score>40 else "#f05470"
    pri_c  = "#f05470" if priority.lower() in ("immediate","emergency") else "#f5b731" if priority.lower() in ("urgent","high") else "#8fa3be"

    def scard(label, val, unit="", ac=False):
        vc = "#00d4aa" if ac else "#e4ecf7"
        su = f'<span style="font-size:10px;font-weight:400;color:#3d5068;margin-left:3px;">{unit}</span>' if unit else ""
        return (f'<div style="background:#090e1a;border:1px solid #1e2d45;border-radius:4px;padding:11px 13px;">'
                f'<div style="font-size:10px;font-weight:500;color:#8fa3be;letter-spacing:.5px;text-transform:uppercase;margin-bottom:5px;">{label}</div>'
                f'<div style="font-size:15px;font-weight:700;color:{vc};">{val}{su}</div></div>')

    def icard(label, val, vc="#8fa3be"):
        return (f'<div style="background:#090e1a;border:1px solid #1e2d45;border-radius:4px;padding:9px 12px;">'
                f'<div style="font-size:10px;font-weight:500;color:#8fa3be;letter-spacing:.5px;text-transform:uppercase;margin-bottom:4px;">{label}</div>'
                f'<div style="font-size:12px;font-weight:500;color:{vc};">{val}</div></div>')

    # Best route card
    brt = ""
    if best and best.get("route"):
        bn = str(best.get("route","")).replace("_"," ").title()
        be = best.get("eta","—"); bd2 = best.get("distance","—")
        brt = (f'<div style="background:#090e1a;border:1px solid #00d4aa30;border-radius:4px;padding:12px 14px;margin-bottom:8px;">'
               f'<div style="font-size:10px;font-weight:600;color:#00d4aa;letter-spacing:.8px;text-transform:uppercase;margin-bottom:10px;">Recommended Route</div>'
               f'<div style="display:flex;align-items:center;justify-content:space-between;">'
               f'<div style="font-size:13px;font-weight:600;color:#e4ecf7;">{bn}</div>'
               f'<div style="display:flex;gap:18px;">'
               f'<div style="text-align:right;"><div style="font-size:14px;font-weight:700;color:#00d4aa;">{be}</div><div style="font-size:10px;color:#8fa3be;">min</div></div>'
               f'<div style="text-align:right;"><div style="font-size:14px;font-weight:700;color:#e4ecf7;">{bd2}</div><div style="font-size:10px;color:#8fa3be;">km</div></div>'
               f'</div></div></div>')

    # Route options
    art = ""
    if len(routes_l) > 1:
        rows = "".join(
            f'<div style="display:flex;align-items:center;justify-content:space-between;padding:7px 0;border-bottom:1px solid #1e2d45;">'
            f'<div style="font-size:12px;font-weight:500;color:{"#00d4aa" if r.get("route")==best.get("route") else "#e4ecf7"};">'
            f'{str(r.get("route","")).replace("_"," ").title()}'
            f'{"&nbsp;<span style=&quot;font-size:9px;background:#00d4aa15;border:1px solid #00d4aa40;color:#00d4aa;border-radius:3px;padding:1px 5px;&quot;>BEST</span>" if r.get("route")==best.get("route") else ""}'
            f'</div>'
            f'<div style="font-size:11px;color:#8fa3be;">{r.get("eta","—")} min · {r.get("distance","—")} km</div></div>'
            for r in routes_l
        )
        art = (f'<div style="background:#090e1a;border:1px solid #1e2d45;border-radius:4px;padding:12px 14px;margin-bottom:8px;">'
               f'<div style="font-size:10px;font-weight:600;color:#8fa3be;letter-spacing:.8px;text-transform:uppercase;margin-bottom:8px;">Route Options</div>'
               f'{rows}</div>')

    # Tags
    tags = "".join(
        f'<span style="font-size:10px;padding:3px 9px;border-radius:3px;border:1px solid #f0547030;color:#f05470;background:#f0547010;margin-right:5px;">{t}</span>'
        for t in inc_types
    )
    if roadwork:
        tags += '<span style="font-size:10px;padding:3px 9px;border-radius:3px;border:1px solid #f5b73130;color:#f5b731;background:#f5b73110;">Roadwork</span>'

    # Advisory
    adv = ""
    if advisory and advisory not in ("—",""):
        adv = (f'<div style="padding:10px 14px;background:#f5b73108;border:1px solid #f5b73120;border-radius:4px;margin-bottom:8px;">'
               f'<div style="font-size:11px;color:#f5b731;line-height:1.65;"><span style="font-weight:600;">Advisory · </span>{advisory}</div></div>')

    # Suggestions
    sugg = ""
    if suggestions:
        items = "".join(f'<div style="display:flex;gap:8px;padding:3px 0;font-size:11px;color:#8fa3be;"><span style="color:#00d4aa;font-weight:600;flex-shrink:0;">→</span><span>{s}</span></div>' for s in suggestions)
        sugg = f'<div style="margin-bottom:8px;">{items}</div>'

    # Full self-contained HTML (rendered via components.html for guaranteed rendering)
    return f"""<!DOCTYPE html><html><head>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Space+Mono:wght@400;700&display=swap" rel="stylesheet">
<style>
*{{box-sizing:border-box;margin:0;padding:0;}}
body{{font-family:'Inter',sans-serif;background:#090e1a;color:#e4ecf7;padding:20px 24px 28px;}}
@keyframes pulse-dot{{0%,100%{{box-shadow:0 0 0 0 rgba(0,212,170,.5)}}50%{{box-shadow:0 0 0 5px rgba(0,212,170,0)}}}}
</style></head><body>
<div style="display:flex;align-items:flex-start;justify-content:space-between;padding-bottom:16px;border-bottom:1px solid #1e2d45;margin-bottom:16px;">
  <div>
    <div style="font-size:22px;font-weight:700;letter-spacing:-.3px;text-transform:capitalize;">{location}</div>
    <div style="display:flex;align-items:center;gap:8px;margin-top:6px;flex-wrap:wrap;">
      <div style="width:8px;height:8px;border-radius:50%;background:{color};box-shadow:0 0 8px {color};animation:pulse-dot 2s infinite;flex-shrink:0;"></div>
      <span style="font-size:12px;font-weight:600;color:{color};text-transform:uppercase;letter-spacing:.5px;">{cong}</span>
      <span style="font-size:12px;color:#3d5068;">· Score {sc}</span>
      <span style="font-size:12px;color:#3d5068;">· {t_str}</span>
    </div>
  </div>
  <div style="text-align:right;flex-shrink:0;margin-left:12px;">
    <div style="font-family:'Space Mono',monospace;font-size:26px;font-weight:700;color:{color};line-height:1;">{speed}</div>
    <div style="font-size:10px;color:#8fa3be;margin-top:2px;">km/h avg</div>
  </div>
</div>
<div style="display:grid;grid-template-columns:repeat(3,1fr);gap:8px;margin-bottom:8px;">
  {scard("Free Flow",ff,"km/h")}{scard("Volume",volume)}{scard("Incidents",incidents)}
  {scard("Spread",spread)}{scard("Mode",mode,"",True)}{scard("Delay",delay)}
</div>
<div style="display:grid;grid-template-columns:repeat(3,1fr);gap:8px;margin-bottom:8px;">
  {icard("Trend",f"{ticon} {trend.title()}",tc)}{icard("Signal",signal)}{icard("Priority",priority,pri_c)}
</div>
{brt}{art}
<div style="background:#090e1a;border:1px solid #1e2d45;border-radius:4px;padding:12px 14px;margin-bottom:8px;">
  <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px;">
    <div style="font-size:10px;font-weight:600;color:#8fa3be;letter-spacing:.8px;text-transform:uppercase;">Travel Efficiency</div>
    <div style="font-family:'Space Mono',monospace;font-size:13px;font-weight:700;color:{ec};">{eff_score}%</div>
  </div>
  <div style="height:4px;background:#1e2d45;border-radius:2px;overflow:hidden;">
    <div style="height:100%;width:{eff_score}%;background:{ec};border-radius:2px;"></div>
  </div>
</div>
<div style="background:#090e1a;border:1px solid #1e2d45;border-radius:4px;padding:9px 13px;margin-bottom:8px;display:flex;align-items:center;justify-content:space-between;">
  <span style="font-size:11px;font-weight:500;color:#8fa3be;">Rerouting</span>
  <span style="font-size:12px;font-weight:600;color:{'#00d4aa' if reroute else '#3d5068'};">{'Active' if reroute else 'None'}</span>
</div>
{'<div style="display:flex;flex-wrap:wrap;gap:6px;margin-bottom:8px;">'+tags+'</div>' if tags else ""}
{adv}{sugg}
</body></html>"""

# ── Session state ──────────────────────────────────────────────────────────────
if "result" not in st.session_state:
    st.session_state.result = None

has_result = st.session_state.result is not None

# ── Layout columns ─────────────────────────────────────────────────────────────
LEFT, RIGHT = st.columns([9, 22], gap="small")

# ══════════════ LEFT PANEL ════════════════════════════════════════════════════
with LEFT:
    dot_col   = "#00d4aa"   if has_result else "#263447"
    dot_anim  = "animation:pulse-dot 2s infinite;" if has_result else ""
    badge_t   = "Live"      if has_result else "Ready"
    badge_bg  = "#00d4aa18" if has_result else "transparent"
    badge_bd  = "#00d4aa40" if has_result else "#1e2d45"
    badge_tc  = "#00d4aa"   if has_result else "#3d5068"

    # Header
    st.markdown(f"""
<div style="padding:24px 24px 20px;border-bottom:1px solid #1e2d45;">
  <div style="display:flex;align-items:center;justify-content:space-between;">
    <div>
      <div style="{IT}font-size:17px;font-weight:700;color:#e4ecf7;letter-spacing:-.3px;">AI City Brain</div>
      <div style="{IT}font-size:11px;color:#3d5068;margin-top:3px;">Bengaluru traffic intelligence</div>
    </div>
    <div style="display:flex;align-items:center;gap:7px;padding:4px 10px;border-radius:20px;background:{badge_bg};border:1px solid {badge_bd};">
      <div style="width:6px;height:6px;border-radius:50%;background:{dot_col};{dot_anim}flex-shrink:0;"></div>
      <span style="{IT}font-size:10px;font-weight:600;color:{badge_tc};letter-spacing:.4px;">{badge_t}</span>
    </div>
  </div>
</div>
<style>
@keyframes pulse-dot{{0%,100%{{box-shadow:0 0 0 0 rgba(0,212,170,.5)}}50%{{box-shadow:0 0 0 5px rgba(0,212,170,0)}}}}
@keyframes spin{{to{{transform:rotate(360deg)}}}}
</style>""", unsafe_allow_html=True)

    # Scenario label + live feed badge
    st.markdown(lp(
        sec("Scenario Input") +
        f'<div style="display:flex;align-items:center;gap:8px;padding:8px 11px;border-radius:4px;'
        f'background:#00d4aa08;border:1px solid #00d4aa18;{IT}font-size:11px;font-weight:500;color:#00d4aa;margin-bottom:12px;">'
        f'<div style="width:5px;height:5px;border-radius:50%;background:#00d4aa;flex-shrink:0;"></div>'
        f'Live feed active · clear · --°C</div>',
        pt=20, pb=0
    ), unsafe_allow_html=True)

    # Input widgets (CSS handles 24px side padding)
    user_input = st.text_input("q", placeholder="e.g. Koramangala at 8am rain", label_visibility="collapsed")
    analyze    = st.button("Analyze Traffic")
    err_ph     = st.empty()

    # Agent pipeline
    st.markdown(hr(), unsafe_allow_html=True)
    st.markdown(lp(sec("Agent Pipeline"), pt=16, pb=0), unsafe_allow_html=True)
    log_ph = st.empty()
    if has_result:
        log_ph.markdown(lp(agent_log(len(AGENTS)), pt=4, pb=4), unsafe_allow_html=True)
    else:
        log_ph.markdown(lp(f'<div style="{IT}font-size:11px;color:#263447;line-height:2;">Run analysis to see agents.</div>', pt=4, pb=4), unsafe_allow_html=True)

    # Explanation
    st.markdown(hr(), unsafe_allow_html=True)
    st.markdown(lp(sec("Analysis Summary"), pt=16, pb=0), unsafe_allow_html=True)
    exp_ph = st.empty()
    if has_result:
        expl = st.session_state.result.get("explanation","")
        exp_ph.markdown(lp(f'<div style="{IT}font-size:12px;line-height:1.85;color:#8fa3be;">{expl}</div>', pt=0, pb=24), unsafe_allow_html=True)
    else:
        exp_ph.markdown(lp(f'<div style="{IT}font-size:11px;color:#263447;line-height:1.8;">Summary will appear here after analysis.</div>', pt=0, pb=24), unsafe_allow_html=True)

# ══════════════ RIGHT PANEL ═══════════════════════════════════════════════════
with RIGHT:
    # Top bar
    st.markdown(f"""
<div style="padding:16px 24px;border-bottom:1px solid #1e2d45;display:flex;align-items:center;justify-content:space-between;">
  <div style="{IT}font-size:13px;font-weight:600;color:#e4ecf7;">City Map</div>
  <div style="{IT}font-size:11px;color:#3d5068;">Bengaluru Metropolitan · OpenStreetMap</div>
</div>""", unsafe_allow_html=True)

    # Map placeholder — components.html always renders correctly
    st.markdown("""
<div style="padding:16px 24px 0 24px;">
  <div style="border:1px solid #1e2d45;border-radius:6px;overflow:hidden;background:#090e1a;">
""", unsafe_allow_html=True)
    map_ph = st.empty()
    with map_ph:
        components.html(make_map(st.session_state.result), height=340, scrolling=False)
    st.markdown("</div></div>", unsafe_allow_html=True)

    st.markdown(hr(), unsafe_allow_html=True)

    # Results — use components.html (full standalone HTML, no markdown parser)
    if has_result:
        components.html(make_results(st.session_state.result), height=640, scrolling=True)
    else:
        st.markdown(
            f'<div style="padding:40px 24px;text-align:center;">'
            f'<div style="width:40px;height:40px;border-radius:50%;border:1px solid #1e2d45;'
            f'margin:0 auto 16px;display:flex;align-items:center;justify-content:center;">'
            f'<div style="width:10px;height:10px;border-radius:50%;background:#1e2d45;"></div></div>'
            f'<div style="{IT}font-size:13px;font-weight:500;color:#3d5068;margin-bottom:8px;">No Analysis Yet</div>'
            f'<div style="{IT}font-size:11px;color:#263447;line-height:1.8;">'
            f'Enter a location and time in the left panel<br>to generate a live traffic analysis.</div></div>',
            unsafe_allow_html=True
        )

# ── Analyse logic ─────────────────────────────────────────────────────────────
if analyze:
    if not user_input.strip():
        err_ph.markdown(
            f'<div style="margin:8px 24px 0;padding:9px 12px;border-radius:4px;{IT}font-size:11px;'
            f'color:#f05470;background:#f0547010;border:1px solid #f0547030;">'
            f'Enter a query — e.g. "traffic in Whitefield at 6pm"</div>',
            unsafe_allow_html=True
        )
    else:
        err_ph.empty()

        # Animate agent log
        for i in range(len(AGENTS)):
            log_ph.markdown(lp(agent_log(i, i), pt=4, pb=4), unsafe_allow_html=True)
            time.sleep(0.35)
        log_ph.markdown(lp(agent_log(len(AGENTS)), pt=4, pb=4), unsafe_allow_html=True)

        # Run backend
        result = run(user_input)

        if "error" in result:
            err_ph.markdown(
                f'<div style="margin:8px 24px 0;padding:9px 12px;border-radius:4px;{IT}font-size:11px;'
                f'color:#f05470;background:#f0547010;border:1px solid #f0547030;">'
                f'{result.get("error","Unknown error")}</div>',
                unsafe_allow_html=True
            )
        else:
            st.session_state.result = result

            # Update map immediately in placeholder
            with map_ph:
                components.html(make_map(result), height=340, scrolling=False)

            # Animate explanation word by word
            st.markdown(hr(), unsafe_allow_html=True)
            st.markdown(lp(sec("Analysis Summary"), pt=16, pb=0), unsafe_allow_html=True)
            words, rendered = result.get("explanation","").split(), ""
            for w in words:
                rendered += w + " "
                exp_ph.markdown(
                    lp(f'<div style="{IT}font-size:12px;line-height:1.85;color:#8fa3be;">{rendered}</div>', pt=0, pb=24),
                    unsafe_allow_html=True
                )
                time.sleep(0.05)

            # Rerun so results render via components.html in the RIGHT panel
            st.rerun()
