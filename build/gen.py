# -*- coding: utf-8 -*-
import json, os
from content import *
STATIC=False
OUT=os.path.join(os.path.dirname(os.path.abspath(__file__)),"canvas_out")
CADET="/_blob/88c8f8cf79800d1034420beda37ce663"
BG="#0B0B0C"; SURF="#18181A"; LINE="#2C2C2F"; TXT="#F2F2F2"; MUT="#A8A8AD"; ACC="#FF6B1A"; SAND="#F5F5F5"
HF="font-family: 'Oswald', sans-serif"
def h(x): return "{{"+x+"}}"
CUT=lambda n: "border-radius: 3px"
def mark(size, fg=None, ac=None):
    fg=fg or TXT; ac=ac or ACC
    return f'<svg aria-hidden="true" width="{size}" height="{size}" viewBox="0 0 48 48" fill="none"><path d="M24 3l18 6v14c0 11-7.6 19-18 22C13.6 42 6 34 6 23V9z" stroke="{ac}" stroke-width="2.6"></path><path d="M14 15l10 19 10-19" stroke="{fg}" stroke-width="4.5" stroke-linecap="square"></path><path d="M19.5 15l4.5 8.5 4.5-8.5" stroke="{ac}" stroke-width="2.5" stroke-linecap="square"></path></svg>'
def icon(k,size=28,color="currentColor",sw="1.6"):
    return f'<svg aria-hidden="true" width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="{sw}" stroke-linecap="square">{I[k]}</svg>'
HEAD_STYLE=f'''<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Barlow:wght@400;500;600&family=Oswald:wght@500;600;700&display=swap">
<style>
body{{margin:0;background:{BG}}}
a{{color:#D2D2D6;text-decoration:none}}a:hover{{color:#FFFFFF}}
@keyframes vzBar{{0%,100%{{transform:scaleY(0.3)}}50%{{transform:scaleY(1)}}}}
@keyframes vzPulse{{0%{{box-shadow:0 0 0 0 rgba(255,107,26,0.55)}}100%{{box-shadow:0 0 0 14px rgba(255,107,26,0)}}}}
@keyframes vzBob{{0%,100%{{transform:translateY(0)}}50%{{transform:translateY(-6px)}}}}
.vz-bar{{display:inline-block;width:3px;height:14px;background:{ACC};transform-origin:bottom;animation:vzBar .6s ease-in-out infinite}}
.vz-pulse{{animation:vzPulse 1.1s ease-out infinite}}
.vz-bob{{animation:vzBob 1.6s ease-in-out infinite}}
@media (prefers-reduced-motion: reduce){{.vz-bar,.vz-pulse,.vz-bob{{animation:none}}}}
</style>'''
ROOT_OPEN=f'<div style="background-color: {BG}; color: {TXT}; font-family: \'Barlow\', system-ui, sans-serif; min-height: 100vh; box-sizing: border-box; overflow: hidden">'
langbase=f"min-width: 44px; min-height: 44px; padding: 0 10px; {HF}; font-weight: 700; font-size: 16px; letter-spacing: 0.1em; cursor: pointer"

def langbtns():
    if STATIC:
        return f'''<sc-if value="{h('l.active')}"><a href="{h('l.href')}" hreflang="{h('l.lc')}" lang="{h('l.lc')}" aria-current="true" aria-label="{h('l.name')}" data-lang="{h('l.lc')}" style="{langbase}; display: inline-flex; align-items: center; justify-content: center; box-sizing: border-box; background: {ACC}; border: 1px solid {ACC}; color: {BG}">{h('l.code')}</a></sc-if>
<sc-if value="{h('l.inactive')}"><a href="{h('l.href')}" hreflang="{h('l.lc')}" lang="{h('l.lc')}" aria-label="{h('l.name')}" data-lang="{h('l.lc')}" style="{langbase}; display: inline-flex; align-items: center; justify-content: center; box-sizing: border-box; background: transparent; border: 1px solid #3A3A3E; color: {TXT}">{h('l.code')}</a></sc-if>'''
    return f'''<sc-if value="{h('l.active')}" hint-placeholder-val="{h('false')}"><button type="button" aria-pressed="true" aria-label="{h('l.name')}" onClick="{h('l.pick')}" style="{langbase}; background: {ACC}; border: 1px solid {ACC}; color: {BG}">{h('l.code')}</button></sc-if>
<sc-if value="{h('l.inactive')}" hint-placeholder-val="{h('true')}"><button type="button" aria-pressed="false" aria-label="{h('l.name')}" onClick="{h('l.pick')}" style="{langbase}; background: transparent; border: 1px solid #3A3A3E; color: {TXT}">{h('l.code')}</button></sc-if>'''
def header(active, home_file):
    LANGBTN=langbtns()
    reg = "#registro" if home_file else ("Main.dc.html#registro" if STATIC else "Main.dc.html")
    links=[("Main.dc.html" if not home_file else "#top", h("t.home"), active=="home")]+[(FILE[k], SHORT[k], active==k) for k in ORDER]
    nav=""
    for href,label,on in links:
        st=f"min-height: 44px; display: inline-flex; align-items: center; border-bottom: 2px solid {ACC if on else 'transparent'}; color: {'#FFFFFF' if on else '#D2D2D6'}"
        cur=' aria-current="page"' if on else ""
        nav+=f'<a href="{href}"{cur} style="{st}">{label}</a>\n'
    return f'''<header style="border-bottom: 1px solid {LINE}; background: rgba(11,11,12,0.92)">
<div style="max-width: 1360px; margin: 0 auto; padding: 10px 24px; display: flex; flex-wrap: wrap; align-items: center; justify-content: space-between; gap: 10px 24px">
<a href="{'#top' if home_file else 'Main.dc.html'}" aria-label="VERTEZ GROUP" style="display: flex; align-items: center; gap: 10px; min-height: 44px">
{mark(40)}
<span style="{HF}; font-weight: 800; font-size: 22px; letter-spacing: 0.16em; color: #FFFFFF">VERTEZ<span style="color: {ACC}"> GROUP</span></span>
</a>
<nav aria-label="VERTEZ" style="display: flex; flex-wrap: wrap; align-items: center; gap: 0 18px; font-size: 13px; font-weight: 600; letter-spacing: 0.12em; text-transform: uppercase">
{nav}</nav>
<div style="display: flex; flex-wrap: wrap; align-items: center; gap: 10px 14px">
<div role="group" aria-label="{h('t.langLabel')}" style="display: flex; align-items: center; gap: 6px">
<sc-for list="{h('langs')}" as="l" hint-placeholder-count="3">
{LANGBTN}
</sc-for>
</div>
<a href="{reg}" style="min-height: 44px; padding: 0 16px; display: inline-flex; align-items: center; border: 1px solid #3A3A3E; color: {TXT}; {HF}; font-weight: 700; font-size: 15px; letter-spacing: 0.12em; text-transform: uppercase">{h('t.login')}</a>
<a href="{reg}" style="min-height: 44px; padding: 0 18px; display: inline-flex; align-items: center; background: {ACC}; color: {BG}; {HF}; font-weight: 800; font-size: 15px; letter-spacing: 0.12em; text-transform: uppercase; {CUT(9)}">{h('t.signup')}</a>
</div>
</div>
</header>'''

def footer(home_file):
    reg = "#registro" if home_file else ("Main.dc.html#registro" if STATIC else "Main.dc.html")
    divs="".join(f'<a href="{FILE[k]}" style="min-height: 32px; display: inline-flex; align-items: center">VERTEZ {SHORT[k].upper()}</a>\n' for k in ORDER)
    return f'''<footer style="border-top: 1px solid {LINE}; background: #070708; margin-top: 24px">
<div style="max-width: 1360px; margin: 0 auto; padding: 48px 24px 28px; display: flex; flex-wrap: wrap; gap: 32px 56px">
<div style="flex: 2 1 300px; min-width: 0; display: flex; flex-direction: column; gap: 14px">
<div style="display: flex; align-items: center; gap: 10px">{mark(44)}<span style="{HF}; font-weight: 800; font-size: 24px; letter-spacing: 0.16em; color: #FFFFFF">VERTEZ<span style="color: {ACC}"> GROUP</span></span></div>
<p style="margin: 0; {HF}; font-weight: 700; font-size: 18px; letter-spacing: 0.06em; color: {SAND}">{h('t.slogan')}</p>
<p style="margin: 0; font-size: 15px; line-height: 1.6; color: {MUT}; max-width: 420px">{h('t.fDesc')}</p>
</div>
<div style="flex: 1 1 200px; min-width: 0; display: flex; flex-direction: column; gap: 6px; font-size: 14px">
<p style="margin: 0 0 6px; {HF}; font-weight: 700; font-size: 15px; letter-spacing: 0.16em; text-transform: uppercase; color: #FFFFFF">{h('t.fDivs')}</p>
{divs}</div>
<div style="flex: 1 1 160px; min-width: 0; display: flex; flex-direction: column; gap: 6px; font-size: 14px">
<p style="margin: 0 0 6px; {HF}; font-weight: 700; font-size: 15px; letter-spacing: 0.16em; text-transform: uppercase; color: #FFFFFF">{h('t.fAcc')}</p>
<a href="{reg}" style="min-height: 32px; display: inline-flex; align-items: center">{h('t.login')}</a>
<a href="{reg}" style="min-height: 32px; display: inline-flex; align-items: center">{h('t.signup')}</a>
<a href="{reg}" style="min-height: 32px; display: inline-flex; align-items: center">{h('t.myspace')}</a>
<a href="#top" style="min-height: 32px; display: inline-flex; align-items: center">{h('t.fLegal')}</a>
<a href="#top" style="min-height: 32px; display: inline-flex; align-items: center">{h('t.fPriv')}</a>
<a href="#top" style="min-height: 32px; display: inline-flex; align-items: center">{h('t.fContact')}</a>
</div>
</div>
<div style="max-width: 1360px; margin: 0 auto; padding: 16px 24px 28px; border-top: 1px solid {LINE}; font-size: 13px; color: {MUT}">{h('t.fRights')}</div>
</footer>'''

JS_COMMON=r'''
const LANGS = [["es","ES","Español","es-ES"],["fr","FR","Français","fr-FR"],["en","EN","English","en-GB"]];
const STORE = "vertez_v1";
function readStore() { try { return JSON.parse(window.localStorage.getItem(STORE) || "{}") || {}; } catch (e) { return {}; } }
function writeStore(p) { try { const v = readStore(); Object.assign(v, p); window.localStorage.setItem(STORE, JSON.stringify(v)); } catch (e) {} }
function startLang() { const v = readStore(); return T[v.lang] ? v.lang : "es"; }
function langList(self, extra) {
  const lang = self.state.lang;
  return LANGS.map((l) => ({ code: l[1], name: l[2], active: l[0] === lang, inactive: l[0] !== lang, pick: () => { if (extra) extra(); writeStore({ lang: l[0] }); self.setState({ lang: l[0] }); } }));
}
'''
def page(title, body, js, T, h_):
    tj=json.dumps(T,ensure_ascii=False); assert "</" not in tj
    return f'''<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<title>{title}</title>
<script src="./support.js"></script>
</head>
<body>
<x-dc>
<helmet>
{HEAD_STYLE}
</helmet>
{ROOT_OPEN}
{body}
</div>
</x-dc>
<script type="text/x-dc" data-dc-script data-props='{{"$preview":{{"width":1440,"height":{h_}}}}}'>
const T = {tj};
{JS_COMMON}
{js}
</script>
</body>
</html>
'''

def sec_title(text, color=ACC):
    return f'''<div style="display: flex; align-items: center; gap: 12px; font-size: 13px; font-weight: 600; letter-spacing: 0.24em; text-transform: uppercase; color: {color}"><span aria-hidden="true" style="width: 36px; height: 2px; background: {color}; display: inline-block"></span><span>{text}</span></div>'''

# ---------------- DIVISION PAGES ----------------
X = {  # small extra strings for bespoke blocks
"es":dict(prod="[Nombre del producto]",price="[Precio]",sizes="Tallas",add="Añadir al carrito",cart="Carrito",coll="Colección",ask="Pregunta al asistente →",prev="← Anterior",next="Siguiente →"),
"fr":dict(prod="[Nom du produit]",price="[Prix]",sizes="Tailles",add="Ajouter au panier",cart="Panier",coll="Collection",ask="Demande à l'assistant →",prev="← Précédente",next="Suivante →"),
"en":dict(prod="[Product name]",price="[Price]",sizes="Sizes",add="Add to cart",cart="Cart",coll="Collection",ask="Ask the assistant →",prev="← Previous",next="Next →"),
}
def division(k, idx):
    T={}
    for L in LANGS:
        d=D[k][L]
        t=dict(C[L]); t.update(X[L]); t.update(dict(tag=d["tag"],intro=d["intro"],note=d["note"],obj=d["obj"]))
        t["sections"]=[{"title":s[0],"items":[{"x":x} for x in s[1]]} for s in d["sections"]]
        if k=="world":
            w=WORLDX[L]; t.update({kk:v for kk,v in w.items() if kk!="regions"}); t["regions"]=w["regions"].split(";")
            t["fields"]=D[k][L]["sections"][2][1]
        if k=="academy":
            tr=TIR[L]; t.update(tirT=tr["t"],tirS=tr["s"],tirP=tr["p"]); t["mods"]=[{"n":f"{i+1:02d}","x":x} for i,x in enumerate(tr["m"].split(";"))]
        if k=="store":
            t["colls"]=[{"x":x} for x in D[k][L]["sections"][2][1]]
        T[L]=t
    num=f"{idx+1:02d}"; prev=ORDER[idx-1]; nxt=ORDER[(idx+1)%8]
    bespoke=""
    if k=="world":
        pos=[(18,30),(30,68),(50,24),(52,58),(62,42),(76,32),(84,74)]
        markers=""
        for i,(x,y) in enumerate(pos):
            markers+=f'''<sc-if value="{h(f'r{i}on')}" hint-placeholder-val="{h('false' if i else 'true')}"><button type="button" aria-pressed="true" onClick="{h(f'pick{i}')}" style="position: absolute; left: {x}%; top: {y}%; transform: translate(-50%, -50%); min-height: 44px; padding: 0 12px; display: inline-flex; align-items: center; gap: 8px; background: {ACC}; border: 1px solid {ACC}; color: {BG}; font-family: 'Barlow', sans-serif; font-size: 14px; font-weight: 600; cursor: pointer; white-space: nowrap"><span aria-hidden="true" style="width: 8px; height: 8px; background: {BG}; transform: rotate(45deg); display: inline-block"></span>{h(f'rn{i}')}</button></sc-if>
<sc-if value="{h(f'r{i}off')}" hint-placeholder-val="{h('true' if i else 'false')}"><button type="button" aria-pressed="false" onClick="{h(f'pick{i}')}" style="position: absolute; left: {x}%; top: {y}%; transform: translate(-50%, -50%); min-height: 44px; padding: 0 12px; display: inline-flex; align-items: center; gap: 8px; background: rgba(11,11,12,0.85); border: 1px solid #3A3A3E; color: {TXT}; font-family: 'Barlow', sans-serif; font-size: 14px; cursor: pointer; white-space: nowrap"><span aria-hidden="true" style="width: 8px; height: 8px; background: {ACC}; transform: rotate(45deg); display: inline-block"></span>{h(f'rn{i}')}</button></sc-if>
'''
        def toggle(key,label):
            return f'''<sc-if value="{h(key+'On')}" hint-placeholder-val="{h('true')}"><button type="button" aria-pressed="true" onClick="{h(key+'Toggle')}" style="min-height: 44px; padding: 0 14px; background: {SURF}; border: 1px solid {ACC}; color: {ACC}; font-family: 'Barlow', sans-serif; font-size: 14px; cursor: pointer">✓ {h('t.'+label)}</button></sc-if>
<sc-if value="{h(key+'Off')}" hint-placeholder-val="{h('false')}"><button type="button" aria-pressed="false" onClick="{h(key+'Toggle')}" style="min-height: 44px; padding: 0 14px; background: transparent; border: 1px solid #3A3A3E; color: {MUT}; font-family: 'Barlow', sans-serif; font-size: 14px; cursor: pointer">{h('t.'+label)}</button></sc-if>'''
        bespoke=f'''<section style="max-width: 1360px; margin: 0 auto; padding: 8px 24px 40px; display: flex; flex-wrap: wrap; gap: 20px">
<div style="flex: 3 1 560px; min-width: 0; display: flex; flex-direction: column; gap: 12px">
<div style="display: flex; flex-wrap: wrap; align-items: center; justify-content: space-between; gap: 10px">
<h2 style="margin: 0; {HF}; font-weight: 700; font-size: 26px; letter-spacing: 0.08em; text-transform: uppercase; color: #FFFFFF">{h('t.mapTitle')}</h2>
<div role="group" aria-label="{h('t.layers')}" style="display: flex; flex-wrap: wrap; gap: 8px">{toggle('lb','lBorders')}{toggle('lc','lCities')}{toggle('li','lInfra')}</div>
</div>
<div style="position: relative; width: 100%; aspect-ratio: 16 / 9; min-height: 340px; background: radial-gradient(ellipse at 50% 45%, #22160F 0%, {BG} 75%); border: 1px solid {LINE}; overflow: hidden">
<span aria-hidden="true" style="position: absolute; inset: 0; background-image: radial-gradient(rgba(255,107,26,0.22) 1.2px, transparent 1.4px); background-size: 18px 18px"></span>
<sc-if value="{h('lbOn')}" hint-placeholder-val="{h('true')}"><span aria-hidden="true" style="position: absolute; inset: 0; background-image: linear-gradient(rgba(255,255,255,0.25) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,0.25) 1px, transparent 1px); background-size: 12.5% 16.66%"></span></sc-if>
<sc-if value="{h('lcOn')}" hint-placeholder-val="{h('true')}"><span aria-hidden="true" style="position: absolute; inset: 0; background-image: radial-gradient(#FFFFFF 2px, transparent 2.5px); background-size: 97px 71px; background-position: 23px 31px; opacity: 0.5"></span></sc-if>
<sc-if value="{h('liOn')}" hint-placeholder-val="{h('false')}"><span aria-hidden="true" style="position: absolute; inset: 0; background-image: repeating-linear-gradient(35deg, rgba(255,160,90,0.28) 0 1px, transparent 1px 64px), repeating-linear-gradient(-20deg, rgba(255,160,90,0.2) 0 1px, transparent 1px 88px)"></span></sc-if>
{markers}</div>
</div>
<aside style="flex: 1 1 300px; min-width: 0; background: {SURF}; border: 1px solid {LINE}; border-top: 3px solid {ACC}; padding: 22px; display: flex; flex-direction: column; gap: 12px">
<p style="margin: 0; font-size: 12px; font-weight: 600; letter-spacing: 0.22em; text-transform: uppercase; color: {MUT}">{h('t.sheet')}</p>
<h3 style="margin: 0; {HF}; font-weight: 800; font-size: 30px; letter-spacing: 0.04em; text-transform: uppercase; color: #FFFFFF">{h('regionName')}</h3>
<dl style="margin: 0; display: flex; flex-direction: column; gap: 0">
<sc-for list="{h('fields')}" as="f" hint-placeholder-count="8">
<div style="display: flex; justify-content: space-between; gap: 12px; padding: 9px 0; border-bottom: 1px solid {LINE}; font-size: 14px"><dt style="color: {TXT}">{h('f.k')}</dt><dd style="margin: 0; color: {MUT}; text-align: right">{h('t.pending')}</dd></div>
</sc-for>
</dl>
<div style="display: flex; flex-wrap: wrap; gap: 8px; margin-top: 4px">
<span style="padding: 4px 10px; background: rgba(255,107,26,0.15); border: 1px solid {ACC}; color: {ACC}; font-size: 12px; font-weight: 600; letter-spacing: 0.1em; text-transform: uppercase">{h('t.confirmed')}</span>
<span style="padding: 4px 10px; background: rgba(255,255,255,0.12); border: 1px dashed {SAND}; color: {SAND}; font-size: 12px; font-weight: 600; letter-spacing: 0.1em; text-transform: uppercase">{h('t.unverified')}</span>
</div>
<p style="margin: 0; font-size: 13px; line-height: 1.5; color: {MUT}">{h('t.legend')}</p>
</aside>
</section>'''
    elif k=="academy":
        bespoke=f'''<section style="max-width: 1360px; margin: 0 auto; padding: 8px 24px 40px">
<div style="background: {SURF}; border: 1px solid {LINE}; border-top: 3px solid {SAND}; padding: 32px; display: flex; flex-wrap: wrap; gap: 28px 44px">
<div style="flex: 1 1 380px; min-width: 0; display: flex; flex-direction: column; gap: 14px">
{sec_title(h('t.tirS'), SAND)}
<h2 style="margin: 0; {HF}; font-weight: 800; font-size: clamp(34px, 4.4vw, 52px); line-height: 1; text-transform: uppercase; color: #FFFFFF">{h('t.tirT')}</h2>
<p style="margin: 0; font-size: 16px; line-height: 1.65; color: #D2D2D6">{h('t.tirP')}</p>
<a href="Main.dc.html" style="align-self: flex-start; min-height: 48px; padding: 0 22px; display: inline-flex; align-items: center; background: {SAND}; color: {BG}; {HF}; font-weight: 800; font-size: 17px; letter-spacing: 0.1em; text-transform: uppercase; {CUT(10)}">{h('t.ask')}</a>
</div>
<ol style="flex: 1 1 440px; min-width: 0; margin: 0; padding: 0; list-style: none; display: grid; grid-template-columns: repeat(auto-fill, minmax(180px, 1fr)); gap: 8px; align-content: start">
<sc-for list="{h('t.mods')}" as="m" hint-placeholder-count="12">
<li style="min-height: 52px; padding: 10px 12px; display: flex; align-items: center; gap: 10px; background: {BG}; border: 1px solid {LINE}; font-size: 14px; line-height: 1.3"><span style="{HF}; font-weight: 800; font-size: 18px; color: {SAND}">{h('m.n')}</span><span>{h('m.x')}</span></li>
</sc-for>
</ol>
</div>
</section>'''
    elif k=="store":
        bespoke=f'''<section style="max-width: 1360px; margin: 0 auto; padding: 8px 24px 40px; display: flex; flex-wrap: wrap; gap: 16px">
<div style="flex: 3 1 560px; min-width: 0; display: grid; grid-template-columns: repeat(auto-fill, minmax(220px, 1fr)); gap: 12px">
<sc-for list="{h('t.colls')}" as="c" hint-placeholder-count="4">
<div style="min-height: 180px; background: {SURF}; border: 1px solid {LINE}; padding: 20px; display: flex; flex-direction: column; justify-content: space-between; gap: 16px">
<span style="font-size: 12px; font-weight: 600; letter-spacing: 0.2em; text-transform: uppercase; color: {MUT}">{h('t.coll')}</span>
<span style="{HF}; font-weight: 800; font-size: 26px; line-height: 1.05; letter-spacing: 0.04em; text-transform: uppercase; color: #FFFFFF">{h('c.x')}</span>
<span aria-hidden="true" style="height: 3px; width: 48px; background: {ACC}; display: block"></span>
</div>
</sc-for>
</div>
<div style="flex: 1 1 280px; min-width: 0; background: {SURF}; border: 1px solid {LINE}; display: flex; flex-direction: column">
<div aria-hidden="true" style="aspect-ratio: 4 / 3; background: repeating-linear-gradient(45deg, #1C1C1F 0 12px, #151517 12px 24px); display: flex; align-items: center; justify-content: center; color: {MUT}">{icon('store',48,MUT)}</div>
<div style="padding: 18px; display: flex; flex-direction: column; gap: 10px">
<p style="margin: 0; {HF}; font-weight: 700; font-size: 22px; color: #FFFFFF">{h('t.prod')}</p>
<p style="margin: 0; font-size: 18px; color: {ACC}; font-weight: 600">{h('t.price')}</p>
<p style="margin: 0; font-size: 13px; letter-spacing: 0.14em; text-transform: uppercase; color: {MUT}">{h('t.sizes')}</p>
<div style="display: flex; gap: 6px"><span style="min-width: 40px; min-height: 36px; display: inline-flex; align-items: center; justify-content: center; border: 1px solid #3A3A3E; font-size: 14px">S</span><span style="min-width: 40px; min-height: 36px; display: inline-flex; align-items: center; justify-content: center; border: 1px solid {ACC}; color: {ACC}; font-size: 14px">M</span><span style="min-width: 40px; min-height: 36px; display: inline-flex; align-items: center; justify-content: center; border: 1px solid #3A3A3E; font-size: 14px">L</span><span style="min-width: 40px; min-height: 36px; display: inline-flex; align-items: center; justify-content: center; border: 1px solid #3A3A3E; font-size: 14px">XL</span></div>
<button type="button" style="min-height: 48px; margin-top: 6px; background: {ACC}; border: 0; color: {BG}; {HF}; font-weight: 800; font-size: 17px; letter-spacing: 0.1em; text-transform: uppercase; cursor: pointer">{h('t.add')}</button>
</div>
</div>
</section>'''
    body=f'''{header(k, False)}
<main id="top">
<section style="max-width: 1360px; margin: 0 auto; padding: 48px 24px 36px; display: flex; flex-wrap: wrap; align-items: center; gap: 32px 56px">
<div style="flex: 1 1 520px; min-width: 0; display: flex; flex-direction: column; gap: 18px">
<a href="Main.dc.html" style="align-self: flex-start; min-height: 44px; display: inline-flex; align-items: center; font-size: 14px; letter-spacing: 0.1em; color: {MUT}">{h('t.back')}</a>
{sec_title(h('t.division')+' '+num)}
<h1 style="margin: 0; {HF}; font-weight: 800; font-size: clamp(44px, 6.4vw, 88px); line-height: 0.92; letter-spacing: 0.02em; text-transform: uppercase; color: #FFFFFF">VERTEZ<br><span style="color: {ACC}">{SHORT[k].upper()}</span></h1>
<p style="margin: 0; {HF}; font-weight: 700; font-size: 22px; letter-spacing: 0.06em; text-transform: uppercase; color: {SAND}">{h('t.tag')}</p>
<p style="margin: 0; max-width: 640px; font-size: 18px; line-height: 1.65; color: #D2D2D6">{h('t.intro')}</p>
</div>
<div aria-hidden="true" style="flex: 0 1 300px; display: flex; justify-content: center">
<div style="position: relative; width: 260px; height: 260px; display: flex; align-items: center; justify-content: center; color: {ACC}">
<svg width="260" height="260" viewBox="0 0 48 48" fill="none" style="position: absolute; inset: 0"><path d="M24 2l19.5 11.25v21.5L24 46 4.5 34.75v-21.5z" stroke="{LINE}" stroke-width="0.8"></path><path d="M24 7l15 8.6v16.8L24 41 9 32.4V15.6z" stroke="{ACC}" stroke-width="0.6" opacity="0.6"></path></svg>
{icon(k,110,ACC,'1.2')}
<span style="position: absolute; right: 18px; bottom: 26px; {HF}; font-weight: 800; font-size: 40px; color: {SAND}">{num}</span>
</div>
</div>
</section>
{bespoke}
<section style="max-width: 1360px; margin: 0 auto; padding: 8px 24px 32px; display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 14px">
<sc-for list="{h('t.sections')}" as="s" hint-placeholder-count="4">
<div style="background: {SURF}; border: 1px solid {LINE}; padding: 22px; display: flex; flex-direction: column; gap: 12px">
<h2 style="margin: 0; {HF}; font-weight: 700; font-size: 22px; letter-spacing: 0.06em; text-transform: uppercase; color: #FFFFFF">{h('s.title')}</h2>
<ul style="margin: 0; padding: 0; list-style: none; display: flex; flex-direction: column; gap: 7px">
<sc-for list="{h('s.items')}" as="it" hint-placeholder-count="5">
<li style="display: flex; align-items: baseline; gap: 10px; font-size: 15px; line-height: 1.45; color: #D2D2D6"><span aria-hidden="true" style="flex: 0 0 auto; width: 6px; height: 6px; background: {ACC}; transform: translateY(-2px) rotate(45deg); display: inline-block"></span><span>{h('it.x')}</span></li>
</sc-for>
</ul>
</div>
</sc-for>
</section>
<section style="max-width: 1360px; margin: 0 auto; padding: 0 24px 40px; display: flex; flex-direction: column; gap: 14px">
<sc-if value="{h('hasNote')}" hint-placeholder-val="{h('true')}"><p style="margin: 0; padding: 14px 16px; border: 1px dashed #3A3A3E; font-size: 15px; line-height: 1.5; color: {MUT}">{h('t.note')}</p></sc-if>
<div style="background: linear-gradient(90deg, rgba(255,107,26,0.12), rgba(255,107,26,0.02)); border: 1px solid rgba(255,107,26,0.4); padding: 26px 28px; display: flex; flex-wrap: wrap; align-items: baseline; gap: 10px 28px">
<span style="{HF}; font-weight: 800; font-size: 18px; letter-spacing: 0.2em; text-transform: uppercase; color: {ACC}">{h('t.objective')}</span>
<p style="margin: 0; flex: 1 1 420px; font-size: 19px; line-height: 1.55; color: #FFFFFF">{h('t.obj')}</p>
</div>
<nav aria-label="{h('t.fDivs')}" style="display: flex; flex-wrap: wrap; justify-content: space-between; gap: 10px; margin-top: 8px">
<a href="{FILE[prev]}" style="min-height: 48px; padding: 0 18px; display: inline-flex; align-items: center; border: 1px solid #3A3A3E; {HF}; font-weight: 700; font-size: 16px; letter-spacing: 0.08em; text-transform: uppercase">{h('t.prev')} · VERTEZ {SHORT[prev].upper()}</a>
<a href="{FILE[nxt]}" style="min-height: 48px; padding: 0 18px; display: inline-flex; align-items: center; border: 1px solid #3A3A3E; {HF}; font-weight: 700; font-size: 16px; letter-spacing: 0.08em; text-transform: uppercase">VERTEZ {SHORT[nxt].upper()} · {h('t.next')}</a>
</nav>
</section>
</main>
{footer(False)}'''
    js=r'''
class Component extends DCLogic {
  constructor(props) { super(props); this.state = { lang: startLang(), region: 2, lb: true, lc: true, li: false }; }
  renderVals() {
    const t = T[this.state.lang];
    const v = { t: t, langs: langList(this), hasNote: !!t.note };
    if (t.regions) {
      v.regionName = t.regions[this.state.region];
      v.fields = t.fields.map((x) => ({ k: x }));
      for (let i = 0; i < t.regions.length; i++) {
        v["r" + i + "on"] = this.state.region === i; v["r" + i + "off"] = this.state.region !== i;
        v["pick" + i] = () => this.setState({ region: i }); v["rn" + i] = t.regions[i];
      }
      ["lb", "lc", "li"].forEach((key) => { v[key + "On"] = this.state[key]; v[key + "Off"] = !this.state[key]; v[key + "Toggle"] = () => this.setState({ [key]: !this.state[key] }); });
    }
    return v;
  }
}'''
    return page(f"VERTEZ {SHORT[k].upper()}", body, js, T, 2100)

# ---------------- HOME ----------------
def home():
    T={}
    for L in LANGS:
        t=dict(C[L]); t.update(H[L])
        t["statusList"]=[{"x":x} for x in H[L]["statuses"].split(";")]
        t["divs"]=[{"n":f"{i+1:02d}","name":"VERTEZ "+SHORT[k].upper(),"tag":D[k][L]["tag"],"href":FILE[k],"k":k} for i,k in enumerate(ORDER)]
        ac=D["academy"][L]["sections"]
        t["courseList"]=[{"x":TIR[L]["t"],"s":TIR[L]["s"]}]+[{"x":ac[i][0],"s":" · ".join(ac[i][1][:3])} for i in (0,1,2,3)]
        t["colls"]=[{"x":x} for x in D["store"][L]["sections"][2][1]]
        T[L]=t
    divcards=""
    for i,k in enumerate(ORDER):
        divcards+=f'''<a href="{FILE[k]}" style="min-height: 210px; background: {SURF}; border: 1px solid {LINE}; padding: 22px; display: flex; flex-direction: column; gap: 12px; color: {TXT}">
<div style="display: flex; align-items: center; justify-content: space-between; color: {ACC}">{icon(k,34,ACC)}<span style="{HF}; font-weight: 800; font-size: 20px; color: {SAND}">{i+1:02d}</span></div>
<h3 style="margin: 0; {HF}; font-weight: 800; font-size: 24px; letter-spacing: 0.06em; text-transform: uppercase; color: #FFFFFF">VERTEZ {SHORT[k].upper()}</h3>
<p style="margin: 0; flex: 1 1 auto; font-size: 15px; line-height: 1.5; color: {MUT}">{h(f'divTag{i}')}</p>
<span style="font-size: 13px; font-weight: 600; letter-spacing: 0.14em; text-transform: uppercase; color: {ACC}">{h('t.open')} →</span>
</a>
'''
    mbase="position: absolute; transform: translate(-50%, -50%); background: #4B1E1B; border-radius: 50%; box-shadow: 0 0 0 1.5px #C98B7B; pointer-events: none"
    def mouths(a,b): return f'''<sc-if value="{h('mouthHalf')}" hint-placeholder-val="{h('false')}"><span aria-hidden="true" style="{a}"></span></sc-if><sc-if value="{h('mouthOpen')}" hint-placeholder-val="{h('false')}"><span aria-hidden="true" style="{b}"></span></sc-if>'''
    body_mouth=mouths(f"{mbase}; left: 53.7%; top: 13.5%; width: 3%; height: 0.35%", f"{mbase}; left: 53.7%; top: 13.6%; width: 3.3%; height: 0.65%")
    face_mouth=mouths(f"{mbase}; left: 42px; top: 62px; width: 14px; height: 4px", f"{mbase}; left: 42px; top: 63px; width: 16px; height: 8px")
    chip=f"min-height: 44px; padding: 0 14px; background: transparent; border: 1px solid #3A3A3E; color: {TXT}; font-family: 'Barlow', sans-serif; font-size: 14px; cursor: pointer; text-align: left"
    mic_svg='<svg aria-hidden="true" width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="square"><rect x="9" y="3" width="6" height="12" rx="3"></rect><path d="M5 11a7 7 0 0 0 14 0M12 18v3"></path></svg>'
    def ph_cards(title_key, ph_key, kind):
        cards=""
        for j in range(3):
            thumb = f'<div aria-hidden="true" style="aspect-ratio: 16 / 9; background: repeating-linear-gradient(45deg, #1C1C1F 0 12px, #151517 12px 24px); display: flex; align-items: center; justify-content: center; color: {MUT}">{icon(kind,30,MUT)}</div>' if kind=="media" else ""
            cards+=f'''<div style="background: {SURF}; border: 1px solid {LINE}; display: flex; flex-direction: column">{thumb}<div style="padding: 14px 16px; display: flex; flex-direction: column; gap: 6px"><span style="font-size: 12px; letter-spacing: 0.16em; text-transform: uppercase; color: {MUT}">{h('t.phDate')}</span><span style="font-size: 16px; font-weight: 600; color: {TXT}">{h('t.'+ph_key)}</span></div></div>'''
        return f'''<div style="flex: 1 1 300px; min-width: 0; display: flex; flex-direction: column; gap: 12px">
<h3 style="margin: 0; {HF}; font-weight: 700; font-size: 22px; letter-spacing: 0.08em; text-transform: uppercase; color: #FFFFFF">{h('t.'+title_key)}</h3>
{cards}
<p style="margin: 0; font-size: 13px; color: {MUT}">{h('t.emptyNote')}</p>
</div>'''
    inp=f"min-height: 52px; padding: 0 14px; background: {BG}; border: 1px solid #3A3A3E; color: {TXT}; font-family: 'Barlow', sans-serif; font-size: 16px; box-sizing: border-box; width: 100%"
    lab=f"font-size: 13px; font-weight: 600; letter-spacing: 0.12em; text-transform: uppercase; color: {MUT}"
    body=f'''{header('home', True)}
<main id="top">
<section style="max-width: 1360px; margin: 0 auto; padding: 44px 24px 24px; display: flex; flex-wrap: wrap; align-items: flex-start; gap: 40px 48px">
<div style="flex: 1 1 460px; min-width: 0; display: flex; flex-direction: column; gap: 22px; padding-top: 16px">
{sec_title(h('t.eyebrow'))}
<div style="display: flex; align-items: center; gap: 18px">{mark(92)}
<h1 style="margin: 0; {HF}; font-weight: 800; font-size: clamp(48px, 7vw, 96px); line-height: 0.9; letter-spacing: 0.08em; color: #FFFFFF">VERTEZ<br><span style="color: {ACC}">GROUP</span></h1></div>
<p style="margin: 0; {HF}; font-weight: 700; font-size: clamp(20px, 2.2vw, 28px); line-height: 1.25; letter-spacing: 0.03em; color: {SAND}">{h('t.slogan')}</p>
<p style="margin: 0; max-width: 560px; font-size: 18px; line-height: 1.65; color: #D2D2D6">{h('t.pres')}</p>
<div style="display: flex; flex-wrap: wrap; gap: 14px">
<a href="#registro" style="min-height: 56px; padding: 0 28px; display: inline-flex; align-items: center; background: {ACC}; color: {BG}; {HF}; font-weight: 800; font-size: 19px; letter-spacing: 0.12em; text-transform: uppercase; {CUT(14)}">{h('t.cta1')}</a>
<a href="#divisiones" style="min-height: 56px; padding: 0 26px; display: inline-flex; align-items: center; border: 1px solid #3A3A3E; color: {TXT}; {HF}; font-weight: 700; font-size: 19px; letter-spacing: 0.12em; text-transform: uppercase">{h('t.cta2')}</a>
</div>
</div>

<section id="asistente" ref="{h('chatRef')}" aria-label="{h('t.asTitle')}" style="flex: 1 1 440px; min-width: 0; background: rgba(24,24,26,0.85); border: 1px solid {LINE}; border-top: 3px solid {ACC}; padding: 20px; display: flex; flex-direction: column; gap: 14px; scroll-margin-top: 16px">
<div style="display: flex; flex-wrap: wrap; align-items: center; justify-content: space-between; gap: 8px 16px">
<div style="display: flex; flex-direction: column; gap: 2px"><h2 style="margin: 0; {HF}; font-weight: 700; font-size: 24px; letter-spacing: 0.08em; text-transform: uppercase; color: #FFFFFF">{h('t.asTitle')}</h2><p style="margin: 0; font-size: 14px; color: {MUT}">{h('t.asSub')}</p></div>
<button type="button" aria-pressed="{h('voicePressed')}" onClick="{h('toggleVoice')}" style="min-height: 44px; padding: 0 12px; display: inline-flex; align-items: center; gap: 8px; background: transparent; border: 1px solid #3A3A3E; color: {TXT}; font-family: 'Barlow', sans-serif; font-size: 13px; letter-spacing: 0.1em; text-transform: uppercase; cursor: pointer">
<svg aria-hidden="true" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="square"><path d="M4 9h4l5-4v14l-5-4H4z"></path><path d="M17 9c1.5 1.5 1.5 4.5 0 6"></path></svg><span>{h('voiceLabel')}</span></button>
</div>
<div style="display: flex; flex-wrap: wrap; align-items: flex-end; gap: 14px">
<div style="position: relative; flex: 0 0 auto; width: clamp(140px, 30%, 190px); display: flex; flex-direction: column; align-items: center; gap: 8px">
<sc-if value="{h('showTap')}" hint-placeholder-val="{h('true')}"><span class="vz-bob" style="background: {SAND}; color: {BG}; padding: 7px 10px; {HF}; font-weight: 700; font-size: 14px; letter-spacing: 0.05em; text-transform: uppercase; text-align: center">{h('t.tap')}</span></sc-if>
<button type="button" onClick="{h('talk')}" aria-label="{h('t.tapAria')}" style="position: relative; display: block; width: 100%; padding: 0; margin: 0; background: transparent; border: 0; cursor: pointer"><img src="{CADET}" alt="{h('t.charAlt')}" style="display: block; width: 100%; height: auto">{body_mouth}</button>
</div>
<div style="flex: 1 1 220px; min-width: 0; display: flex; flex-direction: column; gap: 10px">
<div style="display: flex; align-items: center; gap: 12px">
<button type="button" onClick="{h('talk')}" aria-label="{h('t.tapAria')}" style="position: relative; flex: 0 0 96px; width: 96px; height: 96px; padding: 0; border-radius: 50%; overflow: hidden; border: 2px solid {ACC}; background: #C9CDD3; cursor: pointer">
<sc-if value="{h('speaking')}" hint-placeholder-val="{h('false')}"><span aria-hidden="true" class="vz-pulse" style="position: absolute; inset: 0; border-radius: 50%; pointer-events: none"></span></sc-if>
<img src="{CADET}" alt="" style="position: absolute; left: -160px; top: -28px; width: 376px; max-width: none; height: auto">{face_mouth}</button>
<div style="display: flex; flex-direction: column; gap: 4px">
<span style="{HF}; font-weight: 700; font-size: 17px; letter-spacing: 0.08em; text-transform: uppercase; color: #FFFFFF">VERTEZ AI</span>
<sc-if value="{h('speaking')}" hint-placeholder-val="{h('false')}"><span style="display: inline-flex; align-items: center; gap: 8px; font-size: 12px; font-weight: 600; letter-spacing: 0.18em; text-transform: uppercase; color: {ACC}"><span aria-hidden="true" style="display: inline-flex; align-items: flex-end; gap: 2px; height: 14px"><span class="vz-bar"></span><span class="vz-bar" style="animation-delay: .15s"></span><span class="vz-bar" style="animation-delay: .3s"></span><span class="vz-bar" style="animation-delay: .45s"></span></span><span>{h('t.speaking')}</span></span></sc-if>
<sc-if value="{h('notSpeaking')}" hint-placeholder-val="{h('true')}"><span style="display: inline-flex; align-items: center; gap: 8px; font-size: 12px; font-weight: 600; letter-spacing: 0.18em; text-transform: uppercase; color: {MUT}"><span aria-hidden="true" style="width: 8px; height: 8px; border-radius: 50%; background: {ACC}; display: inline-block"></span><span>{h('t.status')}</span></span></sc-if>
</div>
</div>
<div ref="{h('threadRef')}" aria-live="polite" style="max-height: 260px; overflow-y: auto; display: flex; flex-direction: column; gap: 10px; padding-right: 4px">
<sc-for list="{h('messages')}" as="m" hint-placeholder-count="1">
<sc-if value="{h('m.bot')}" hint-placeholder-val="{h('true')}"><div style="align-self: flex-start; max-width: 96%; background: {BG}; border: 1px solid {LINE}; border-top: 2px solid {ACC}; padding: 12px 14px; font-size: 15px; line-height: 1.5; color: {TXT}; display: flex; flex-direction: column; gap: 8px"><span>{h('m.text')}</span><sc-if value="{h('m.hasLink')}" hint-placeholder-val="{h('false')}"><a href="{h('m.href')}" style="min-height: 36px; display: inline-flex; align-items: center; font-size: 13px; font-weight: 600; letter-spacing: 0.12em; text-transform: uppercase; color: {ACC}">{h('t.openLink')}</a></sc-if></div></sc-if>
<sc-if value="{h('m.user')}" hint-placeholder-val="{h('false')}"><div style="align-self: flex-end; max-width: 88%; background: {SAND}; color: {BG}; padding: 10px 14px; font-size: 15px; line-height: 1.5; font-weight: 500">{h('m.text')}</div></sc-if>
</sc-for>
</div>
<div style="display: flex; flex-wrap: wrap; gap: 8px">
<button type="button" onClick="{h('ask1')}" style="{chip}">{h('t.chip1')}</button>
<button type="button" onClick="{h('ask2')}" style="{chip}">{h('t.chip2')}</button>
<button type="button" onClick="{h('ask3')}" style="{chip}">{h('t.chip3')}</button>
</div>
</div>
</div>
<form onSubmit="{h('submit')}" style="position: relative; display: flex; align-items: stretch; background: {BG}; border: 1px solid {LINE}; border-top: 2px solid {ACC}">
<label for="vzmsg" style="position: absolute; width: 1px; height: 1px; overflow: hidden; clip-path: inset(50%)">{h('t.ph')}</label>
<input id="vzmsg" type="text" autocomplete="off" value="{h('input')}" onChange="{h('onInput')}" placeholder="{h('t.ph')}" style="flex: 1 1 0; min-width: 0; min-height: 54px; padding: 0 16px; background: transparent; border: 0; outline-offset: -2px; color: {TXT}; font-family: 'Barlow', sans-serif; font-size: 16px">
<sc-if value="{h('listening')}" hint-placeholder-val="{h('false')}"><button type="button" aria-label="{h('t.micAria')}" aria-pressed="true" onClick="{h('mic')}" style="flex: 0 0 54px; min-height: 54px; background: {SAND}; border: 0; color: {BG}; cursor: pointer; display: inline-flex; align-items: center; justify-content: center">{mic_svg}</button></sc-if>
<sc-if value="{h('notListening')}" hint-placeholder-val="{h('true')}"><button type="button" aria-label="{h('t.micAria')}" aria-pressed="false" onClick="{h('mic')}" style="flex: 0 0 54px; min-height: 54px; background: transparent; border: 0; border-left: 1px solid {LINE}; color: {TXT}; cursor: pointer; display: inline-flex; align-items: center; justify-content: center">{mic_svg}</button></sc-if>
<button type="submit" aria-label="{h('t.send')}" style="flex: 0 0 58px; min-height: 54px; background: {ACC}; border: 0; color: {BG}; cursor: pointer; display: inline-flex; align-items: center; justify-content: center"><svg aria-hidden="true" width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="square"><path d="M4 12l16-8-6 16-3-7z"></path></svg></button>
</form>
</section>
</section>

<section id="divisiones" style="max-width: 1360px; margin: 0 auto; padding: 48px 24px 24px; display: flex; flex-direction: column; gap: 20px">
<h2 style="margin: 0; {HF}; font-weight: 800; font-size: clamp(30px, 3.6vw, 44px); letter-spacing: 0.06em; text-transform: uppercase; color: #FFFFFF">{h('t.divTitle')}</h2>
<div style="display: grid; grid-template-columns: repeat(auto-fill, minmax(270px, 1fr)); gap: 14px">
{divcards}</div>
</section>

<section style="max-width: 1360px; margin: 0 auto; padding: 40px 24px 16px; display: flex; flex-wrap: wrap; gap: 24px">
<div style="flex: 1 1 440px; min-width: 0; display: flex; flex-direction: column; gap: 12px">
<div style="display: flex; align-items: baseline; justify-content: space-between; gap: 12px"><h3 style="margin: 0; {HF}; font-weight: 700; font-size: 22px; letter-spacing: 0.08em; text-transform: uppercase; color: #FFFFFF">{h('t.courses')}</h3><a href="Academy.dc.html" style="min-height: 44px; display: inline-flex; align-items: center; font-size: 13px; font-weight: 600; letter-spacing: 0.12em; text-transform: uppercase; color: {ACC}">VERTEZ ACADEMY →</a></div>
<sc-for list="{h('t.courseList')}" as="c" hint-placeholder-count="5">
<a href="Academy.dc.html" style="min-height: 64px; background: {SURF}; border: 1px solid {LINE}; padding: 12px 16px; display: flex; align-items: center; gap: 14px; color: {TXT}">{icon('academy',26,SAND)}<span style="display: flex; flex-direction: column; gap: 2px; min-width: 0"><span style="font-size: 16px; font-weight: 600">{h('c.x')}</span><span style="font-size: 13px; color: {MUT}">{h('c.s')}</span></span></a>
</sc-for>
</div>
<div style="flex: 1 1 440px; min-width: 0; display: flex; flex-direction: column; gap: 12px">
<div style="display: flex; align-items: baseline; justify-content: space-between; gap: 12px"><h3 style="margin: 0; {HF}; font-weight: 700; font-size: 22px; letter-spacing: 0.08em; text-transform: uppercase; color: #FFFFFF">{h('t.products')}</h3><a href="Store.dc.html" style="min-height: 44px; display: inline-flex; align-items: center; font-size: 13px; font-weight: 600; letter-spacing: 0.12em; text-transform: uppercase; color: {ACC}">VERTEZ STORE →</a></div>
<div style="display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 10px">
<sc-for list="{h('t.colls')}" as="c" hint-placeholder-count="4">
<a href="Store.dc.html" style="min-height: 150px; background: {SURF}; border: 1px solid {LINE}; padding: 16px; display: flex; flex-direction: column; justify-content: space-between; gap: 10px; color: {TXT}"><span aria-hidden="true" style="color: {MUT}">{icon('store',26,MUT)}</span><span style="{HF}; font-weight: 800; font-size: 21px; line-height: 1.05; text-transform: uppercase; color: #FFFFFF">{h('c.x')}</span></a>
</sc-for>
</div>
</div>
</section>

<section style="max-width: 1360px; margin: 0 auto; padding: 32px 24px 16px; display: flex; flex-wrap: wrap; gap: 24px">
{ph_cards('news','phNews','world')}
{ph_cards('videos','phVideo','media')}
{ph_cards('events','phEvent','conferences')}
</section>

<section id="registro" style="max-width: 1360px; margin: 0 auto; padding: 40px 24px 48px; scroll-margin-top: 16px">
<div style="background: {SURF}; border: 1px solid {LINE}; border-top: 3px solid {ACC}; padding: 32px; display: flex; flex-wrap: wrap; gap: 28px 48px">
<div style="flex: 1 1 320px; min-width: 0; display: flex; flex-direction: column; gap: 14px">
{mark(64)}
<h2 style="margin: 0; {HF}; font-weight: 800; font-size: clamp(30px, 3.6vw, 44px); letter-spacing: 0.04em; text-transform: uppercase; color: #FFFFFF">{h('t.regTitle')}</h2>
<p style="margin: 0; font-size: 17px; line-height: 1.6; color: #D2D2D6">{h('t.regSub')}</p>
</div>
<form onSubmit="{h('register')}" style="flex: 1 1 440px; min-width: 0; display: grid; grid-template-columns: repeat(auto-fill, minmax(220px, 1fr)); gap: 14px">
<div style="display: flex; flex-direction: column; gap: 6px"><label for="vzName" style="{lab}">{h('t.fName')}</label><input id="vzName" type="text" autocomplete="username" style="{inp}"></div>
<div style="display: flex; flex-direction: column; gap: 6px"><label for="vzEmail" style="{lab}">{h('t.fEmail')}</label><input id="vzEmail" type="email" autocomplete="email" style="{inp}"></div>
<div style="display: flex; flex-direction: column; gap: 6px"><label for="vzStatus" style="{lab}">{h('t.fStatus')}</label><select id="vzStatus" style="{inp}"><sc-for list="{h('t.statusList')}" as="s" hint-placeholder-count="6"><option>{h('s.x')}</option></sc-for></select></div>
<div style="display: flex; flex-direction: column; gap: 6px"><label for="vzPass" style="{lab}">{h('t.fPass')}</label><input id="vzPass" type="password" autocomplete="new-password" style="{inp}"></div>
<div style="grid-column: 1 / -1; display: flex; align-items: flex-start; gap: 10px"><input id="vzConsent" type="checkbox" style="width: 22px; height: 22px; margin: 2px 0 0; accent-color: {ACC}"><label for="vzConsent" style="font-size: 15px; line-height: 1.5; color: #D2D2D6">{h('t.fConsent')}</label></div>
<button type="submit" style="grid-column: 1 / -1; min-height: 56px; background: {ACC}; border: 0; color: {BG}; {HF}; font-weight: 800; font-size: 19px; letter-spacing: 0.12em; text-transform: uppercase; cursor: pointer">{h('t.fSubmit')}</button>
<sc-if value="{h('regSent')}" hint-placeholder-val="{h('false')}"><p role="status" style="grid-column: 1 / -1; margin: 0; padding: 12px 14px; border: 1px solid {ACC}; color: {ACC}; font-size: 15px; line-height: 1.5">{h('t.regDone')}</p></sc-if>
</form>
</div>
</section>
</main>
{footer(True)}'''
    js=r'''
const LINKS = { r_community: "Community.dc.html", r_store: "Store.dc.html", r_world: "World.dc.html", r_media: "Media.dc.html", r_academy: "Academy.dc.html", r_sniper: "Academy.dc.html", r_tech: "Technology.dc.html", r_ai: "AI.dc.html", r_conf: "Conferences.dc.html" };
const RULES = [
["r_limits", /dispar|sparar|shoot|apunt|\bviser|\btirer\b|matar|\btuer|uccid|\bkill|\barmas?\b|\barmes?\b|weapon|fusil|rifle|munici|munition|bullet|\bbalas?\b/],
["r_sniper", /tirador|tireur|tirator|marksman|sniper|precision/],
["r_signup", /cuenta|compte|account|registr|inscri|sign ?up|login|conex|connex|rejoindre|\bunirme|\bjoin/],
["r_conf", /conferen|debat|evento|evenement|event|visio|entrevista|interview/],
["r_community", /communit|comunidad|red social|reseau|social network|perfil|profil|\bgrupos?\b|\bgroupes?\b|\bgroups\b|foro|forum|mensaje|message/],
["r_store", /store|tienda|boutique|\bshop|producto|produit|product|ropa|vetement|cloth|comprar|acheter|\bbuy|coleccion|collection|mochila|backpack/],
["r_world", /world|mundo|monde|mapa|\bcarte\b|\bmaps?\b|geopolit|conflict|conflit|\bpais|\bpays|countr|frontera|frontiere|border/],
["r_media", /media|video|documental|documentaire|documentar|noticia|actualit|news|reportaj|reportage/],
["r_academy", /academ|formacion|formation|curso|\bcours|course|training|aprend|apprend|learn|auxil|secour|first aid|liderazgo|leadership/],
["r_tech", /tecnolog|technolog|dron|\bapps?\b|aplicacion|application|software|logiciel/],
["r_ai", /\bia\b|(^|[^'a-z])ai\b|intelig|intellig|asistente|assistant|idioma|langue|language|ingles|anglais|english|frances|francais|french|espanol|espagnol|spanish/],
["r_about", /vertez|que es|qu.est|c.est quoi|what is|plataforma|plateforme|platform|quien|qui etes|who are/],
["r_hello", /^(hola|bonjour|salut|ciao|hello|hi|hey|buenas|buongiorno|salve)\b/]
];
const MALE = /jorge|diego|pablo|juan|carlos|enrique|alvaro|raul|miguel|thomas|henri|paul|nicolas|mathieu|daniel|arthur|george|oliver|male|hombre|homme/i;
function norm(s) { return String(s || "").toLowerCase().normalize("NFD").replace(/[̀-ͯ]/g, ""); }
class Component extends DCLogic {
  constructor(props) {
    super(props);
    const saved = readStore();
    const msgs = Array.isArray(saved.chat) ? saved.chat.filter((m) => m && (m.from === "user" ? typeof m.text === "string" : T.es[m.key])).slice(-30) : [];
    this.state = { lang: startLang(), input: "", voice: saved.voice !== false, greeted: !!saved.greeted, speaking: false, mouth: 0, listening: false, regSent: false,
      messages: msgs.length ? msgs : [{ id: 0, from: "bot", key: "r_hello" }] };
    this.nextId = this.state.messages.reduce((a, m) => Math.max(a, m.id || 0), 0) + 1;
    this.thread = null; this.chat = null;
  }
  componentDidMount() {
    try { const s = window.speechSynthesis; if (s) { s.getVoices(); s.onvoiceschanged = () => s.getVoices(); } } catch (e) {}
    if (this.thread) this.thread.scrollTop = this.thread.scrollHeight;
  }
  componentDidUpdate(pp, ps) {
    if (!ps) return;
    if (this.thread && ps.messages !== this.state.messages) this.thread.scrollTop = this.thread.scrollHeight;
    if (ps.messages !== this.state.messages || ps.voice !== this.state.voice || ps.greeted !== this.state.greeted) writeStore({ chat: this.state.messages.slice(-30), voice: this.state.voice, greeted: this.state.greeted });
  }
  componentWillUnmount() { clearTimeout(this.timer); this.stopMouth(); try { window.speechSynthesis.cancel(); } catch (e) {} try { if (this.rec) this.rec.abort(); } catch (e) {} }
  startMouth(ms) {
    this.stopMouth();
    const seq = [2, 1, 2, 0, 1, 2, 1, 0, 2, 1]; let i = 0;
    this.setState({ speaking: true });
    this.mouthTimer = setInterval(() => { i = (i + 1) % seq.length; this.setState({ mouth: seq[(i + Math.floor(Math.random() * 3)) % seq.length] }); }, 105);
    this.safety = setTimeout(() => this.stopMouth(), ms);
  }
  stopMouth() {
    clearInterval(this.mouthTimer); clearTimeout(this.safety); this.mouthTimer = null;
    if (this.state && (this.state.speaking || this.state.mouth)) this.setState({ speaking: false, mouth: 0 });
  }
  pickVoice(code) {
    try {
      const all = window.speechSynthesis.getVoices() || []; const base = code.slice(0, 2);
      const same = all.filter((v) => (v.lang || "").toLowerCase().replace("_", "-").indexOf(base) === 0);
      if (!same.length) return null;
      const exact = same.filter((v) => (v.lang || "").replace("_", "-") === code); const pool = exact.length ? exact : same;
      return pool.find((v) => MALE.test(v.name)) || pool.find((v) => /google|natural|neural|premium|enhanced/i.test(v.name)) || pool[0];
    } catch (e) { return null; }
  }
  speak(key) {
    const text = T[this.state.lang][key];
    if (!this.state.voice || !text) return;
    const est = Math.min(30000, 1500 + text.length * 75); const short = Math.min(9000, text.length * 55);
    let s = null; try { s = window.speechSynthesis; } catch (e) {}
    if (!s || typeof SpeechSynthesisUtterance === "undefined") { this.startMouth(short); return; }
    try {
      s.cancel();
      const code = LANGS.find((l) => l[0] === this.state.lang)[3];
      const u = new SpeechSynthesisUtterance(text); u.lang = code;
      const v = this.pickVoice(code); if (v) u.voice = v;
      u.rate = 1; u.pitch = 0.95;
      let started = false;
      u.onstart = () => { started = true; this.startMouth(est); };
      u.onboundary = () => this.setState({ mouth: 2 });
      u.onend = () => this.stopMouth(); u.onerror = () => this.stopMouth();
      s.speak(u);
      setTimeout(() => { if (!started && !s.speaking) this.startMouth(short); }, 900);
    } catch (e) { this.startMouth(short); }
  }
  reply(key) { this.setState({ messages: this.state.messages.concat([{ id: this.nextId++, from: "bot", key: key }]), greeted: true }); this.speak(key); }
  ask(text) {
    const clean = String(text || "").trim(); if (!clean) return;
    const low = norm(clean); let key = "r_default";
    for (const r of RULES) { if (r[1].test(low)) { key = r[0]; break; } }
    this.setState({ input: "", messages: this.state.messages.concat([{ id: this.nextId++, from: "user", text: clean }]) });
    clearTimeout(this.timer); this.timer = setTimeout(() => this.reply(key), 450);
  }
  talk() {
    const bots = this.state.messages.filter((m) => m.from === "bot");
    this.setState({ greeted: true }); this.speak(bots.length ? bots[bots.length - 1].key : "r_hello");
  }
  mic() {
    if (this.state.listening) { try { this.rec.stop(); } catch (e) {} this.setState({ listening: false }); return; }
    let SR = null; try { SR = window.SpeechRecognition || window.webkitSpeechRecognition; } catch (e) {}
    if (!SR) { this.reply("micNo"); return; }
    try {
      try { window.speechSynthesis.cancel(); } catch (e) {} this.stopMouth();
      const rec = new SR(); rec.lang = LANGS.find((l) => l[0] === this.state.lang)[3]; rec.interimResults = false; rec.maxAlternatives = 1;
      rec.onresult = (ev) => { const r = ev.results && ev.results[0] && ev.results[0][0]; this.ask(r ? r.transcript : ""); };
      rec.onerror = () => { this.setState({ listening: false }); this.reply("micNo"); };
      rec.onend = () => this.setState({ listening: false });
      this.rec = rec; rec.start(); this.setState({ listening: true });
    } catch (e) { this.setState({ listening: false }); this.reply("micNo"); }
  }
  renderVals() {
    const t = T[this.state.lang];
    const v = {
      t: t,
      langs: langList(this, () => { try { window.speechSynthesis.cancel(); } catch (e) {} this.stopMouth(); }),
      input: this.state.input, voiceLabel: this.state.voice ? t.voiceOn : t.voiceOff, voicePressed: this.state.voice ? "true" : "false",
      speaking: this.state.speaking, notSpeaking: !this.state.speaking, mouthHalf: this.state.mouth === 1, mouthOpen: this.state.mouth === 2,
      showTap: !this.state.greeted, listening: this.state.listening, notListening: !this.state.listening, regSent: this.state.regSent,
      messages: this.state.messages.map((m) => ({ bot: m.from === "bot", user: m.from === "user", text: m.from === "bot" ? t[m.key] : m.text, hasLink: m.from === "bot" && !!LINKS[m.key], href: LINKS[m.key] || "#top" })),
      threadRef: (el) => { this.thread = el; }, chatRef: (el) => { this.chat = el; },
      onInput: (e) => this.setState({ input: e.target.value }),
      submit: (e) => { e.preventDefault(); this.ask(this.state.input); },
      register: (e) => { e.preventDefault(); this.setState({ regSent: true }); },
      ask1: () => this.ask(t.chip1), ask2: () => this.ask(t.chip2), ask3: () => this.ask(t.chip3),
      talk: () => this.talk(), mic: () => this.mic(),
      toggleVoice: () => { try { window.speechSynthesis.cancel(); } catch (e) {} this.stopMouth(); this.setState({ voice: !this.state.voice }); }
    };
    t.divs.forEach((d, i) => { v["divTag" + i] = d.tag; });
    return v;
  }
}'''
    return page("VERTEZ GROUP — Inicio", body, js, T, 3600)

# ---------------- IDENTITY ----------------
def identity():
    sw=[("Noche",BG,"Fondo principal"),("Grafito",SURF,"Superficies"),("Línea",LINE,"Bordes y separadores"),("Verde VERTEZ",ACC,"Acento, acciones"),("Arena",SAND,"Acento secundario"),("Blanco",TXT,"Texto")]
    sws="".join(f'''<div style="display: flex; flex-direction: column; gap: 8px"><div style="height: 120px; background: {c}; border: 1px solid #3A3A3E"></div><span style="{HF}; font-weight: 700; font-size: 20px; color: #FFFFFF">{n}</span><span style="font-size: 14px; color: {MUT}">{c.upper()} · {u}</span></div>''' for n,c,u in sw)
    icons="".join(f'''<div style="background: {SURF}; border: 1px solid {LINE}; padding: 18px; display: flex; flex-direction: column; align-items: flex-start; gap: 12px">{icon(k,40,ACC)}<span style="{HF}; font-weight: 800; font-size: 18px; letter-spacing: 0.06em; color: #FFFFFF">VERTEZ {SHORT[k].upper()}</span><span style="font-size: 13px; color: {MUT}">{i+1:02d}</span></div>''' for i,k in enumerate(ORDER))
    body=f'''<main style="width: 1440px; box-sizing: border-box; padding: 64px; display: flex; flex-direction: column; gap: 48px">
<div style="display: flex; flex-direction: column; gap: 10px">{sec_title('Etapa 1 · Identidad visual')}<h1 style="margin: 0; {HF}; font-weight: 800; font-size: 64px; letter-spacing: 0.06em; text-transform: uppercase; color: #FFFFFF">VERTEZ GROUP</h1><p style="margin: 0; font-size: 18px; color: {MUT}">Logotipo, colores, tipografía, estilo gráfico e iconos de las ocho divisiones.</p></div>
<div style="display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 16px">
<div style="background: {BG}; border: 1px solid {LINE}; min-height: 240px; display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 14px">{mark(96)}<span style="{HF}; font-weight: 800; font-size: 34px; letter-spacing: 0.18em; color: #FFFFFF">VERTEZ<span style="color: {ACC}"> GROUP</span></span><span style="font-size: 13px; color: {MUT}">Principal · fondo oscuro</span></div>
<div style="background: {TXT}; border: 1px solid {LINE}; min-height: 240px; display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 14px"><svg aria-hidden="true" width="96" height="96" viewBox="0 0 48 48" fill="none"><path d="M24 3l18 10.5v21L24 45 6 34.5v-21z" stroke="#D9540B" stroke-width="2.5"></path><path d="M13.5 15l10.5 19 10.5-19" stroke="{BG}" stroke-width="4.5" stroke-linecap="square"></path><path d="M19.5 15l4.5 8 4.5-8" stroke="#D9540B" stroke-width="2.5" stroke-linecap="square"></path></svg><span style="{HF}; font-weight: 800; font-size: 34px; letter-spacing: 0.18em; color: {BG}">VERTEZ<span style="color: #D9540B"> GROUP</span></span><span style="font-size: 13px; color: #3A3A3E">Versión clara</span></div>
<div style="background: {ACC}; min-height: 240px; display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 14px"><svg aria-hidden="true" width="120" height="120" viewBox="0 0 48 48" fill="none"><path d="M24 3l18 10.5v21L24 45 6 34.5v-21z" stroke="{BG}" stroke-width="2.5"></path><path d="M13.5 15l10.5 19 10.5-19" stroke="{BG}" stroke-width="4.5" stroke-linecap="square"></path></svg><span style="font-size: 13px; color: {BG}; font-weight: 600">Símbolo · icono de la app</span></div>
</div>
<div style="display: flex; flex-direction: column; gap: 16px"><h2 style="margin: 0; {HF}; font-weight: 700; font-size: 28px; letter-spacing: 0.1em; text-transform: uppercase; color: #FFFFFF">Colores</h2><div style="display: grid; grid-template-columns: repeat(6, minmax(0, 1fr)); gap: 16px">{sws}</div></div>
<div style="display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 16px">
<div style="background: {SURF}; border: 1px solid {LINE}; padding: 28px; display: flex; flex-direction: column; gap: 10px"><span style="font-size: 13px; letter-spacing: 0.2em; text-transform: uppercase; color: {MUT}">Títulos · Saira Condensed 800</span><span style="{HF}; font-weight: 800; font-size: 72px; line-height: 1; text-transform: uppercase; color: #FFFFFF">Construir el futuro</span></div>
<div style="background: {SURF}; border: 1px solid {LINE}; padding: 28px; display: flex; flex-direction: column; gap: 10px"><span style="font-size: 13px; letter-spacing: 0.2em; text-transform: uppercase; color: {MUT}">Texto · Saira 400 / 600</span><p style="margin: 0; font-size: 20px; line-height: 1.6; color: #D2D2D6">Conectar las competencias. Compartir los conocimientos. Construir el futuro. Una plataforma internacional de comunidad, tecnología, información y formación.</p></div>
</div>
<div style="display: flex; flex-direction: column; gap: 16px"><h2 style="margin: 0; {HF}; font-weight: 700; font-size: 28px; letter-spacing: 0.1em; text-transform: uppercase; color: #FFFFFF">Iconos de las divisiones</h2><div style="display: grid; grid-template-columns: repeat(8, minmax(0, 1fr)); gap: 12px">{icons}</div></div>
<div style="display: flex; flex-wrap: wrap; gap: 12px; align-items: center"><span style="{HF}; font-weight: 700; font-size: 20px; letter-spacing: 0.1em; text-transform: uppercase; color: #FFFFFF">Estilo gráfico:</span>
<span style="min-height: 48px; padding: 0 22px; display: inline-flex; align-items: center; background: {ACC}; color: {BG}; {HF}; font-weight: 800; font-size: 18px; letter-spacing: 0.12em; text-transform: uppercase; {CUT(12)}">Esquinas cortadas</span>
<span style="min-height: 48px; padding: 0 22px; display: inline-flex; align-items: center; border: 1px solid #3A3A3E; color: {TXT}; font-size: 16px">Retícula táctica de fondo</span>
<span style="min-height: 48px; padding: 0 22px; display: inline-flex; align-items: center; border: 1px solid #3A3A3E; color: {TXT}; font-size: 16px">Hexágono como forma de marca</span>
<span style="min-height: 48px; padding: 0 22px; display: inline-flex; align-items: center; border: 1px solid #3A3A3E; color: {TXT}; font-size: 16px">Mayúsculas espaciadas en títulos</span></div>
</main>'''
    js="class Component extends DCLogic { renderVals() { return {}; } }"
    return page("VERTEZ GROUP — Identidad visual", body, js, {"es":{}}, 1500).replace("const T = {\"es\": {}};","const T = {};")

if __name__=="__main__":
  files={"Main.dc.html":home(),"Identidad.dc.html":identity()}
  for i,k in enumerate(ORDER): files[FILE[k]]=division(k,i)
  os.makedirs(OUT,exist_ok=True)
  for f,c in files.items(): open(os.path.join(OUT,f),"w").write(c)
  print({f:len(c) for f,c in files.items()})
