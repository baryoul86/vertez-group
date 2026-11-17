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
    var LINKS = { r_community: "community", r_store: "store", r_world: "world", r_media: "media", r_academy: "academy", r_sniper: "academy", r_tech: "technology", r_ai: "ai", r_conf: "conferences" };
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
        if (link) { if (m.from === "bot" && LINKS[m.key]) link.setAttribute("href", "/" + L + "/" + LINKS[m.key]); else link.remove(); }
        var wrap = document.createElement("div");
        wrap.setAttribute("data-msg", "");
        wrap.style.display = "contents";
        wrap.appendChild(frag);
        thread.appendChild(wrap);
      });
      thread.scrollTop = thread.scrollHeight;
      writeStore({ chat: state.messages.slice(-30), voice: state.voice });
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
    function ask(text) {
      var clean = String(text || "").trim(); if (!clean) return;
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

  var pageCompute = compute;
  compute = function (s) { var v = pageCompute(s); var b = baseCompute(s); for (var k in b) if (!(k in v)) v[k] = b[k]; return v; };
  update();
})();
