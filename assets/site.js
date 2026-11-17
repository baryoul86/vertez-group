(function () {
  "use strict";
  var VZ = window.VZ || {};
  var L = document.documentElement.lang || "es";
  var KEY = "vertez_v1";
  var CODES = { es: "es-ES", fr: "fr-FR", en: "en-GB" };

  function readStore() { try { return JSON.parse(localStorage.getItem(KEY) || "{}") || {}; } catch (e) { return {}; } }
  function writeStore(p) { try { var v = readStore(); for (var k in p) v[k] = p[k]; localStorage.setItem(KEY, JSON.stringify(v)); } catch (e) {} }

  // ---- language memory
  writeStore({ lang: L });
  document.querySelectorAll("[data-lang]").forEach(function (a) {
    a.addEventListener("click", function () { writeStore({ lang: a.getAttribute("data-lang") }); try { speechSynthesis.cancel(); } catch (e) {} });
  });


  // ---- Supabase (REST, sin dependencias)
  var CFG = window.VZ_CONFIG || {};
  var AUTH_KEY = "vertez_auth";
  var DB = {
    ok: function () { return !!(CFG.supabaseUrl && CFG.supabaseKey); },
    session: function () { try { return JSON.parse(localStorage.getItem(AUTH_KEY) || "null"); } catch (e) { return null; } },
    save: function (s) { try { if (s) localStorage.setItem(AUTH_KEY, JSON.stringify(s)); else localStorage.removeItem(AUTH_KEY); } catch (e) {} },
    headers: function (token, extra) {
      var h = { apikey: CFG.supabaseKey, Authorization: "Bearer " + (token || CFG.supabaseKey) };
      for (var k in (extra || {})) h[k] = extra[k];
      return h;
    },
    authReq: function (grant, body) {
      return fetch(CFG.supabaseUrl + "/auth/v1/token?grant_type=" + grant, { method: "POST", headers: DB.headers(null, { "Content-Type": "application/json" }), body: JSON.stringify(body) })
        .then(function (r) { return r.json().then(function (j) { if (!r.ok || !j.access_token) throw new Error(j.error_description || j.msg || "auth"); return j; }); })
        .then(function (j) { var s = { access_token: j.access_token, refresh_token: j.refresh_token, expires_at: Date.now() + (j.expires_in || 3600) * 1000 }; DB.save(s); return s; });
    },
    login: function (password) { return DB.authReq("password", { email: CFG.adminEmail, password: password }); },
    logout: function () { var s = DB.session(); DB.save(null); if (s && DB.ok()) fetch(CFG.supabaseUrl + "/auth/v1/logout", { method: "POST", headers: DB.headers(s.access_token) }).catch(function () {}); },
    token: function () {
      var s = DB.session(); if (!s) return Promise.reject(new Error("no session"));
      if (Date.now() < s.expires_at - 60000) return Promise.resolve(s.access_token);
      return DB.authReq("refresh_token", { refresh_token: s.refresh_token }).then(function (n) { return n.access_token; }, function (e) { DB.save(null); throw e; });
    },
    select: function (table, query) {
      return fetch(CFG.supabaseUrl + "/rest/v1/" + table + "?" + query, { headers: DB.headers() }).then(function (r) { if (!r.ok) throw new Error(r.status); return r.json(); });
    },
    write: function (method, table, query, body) {
      return DB.token().then(function (tk) {
        return fetch(CFG.supabaseUrl + "/rest/v1/" + table + (query ? "?" + query : ""), { method: method, headers: DB.headers(tk, { "Content-Type": "application/json", Prefer: "return=representation,resolution=merge-duplicates" }), body: body ? JSON.stringify(body) : undefined })
          .then(function (r) { if (!r.ok) return r.text().then(function (t) { throw new Error(t || r.status); }); return r.status === 204 ? null : r.json(); });
      });
    },
    upload: function (file) {
      var ext = (file.name.split(".").pop() || "bin").toLowerCase().replace(/[^a-z0-9]/g, "");
      var path = new Date().toISOString().slice(0, 10) + "/" + Math.random().toString(36).slice(2) + Date.now().toString(36) + "." + ext;
      return DB.token().then(function (tk) {
        return fetch(CFG.supabaseUrl + "/storage/v1/object/" + CFG.bucket + "/" + path, { method: "POST", headers: DB.headers(tk, { "Content-Type": file.type || "application/octet-stream", "x-upsert": "false" }), body: file })
          .then(function (r) { if (!r.ok) return r.text().then(function (t) { throw new Error(t || r.status); }); return CFG.supabaseUrl + "/storage/v1/object/public/" + CFG.bucket + "/" + path; });
      });
    },
    isAdmin: function () { return DB.token().then(function (tk) { return fetch(CFG.supabaseUrl + "/rest/v1/rpc/is_admin", { method: "POST", headers: DB.headers(tk, { "Content-Type": "application/json" }), body: "{}" }).then(function (r) { return r.ok ? r.json() : false; }); }); }
  };
  window.VZDB = DB;

  function el(tag, attrs, kids) {
    var n = document.createElement(tag);
    for (var k in (attrs || {})) { if (k === "style") n.style.cssText = attrs[k]; else if (k === "text") n.textContent = attrs[k]; else n.setAttribute(k, attrs[k]); }
    (kids || []).forEach(function (c) { if (c) n.appendChild(c); });
    return n;
  }
  function safeUrl(u) { try { var x = new URL(u, location.href); return (x.protocol === "https:" || x.protocol === "http:") ? x.href : ""; } catch (e) { return ""; } }
  function ytId(u) { var m = String(u || "").match(/(?:youtube\.com\/(?:watch\?v=|embed\/|shorts\/)|youtu\.be\/)([\w-]{11})/); return m ? m[1] : ""; }
  function fmtDate(d) { try { return new Date(d + (String(d).length === 10 ? "T12:00:00" : "")).toLocaleDateString(L, { day: "numeric", month: "long", year: "numeric" }); } catch (e) { return d || ""; } }
  var CARD = "background:#18181A;border:1px solid #2C2C2F;border-radius:4px;overflow:hidden;display:flex;flex-direction:column";
  function cardFor(kind, it) {
    var body = el("div", { style: "padding:14px 16px;display:flex;flex-direction:column;gap:6px" });
    var media = null, img = safeUrl(it.image_url || "");
    if (kind === "photos") {
      var pu = safeUrl(it.url); if (!pu) return null;
      return el("a", { href: pu, target: "_blank", rel: "noopener", style: CARD + ";text-decoration:none;color:#F2F2F2" }, [
        el("img", { src: pu, alt: it.caption || "", loading: "lazy", style: "display:block;width:100%;aspect-ratio:4/3;object-fit:cover" }),
        it.caption ? el("span", { text: it.caption, style: "padding:10px 12px;font-size:14px;color:#D2D2D6" }) : null ]);
    }
    if (kind === "videos") {
      var vu = safeUrl(it.url); if (!vu) return null;
      var id = ytId(vu);
      if (id) media = el("iframe", { src: "https://www.youtube-nocookie.com/embed/" + id, title: it.title || "", loading: "lazy", allow: "accelerometer; encrypted-media; gyroscope; picture-in-picture; fullscreen", allowfullscreen: "", style: "display:block;width:100%;aspect-ratio:16/9;border:0" });
      else if (/\.(mp4|webm|mov)(\?|$)/i.test(vu)) media = el("video", { src: vu, controls: "", preload: "metadata", playsinline: "", style: "display:block;width:100%;aspect-ratio:16/9;background:#000" });
      body.appendChild(el("span", { text: it.title || "", style: "font-size:16px;font-weight:600;color:#F2F2F2" }));
      if (it.body) body.appendChild(el("span", { text: it.body, style: "font-size:14px;line-height:1.45;color:#A8A8AD" }));
      if (!media) body.appendChild(el("a", { href: vu, target: "_blank", rel: "noopener", text: ((VZ.adm && VZ.adm.watch) || "▶") + " →", style: "font-size:13px;font-weight:600;letter-spacing:.12em;text-transform:uppercase;color:#FF6B1A" }));
      return el("div", { style: CARD }, [media, body]);
    }
    if (img) media = el("img", { src: img, alt: "", loading: "lazy", style: "display:block;width:100%;aspect-ratio:16/9;object-fit:cover" });
    body.appendChild(el("span", { text: fmtDate(it.date) + (it.place ? " · " + it.place : ""), style: "font-size:12px;letter-spacing:.16em;text-transform:uppercase;color:#FF6B1A" }));
    body.appendChild(el("span", { text: it.title || "", style: "font-size:17px;font-weight:600;color:#F2F2F2" }));
    if (it.body) body.appendChild(el("span", { text: it.body.length > 260 ? it.body.slice(0, 257) + "…" : it.body, style: "font-size:14px;line-height:1.5;color:#A8A8AD;white-space:pre-line" }));
    return el("div", { style: CARD }, [media, body]);
  }
  var QUERY = {
    news: "select=*&order=date.desc,created_at.desc",
    events: "select=*&order=date.asc&date=gte." + new Date().toISOString().slice(0, 10),
    videos: "select=*&order=created_at.desc",
    photos: "select=*&order=created_at.desc"
  };
  function loadFeeds() {
    if (!DB.ok()) return;
    document.querySelectorAll("[data-feed]").forEach(function (box) {
      var kind = box.getAttribute("data-feed"), lim = box.getAttribute("data-limit") || "3";
      DB.select(kind, QUERY[kind] + "&limit=" + lim).then(function (rows) {
        if (!rows || !rows.length) return;
        box.textContent = "";
        rows.forEach(function (r) { var c = cardFor(kind, r); if (c) box.appendChild(c); });
      }).catch(function () {});
    });
    var heroImg = document.querySelector("[data-hero-custom]");
    if (heroImg) DB.select("settings", "select=value&key=eq.hero_image").then(function (rows) {
      var u = rows && rows[0] && safeUrl(rows[0].value);
      if (u) { heroImg.src = u; heroImg.hidden = false; var d = document.querySelector("[data-hero-default]"); if (d) d.hidden = true; }
    }).catch(function () {});
  }
  loadFeeds();

  // ---- tiny state → DOM binding (x-if / x-v)
  var state = {};
  var acts = {};
  var submits = {};
  var compute = function () { return {}; };
  function update() {
    var v = compute(state);
    document.querySelectorAll("x-if[data-if]").forEach(function (el) { var k = el.getAttribute("data-if"); if (k in v) el.hidden = !v[k]; });
    document.querySelectorAll("x-v[data-v]").forEach(function (el) { var k = el.getAttribute("data-v"); if (k in v) el.textContent = v[k]; });
  }
  function set(p) { for (var k in p) state[k] = p[k]; update(); }
  document.addEventListener("click", function (e) {
    var b = e.target.closest ? e.target.closest("[data-act]") : null;
    if (b && acts[b.getAttribute("data-act")]) acts[b.getAttribute("data-act")](e, b);
  });
  document.addEventListener("submit", function (e) {
    var f = e.target.closest ? e.target.closest("[data-submit]") : null;
    if (f && submits[f.getAttribute("data-submit")]) { e.preventDefault(); submits[f.getAttribute("data-submit")](e, f); }
  });

  // ---- registration (step 3 not active yet)
  submits.register = function () { set({ regSent: true }); };
  var baseCompute = function (s) { return { regSent: !!s.regSent }; };
  compute = baseCompute;

  // ---- VERTEZ WORLD
  if (VZ.page === "world" && VZ.regions) {
    state = { region: 2, lb: true, lc: true, li: false };
    VZ.regions.forEach(function (_, i) { acts["pick" + i] = function () { set({ region: i }); }; });
    ["lb", "lc", "li"].forEach(function (k) { acts[k + "Toggle"] = function () { var p = {}; p[k] = !state[k]; set(p); }; });
    compute = function (s) {
      var v = { regionName: VZ.regions[s.region] };
      VZ.regions.forEach(function (_, i) { v["r" + i + "on"] = s.region === i; v["r" + i + "off"] = s.region !== i; });
      ["lb", "lc", "li"].forEach(function (k) { v[k + "On"] = !!s[k]; v[k + "Off"] = !s[k]; });
      return v;
    };
  }

  // ---- VERTEZ AI assistant (full page)
  if (VZ.page === "assistant" && VZ.chat) {
    var T = VZ.chat;
    var LINKS = { adm_ok: "admin", r_community: "community", r_store: "store", r_world: "world", r_media: "media", r_academy: "academy", r_sniper: "academy", r_tech: "technology", r_ai: "ai", r_conf: "conferences" };
    var RULES = [
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
    var MALE = /jorge|diego|pablo|juan|carlos|enrique|alvaro|raul|miguel|thomas|henri|paul|nicolas|mathieu|daniel|arthur|george|oliver|male|hombre|homme/i;
    function norm(s) { return String(s || "").toLowerCase().normalize("NFD").replace(/[̀-ͯ]/g, ""); }

    var saved = readStore();
    var msgs = Array.isArray(saved.chat) ? saved.chat.filter(function (m) { return m && (m.from === "user" ? typeof m.text === "string" : T[m.key]); }).slice(-30) : [];
    state = { voice: saved.voice !== false, greeted: false, speaking: false, mouth: 0, listening: false, messages: msgs.length ? msgs : [{ from: "bot", key: "r_hello" }] };

    var thread = document.querySelector('[data-ref="threadRef"]');
    var tplBot = thread ? thread.querySelector('template[data-tpl="bot"]') : null;
    var tplUser = thread ? thread.querySelector('template[data-tpl="user"]') : null;
    var input = document.getElementById("vzmsg");
    var voiceBtn = document.querySelector('[data-act="toggleVoice"]');

    function renderThread() {
      if (!thread || !tplBot || !tplUser) return;
      thread.querySelectorAll("[data-msg]").forEach(function (n) { n.remove(); });
      state.messages.forEach(function (m) {
        var frag = (m.from === "bot" ? tplBot : tplUser).content.cloneNode(true);
        var slot = frag.querySelector('[data-slot="text"]');
        if (slot) slot.textContent = m.from === "bot" ? (T[m.key] || "") : m.text;
        var link = frag.querySelector('[data-slot="href"]');
        if (link) { if (m.from === "bot" && LINKS[m.key]) { link.setAttribute("href", "/" + L + "/" + LINKS[m.key]); if (m.key === "adm_ok" && T.adm_open) link.textContent = T.adm_open; } else link.remove(); }
        var wrap = document.createElement("div");
        wrap.setAttribute("data-msg", "");
        wrap.style.display = "contents";
        wrap.appendChild(frag);
        thread.appendChild(wrap);
      });
      thread.scrollTop = thread.scrollHeight;
      writeStore({ chat: state.messages.filter(function (m) { return !m.tmp && String(m.key || "").indexOf("adm_") !== 0; }).slice(-30), voice: state.voice });
    }

    compute = function (s) {
      return {
        speaking: s.speaking, notSpeaking: !s.speaking,
        mouthHalf: s.mouth === 1, mouthOpen: s.mouth === 2,
        showTap: !s.greeted,
        listening: s.listening, notListening: !s.listening,
        voiceLabel: s.voice ? T.voiceOn : T.voiceOff
      };
    };

    var mouthTimer = null, safety = null;
    function stopMouth() { clearInterval(mouthTimer); clearTimeout(safety); mouthTimer = null; set({ speaking: false, mouth: 0 }); }
    function startMouth(ms) {
      clearInterval(mouthTimer); clearTimeout(safety);
      var seq = [2, 1, 2, 0, 1, 2, 1, 0, 2, 1], i = 0;
      set({ speaking: true });
      mouthTimer = setInterval(function () { i = (i + 1) % seq.length; set({ mouth: seq[(i + Math.floor(Math.random() * 3)) % seq.length] }); }, 105);
      safety = setTimeout(stopMouth, ms);
    }
    function pickVoice(code) {
      try {
        var all = speechSynthesis.getVoices() || [], base = code.slice(0, 2);
        var same = all.filter(function (v) { return (v.lang || "").toLowerCase().replace("_", "-").indexOf(base) === 0; });
        if (!same.length) return null;
        var exact = same.filter(function (v) { return (v.lang || "").replace("_", "-") === code; });
        var pool = exact.length ? exact : same;
        return pool.find(function (v) { return MALE.test(v.name); }) || pool.find(function (v) { return /google|natural|neural|premium|enhanced/i.test(v.name); }) || pool[0];
      } catch (e) { return null; }
    }
    try { if (window.speechSynthesis) { speechSynthesis.getVoices(); speechSynthesis.onvoiceschanged = function () { speechSynthesis.getVoices(); }; } } catch (e) {}

    function speak(key) {
      var text = T[key];
      if (!state.voice || !text) return;
      var est = Math.min(30000, 1500 + text.length * 75), short = Math.min(9000, text.length * 55);
      if (!window.speechSynthesis || typeof SpeechSynthesisUtterance === "undefined") { startMouth(short); return; }
      try {
        speechSynthesis.cancel();
        var code = CODES[L] || "es-ES";
        var u = new SpeechSynthesisUtterance(text);
        u.lang = code;
        var v = pickVoice(code); if (v) u.voice = v;
        u.rate = 1; u.pitch = 0.95;
        var started = false;
        u.onstart = function () { started = true; startMouth(est); };
        u.onboundary = function () { set({ mouth: 2 }); };
        u.onend = stopMouth; u.onerror = stopMouth;
        speechSynthesis.speak(u);
        setTimeout(function () { if (!started && !speechSynthesis.speaking) startMouth(short); }, 900);
      } catch (e) { startMouth(short); }
    }
    function reply(key) { state.messages = state.messages.concat([{ from: "bot", key: key }]); state.greeted = true; renderThread(); update(); speak(key); }
    var timer = null;
    var PASS_HASH = "9dc7eb57681796e15c16227ec5a8c47d4d96cbe71bbb779a7b2b7231c5dea9b7";
    var awaitPass = false;
    function sha(txt) {
      try { return crypto.subtle.digest("SHA-256", new TextEncoder().encode(txt)).then(function (b) { return Array.prototype.map.call(new Uint8Array(b), function (x) { return ("0" + x.toString(16)).slice(-2); }).join(""); }); }
      catch (e) { return Promise.resolve(""); }
    }
    function passMode(on) {
      awaitPass = on;
      if (input) { input.type = on ? "password" : "text"; input.placeholder = on ? (T.passPh || "") : (T.ph || input.placeholder); input.setAttribute("autocomplete", on ? "current-password" : "off"); if (on) input.focus(); }
    }
    function tryPassword(pw) {
      state.messages = state.messages.concat([{ from: "user", text: "••••••••", tmp: true }]);
      if (input) input.value = "";
      passMode(false); renderThread();
      if (!DB.ok()) { reply("adm_nodb"); return; }
      DB.login(pw).then(function () { return DB.isAdmin(); }).then(function (ok) {
        if (!ok) { DB.save(null); throw new Error("x"); }
        reply("adm_ok");
      }).catch(function () { reply("adm_bad"); });
    }
    function ask(text) {
      var clean = String(text || "").trim(); if (!clean) return;
      if (awaitPass) { tryPassword(clean); return; }
      var raw = clean;
      sha(norm(raw).replace(/[^a-z0-9]/g, "")).then(function (h) {
        if (h === PASS_HASH) {
          if (input) input.value = "";
          state.messages = state.messages.concat([{ from: "user", text: "✦ ✦ ✦", tmp: true }]); renderThread();
          clearTimeout(timer); timer = setTimeout(function () { reply("adm_ask"); passMode(true); }, 350);
          return;
        }
        askNormal(raw);
      });
    }
    function askNormal(clean) {
      var low = norm(clean), key = "r_default";
      for (var i = 0; i < RULES.length; i++) { if (RULES[i][1].test(low)) { key = RULES[i][0]; break; } }
      state.messages = state.messages.concat([{ from: "user", text: clean }]);
      if (input) input.value = "";
      renderThread();
      clearTimeout(timer); timer = setTimeout(function () { reply(key); }, 450);
    }
    acts.talk = function () {
      var bots = state.messages.filter(function (m) { return m.from === "bot"; });
      set({ greeted: true });
      speak(bots.length ? bots[bots.length - 1].key : "r_hello");
    };
    acts.ask1 = function () { ask(T.chip1); };
    acts.ask2 = function () { ask(T.chip2); };
    acts.ask3 = function () { ask(T.chip3); };
    acts.toggleVoice = function () {
      try { speechSynthesis.cancel(); } catch (e) {}
      stopMouth();
      set({ voice: !state.voice });
      if (voiceBtn) voiceBtn.setAttribute("aria-pressed", state.voice ? "true" : "false");
      writeStore({ voice: state.voice });
    };
    var rec = null;
    acts.mic = function () {
      if (state.listening) { try { rec.stop(); } catch (e) {} set({ listening: false }); return; }
      var SR = window.SpeechRecognition || window.webkitSpeechRecognition;
      if (!SR) { reply("micNo"); return; }
      try {
        try { speechSynthesis.cancel(); } catch (e) {}
        stopMouth();
        rec = new SR(); rec.lang = CODES[L] || "es-ES"; rec.interimResults = false; rec.maxAlternatives = 1;
        rec.onresult = function (ev) { var r = ev.results && ev.results[0] && ev.results[0][0]; ask(r ? r.transcript : ""); };
        rec.onerror = function () { set({ listening: false }); reply("micNo"); };
        rec.onend = function () { set({ listening: false }); };
        rec.start(); set({ listening: true });
      } catch (e) { set({ listening: false }); reply("micNo"); }
    };
    submits.submit = function () { ask(input ? input.value : ""); };
    if (voiceBtn) voiceBtn.setAttribute("aria-pressed", state.voice ? "true" : "false");
    window.addEventListener("pagehide", function () { try { speechSynthesis.cancel(); } catch (e) {} });
    renderThread();
  }


  // ---- panel de mando
  if (VZ.page === "admin") {
    var A = VZ.adm || {};
    var q = function (sel) { return document.querySelector(sel); };
    var loginF = q("[data-admin-login]"), app = q("[data-admin-app]"), nodb = q("[data-admin-nodb]");
    function showApp(on) { if (app) app.hidden = !on; if (loginF) loginF.hidden = on || !DB.ok(); }
    if (!DB.ok()) { if (nodb) nodb.hidden = false; showApp(false); }
    else if (DB.session()) { DB.isAdmin().then(function (ok) { if (ok) { showApp(true); refreshAll(); } else { DB.save(null); showApp(false); } }, function () { DB.save(null); showApp(false); }); }
    else showApp(false);
    if (loginF) loginF.addEventListener("submit", function (e) {
      e.preventDefault();
      var st = loginF.querySelector("[data-admin-status]"), pw = loginF.querySelector("input[type=password]");
      st.textContent = A.saving || "…";
      DB.login(pw.value).then(function () { return DB.isAdmin(); }).then(function (ok) {
        pw.value = ""; if (!ok) { DB.save(null); throw new Error("x"); } st.textContent = ""; showApp(true); refreshAll();
      }).catch(function () { pw.value = ""; st.textContent = A.badpass || "✗"; });
    });
    document.querySelectorAll("[data-admin-tab]").forEach(function (b) {
      b.addEventListener("click", function () {
        var k = b.getAttribute("data-admin-tab");
        document.querySelectorAll("[data-admin-tab]").forEach(function (x) { var on = x === b; x.setAttribute("aria-selected", on ? "true" : "false"); x.style.background = on ? "#FF6B1A" : "transparent"; x.style.color = on ? "#0B0B0C" : "#F2F2F2"; x.style.borderColor = on ? "#FF6B1A" : "#3A3A3E"; });
        document.querySelectorAll("[data-admin-panel]").forEach(function (p) { p.hidden = p.getAttribute("data-admin-panel") !== k; });
      });
    });
    var first = q("[data-admin-tab]"); if (first) first.click();
    var lo = q("[data-admin-logout]"); if (lo) lo.addEventListener("click", function () { DB.logout(); showApp(false); });
    function refresh(kind) {
      var box = q('[data-admin-list="' + kind + '"]'); if (!box) return;
      var query = kind === "cover" ? "select=*&key=eq.hero_image" : (kind === "events" ? "select=*&order=date.desc" : QUERY[kind]) + "&limit=200";
      DB.select(kind === "cover" ? "settings" : kind, query).then(function (rows) {
        box.textContent = "";
        if (!rows.length) { box.appendChild(el("p", { text: A.empty || "—", style: "margin:0;color:#A8A8AD" })); return; }
        rows.forEach(function (r) {
          var label = kind === "photos" ? (r.caption || r.url.split("/").pop()) : kind === "cover" ? (A.saved || "") : ((r.date ? fmtDate(r.date) + " · " : "") + (r.title || ""));
          var thumbU = safeUrl(kind === "photos" ? r.url : kind === "cover" ? r.value : (r.image_url || ""));
          var del = el("button", { type: "button", text: A.del_ || "✕", style: "min-height:44px;padding:0 14px;background:transparent;border:1px solid #6B2A10;border-radius:3px;color:#FF8A4D;cursor:pointer;flex:0 0 auto" });
          del.addEventListener("click", function () {
            if (!window.confirm(A.confirmDel || "?")) return;
            var p = kind === "cover" ? DB.write("DELETE", "settings", "key=eq.hero_image") : DB.write("DELETE", kind, "id=eq." + encodeURIComponent(r.id));
            p.then(function () { refresh(kind); }).catch(function (e) { alertStatus(kind, (A.err || "") + e.message); });
          });
          box.appendChild(el("div", { style: "display:flex;align-items:center;gap:12px;background:#18181A;border:1px solid #2C2C2F;border-radius:4px;padding:10px 12px" }, [
            thumbU ? el("img", { src: thumbU, alt: "", style: "width:64px;height:48px;object-fit:cover;border-radius:3px;flex:0 0 auto" }) : null,
            el("span", { text: label, style: "flex:1 1 auto;min-width:0;font-size:15px;color:#F2F2F2;overflow:hidden;text-overflow:ellipsis" }), del ]));
        });
      }).catch(function (e) { box.textContent = (A.err || "") + e.message; });
    }
    function refreshAll() { ["news", "events", "videos", "photos", "cover"].forEach(refresh); }
    function alertStatus(kind, msg) { var f = q('[data-admin-form="' + kind + '"]'); if (f) f.querySelector("[data-admin-status]").textContent = msg; }
    document.querySelectorAll("[data-admin-form]").forEach(function (f) {
      var kind = f.getAttribute("data-admin-form");
      f.addEventListener("submit", function (e) {
        e.preventDefault();
        var st = f.querySelector("[data-admin-status]"), btn = f.querySelector("[type=submit]");
        var val = function (n) { var x = f.elements[n]; return x ? String(x.value || "").trim() : ""; };
        var file = function (n) { var x = f.elements[n]; return x && x.files && x.files[0] ? x.files[0] : null; };
        st.textContent = A.saving || "…"; btn.disabled = true;
        var job;
        if (kind === "photos") {
          var files = Array.prototype.slice.call(f.elements.files.files || []);
          job = files.reduce(function (p, fl) { return p.then(function () { return DB.upload(fl).then(function (u) { return DB.write("POST", "photos", "", { url: u, caption: val("caption") || null }); }); }); }, Promise.resolve());
        } else if (kind === "cover") {
          job = DB.upload(file("file")).then(function (u) { return DB.write("POST", "settings", "on_conflict=key", { key: "hero_image", value: u }); });
        } else if (kind === "videos") {
          if (!val("title") || (!val("url") && !file("file"))) { st.textContent = A.need || "!"; btn.disabled = false; return; }
          job = (file("file") ? DB.upload(file("file")) : Promise.resolve(val("url"))).then(function (u) { return DB.write("POST", "videos", "", { title: val("title"), url: u, body: val("body") || null }); });
        } else {
          var row = { title: val("title"), body: val("body") || null };
          if (val("date")) row.date = val("date");
          if (kind === "events") row.place = val("place") || null;
          job = (file("image") ? DB.upload(file("image")) : Promise.resolve(null)).then(function (u) { if (u) row.image_url = u; return DB.write("POST", kind, "", row); });
        }
        job.then(function () { f.reset(); st.textContent = A.saved || "✓"; refresh(kind); })
          .catch(function (er) { st.textContent = (A.err || "") + er.message; })
          .then(function () { btn.disabled = false; });
      });
    });
    var rs = q("[data-admin-reset]");
    if (rs) rs.addEventListener("click", function () { if (!window.confirm(A.confirmDel || "?")) return; DB.write("DELETE", "settings", "key=eq.hero_image").then(function () { refresh("cover"); }).catch(function (e) { alertStatus("cover", (A.err || "") + e.message); }); });
  }

  var pageCompute = compute;
  compute = function (s) { var v = pageCompute(s); var b = baseCompute(s); for (var k in b) if (!(k in v)) v[k] = b[k]; return v; };
  update();
})();
