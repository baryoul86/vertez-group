# -*- coding: utf-8 -*-
import re, json, html, os, shutil
import gen
gen.STATIC = True
from gen import *
from content import *
HERE=os.path.dirname(os.path.abspath(__file__))
SITE=os.path.dirname(HERE)
CONFIG_JS="""// VERTEZ GROUP — conexión con Supabase (valores públicos: la seguridad la ponen las reglas RLS)
window.VZ_CONFIG = {
  supabaseUrl: "https://ngsowaxieldasugogbjv.supabase.co",
  supabaseKey: "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im5nc293YXhpZWxkYXN1Z29nYmp2Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3OTQ5Mzg1OTIsImV4cCI6MjExMDUxNDU5Mn0.S2lZe4uwC5HwNGZM0BGRbU998zjlSPgud2ojak4ppAc",
  adminEmail: "admin@vertez-group.app",
  bucket: "media"
};
"""
if os.path.exists(SITE):
    for _n in os.listdir(SITE):
        if _n in (".git","assets","build",".gitignore"): continue
        _p=os.path.join(SITE,_n); shutil.rmtree(_p) if os.path.isdir(_p) else os.remove(_p)
os.makedirs(SITE+"/assets",exist_ok=True)
CADET_URL="/assets/cadet.webp"
from extra import EXTRA
SLUG={k:k for k in ORDER}

# ---------- tiny template engine for the .dc markup ----------
DYN_IF=re.compile(r'^(r\d+(on|off)|l[bci](On|Off)|speaking|notSpeaking|mouthHalf|mouthOpen|showTap|listening|notListening|regSent)$')
DYN_V={"voiceLabel","regionName"}
def lookup(ctx,path):
    if path=="true": return True
    if path=="false": return False
    cur=ctx
    for p in path.split("."):
        if isinstance(cur,list): cur=cur[int(p)]
        elif isinstance(cur,dict): cur=cur.get(p,"")
        else: return ""
    return cur
def find_close(s,i,tag):
    depth=1; pat=re.compile(r'<(/?)'+tag+r'\b')
    while True:
        m=pat.search(s,i)
        if not m: raise ValueError("unclosed "+tag)
        if m.group(1): depth-=1
        else: depth+=1
        if depth==0: return m.start()
        i=m.end()
def holes(s,ctx):
    s=re.sub(r'onClick="\{\{\s*([\w.]+)\s*\}\}"',r'data-act="\1"',s)
    s=re.sub(r'onSubmit="\{\{\s*([\w.]+)\s*\}\}"',r'data-submit="\1"',s)
    s=re.sub(r'\s(onChange|value)="\{\{\s*[\w.]+\s*\}\}"','',s)
    s=re.sub(r'(?<![\w-])ref="\{\{\s*([\w.]+)\s*\}\}"',r'data-ref="\1"',s)
    s=re.sub(r'\shint-[\w-]+="[^"]*"','',s)
    def rep(m):
        p=m.group(1); v=lookup(ctx,p)
        if v is True: v="true"
        if v is False: v="false"
        txt=html.escape(str(v),quote=True)
        return f'<x-v data-v="{p}">{txt}</x-v>' if p in DYN_V else txt
    return re.sub(r'\{\{\s*([\w.$]+)\s*\}\}',rep,s)
def render(s,ctx):
    out=[]; pos=0; pat=re.compile(r'<(sc-for|sc-if)\b([^>]*)>')
    while True:
        m=pat.search(s,pos)
        if not m: out.append(holes(s[pos:],ctx)); break
        out.append(holes(s[pos:m.start()],ctx))
        tag=m.group(1); attrs=m.group(2); a=m.end(); c=find_close(s,a,tag); inner=s[a:c]; pos=c+len(f'</{tag}>')
        if tag=="sc-for":
            lp=re.search(r'list="\{\{\s*([\w.]+)\s*\}\}"',attrs).group(1); nm=re.search(r'as="(\w+)"',attrs).group(1)
            if lp=="messages":
                for kind in ("bot","user"):
                    mctx=dict(ctx); mctx[nm]={"bot":kind=="bot","user":kind=="user","text":"@@TEXT@@","hasLink":True,"href":"@@HREF@@"}
                    tp=render(inner,mctx).replace("@@TEXT@@",'<x-slot data-slot="text"></x-slot>').replace('href="@@HREF@@"','href="#" data-slot="href"')
                    out.append(f'<template data-tpl="{kind}">{tp}</template>')
            else:
                for i,it in enumerate(lookup(ctx,lp) or []):
                    c2=dict(ctx); c2[nm]=it; c2["$index"]=i; out.append(render(inner,c2))
        else:
            p=re.search(r'value="\{\{\s*([\w.]+)\s*\}\}"',attrs).group(1); v=lookup(ctx,p)
            if DYN_IF.match(p): out.append(f'<x-if data-if="{p}"{"" if v else " hidden"}>{render(inner,ctx)}</x-if>')
            elif v: out.append(render(inner,ctx))
    return "".join(out)

def extract_body(dc):
    b=dc.split("<x-dc>",1)[1].split("</x-dc>",1)[0]
    b=re.sub(r'<helmet>.*?</helmet>','',b,flags=re.S)
    return b
def fix_links(s,L):
    s=s.replace('href="Main.dc.html#registro"',f'href="/{L}#registro"').replace('href="Main.dc.html"',f'href="/{L}"')
    for k in ORDER: s=s.replace(f'href="{FILE[k]}"',f'href="/{L}/{SLUG[k]}"')
    s=s.replace("/_blob/88c8f8cf79800d1034420beda37ce663",CADET_URL)
    return s

def home_sections(raw,L,t):
    e=EXTRA[L]
    m=raw.index('<main id="top">')+len('<main id="top">')
    hs=raw.index('<section',m); he=raw.index('<section id="divisiones"')
    hero=f'''<section id="portada" style="position: relative; overflow: hidden; background: #0B0B0C; border-bottom: 1px solid {LINE}">
<div aria-hidden="true" data-hero-default style="position: absolute; inset: 0; display: flex; justify-content: space-between">
<img src="/assets/hero-left.webp" alt="" style="height: 100%; width: 48%; object-fit: cover; object-position: left center; -webkit-mask-image: linear-gradient(to right, #000 55%, transparent); mask-image: linear-gradient(to right, #000 55%, transparent)">
<img src="/assets/hero-right.webp" alt="" style="height: 100%; width: 48%; object-fit: cover; object-position: right center; -webkit-mask-image: linear-gradient(to left, #000 55%, transparent); mask-image: linear-gradient(to left, #000 55%, transparent)">
</div>
<img aria-hidden="true" data-hero-custom alt="" hidden style="position: absolute; inset: 0; width: 100%; height: 100%; object-fit: cover">
<div aria-hidden="true" style="position: absolute; inset: 0; background: radial-gradient(ellipse at center, rgba(11,11,12,0.9) 0%, rgba(11,11,12,0.72) 38%, rgba(11,11,12,0.2) 78%)"></div>
<div style="position: relative; max-width: 940px; margin: 0 auto; padding: clamp(72px, 12vw, 132px) 24px clamp(64px, 10vw, 112px); text-align: center; display: flex; flex-direction: column; align-items: center; gap: 22px">
<p style="margin: 0; font-size: 14px; font-weight: 600; letter-spacing: 0.3em; text-transform: uppercase; color: {ACC}">VERTEZ GROUP · {{{{t.eyebrow}}}}</p>
<h1 style="margin: 0; font-family: 'Oswald', sans-serif; font-weight: 600; font-size: clamp(34px, 5.4vw, 64px); line-height: 1.08; letter-spacing: 0.01em; text-transform: uppercase; color: #FFFFFF">{html.escape(e['heroA'])}<br><span style="color: {ACC}">{html.escape(e['heroB'])}</span></h1>
<p style="margin: 0; max-width: 720px; font-size: clamp(17px, 1.6vw, 20px); line-height: 1.55; color: #E6E6E8">{{{{t.pres}}}}</p>
<div style="display: flex; flex-wrap: wrap; justify-content: center; gap: 14px; margin-top: 6px">
<a href="#registro" style="min-height: 52px; padding: 0 28px; display: inline-flex; align-items: center; background: {ACC}; color: #0B0B0C; border-radius: 3px; font-family: 'Oswald', sans-serif; font-weight: 600; font-size: 17px; letter-spacing: 0.06em; text-transform: uppercase">{{{{t.cta1}}}}</a>
<a href="#divisiones" style="min-height: 52px; padding: 0 28px; display: inline-flex; align-items: center; background: #FFFFFF; color: #0B0B0C; border-radius: 3px; font-family: 'Oswald', sans-serif; font-weight: 600; font-size: 17px; letter-spacing: 0.06em; text-transform: uppercase">{{{{t.cta2}}}}</a>
</div>
</div>
</section>
<section style="max-width: 1240px; margin: 0 auto; padding: 0 24px"><div style="display: flex; flex-wrap: wrap; align-items: center; justify-content: center; gap: 18px 28px; padding: 26px 0; border-bottom: 1px solid {LINE}">
<section id="asistente"></section>
</div></section>'''
    raw=raw[:hs]+hero+raw[he:]
    # divisions
    ds=raw.index('<section id="divisiones"'); de=raw.index('</section>',ds)+len('</section>')
    cards=""
    for i,k in enumerate(ORDER):
        cards+=f'''<a href="{FILE[k]}" class="vz-card" style="min-height: 190px; background: #18181A; border: 1px solid #2C2C2F; border-radius: 4px; padding: 22px; display: flex; flex-direction: column; gap: 12px; color: #F2F2F2; text-decoration: none">
<div style="display: flex; align-items: flex-start; justify-content: space-between; color: {ACC}">{icon(k,46,ACC,"1.5")}<span style="font-family: 'Oswald', sans-serif; font-weight: 600; font-size: 15px; color: #6E6E73">{i+1:02d}</span></div>
<h3 style="margin: 0; font-family: 'Oswald', sans-serif; font-weight: 500; font-size: 21px; letter-spacing: 0.03em; text-transform: uppercase; color: #FFFFFF">VERTEZ {SHORT[k].upper()}</h3>
<p style="margin: 0; flex: 1 1 auto; font-size: 15px; line-height: 1.45; color: {MUT}">{{{{divTag{i}}}}}</p>
<span style="font-size: 13px; font-weight: 600; letter-spacing: 0.12em; text-transform: uppercase; color: {ACC}">{{{{t.open}}}} →</span>
</a>
'''
    divs=f'''<section id="divisiones" style="position: relative; padding: 56px 24px 48px; border-bottom: 1px solid {LINE}">
<img src="/assets/flank-left.webp" alt="" aria-hidden="true" class="vz-flank" style="position: absolute; left: 0; bottom: 0; height: 360px; width: auto; -webkit-mask-image: linear-gradient(to right, #000 60%, transparent); mask-image: linear-gradient(to right, #000 60%, transparent)">
<img src="/assets/flank-right.webp" alt="" aria-hidden="true" class="vz-flank" style="position: absolute; right: 0; bottom: 0; height: 360px; width: auto; -webkit-mask-image: linear-gradient(to left, #000 60%, transparent); mask-image: linear-gradient(to left, #000 60%, transparent)">
<div style="position: relative; max-width: 1100px; margin: 0 auto; display: flex; flex-direction: column; gap: 26px">
<h2 style="margin: 0; text-align: center; font-family: 'Oswald', sans-serif; font-weight: 500; font-size: clamp(28px, 3.4vw, 38px); letter-spacing: 0.04em; text-transform: uppercase; color: #FFFFFF">{{{{t.divTitle}}}}</h2>
<div style="display: grid; grid-template-columns: repeat(auto-fill, minmax(240px, 1fr)); gap: 14px">
{cards}</div>
</div>
</section>'''
    raw=raw[:ds]+divs+raw[de:]
    # feeds (news / videos / events)
    fs=raw.index('<section style="max-width: 1360px; margin: 0 auto; padding: 32px 24px 16px; display: flex; flex-wrap: wrap; gap: 24px">')
    fe=raw.index('</section>',fs)+len('</section>')
    def col(kind,title,ph,ic):
        phc="".join(f'''<div style="background: #18181A; border: 1px solid #2C2C2F; border-radius: 4px; padding: 14px 16px; display: flex; flex-direction: column; gap: 6px"><span style="font-size: 12px; letter-spacing: 0.16em; text-transform: uppercase; color: {MUT}">{{{{t.phDate}}}}</span><span style="font-size: 16px; font-weight: 600">{{{{t.{ph}}}}}</span></div>''' for _ in range(3))
        return f'''<div style="flex: 1 1 300px; min-width: 0; display: flex; flex-direction: column; gap: 12px">
<h3 style="margin: 0; display: flex; align-items: center; gap: 10px; font-family: 'Oswald', sans-serif; font-weight: 500; font-size: 22px; letter-spacing: 0.06em; text-transform: uppercase; color: #FFFFFF">{icon(ic,24,ACC)}{{{{t.{title}}}}}</h3>
<div data-feed="{kind}" data-limit="3" style="display: flex; flex-direction: column; gap: 12px">{phc}<p style="margin: 0; font-size: 13px; color: {MUT}">{{{{t.emptyNote}}}}</p></div>
</div>'''
    feeds=f'''<section style="max-width: 1360px; margin: 0 auto; padding: 40px 24px 16px; display: flex; flex-wrap: wrap; gap: 24px">
{col("news","news","phNews","world")}
{col("videos","videos","phVideo","media")}
{col("events","events","phEvent","conferences")}
</section>'''
    raw=raw[:fs]+feeds+raw[fe:]
    return raw

def feed_block(kind,L):
    e=EXTRA[L]
    title={"photos":e["gallery"],"videos":e["allVideos"],"events":e["agenda"]}[kind]
    grid="repeat(auto-fill, minmax(220px, 1fr))" if kind=="photos" else "repeat(auto-fill, minmax(300px, 1fr))"
    return f'''<section style="max-width: 1360px; margin: 0 auto; padding: 8px 24px 32px; display: flex; flex-direction: column; gap: 14px">
<h2 style="margin: 0; font-family: 'Oswald', sans-serif; font-weight: 500; font-size: 26px; letter-spacing: 0.06em; text-transform: uppercase; color: #FFFFFF">{html.escape(title)}</h2>
<div data-feed="{kind}" data-limit="60" style="display: grid; grid-template-columns: {grid}; gap: 12px"><p style="margin: 0; font-size: 14px; color: {MUT}">{html.escape(e["empty"])}</p></div>
</section>'''

def langs_ctx(L,slug):
    return [{"code":c.upper(),"lc":c,"name":n,"active":c==L,"inactive":c!=L,"href":f"/{c}" + (f"/{slug}" if slug else "")} for c,n in (("es","Español"),("fr","Français"),("en","English"))]

FAVICON='<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 48 48"><rect width="48" height="48" fill="#0B0B0C"/><path d="M24 3l18 6v14c0 11-7.6 19-18 22C13.6 42 6 34 6 23V9z" fill="none" stroke="#FF6B1A" stroke-width="2.6"/><path d="M14 15l10 19 10-19" fill="none" stroke="#F2F2F2" stroke-width="4.5" stroke-linecap="square"/><path d="M19.5 15l4.5 8.5 4.5-8.5" fill="none" stroke="#FF6B1A" stroke-width="2.5" stroke-linecap="square"/></svg>'
def fab_html(L):
    e=EXTRA[L]
    return f'''<a href="/{L}/asistente" class="vz-fab" aria-label="{html.escape(e['talkCta'],quote=True)}" style="position: fixed; right: 16px; bottom: 16px; z-index: 60; display: inline-flex; align-items: center; gap: 10px; min-height: 56px; padding: 5px 18px 5px 5px; background: {ACC}; color: #0B0B0C; border-radius: 999px; box-shadow: 0 8px 28px rgba(0,0,0,0.55); font-family: 'Oswald', sans-serif; font-weight: 600; font-size: 17px; letter-spacing: 0.06em; text-transform: uppercase; text-decoration: none">
<span aria-hidden="true" style="position: relative; flex: 0 0 48px; width: 48px; height: 48px; border-radius: 50%; overflow: hidden; background: #C9CDD3; border: 2px solid #0B0B0C"><img src="{CADET_URL}" alt="" style="position: absolute; left: -82px; top: -15px; width: 196px; max-width: none; height: auto"></span>
<span>{html.escape(e['talkCta'])}</span></a>'''
def doc(L,slug,title,desc,body,vz,fab=True):
    alts="".join(f'<link rel="alternate" hreflang="{c}" href="/{c}{"/"+slug if slug else ""}">' for c in LANGS)
    style=HEAD_STYLE.replace("<style>","<style>\n[hidden]{display:none!important}x-if{display:contents}x-if[hidden]{display:none}x-v{display:inline}\n.vz-flank{display:none}@media (min-width:1200px){.vz-flank{display:block}}\n.vz-card{transition:border-color .15s,transform .15s}.vz-card:hover{border-color:#FF6B1A!important;transform:translateY(-2px)}\n[data-admin] input,[data-admin] textarea{font:inherit}\n@media (max-width:520px){.vz-fab span:last-child{display:none}.vz-fab{padding:5px!important}}\nhtml{scroll-behavior:smooth}\n@media (max-width:760px){header nav{flex-wrap:nowrap!important;overflow-x:auto;width:100%;padding-bottom:4px;scrollbar-width:none}header nav::-webkit-scrollbar{display:none}header nav a{flex:0 0 auto}}\n*{-webkit-tap-highlight-color:transparent}")
    return f'''<!doctype html>
<html lang="{L}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(title)}</title>
<meta name="description" content="{html.escape(desc,quote=True)}">
<meta name="theme-color" content="#0B0B0C">
<meta property="og:title" content="{html.escape(title,quote=True)}">
<meta property="og:description" content="{html.escape(desc,quote=True)}">
<meta property="og:type" content="website">
<link rel="icon" href="/assets/favicon.svg" type="image/svg+xml">
{alts}
{style}
</head>
<body>
{body}
{fab_html(L) if fab else ""}
<script src="/assets/config.js"></script>
<script>window.VZ={json.dumps(vz,ensure_ascii=False)};</script>
<script src="/assets/site.js" defer></script>
</body>
</html>
'''

def page_ctx(L,slug):
    t=dict(C[L]); t.update(H[L]); t.update(EXTRA[L])
    return t

pages=0
for L in LANGS:
    os.makedirs(f"{SITE}/{L}",exist_ok=True)
    # ---- divisions
    for i,k in enumerate(ORDER):
        dc=division(k,i)
        T=json.loads(dc.split("const T = ",1)[1].split(";\n",1)[0])
        t=T[L]; ctx={"t":t,"langs":langs_ctx(L,SLUG[k]),"hasNote":bool(t.get("note"))}
        vz={"page":k,"lang":L}
        if k=="world":
            ctx.update(regionName=t["regions"][2],fields=[{"k":x} for x in t["fields"]],lbOn=True,lbOff=False,lcOn=True,lcOff=False,liOn=False,liOff=True)
            for j,rn in enumerate(t["regions"]): ctx[f"rn{j}"]=rn; ctx[f"r{j}on"]=j==2; ctx[f"r{j}off"]=j!=2
            vz["regions"]=t["regions"]
        body=render(extract_body(dc),ctx)
        GRID='<section style="max-width: 1360px; margin: 0 auto; padding: 8px 24px 32px; display: grid'
        if k=="media": body=body.replace(GRID,feed_block("videos",L)+feed_block("photos",L)+GRID,1)
        if k=="conferences": body=body.replace(GRID,feed_block("events",L)+GRID,1)
        if k=="academy":
            body=body.replace('href="Main.dc.html" style="align-self: flex-start; min-height: 48px',f'href="/{L}/asistente" style="align-self: flex-start; min-height: 48px')
        body=fix_links(body,L)
        open(f"{SITE}/{L}/{SLUG[k]}.html","w").write(doc(L,SLUG[k],f"VERTEZ {SHORT[k].upper()} — {t['tag']}",t["intro"],body,vz)); pages+=1
    # ---- home
    dc=home(); T=json.loads(dc.split("const T = ",1)[1].split(";\n",1)[0]); t=T[L]; t.update(EXTRA[L])
    ctx={"t":t,"langs":langs_ctx(L,""),"regSent":False}
    for j,d in enumerate(t["divs"]): ctx[f"divTag{j}"]=d["tag"]
    raw=extract_body(dc)
    raw=home_sections(raw,L,t)
    a=raw.index('<section id="asistente"'); b=raw.index('</section>',a)+len('</section>')
    teaser=f'''<section id="asistente" aria-label="{{{{t.asTitle}}}}" style="display: contents">
<a href="/{L}/asistente" style="flex: 0 0 auto; display: block; width: 74px; height: 74px; border-radius: 50%; overflow: hidden; position: relative; background: #C9CDD3; border: 2px solid {ACC}"><img src="{CADET_URL}" alt="{{{{t.charAlt}}}}" style="position: absolute; left: -125px; top: -22px; width: 294px; max-width: none; height: auto"></a>
<div style="flex: 1 1 260px; min-width: 0; max-width: 560px; display: flex; flex-direction: column; gap: 4px"><h2 style="margin: 0; font-family: 'Oswald', sans-serif; font-weight: 500; font-size: 22px; letter-spacing: 0.04em; text-transform: uppercase; color: #FFFFFF">{{{{t.asTitle}}}}</h2><p style="margin: 0; font-size: 15px; color: {MUT}">{{{{t.asSub}}}}</p></div>
<a href="/{L}/asistente" style="min-height: 50px; padding: 0 22px; display: inline-flex; align-items: center; gap: 10px; background: {ACC}; color: #0B0B0C; border-radius: 3px; font-family: 'Oswald', sans-serif; font-weight: 600; font-size: 17px; letter-spacing: 0.06em; text-transform: uppercase"><svg aria-hidden="true" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="square"><path d="M4 5h16v11H9l-5 4z"></path></svg>{{{{t.talkCta}}}}</a>
</section>'''
    body=render(raw[:a]+teaser+raw[b:],ctx)
    body=fix_links(body,L)
    open(f"{SITE}/{L}/index.html","w").write(doc(L,"",f"VERTEZ GROUP — {t['slogan']}",t["pres"],body,{"page":"home","lang":L})); pages+=1
    # ---- assistant page (full screen)
    mbase="position: absolute; transform: translate(-50%, -50%); background: #4B1E1B; border-radius: 50%; box-shadow: 0 0 0 2px #C98B7B; pointer-events: none"
    def mouths(a_,b_): return f'''<sc-if value="{{{{mouthHalf}}}}"><span aria-hidden="true" style="{a_}"></span></sc-if><sc-if value="{{{{mouthOpen}}}}"><span aria-hidden="true" style="{b_}"></span></sc-if>'''
    # face close-up 180px: scale 0.75 → img 706px, left -300, top -52; mouth (505*.75-300, 225*.75-52)=(78.75,116.75)
    face=f'''<button type="button" data-act="talk" aria-label="{{{{t.tapAria}}}}" style="position: relative; flex: 0 0 180px; width: 180px; height: 180px; padding: 0; border-radius: 50%; overflow: hidden; border: 3px solid {ACC}; background: #C9CDD3; cursor: pointer">
<sc-if value="{{{{speaking}}}}"><span aria-hidden="true" class="vz-pulse" style="position: absolute; inset: 0; border-radius: 50%; pointer-events: none; z-index: 2"></span></sc-if>
<img src="{CADET_URL}" alt="" style="position: absolute; left: -300px; top: -52px; width: 706px; max-width: none; height: auto">
{mouths(f"{mbase}; left: 79px; top: 117px; width: 26px; height: 7px", f"{mbase}; left: 79px; top: 119px; width: 30px; height: 15px")}
</button>'''
    chip=f"min-height: 48px; padding: 0 16px; background: transparent; border: 1px solid #3A3A3E; color: {TXT}; font-family: 'Barlow', sans-serif; font-size: 15px; cursor: pointer; text-align: left"
    mic_svg='<svg aria-hidden="true" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="square"><rect x="9" y="3" width="6" height="12" rx="3"></rect><path d="M5 11a7 7 0 0 0 14 0M12 18v3"></path></svg>'
    as_main=f'''<main id="top" style="max-width: 1360px; margin: 0 auto; padding: 20px 24px 40px; min-height: calc(100vh - 90px); box-sizing: border-box; display: flex; flex-direction: column; gap: 16px">
<a href="/{L}" style="align-self: flex-start; min-height: 44px; display: inline-flex; align-items: center; font-size: 14px; letter-spacing: 0.1em; color: {MUT}">{{{{t.back}}}}</a>
<div style="flex: 1 1 auto; display: flex; flex-wrap: wrap; align-items: stretch; gap: 24px 40px">
<div style="position: relative; flex: 1 1 340px; min-width: 0; display: flex; flex-direction: column; align-items: center; justify-content: flex-end; gap: 12px; background: radial-gradient(ellipse at 50% 60%, rgba(255,107,26,0.16) 0%, rgba(11,11,12,0) 65%)">
<sc-if value="{{{{showTap}}}}"><button type="button" data-act="talk" class="vz-bob" style="position: relative; z-index: 2; min-height: 48px; padding: 0 18px; background: {SAND}; border: 0; color: {BG}; {HF}; font-weight: 800; font-size: 20px; letter-spacing: 0.06em; text-transform: uppercase; cursor: pointer">{{{{t.tap}}}}</button></sc-if>
<button type="button" data-act="talk" aria-label="{{{{t.tapAria}}}}" style="position: relative; display: block; width: min(100%, 440px, 46vh); padding: 0; margin: 0; background: transparent; border: 0; cursor: pointer">
<img src="{CADET_URL}" alt="{{{{t.charAlt}}}}" style="display: block; width: 100%; height: auto">
{mouths(f"{mbase}; left: 53.7%; top: 13.5%; width: 3.2%; height: 0.4%", f"{mbase}; left: 53.7%; top: 13.65%; width: 3.6%; height: 0.8%")}
</button>
</div>
<section aria-label="{{{{t.asTitle}}}}" style="flex: 1.4 1 420px; min-width: 0; background: rgba(24,24,26,0.9); border: 1px solid {LINE}; border-top: 3px solid {ACC}; padding: 22px; display: flex; flex-direction: column; gap: 16px">
<div style="display: flex; flex-wrap: wrap; align-items: center; gap: 16px 20px">
{face}
<div style="flex: 1 1 200px; min-width: 0; display: flex; flex-direction: column; gap: 8px">
<h1 style="margin: 0; {HF}; font-weight: 800; font-size: clamp(28px, 3.4vw, 40px); line-height: 1; letter-spacing: 0.04em; text-transform: uppercase; color: #FFFFFF">{{{{t.asTitle}}}}</h1>
<p style="margin: 0; font-size: 15px; color: {MUT}">{{{{t.asSub}}}}</p>
<sc-if value="{{{{speaking}}}}"><span style="display: inline-flex; align-items: center; gap: 8px; font-size: 13px; font-weight: 600; letter-spacing: 0.18em; text-transform: uppercase; color: {ACC}"><span aria-hidden="true" style="display: inline-flex; align-items: flex-end; gap: 2px; height: 14px"><span class="vz-bar"></span><span class="vz-bar" style="animation-delay: .15s"></span><span class="vz-bar" style="animation-delay: .3s"></span><span class="vz-bar" style="animation-delay: .45s"></span></span><span>{{{{t.speaking}}}}</span></span></sc-if>
<sc-if value="{{{{notSpeaking}}}}"><span style="display: inline-flex; align-items: center; gap: 8px; font-size: 13px; font-weight: 600; letter-spacing: 0.18em; text-transform: uppercase; color: {MUT}"><span aria-hidden="true" style="width: 8px; height: 8px; border-radius: 50%; background: {ACC}; display: inline-block"></span><span>{{{{t.status}}}}</span></span></sc-if>
<button type="button" data-act="toggleVoice" aria-pressed="true" style="align-self: flex-start; min-height: 44px; padding: 0 12px; display: inline-flex; align-items: center; gap: 8px; background: transparent; border: 1px solid #3A3A3E; color: {TXT}; font-family: 'Barlow', sans-serif; font-size: 13px; letter-spacing: 0.1em; text-transform: uppercase; cursor: pointer"><svg aria-hidden="true" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="square"><path d="M4 9h4l5-4v14l-5-4H4z"></path><path d="M17 9c1.5 1.5 1.5 4.5 0 6"></path></svg><span>{{{{voiceLabel}}}}</span></button>
</div>
</div>
<div ref="{{{{threadRef}}}}" aria-live="polite" style="flex: 1 1 auto; min-height: 220px; max-height: 46vh; overflow-y: auto; display: flex; flex-direction: column; gap: 12px; padding-right: 4px">
<sc-for list="{{{{messages}}}}" as="m">
<sc-if value="{{{{m.bot}}}}"><div style="align-self: flex-start; max-width: 94%; background: {BG}; border: 1px solid {LINE}; border-top: 2px solid {ACC}; padding: 14px 16px; font-size: 17px; line-height: 1.55; color: {TXT}; display: flex; flex-direction: column; gap: 8px"><span>{{{{m.text}}}}</span><sc-if value="{{{{m.hasLink}}}}"><a href="{{{{m.href}}}}" style="min-height: 40px; display: inline-flex; align-items: center; font-size: 14px; font-weight: 600; letter-spacing: 0.12em; text-transform: uppercase; color: {ACC}">{{{{t.openLink}}}}</a></sc-if></div></sc-if>
<sc-if value="{{{{m.user}}}}"><div style="align-self: flex-end; max-width: 88%; background: {SAND}; color: {BG}; padding: 12px 16px; font-size: 17px; line-height: 1.5; font-weight: 500">{{{{m.text}}}}</div></sc-if>
</sc-for>
</div>
<div style="display: flex; flex-wrap: wrap; gap: 8px">
<button type="button" data-act="ask1" style="{chip}">{{{{t.chip1}}}}</button>
<button type="button" data-act="ask2" style="{chip}">{{{{t.chip2}}}}</button>
<button type="button" data-act="ask3" style="{chip}">{{{{t.chip3}}}}</button>
</div>
<form data-submit="submit" style="position: relative; display: flex; align-items: stretch; background: {BG}; border: 1px solid {LINE}; border-top: 2px solid {ACC}">
<label for="vzmsg" style="position: absolute; width: 1px; height: 1px; overflow: hidden; clip-path: inset(50%)">{{{{t.ph}}}}</label>
<input id="vzmsg" type="text" autocomplete="off" placeholder="{{{{t.ph}}}}" style="flex: 1 1 0; min-width: 0; min-height: 60px; padding: 0 16px; background: transparent; border: 0; outline-offset: -2px; color: {TXT}; font-family: 'Barlow', sans-serif; font-size: 17px">
<sc-if value="{{{{listening}}}}"><button type="button" data-act="mic" aria-label="{{{{t.micAria}}}}" aria-pressed="true" style="flex: 0 0 60px; min-height: 60px; background: {SAND}; border: 0; color: {BG}; cursor: pointer; display: inline-flex; align-items: center; justify-content: center">{mic_svg}</button></sc-if>
<sc-if value="{{{{notListening}}}}"><button type="button" data-act="mic" aria-label="{{{{t.micAria}}}}" aria-pressed="false" style="flex: 0 0 60px; min-height: 60px; background: transparent; border: 0; border-left: 1px solid {LINE}; color: {TXT}; cursor: pointer; display: inline-flex; align-items: center; justify-content: center">{mic_svg}</button></sc-if>
<button type="submit" aria-label="{{{{t.send}}}}" style="flex: 0 0 64px; min-height: 60px; background: {ACC}; border: 0; color: {BG}; cursor: pointer; display: inline-flex; align-items: center; justify-content: center"><svg aria-hidden="true" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="square"><path d="M4 12l16-8-6 16-3-7z"></path></svg></button>
</form>
</section>
</div>
</main>'''
    hdr=header("none",False); ftr=footer(False)
    actx={"t":t,"langs":langs_ctx(L,"asistente"),"speaking":False,"notSpeaking":True,"mouthHalf":False,"mouthOpen":False,"showTap":True,"listening":False,"notListening":True,"voiceLabel":t["voiceOn"]}
    body=fix_links(render(ROOT_OPEN+hdr+as_main+ftr+"</div>",actx),L)
    chatkeys={k:v for k,v in t.items() if k.startswith("r_") or k.startswith("adm_") or k in ("micNo","voiceOn","voiceOff","chip1","chip2","chip3","passPh","ph")}
    open(f"{SITE}/{L}/asistente.html","w").write(doc(L,"asistente",f"{t['asTitle']} — VERTEZ GROUP",t["asSub"],body,{"page":"assistant","lang":L,"chat":chatkeys},fab=False)); pages+=1
    # ---- admin page
    e=EXTRA[L]
    fld="display: flex; flex-direction: column; gap: 6px"
    lab="font-size: 13px; font-weight: 600; letter-spacing: 0.12em; text-transform: uppercase; color: #A8A8AD"
    inp="min-height: 50px; padding: 0 14px; background: #0B0B0C; border: 1px solid #3A3A3E; border-radius: 3px; color: #F2F2F2; font-size: 16px; box-sizing: border-box; width: 100%"
    ta="min-height: 110px; padding: 12px 14px; background: #0B0B0C; border: 1px solid #3A3A3E; border-radius: 3px; color: #F2F2F2; font-size: 16px; box-sizing: border-box; width: 100%; resize: vertical"
    btn=f"min-height: 52px; padding: 0 26px; background: {ACC}; border: 0; border-radius: 3px; color: #0B0B0C; font-family: 'Oswald', sans-serif; font-weight: 600; font-size: 17px; letter-spacing: 0.06em; text-transform: uppercase; cursor: pointer"
    def F(name,label,kind="text",extra=""):
        idn=f"a-{name}"
        if kind=="textarea": ctl=f'<textarea id="{idn}" name="{name}" style="{ta}"></textarea>'
        elif kind=="file": ctl=f'<input id="{idn}" name="{name}" type="file" {extra} style="{inp}; padding: 12px 14px">'
        else: ctl=f'<input id="{idn}" name="{name}" type="{kind}" {extra} style="{inp}">'
        return f'<div style="{fld}"><label for="{idn}" style="{lab}">{html.escape(label)}</label>{ctl}</div>'
    def form(kind,fields):
        return f'''<form data-admin-form="{kind}" style="display: grid; grid-template-columns: repeat(auto-fill, minmax(240px, 1fr)); gap: 14px; background: #18181A; border: 1px solid #2C2C2F; border-radius: 4px; padding: 20px">{fields}
<div style="grid-column: 1 / -1; display: flex; flex-wrap: wrap; align-items: center; gap: 12px"><button type="submit" style="{btn}">{html.escape(e["publish"] if kind!="cover" else e["upload"])}</button><span data-admin-status role="status" style="font-size: 15px; color: #A8A8AD"></span></div></form>
<h3 style="margin: 8px 0 0; font-family: 'Oswald', sans-serif; font-weight: 500; font-size: 20px; letter-spacing: 0.06em; text-transform: uppercase; color: #FFFFFF">{html.escape(e["list"])}</h3>
<div data-admin-list="{kind}" style="display: flex; flex-direction: column; gap: 10px"></div>'''
    tabs=[("news",e["tNews"],form("news",F("title",e["fTitle"],"text","required")+F("date",e["fDate"],"date")+F("image",e["fImage"],"file",'accept="image/*"')+'<div style="grid-column: 1 / -1">'+F("body",e["fText"],"textarea")+"</div>")),
          ("events",e["tEvents"],form("events",F("title",e["fTitle"],"text","required")+F("date",e["fDate"],"date","required")+F("place",e["fPlace"])+F("image",e["fImage"],"file",'accept="image/*"')+'<div style="grid-column: 1 / -1">'+F("body",e["fText"],"textarea")+"</div>")),
          ("videos",e["tVideos"],form("videos",F("title",e["fTitle"],"text","required")+F("url",e["fUrl"],"url")+F("file",e["fFile"],"file",'accept="video/*"')+'<div style="grid-column: 1 / -1">'+F("body",e["fText"],"textarea")+"</div>")),
          ("photos",e["tPhotos"],form("photos",F("files",e["fPhotos"],"file",'accept="image/*" multiple required')+F("caption",e["fCaption"]))),
          ("cover",e["tCover"],form("cover",F("file",e["fCover"],"file",'accept="image/*" required'))+f'<button type="button" data-admin-reset style="min-height: 48px; padding: 0 18px; align-self: flex-start; background: transparent; border: 1px solid #3A3A3E; border-radius: 3px; color: #F2F2F2; font-size: 15px; cursor: pointer">{html.escape(e["reset"])}</button>')]
    tabbar="".join(f'<button type="button" role="tab" data-admin-tab="{k}" aria-selected="{"true" if i==0 else "false"}" style="min-height: 48px; padding: 0 18px; background: transparent; border: 1px solid #3A3A3E; border-radius: 3px; color: #F2F2F2; font-family: \'Oswald\', sans-serif; font-weight: 500; font-size: 16px; letter-spacing: 0.06em; text-transform: uppercase; cursor: pointer">{html.escape(lbl)}</button>' for i,(k,lbl,_) in enumerate(tabs))
    panels="".join(f'<div role="tabpanel" data-admin-panel="{k}" {"" if i==0 else "hidden"} style="display: flex; flex-direction: column; gap: 14px">{p}</div>' for i,(k,_,p) in enumerate(tabs))
    admin_main=f'''<main id="top" data-admin style="max-width: 1100px; margin: 0 auto; padding: 32px 24px 64px; min-height: 70vh; display: flex; flex-direction: column; gap: 22px">
<div style="display: flex; flex-wrap: wrap; align-items: center; gap: 16px">{mark(56)}<div style="display: flex; flex-direction: column; gap: 4px"><h1 style="margin: 0; font-family: 'Oswald', sans-serif; font-weight: 600; font-size: clamp(30px, 4vw, 44px); letter-spacing: 0.03em; text-transform: uppercase; color: #FFFFFF">{html.escape(e["aTitle"])}</h1><p style="margin: 0; font-size: 16px; color: #A8A8AD">{html.escape(e["aSub"])}</p></div></div>
<p data-admin-nodb hidden style="margin: 0; padding: 14px 16px; border: 1px solid {ACC}; border-radius: 4px; color: {ACC}; font-size: 16px">{html.escape(e["nodb"])}</p>
<form data-admin-login hidden style="max-width: 440px; display: flex; flex-direction: column; gap: 14px; background: #18181A; border: 1px solid #2C2C2F; border-top: 3px solid {ACC}; border-radius: 4px; padding: 24px">
<h2 style="margin: 0; font-family: 'Oswald', sans-serif; font-weight: 500; font-size: 24px; letter-spacing: 0.05em; text-transform: uppercase; color: #FFFFFF">{html.escape(e["aLogin"])}</h2>
{F("password",e["aPass"],"password",'autocomplete="current-password" required')}
<button type="submit" style="{btn}">{html.escape(e["aEnter"])}</button><span data-admin-status role="status" style="font-size: 15px; color: {ACC}"></span></form>
<div data-admin-app hidden style="display: flex; flex-direction: column; gap: 18px">
<div style="display: flex; flex-wrap: wrap; align-items: center; justify-content: space-between; gap: 12px"><div role="tablist" style="display: flex; flex-wrap: wrap; gap: 8px">{tabbar}</div>
<div style="display: flex; gap: 10px"><a href="/{L}" style="min-height: 48px; padding: 0 16px; display: inline-flex; align-items: center; border: 1px solid #3A3A3E; border-radius: 3px; font-size: 15px">{html.escape(e["viewSite"])}</a><button type="button" data-admin-logout style="min-height: 48px; padding: 0 16px; background: transparent; border: 1px solid #3A3A3E; border-radius: 3px; color: #F2F2F2; font-size: 15px; cursor: pointer">{html.escape(e["aLogout"])}</button></div></div>
<p style="margin: 0; font-size: 14px; color: #A8A8AD">{html.escape(e["langNote"])}</p>
{panels}
</div>
</main>'''
    actx2={"t":t,"langs":langs_ctx(L,"admin")}
    body=fix_links(render(ROOT_OPEN+header("none",False)+admin_main+footer(False)+"</div>",actx2),L)
    adm={k:e[k] for k in ("confirmDel","empty","saving","saved","err","nodb","badpass","del_","watch","need")}
    open(f"{SITE}/{L}/admin.html","w").write(doc(L,"admin",f"{e['aTitle']} — VERTEZ GROUP",e["aSub"],body.replace("<head>","<head>"),{"page":"admin","lang":L,"adm":adm},fab=False).replace('<meta name="theme-color"','<meta name="robots" content="noindex, nofollow">\n<meta name="theme-color"')); pages+=1
# home body needs root wrapper: render home used extract_body which already includes ROOT_OPEN div
for n in ("hero-left","hero-right","flank-left","flank-right"): shutil.copy(f"{HERE}/img/{n}.webp",f"{SITE}/assets/{n}.webp")
from PIL import Image as _I; _I.open(f"{HERE}/img/cadet.png").save(f"{SITE}/assets/cadet.webp","WEBP",quality=86,method=6)
open(f"{SITE}/assets/config.js","w").write(CONFIG_JS)
open(f"{SITE}/assets/favicon.svg","w").write(FAVICON)
open(f"{SITE}/index.html","w").write('''<!doctype html>
<html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>VERTEZ GROUP</title>
<link rel="icon" href="/assets/favicon.svg" type="image/svg+xml"><meta name="theme-color" content="#0B0B0C">
<script>(function(){var l="es";try{var v=JSON.parse(localStorage.getItem("vertez_v1")||"{}");if(v&&["es","fr","en"].indexOf(v.lang)>-1)l=v.lang;}catch(e){}location.replace("/"+l);})();</script>
<noscript><meta http-equiv="refresh" content="0; url=/es"></noscript>
<style>body{margin:0;background:#0B0B0C}</style></head><body><a href="/es" style="color:#FF6B1A;font-family:sans-serif;display:block;padding:24px">VERTEZ GROUP →</a></body></html>''')
open(f"{SITE}/vercel.json","w").write(json.dumps({"cleanUrls":True,"trailingSlash":False},indent=2))
open(f"{SITE}/robots.txt","w").write("User-agent: *\nAllow: /\n")
print("pages",pages)
os.makedirs(f"{SITE}/supabase",exist_ok=True)
open(f"{SITE}/supabase/schema.sql","w").write(open(f"{HERE}/schema.sql").read())
open(f"{SITE}/README.md","w").write("""# VERTEZ GROUP

Sitio estático multilingüe (ES / FR / EN).

- `/` redirige al idioma guardado (por defecto español).
- `/es`, `/fr`, `/en`: inicio, 8 divisiones, `/asistente` (asistente con voz) y `/admin` (panel de mando).
- Contenidos dinámicos (noticias, eventos, vídeos, fotos, portada) en Supabase: ver `supabase/schema.sql`
  y rellenar `assets/config.js` con la URL y la clave pública del proyecto.
- Despliegue: Vercel, sin build (Framework Preset: Other).
""")
shutil.copy(f"{HERE}/site.js",f"{SITE}/assets/site.js")
