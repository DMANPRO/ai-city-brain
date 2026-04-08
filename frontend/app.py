# frontend/app.py — AI City Brain — Premium UI v3
# Run: streamlit run frontend/app.py (from project root)

import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import math
import base64
import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
from datetime import datetime

from backend.orchestrator import run
from backend.agents.explanation_agent import generate_audio

st.set_page_config(
    page_title="AI City Brain",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ── CSS ───────────────────────────────────────────────────────────────────────
def inject_css():
    st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');
html,body,[class*="css"]{font-family:'Inter',sans-serif !important;}
.stApp{background:#0a101f !important;}
.block-container{padding:1.8rem 2.2rem 4rem !important;max-width:1080px !important;}
#MainMenu,footer,header,[data-testid="stToolbar"],[data-testid="stDecoration"]
  {visibility:hidden !important;display:none !important;}

.hdr{background:linear-gradient(130deg,#0c4a6e 0%,#0369a1 45%,#0891b2 100%);
  border-radius:18px;padding:26px 28px;margin-bottom:22px;position:relative;overflow:hidden;}
.hdr::after{content:'';position:absolute;top:-60%;right:-8%;width:260px;height:260px;
  background:rgba(255,255,255,0.05);border-radius:50%;pointer-events:none;}
.hdr h1{font-size:clamp(1.3rem,3.5vw,1.9rem);font-weight:700;color:#fff;margin:0;letter-spacing:-.3px;}
.hdr p{color:rgba(255,255,255,0.72);margin:5px 0 0;font-size:.85rem;font-weight:400;}
.badge{display:inline-flex;align-items:center;gap:7px;background:rgba(255,255,255,0.1);
  border:1px solid rgba(255,255,255,0.18);border-radius:20px;padding:4px 13px;
  font-size:.7rem;color:rgba(255,255,255,0.85);margin-top:14px;}
.dot{width:7px;height:7px;background:#4ade80;border-radius:50%;animation:blink 2s ease infinite;}
@keyframes blink{0%,100%{opacity:1}50%{opacity:.35}}

.lbl{font-size:.72rem;font-weight:600;color:#4a6080;text-transform:uppercase;
  letter-spacing:.8px;margin:20px 0 7px 2px;}

.stTextInput>div>div>input{background:#111c30 !important;border:1.5px solid #1e3050 !important;
  border-radius:12px !important;color:#e2e8f0 !important;padding:13px 16px !important;
  font-size:.92rem !important;font-family:'DM Sans',sans-serif !important;
  transition:border-color .2s,box-shadow .2s !important;}
.stTextInput>div>div>input:focus{border-color:#0891b2 !important;
  box-shadow:0 0 0 3px rgba(8,145,178,.15) !important;}
.stTextInput>div>div>input::placeholder{color:#2d4060 !important;}

.stButton>button{background:linear-gradient(135deg,#0369a1,#0891b2) !important;
  color:#fff !important;border:none !important;border-radius:12px !important;
  padding:13px !important;font-size:.92rem !important;font-weight:600 !important;
  width:100% !important;margin-top:10px !important;letter-spacing:.2px !important;
  font-family:'DM Sans',sans-serif !important;transition:all .2s !important;}
.stButton>button:hover{transform:translateY(-2px) !important;
  box-shadow:0 8px 22px rgba(8,145,178,.35) !important;}
.stButton>button:active{transform:translateY(0) !important;}

.banner{border-radius:13px;padding:14px 20px;display:flex;align-items:center;
  gap:12px;margin:18px 0 6px;font-weight:600;font-size:.92rem;animation:rise .4s ease;}
@keyframes rise{from{opacity:0;transform:translateY(7px)}to{opacity:1;transform:translateY(0)}}
.b-high  {background:rgba(239,68,68,.1); border:1px solid rgba(239,68,68,.32); color:#fca5a5;}
.b-medium{background:rgba(245,158,11,.1);border:1px solid rgba(245,158,11,.32);color:#fde68a;}
.b-low   {background:rgba(34,197,94,.1); border:1px solid rgba(34,197,94,.32); color:#86efac;}

.mgrid{display:grid;grid-template-columns:repeat(3,1fr);gap:13px;margin:18px 0;}
.mcard{background:#111c30;border:1px solid #1a2d48;border-radius:16px;padding:18px 14px;
  text-align:center;transition:transform .2s,box-shadow .2s;animation:rise .5s ease;}
.mcard:hover{transform:translateY(-3px);box-shadow:0 8px 22px rgba(0,0,0,.4);}
.mi{font-size:1.5rem;margin-bottom:7px;}
.mv{font-size:1rem;font-weight:700;margin-bottom:4px;letter-spacing:-.1px;}
.ml{font-size:.67rem;color:#3d5570;text-transform:uppercase;letter-spacing:.6px;font-weight:600;}
.r{color:#ef4444}.a{color:#f59e0b}.g{color:#22c55e}
.c{color:#06b6d4}.b{color:#60a5fa}.p{color:#a78bfa}

.igrid{display:grid;grid-template-columns:repeat(2,1fr);gap:14px;margin:16px 0;}
.icard{background:#111c30;border:1px solid #1a2d48;border-radius:16px;
  padding:20px 18px;animation:rise .5s ease;}
.ictitle{font-size:.68rem;font-weight:700;color:#0891b2;text-transform:uppercase;
  letter-spacing:.8px;margin-bottom:14px;}
.irow{display:flex;justify-content:space-between;align-items:flex-start;
  padding:7px 0;border-bottom:1px solid #172236;font-size:.82rem;gap:12px;}
.irow:last-child{border-bottom:none;}
.ik{color:#3d5570;font-weight:500;}
.iv{color:#d1ddf5;font-weight:600;text-align:right;}
.pills{display:flex;flex-wrap:wrap;gap:7px;margin-top:10px;}
.pill{background:#0c1e38;color:#7dd3fc;border:1px solid #1e4878;
  border-radius:20px;padding:4px 12px;font-size:.72rem;font-weight:500;}

.rcard{background:rgba(245,158,11,.07);border:1px solid rgba(245,158,11,.26);
  border-radius:13px;padding:18px 20px;font-size:.84rem;line-height:1.8;
  color:#e2e8f0;margin:10px 0;animation:rise .5s ease;}
.rcard strong{color:#fbbf24;}

.emgbanner{background:rgba(239,68,68,.1);border:1.5px solid #ef4444;
  border-radius:13px;padding:15px 20px;color:#fca5a5;font-weight:600;
  font-size:.9rem;margin:10px 0;animation:pulse 1.5s ease infinite;}
@keyframes pulse{0%,100%{box-shadow:0 0 0 0 rgba(239,68,68,0)}
  50%{box-shadow:0 0 10px 2px rgba(239,68,68,.2)}}

.slabel{font-size:.68rem;font-weight:700;color:#0891b2;text-transform:uppercase;
  letter-spacing:.9px;margin:26px 0 12px;display:flex;align-items:center;gap:10px;}
.slabel::after{content:'';flex:1;height:1px;background:#172236;}

audio{width:100% !important;border-radius:12px !important;margin-top:4px !important;}
.vhint{font-size:.68rem;color:#2d4060;text-align:center;margin-top:5px;}

[data-testid="stExpander"]>div:first-child{background:#111c30 !important;
  border-radius:12px !important;border:1px solid #1a2d48 !important;color:#4a6080 !important;}
[data-testid="stDeckGlJsonChart"]{border-radius:16px !important;overflow:hidden !important;}

::-webkit-scrollbar{width:5px}
::-webkit-scrollbar-track{background:#0a101f}
::-webkit-scrollbar-thumb{background:#1a2d48;border-radius:3px}

@media (max-width:768px){
  .block-container{padding:.9rem .9rem 3rem !important;}
  .mgrid{grid-template-columns:repeat(2,1fr) !important;}
  .igrid{grid-template-columns:1fr !important;}
}
@media (max-width:400px){.mcard{padding:12px 8px;}.mi{font-size:1.2rem;}.mv{font-size:.85rem;}}
@media (orientation:landscape) and (max-height:500px){
  .hdr{padding:12px 18px;}.hdr h1{font-size:1.1rem;}.hdr p,.badge{display:none;}}
</style>""", unsafe_allow_html=True)


# ── Helpers ───────────────────────────────────────────────────────────────────
def cg_cls(v): return {"high":"r","medium":"a","low":"g"}.get(str(v).lower(),"c")
def bn_cls(v): return {"high":"b-high","medium":"b-medium","low":"b-low"}.get(str(v).lower(),"b-low")
def cg_em(v):  return {"high":"🔴","medium":"🟡","low":"🟢"}.get(str(v).lower(),"⚪")
WI = {"rain":"🌧️","clear":"☀️","fog":"🌫️","storm":"⛈️","cloudy":"☁️","mist":"🌫️","drizzle":"🌦️"}
def irow(k,v): return f'<div class="irow"><span class="ik">{k}</span><span class="iv">{v}</span></div>'


# ── Metrics ───────────────────────────────────────────────────────────────────
def render_metrics(r):
    cc = cg_cls(r.get("congestion",""))
    st.markdown(f"""
<div class="mgrid">
  <div class="mcard"><div class="mi">🚦</div>
    <div class="mv {cc}">{str(r.get("congestion","-")).upper()}</div>
    <div class="ml">Congestion</div></div>
  <div class="mcard"><div class="mi">🚗</div>
    <div class="mv c">{r.get("avg_speed","-")} km/h</div>
    <div class="ml">Avg Speed</div></div>
  <div class="mcard"><div class="mi">⏱️</div>
    <div class="mv a">{r.get("estimated_delay","-")}</div>
    <div class="ml">Est. Delay</div></div>
  <div class="mcard"><div class="mi">🚌</div>
    <div class="mv b">{str(r.get("recommended_mode","-")).upper()}</div>
    <div class="ml">Best Mode</div></div>
  <div class="mcard"><div class="mi">📉</div>
    <div class="mv a">{str(r.get("trend","-")).upper()}</div>
    <div class="ml">Trend</div></div>
  <div class="mcard"><div class="mi">📊</div>
    <div class="mv p">{r.get("congestion_score","-")}</div>
    <div class="ml">Score</div></div>
</div>""", unsafe_allow_html=True)


# ── Info Cards ────────────────────────────────────────────────────────────────
def render_info(r):
    sig   = r.get("signal_control", {})
    pills = "".join(f'<span class="pill">{s}</span>' for s in r.get("suggestions",[]))
    wi    = WI.get(str(r.get("weather","")).lower(),"🌤️")
    rw    = "⚠️ Yes" if r.get("roadwork_active") else "✅ No"
    tdate = r.get("target_date","Now (Live)")
    st.markdown(f"""
<div class="igrid">
  <div class="icard">
    <div class="ictitle">🌆 Real-Time Conditions</div>
    {irow("Location",      r.get("location","-"))}
    {irow("Scenario Date", tdate)}
    {irow("Weather",       f"{wi} {str(r.get('weather','-')).capitalize()}")}
    {irow("Time",          r.get("time","-"))}
    {irow("Free Flow",     f"{r.get('free_flow_speed','-')} km/h")}
    {irow("Volume",        str(r.get("traffic_volume","-")).capitalize())}
    {irow("Incidents",     r.get("incident_count","0"))}
    {irow("Roadwork",      rw)}
  </div>
  <div class="icard">
    <div class="ictitle">🚦 Signal &amp; Advisory</div>
    {irow("Signal Mode",   sig.get("signal_mode","-"))}
    {irow("Action",        sig.get("description","-"))}
    {irow("Cycle Adj.",    sig.get("cycle_adjustment","-"))}
    {irow("Advisory",      r.get("travel_advisory","-"))}
    {irow("Experience",    r.get("experience_level","-"))}
    {irow("Spread",        str(r.get("spread_level","-")).upper())}
    <div class="pills">{pills}</div>
  </div>
</div>""", unsafe_allow_html=True)


# ── Typewriter + Voice ────────────────────────────────────────────────────────
def render_typewriter_voice(text: str, audio_bytes):
    audio_tag = ""
    if audio_bytes:
        b64 = base64.b64encode(audio_bytes).decode()
        audio_tag = f'<audio autoplay><source src="data:audio/mp3;base64,{b64}" type="audio/mp3"></audio>'

    safe = (text.replace("\\","\\\\").replace("`","\\`")
                .replace("<","&lt;").replace(">","&gt;"))

    components.html(f"""
<link href="https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;600&display=swap" rel="stylesheet">
<style>
  *{{box-sizing:border-box;margin:0;padding:0}}
  body{{background:transparent;font-family:'DM Sans',sans-serif}}
  .card{{background:linear-gradient(135deg,#0c1e38,#0d2545);
    border:1px solid #1565a0;border-radius:16px;padding:22px 20px;}}
  .lbl{{font-size:.68rem;font-weight:700;color:#0891b2;
    text-transform:uppercase;letter-spacing:.8px;margin-bottom:12px}}
  .body{{font-size:.93rem;line-height:1.8;color:#bfdbfe;
    font-style:italic;min-height:72px}}
  .cur{{display:inline-block;width:2px;height:.95em;background:#0891b2;
    margin-left:1px;vertical-align:text-bottom;
    animation:blink .65s steps(1) infinite}}
  @keyframes blink{{0%,100%{{opacity:1}}50%{{opacity:0}}}}
</style>
{audio_tag}
<div class="card">
  <div class="lbl">🤖 AI Explanation</div>
  <div class="body" id="tw"><span class="cur"></span></div>
</div>
<script>
  const txt=`{safe}`;
  const el=document.getElementById('tw');
  let i=0;
  function type(){{
    if(i<txt.length){{
      const cur=el.querySelector('.cur');
      el.insertBefore(document.createTextNode(txt[i]),cur);
      i++;setTimeout(type,28);
    }}else{{
      const cur=el.querySelector('.cur');
      if(cur)cur.style.display='none';
    }}
  }}
  setTimeout(type,350);
</script>
""", height=175)


# ── Interactive Map ───────────────────────────────────────────────────────────

def render_map(result: dict, zones: list):
    try:
        import pydeck as pdk
        import os
        from dotenv import load_dotenv
        load_dotenv()

        TOMTOM_KEY = os.getenv("TOMTOM_API_KEY", "")

        clat  = zones[0]["lat"]
        clon  = zones[0]["lon"]
        score = float(result.get("congestion_score") or 0)

        # Layer 1 — TomTom live traffic tile overlay (real road colors)
        traffic_tile = pdk.Layer(
            "TileLayer",
            data=(
                f"https://api.tomtom.com/traffic/map/4/tile/flow/relative0"
                f"/{{z}}/{{x}}/{{y}}.png?key={TOMTOM_KEY}"
            ),
            min_zoom=0,
            max_zoom=19,
            opacity=0.75,
            pickable=False,
        )

        # Layer 2 — Heatmap for congestion impact zone
        heat_layer = pdk.Layer(
            "HeatmapLayer",
            data=[{"lat": clat, "lon": clon, "weight": min(score / 150, 1.0)}],
            get_position=["lon", "lat"],
            get_weight="weight",
            radius_pixels=110,
            intensity=2.5,
            threshold=0.04,
            color_range=[
                [34,  197, 94,  180],
                [234, 179, 8,   200],
                [245, 158, 11,  210],
                [239, 68,  68,  230],
            ],
            pickable=False,
        )

        # Layer 3 — Center dot for queried hotspot
        dot_color = (
            [239, 68,  68,  240] if score > 70 else
            [245, 158, 11,  240] if score > 40 else
            [34,  197, 94,  240]
        )
        center_dot = pdk.Layer(
            "ScatterplotLayer",
            data=[{"lat": clat, "lon": clon}],
            get_position=["lon", "lat"],
            get_fill_color=dot_color[:3] + [200],
            get_line_color=[255, 255, 255, 230],
            get_radius=350,
            line_width_min_pixels=2,
            stroked=True,
            filled=True,
            pickable=True,
        )

        st.pydeck_chart(pdk.Deck(
            layers=[traffic_tile, heat_layer, center_dot],
            initial_view_state=pdk.ViewState(
                latitude=clat, longitude=clon,
                zoom=12, pitch=35, bearing=0),
            map_style="https://basemaps.cartocdn.com/gl/dark-matter-gl-style/style.json",
        ))

    except Exception as e:
        st.warning(f"Map error: {e}")

# ══════════════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════════════
inject_css()

now_str = datetime.now().strftime("%d %b %Y, %I:%M %p")
st.markdown(f"""
<div class="hdr">
  <h1>🧠 AI City Brain</h1>
  <p>Real-Time Urban Traffic Intelligence — Bengaluru</p>
  <div class="badge"><div class="dot"></div>Live &nbsp;·&nbsp; {now_str}</div>
</div>""", unsafe_allow_html=True)

st.markdown('<p class="lbl">📍 Traffic Scenario</p>', unsafe_allow_html=True)
user_input = st.text_input("",
    placeholder="e.g.  Heavy rain at 6 PM in Whitefield  /  Storm next Monday at 9 AM in Koramangala",
    label_visibility="collapsed")
analyze = st.button("🔍  Analyze Traffic")

if analyze:
    if not user_input.strip():
        st.warning("Please enter a scenario.")
    else:
        with st.spinner("⚡ Fetching live data…"):
            result = run(user_input)

        if "error" in result:
            st.markdown(f'<div class="emgbanner">❌ {result["error"]}</div>',
                        unsafe_allow_html=True)
        else:
            cg = str(result.get("congestion","low")).lower()

            # Status banner
            st.markdown(f"""
<div class="banner {bn_cls(cg)}">
  {cg_em(cg)}&nbsp;<strong>{cg.upper()} CONGESTION</strong>
  &nbsp;—&nbsp;{result.get("location","Bengaluru")}
  &nbsp;·&nbsp;{result.get("target_date","Now")}
</div>""", unsafe_allow_html=True)

            # Metrics
            render_metrics(result)

            # Typewriter + voice
            st.markdown('<p class="slabel">🤖 AI Explanation &amp; Voice</p>',
                        unsafe_allow_html=True)
            with st.spinner("Generating voice…"):
                audio_bytes = generate_audio(result.get("explanation",""))
            render_typewriter_voice(result.get("explanation",""), audio_bytes)
            st.markdown('<p class="vhint">🎧 Voice auto-plays · tap player to replay</p>',
                        unsafe_allow_html=True)

            # Info cards
            st.markdown('<p class="slabel">📡 Live Conditions &amp; Signals</p>',
                        unsafe_allow_html=True)
            render_info(result)

            # Rerouting card
            rt = result.get("rerouting",{})
            if rt.get("reroute"):
                routes_str = ", ".join(rt.get("routes",[])) or "N/A"
                st.markdown(f"""
<p class="slabel">🗺️ Rerouting Plan</p>
<div class="rcard">
  <strong>Strategy:</strong> {rt.get("strategy","-")}<br>
  <strong>Alternate Routes:</strong> {routes_str}<br>
  <strong>Priority:</strong> {rt.get("priority","-")}
</div>""", unsafe_allow_html=True)

            # Emergency
            em = result.get("emergency",{})
            if em.get("emergency_mode"):
                st.markdown(f'<div class="emgbanner">🚨 EMERGENCY — {em.get("description","")}</div>',
                            unsafe_allow_html=True)

            # Map — always show if we have zones (guaranteed now)
            zones = result.get("affected_zones", [])
            if zones:
                st.markdown('<p class="slabel">🗺️ Live Traffic Map</p>',
                            unsafe_allow_html=True)
                render_map(result, zones)

            # Raw output
            with st.expander("📦 Full Raw Output"):
                st.json(result)
