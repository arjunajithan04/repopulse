from __future__ import annotations
from typing import Any, Mapping
import html

STAGES = (
    'Connecting to GitHub','Loading repository metadata','Loading contributors',
    'Loading pull requests','Loading issues','Loading languages and activity',
    'Building repository inventory','Calculating engineering intelligence',
    'Checking API capacity','Finalizing repository intelligence',
)

def render_scan_loader(
    container: Any,
    repository: str,
    progress: int,
    stage: str,
    detail: str = '',
    stats: Mapping[str, Any] | None = None,
    completed: bool = False,
    avatar_url: str | None = None,
    owner_login: str | None = None,
):
    stats = stats or {}
    # Only render remote images from HTTPS URLs; escape values for HTML attributes.
    safe_avatar_url = avatar_url.strip() if isinstance(avatar_url, str) else ''
    if not safe_avatar_url.startswith('https://'):
        safe_avatar_url = ''
    safe_avatar_url = html.escape(safe_avatar_url, quote=True)
    safe_owner = html.escape(owner_login or repository.split('/', 1)[0], quote=True)
    identity_revealed = bool(owner_login)
    owner_initial = html.escape((owner_login or repository.split("/", 1)[0])[:1].upper(), quote=True)
    pct = max(0, min(100, int(progress)))
    # Keep the avatar visible and draw its circular progress outline in sync
    # with the actual scan progress. SVG pathLength=100 makes progress direct.
    ring_pct = 100 if completed else pct
    ring_offset = max(0, min(100, 100 - ring_pct))
    ring_style = f"--ring-offset:{ring_offset};"
    idx = len(STAGES) if completed else next((i for i,s in enumerate(STAGES) if s == stage), 0)
    steps=[]
    for i,label in enumerate(STAGES):
        state='done' if i<idx else 'active' if i==idx and not completed else 'pending'
        icon='✓' if state=='done' else '●' if state=='active' else '○'
        steps.append(f'<div class="rp-scan-step {state}"><b>{i+1:02d}</b><i>{icon}</i><span>{html.escape(label.upper())}</span></div>')
    chips=''.join(f'<span class="rp-scan-stat"><strong>{html.escape(str(v))}</strong> {html.escape(str(k))}</span>' for k,v in stats.items() if v not in (None,''))
    container.markdown(f'''<div class="rp-scan-screen"><div class="rp-scan-grid"></div><div class="rp-scan-content">
    <div class="rp-scan-brand">REPOPULSE</div><div class="rp-scan-kicker">REPOSITORY INTELLIGENCE / LIVE SCAN</div>
    <div class="rp-pulse-orb {'identity-revealed' if identity_revealed else ''} {'complete' if completed else ''}"><div class="rp-pulse-ring rp-ring-1"></div><div class="rp-pulse-ring rp-ring-2"></div><div class="rp-pulse-ring rp-ring-3"></div><div class="rp-pulse-core {'has-avatar' if safe_avatar_url else ''}">{'<img class="rp-owner-avatar" src="' + safe_avatar_url + '" alt="GitHub avatar for ' + safe_owner + '" referrerpolicy="no-referrer" onerror="this.parentElement.innerHTML=\'\u25cf\';this.parentElement.classList.add(\'avatar-failed\')" />' if safe_avatar_url else (owner_initial if identity_revealed else ('✓' if completed else '●'))}</div>{'<svg class="rp-avatar-progress-ring" viewBox="0 0 100 100" aria-hidden="true" style="' + ring_style + '"><circle class="rp-avatar-ring-track" cx="50" cy="50" r="46" pathLength="100"/><circle class="rp-avatar-ring-progress" cx="50" cy="50" r="46" pathLength="100"/></svg>' if safe_avatar_url else ''}</div>
    <div class="rp-scan-identity" style="display:{'flex' if identity_revealed else 'none'}"><span class="rp-identity-kicker">REPOSITORY OWNER</span><strong>{safe_owner}</strong><span class="rp-identity-repo">{html.escape(repository)}</span></div>
    <div class="rp-scan-title">{'INTELLIGENCE READY' if completed else 'ANALYZING REPOSITORY'}</div><div class="rp-scan-repo">{html.escape(repository)}</div>
    <div class="rp-scan-progress"><span style="width:{pct}%"></span></div><div class="rp-scan-percent">{pct}%</div>
    <div class="rp-scan-stage"><i></i><span>{html.escape(stage)}</span></div><div class="rp-scan-detail">{html.escape(detail)}</div>
    <div class="rp-scan-stats">{chips}</div><div class="rp-scan-steps">{''.join(steps)}</div>
    <div class="rp-scan-terminal"><div>&gt; repopulse.scan()</div><div>&gt; {html.escape(stage.lower())}…</div><div>&gt; {html.escape(detail)}</div></div>
    </div></div>''', unsafe_allow_html=True)

def scan_styles():
    return '''<style>
    .rp-scan-screen{position:fixed;inset:0;width:100vw;height:100vh;min-height:100vh;margin:0;overflow:hidden;display:flex;align-items:center;justify-content:center;z-index:2147483000;background:radial-gradient(circle at 50% 40%,rgba(112,88,255,.15),transparent 30%),radial-gradient(circle at 20% 80%,rgba(65,105,225,.08),transparent 28%),#07070b;border:1px solid rgba(255,255,255,.07);border-radius:24px}.rp-scan-grid{position:absolute;inset:0;opacity:.2;background-image:linear-gradient(rgba(255,255,255,.035) 1px,transparent 1px),linear-gradient(90deg,rgba(255,255,255,.035) 1px,transparent 1px);background-size:42px 42px;animation:rp-grid-drift 12s linear infinite}.rp-scan-content{position:relative;z-index:2;width:min(700px,88vw);max-height:92vh;overflow:auto;text-align:center;padding:2rem 0}.rp-scan-content::-webkit-scrollbar{display:none}.rp-scan-content{scrollbar-width:none}.rp-scan-brand{font-size:1.65rem;font-weight:850;letter-spacing:.24em;color:#f6f5ff}.rp-scan-kicker{margin-top:.35rem;font-size:.62rem;letter-spacing:.24em;color:rgba(190,185,255,.58)}.rp-pulse-orb{position:relative;width:142px;height:142px;margin:2.1rem auto 1.25rem;display:grid;place-items:center}.rp-pulse-core{position:relative;z-index:4;width:46px;height:46px;display:grid;place-items:center;border-radius:50%;overflow:hidden;color:#fff;background:radial-gradient(circle at 35% 30%,#c9c2ff,#7765ff 48%,#3f2fa5);box-shadow:0 0 36px rgba(116,97,255,.65);animation:rp-core-pulse 1.8s ease-in-out infinite}.rp-owner-avatar{display:block;width:100%;height:100%;object-fit:cover;border-radius:50%;opacity:1;transform:scale(1);filter:brightness(1) saturate(1)}.rp-avatar-progress-ring{position:absolute;z-index:6;inset:calc(50% - 46px);width:92px;height:92px;overflow:visible;transform:rotate(-90deg);pointer-events:none;filter:drop-shadow(0 0 5px rgba(139,92,246,.65))}.rp-avatar-ring-track,.rp-avatar-ring-progress{fill:none;stroke-width:1.8;vector-effect:non-scaling-stroke}.rp-avatar-ring-track{stroke:rgba(190,180,255,.16)}.rp-avatar-ring-progress{stroke:#a99aff;stroke-linecap:round;stroke-dasharray:100;stroke-dashoffset:var(--ring-offset,100);transition:stroke-dashoffset .65s cubic-bezier(.22,.75,.2,1),stroke .35s ease}.rp-pulse-orb.complete .rp-avatar-ring-progress{stroke:#6ee7b7}.rp-pulse-core.has-avatar.avatar-failed+.rp-avatar-progress-ring{display:none}.rp-pulse-orb.identity-revealed .rp-pulse-core{width:76px;height:76px;background:#17132d;border:2px solid rgba(167,139,250,.9);box-shadow:0 0 0 7px rgba(139,92,246,.10),0 0 42px rgba(116,97,255,.62);transition:width .45s ease,height .45s ease,border-radius .45s ease}.rp-pulse-orb.identity-revealed .rp-pulse-ring{inset:13px}.rp-scan-identity{align-items:center;justify-content:center;flex-direction:column;gap:.22rem;margin:-.25rem auto 1rem;animation:rp-fade-up .45s ease both}.rp-identity-kicker{font-size:.55rem;letter-spacing:.2em;color:rgba(190,185,255,.56)}.rp-scan-identity strong{font-size:.85rem;letter-spacing:.04em;color:#f0efff}.rp-identity-repo{font:.66rem ui-monospace,monospace;color:rgba(224,222,240,.5)}.rp-pulse-core.avatar-failed{width:46px;height:46px}.rp-pulse-orb.complete .rp-pulse-core{background:radial-gradient(circle at 35% 30%,#b9ffe2,#34d399 48%,#087a55)}.rp-pulse-ring{position:absolute;inset:23px;border:1px solid rgba(139,124,255,.5);border-radius:50%;animation:rp-ring 2.4s ease-out infinite}.rp-ring-2{animation-delay:.8s}.rp-ring-3{animation-delay:1.6s}.rp-scan-title{font-size:.76rem;letter-spacing:.22em;font-weight:750;color:#f0eff8}.rp-scan-repo{margin-top:.5rem;font:.82rem ui-monospace,monospace;color:rgba(224,222,240,.56)}.rp-scan-progress{width:100%;height:4px;margin:1.5rem auto .35rem;overflow:hidden;border-radius:99px;background:rgba(255,255,255,.07)}.rp-scan-progress span{display:block;height:100%;border-radius:inherit;background:linear-gradient(90deg,#6554ff,#a397ff);box-shadow:0 0 18px rgba(111,91,255,.55);transition:width .45s ease}.rp-scan-percent{text-align:right;font:.62rem ui-monospace,monospace;color:rgba(190,185,255,.6)}.rp-scan-stage{display:flex;justify-content:center;align-items:center;gap:.55rem;min-height:22px;color:rgba(235,233,247,.86);font-size:.76rem}.rp-scan-stage i{width:6px;height:6px;border-radius:50%;background:#8d7dff;box-shadow:0 0 12px #8d7dff;animation:rp-dot 1s ease-in-out infinite}.rp-scan-detail{min-height:20px;margin-top:.35rem;color:rgba(170,165,195,.55);font-size:.65rem}.rp-scan-stats{display:flex;flex-wrap:wrap;justify-content:center;gap:.45rem;margin:1rem auto}.rp-scan-stat{padding:.36rem .55rem;border:1px solid rgba(255,255,255,.06);border-radius:999px;background:rgba(255,255,255,.025);color:rgba(215,212,230,.52);font-size:.58rem}.rp-scan-stat strong{color:#dcd8ff}.rp-scan-steps{margin:1.1rem auto 0;display:grid;grid-template-columns:repeat(2,1fr);gap:.42rem;text-align:left}.rp-scan-step{display:grid;grid-template-columns:25px 14px 1fr;align-items:center;gap:.35rem;padding:.52rem .62rem;border:1px solid rgba(255,255,255,.055);border-radius:9px;background:rgba(255,255,255,.018);color:rgba(221,219,235,.34);font-size:.57rem;letter-spacing:.06em}.rp-scan-step b{font:.56rem ui-monospace,monospace;color:rgba(151,139,255,.45)}.rp-scan-step i{font-style:normal}.rp-scan-step.done{color:rgba(221,235,229,.56);border-color:rgba(52,211,153,.12)}.rp-scan-step.done i{color:#34d399}.rp-scan-step.active{border-color:rgba(139,92,246,.3);background:rgba(139,92,246,.08);color:#e9e6ff;box-shadow:inset 2px 0 #8b5cf6}.rp-scan-terminal{margin:1rem auto 0;padding:.65rem .85rem;text-align:left;border:1px solid rgba(255,255,255,.05);border-radius:10px;background:rgba(0,0,0,.22);font:.59rem/1.55 ui-monospace,monospace;color:rgba(170,165,195,.44)}@keyframes rp-ring{0%{transform:scale(.65);opacity:.8}80%,100%{transform:scale(1.55);opacity:0}}@keyframes rp-core-pulse{0%,100%{transform:scale(.94)}50%{transform:scale(1.08)}}@keyframes rp-dot{0%,100%{opacity:.35;transform:scale(.8)}50%{opacity:1;transform:scale(1.15)}}@keyframes rp-grid-drift{from{transform:translate(0,0)}to{transform:translate(42px,42px)}}@media(max-width:700px){.rp-scan-screen{min-height:84vh}.rp-scan-steps{grid-template-columns:1fr}.rp-scan-stats{display:none}}@media(prefers-reduced-motion:reduce){.rp-scan-grid,.rp-pulse-core,.rp-pulse-ring,.rp-scan-stage i{animation:none!important}.rp-avatar-ring-progress{transition:none!important}.rp-scan-progress span{transition:none!important}}
    </style>'''
