from __future__ import annotations

import base64
from pathlib import Path

import streamlit as st


BOOT_DURATION_MS = 6760


def render_boot_sequence() -> None:
    """Render the one-time RepoPulse v2.0 cinematic boot overlay.

    The animation is intentionally CSS/SVG based: no video asset, no blocking
    sleep, and no artificial progress percentage. It is shown once per
    Streamlit browser session and fades away within three seconds.
    """
    if st.session_state.get("repopulse_boot_seen", False):
        return

    st.session_state["repopulse_boot_seen"] = True

    logo_path = Path(__file__).resolve().parents[1] / "assets" / "final-logo.png"
    logo_b64 = base64.b64encode(logo_path.read_bytes()).decode("ascii")

    boot_html = f"""
        <div class="rp-boot" aria-label="RepoPulse initializing">
          <div class="rp-boot-noise"></div>
          <div class="rp-boot-grid"></div>

          <div class="rp-boot-stage">
            <div class="rp-boot-signal signal-a"></div>
            <div class="rp-boot-signal signal-b"></div>
            <div class="rp-boot-signal signal-c"></div>
            <div class="rp-boot-signal signal-d"></div>

            <div class="rp-boot-orbit orbit-one"></div>
            <div class="rp-boot-orbit orbit-two"></div>
            <div class="rp-boot-orbit orbit-three"></div>
            <div class="rp-boot-scan"></div>
            <div class="rp-boot-core-glow"></div>

            <div class="rp-boot-logo-wrap">
              <div class="rp-boot-logo-halo"></div>
              <img class="rp-boot-logo" src="data:image/png;base64,{logo_b64}" alt="RepoPulse" />
            </div>

            <div class="rp-boot-wordmark">REPOPULSE</div>
            <div class="rp-boot-subtitle">REPOSITORY INTELLIGENCE</div>

            <div class="rp-boot-status">
              <span class="rp-boot-status-dot"></span>
              <span>INITIALIZING INTELLIGENCE</span>
            </div>
          </div>
        </div>

        <style>
        .rp-boot,
        .rp-boot * {{ box-sizing: border-box; }}

        .rp-boot {{
          position: fixed;
          inset: 0;
          z-index: 2147483000;
          overflow: hidden;
          display: grid;
          place-items: center;
          background:
            radial-gradient(circle at 50% 47%, rgba(98, 70, 255, .13), transparent 24%),
            radial-gradient(circle at 50% 50%, rgba(22, 34, 102, .18), transparent 43%),
            #03050d;
          color: #f6f3ff;
          pointer-events: auto;
          animation: rpBootExit 760ms cubic-bezier(.22,.61,.36,1) forwards;
          animation-delay: 2000ms;
        }}

        .rp-boot-grid {{
          position: absolute;
          inset: -20%;
          opacity: .22;
          background-image:
            linear-gradient(rgba(139,92,246,.07) 1px, transparent 1px),
            linear-gradient(90deg, rgba(99,102,241,.07) 1px, transparent 1px);
          background-size: 56px 56px;
          transform: perspective(700px) rotateX(58deg) translateY(19%);
          transform-origin: center bottom;
          animation: rpBootGrid 2.7s ease-out both;
        }}

        .rp-boot-noise {{
          position: absolute;
          inset: 0;
          opacity: .035;
          background-image: radial-gradient(rgba(255,255,255,.9) .55px, transparent .7px);
          background-size: 4px 4px;
          mix-blend-mode: screen;
        }}

        .rp-boot-stage {{
          position: relative;
          width: min(640px, 88vw);
          height: min(640px, 88vw);
          display: grid;
          place-items: center;
        }}

        .rp-boot-core-glow {{
          position: absolute;
          width: 280px;
          height: 280px;
          border-radius: 50%;
          background: radial-gradient(circle, rgba(157,112,255,.22), rgba(82,55,255,.08) 38%, transparent 70%);
          filter: blur(7px);
          animation: rpBootBreath 1.55s ease-in-out infinite;
        }}

        .rp-boot-logo-wrap {{
          position: absolute;
          width: 164px;
          height: 164px;
          display: grid;
          place-items: center;
          z-index: 7;
          animation: rpBootLogo 1.15s cubic-bezier(.16,1,.3,1) both;
        }}

        .rp-boot-logo {{
          width: 126px;
          height: 126px;
          object-fit: contain;
          filter: drop-shadow(0 0 22px rgba(118,79,255,.78)) drop-shadow(0 0 52px rgba(54,91,255,.35));
          animation: rpBootLogoPulse 1.45s ease-in-out .72s infinite;
        }}

        .rp-boot-logo-halo {{
          position: absolute;
          inset: 13px;
          border-radius: 50%;
          border: 1px solid rgba(164,139,255,.44);
          box-shadow: 0 0 24px rgba(122,83,255,.28), inset 0 0 24px rgba(79,104,255,.15);
          animation: rpBootHalo 1.55s cubic-bezier(.2,.7,.3,1) both;
        }}

        .rp-boot-orbit {{
          position: absolute;
          border-radius: 50%;
          border: 1px solid transparent;
          transform: rotate(-24deg);
          opacity: 0;
        }}
        .orbit-one {{ width: 252px; height: 252px; border-top-color: rgba(139,92,246,.9); border-right-color: rgba(99,102,241,.35); animation: rpBootOrbit 1.9s cubic-bezier(.22,.61,.36,1) .12s forwards; }}
        .orbit-two {{ width: 338px; height: 214px; border-bottom-color: rgba(69,122,255,.82); border-left-color: rgba(172,92,255,.48); animation: rpBootOrbit 2.1s cubic-bezier(.22,.61,.36,1) .28s forwards; transform: rotate(28deg) scaleY(.72); }}
        .orbit-three {{ width: 430px; height: 300px; border-top-color: rgba(63,122,255,.48); border-right-color: rgba(155,82,255,.34); animation: rpBootOrbit 2.35s cubic-bezier(.22,.61,.36,1) .42s forwards; transform: rotate(-42deg) scaleY(.62); }}

        .rp-boot-scan {{
          position: absolute;
          width: 300px;
          height: 300px;
          border-radius: 50%;
          background: conic-gradient(from 0deg, transparent 0deg, transparent 305deg, rgba(164,123,255,.86) 332deg, transparent 350deg);
          -webkit-mask: radial-gradient(circle, transparent 67%, #000 68%, #000 69%, transparent 70%);
          mask: radial-gradient(circle, transparent 67%, #000 68%, #000 69%, transparent 70%);
          animation: rpBootScan 1.35s linear .55s both;
        }}

        .rp-boot-signal {{
          position: absolute;
          width: 7px;
          height: 7px;
          border-radius: 50%;
          background: #bba7ff;
          box-shadow: 0 0 9px #9d7cff, 0 0 22px rgba(78,109,255,.82);
          opacity: 0;
        }}
        .signal-a {{ animation: rpBootParticleA 1.35s cubic-bezier(.4,0,.2,1) .35s both; }}
        .signal-b {{ animation: rpBootParticleB 1.5s cubic-bezier(.4,0,.2,1) .48s both; }}
        .signal-c {{ animation: rpBootParticleC 1.25s cubic-bezier(.4,0,.2,1) .6s both; }}
        .signal-d {{ animation: rpBootParticleD 1.6s cubic-bezier(.4,0,.2,1) .32s both; }}

        .rp-boot-wordmark {{
          position: absolute;
          top: calc(50% + 113px);
          width: 100%;
          text-align: center;
          font: 800 19px/1 Inter, "Segoe UI", Arial, sans-serif;
          letter-spacing: .42em;
          padding-left: .42em;
          color: #f7f5ff;
          opacity: 0;
          transform: translateY(10px) scale(.96);
          text-shadow: 0 0 24px rgba(142,103,255,.32);
          animation: rpBootText 650ms cubic-bezier(.16,1,.3,1) 1.02s forwards;
        }}

        .rp-boot-subtitle {{
          position: absolute;
          top: calc(50% + 142px);
          width: 100%;
          text-align: center;
          font: 650 8px/1 Inter, "Segoe UI", Arial, sans-serif;
          letter-spacing: .34em;
          padding-left: .34em;
          color: rgba(176,165,220,.68);
          opacity: 0;
          animation: rpBootText 600ms ease 1.28s forwards;
        }}

        .rp-boot-status {{
          position: absolute;
          top: calc(50% + 181px);
          display: flex;
          align-items: center;
          gap: 7px;
          font: 650 8px/1 "SFMono-Regular", Consolas, monospace;
          letter-spacing: .16em;
          color: rgba(139,151,180,.7);
          opacity: 0;
          animation: rpBootText 600ms ease 1.48s forwards;
        }}
        .rp-boot-status-dot {{
          width: 5px;
          height: 5px;
          border-radius: 50%;
          background: #9c78ff;
          box-shadow: 0 0 10px rgba(156,120,255,.95);
          animation: rpBootDot .8s ease-in-out infinite;
        }}

        @keyframes rpBootExit {{
          0% {{ opacity: 1; transform: scale(1); }}
          55% {{ opacity: 1; transform: scale(1.01); }}
          100% {{ opacity: 0; transform: scale(1.025); visibility: hidden; pointer-events: none; }}
        }}
        @keyframes rpBootLogo {{ from {{ opacity:0; transform:scale(.48); }} 62% {{ opacity:1; transform:scale(1.08); }} to {{ opacity:1; transform:scale(1); }} }}
        @keyframes rpBootLogoPulse {{ 0%,100% {{ transform:scale(1); }} 50% {{ transform:scale(1.035); }} }}
        @keyframes rpBootHalo {{ from {{ opacity:0; transform:scale(.55); }} 55% {{ opacity:1; transform:scale(1.1); }} to {{ opacity:.75; transform:scale(1); }} }}
        @keyframes rpBootOrbit {{ 0% {{ opacity:0; transform:rotate(-24deg) scale(.45); }} 25% {{ opacity:.95; }} 100% {{ opacity:.75; transform:rotate(336deg) scale(1); }} }}
        @keyframes rpBootScan {{ from {{ opacity:0; transform:rotate(-110deg) scale(.62); }} 20% {{ opacity:.9; }} to {{ opacity:.7; transform:rotate(250deg) scale(1); }} }}
        @keyframes rpBootBreath {{ 0%,100% {{ transform:scale(.84); opacity:.62; }} 50% {{ transform:scale(1.08); opacity:1; }} }}
        @keyframes rpBootText {{ from {{ opacity:0; transform:translateY(10px) scale(.96); }} to {{ opacity:1; transform:translateY(0) scale(1); }} }}
        @keyframes rpBootDot {{ 0%,100% {{ opacity:.4; transform:scale(.75); }} 50% {{ opacity:1; transform:scale(1.2); }} }}
        @keyframes rpBootGrid {{ from {{ opacity:0; transform:perspective(700px) rotateX(58deg) translateY(28%) scale(1.08); }} to {{ opacity:.22; transform:perspective(700px) rotateX(58deg) translateY(19%) scale(1); }} }}
        @keyframes rpBootParticleA {{ 0% {{ opacity:0; left:8%; top:30%; transform:scale(.4); }} 18% {{ opacity:1; }} 100% {{ opacity:.8; left:43%; top:46%; transform:scale(.8); }} }}
        @keyframes rpBootParticleB {{ 0% {{ opacity:0; left:90%; top:35%; transform:scale(.3); }} 20% {{ opacity:1; }} 100% {{ opacity:.7; left:57%; top:49%; transform:scale(.7); }} }}
        @keyframes rpBootParticleC {{ 0% {{ opacity:0; left:72%; top:86%; transform:scale(.3); }} 22% {{ opacity:1; }} 100% {{ opacity:.65; left:55%; top:57%; transform:scale(.65); }} }}
        @keyframes rpBootParticleD {{ 0% {{ opacity:0; left:25%; top:82%; transform:scale(.35); }} 20% {{ opacity:1; }} 100% {{ opacity:.75; left:47%; top:55%; transform:scale(.7); }} }}

        @media (max-width: 640px) {{
          .rp-boot-stage {{ width: 100vw; height: 100vw; }}
          .rp-boot-logo-wrap {{ width: 132px; height:132px; }}
          .rp-boot-logo {{ width:102px; height:102px; }}
          .orbit-one {{ width:205px; height:205px; }}
          .orbit-two {{ width:275px; height:175px; }}
          .orbit-three {{ width:350px; height:245px; }}
          .rp-boot-scan {{ width:245px; height:245px; }}
          .rp-boot-wordmark {{ top:calc(50% + 94px); font-size:15px; }}
          .rp-boot-subtitle {{ top:calc(50% + 119px); font-size:7px; }}
          .rp-boot-status {{ top:calc(50% + 151px); font-size:7px; }}
        }}

        @media (prefers-reduced-motion: reduce) {{
          .rp-boot {{ animation-delay: 500ms; animation-duration: 250ms; }}
          .rp-boot-grid, .rp-boot-orbit, .rp-boot-scan, .rp-boot-signal, .rp-boot-logo-wrap,
          .rp-boot-logo, .rp-boot-logo-halo, .rp-boot-core-glow, .rp-boot-wordmark,
          .rp-boot-subtitle, .rp-boot-status {{ animation-duration: 1ms !important; animation-iteration-count: 1 !important; }}
        }}
        </style>
        """

    # Use Streamlit's dedicated HTML renderer rather than st.markdown.
    # st.markdown parses the payload as Markdown first, which can cause
    # block-level HTML to fall back to literal source text in some
    # Streamlit/browser combinations. st.html renders the document directly.
    if hasattr(st, "html"):
        st.html(boot_html)
    else:
        # RepoPulse requires Streamlit >= 1.45 for st.html. This fallback is
        # intentionally kept only for older environments so the app does not
        # crash; modern installations use st.html above.
        st.markdown(boot_html, unsafe_allow_html=True)
