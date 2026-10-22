(function(){
  "use strict";

  // =========================================================================
  // 1. УПРАВЛЕНИЕ ВКЛАДКАМИ (ТАБАМИ)
  // =========================================================================
  const tabs = {
    btnDict: document.getElementById("tabBtnDict"),
    btnTrans: document.getElementById("tabBtnTrans"),
    viewDict: document.getElementById("dictView"),
    viewTrans: document.getElementById("transView"),
    dictNavWrap: document.getElementById("dictNavWrap"),
  };

  let currentTab = "dict";

  function switchTab(tabId){
    currentTab = tabId;
    const isDict = tabId === "dict";
    
    tabs.btnDict.classList.toggle("active", isDict);
    tabs.btnDict.setAttribute("aria-selected", isDict);
    tabs.btnTrans.classList.toggle("active", !isDict);
    tabs.btnTrans.setAttribute("aria-selected", !isDict);

    tabs.viewDict.classList.toggle("hidden", !isDict);
    tabs.viewTrans.classList.toggle("hidden", isDict);
    tabs.dictNavWrap.classList.toggle("hidden", !isDict);

    if (!isDict) {
      initTranslatorIfNeeded();
      const input = document.getElementById("transInput");
      if (input) input.focus();
    } else {
      const search = document.getElementById("searchInput");
      if (search && !search.value) search.focus();
    }
  }

  tabs.btnDict.addEventListener("click", () => switchTab("dict"));
  tabs.btnTrans.addEventListener("click", () => switchTab("trans"));


  // =========================================================================
  // 2. МОДУЛЬ СЛОВАРЯ (БЫСТРЫЙ ЧИСТЫЙ JS)
  // =========================================================================
  const LETTER_ORDER = "ABCČDEFGHIJKLMNOPRSŠTUVWZŽ".split("");
  const PAGE_SIZE = 150;

  const MACRON = {
    'ā':'a','ī':'i','ū':'u','ē':'e','ō':'o','à':'a','á':'a','è':'e',
    'ì':'i','í':'i','ó':'o','ù':'u','ú':'u','ỹ':'y','ỳ':'y',
    'š':'s','č':'c','ž':'z',
    'ķ':'k','ģ':'g','ļ':'l','ĺ':'l','ľ':'l','ņ':'n','ń':'n',
    'ŗ':'r','ŕ':'r','ţ':'t','ț':'t','ḑ':'d','ź':'z','ḿ':'m'
  };

  const normCache = new Map();
  function stripAccents(s){
    const cached = normCache.get(s);
    if (cached !== undefined) return cached;
    let out = "";
    for (const ch of s.toLowerCase()){
      if (ch >= "\u0300" && ch <= "\u036f") continue; // combining marks
      out += MACRON[ch] || ch;
    }
    normCache.set(s, out);
    return out;
  }

  function deriveLetter(w){
    if (!w) return "A";
    const first = w[0].toLowerCase();
    if (first === "č" || first === "š" || first === "ž") return first.toUpperCase();
    return (MACRON[first] || first).toUpperCase();
  }

  const LANG_LABELS = {ru:"рус.", lt:"lit.", lv:"latv.", de:"deu.", en:"eng.", pl:"pol."};
  const CASE_ORDER = ["nom","gen","dat","akk","ins","loct","voc"];
  const CASE_LABEL = {nom:"Nom", gen:"Gen", dat:"Dat", akk:"Acc", ins:"Ins", loct:"Loc", voc:"Voc"};
  const NUMBER_LABEL = {sg:"ед. ч.", pl:"мн. ч."};
  const GENDER_LABEL = {masc:"муж. род", fem:"жен. род", neut:"ср. род"};
  const DEGREE_KEYS = ["positive","comparative","superlative"];
  const DEGREE_LABEL = {positive:"Положительная", comparative:"Сравнительная", superlative:"Превосходная"};

  let DATA = [];
  let byLetter = {};
  let byWordLower = {};
  let formsOfBase = {};

  let dictState = {
    letter: "A",
    query: "",
    visible: PAGE_SIZE,
  };

  const el = {
    totalCount: document.getElementById("totalCount"),
    letterNav: document.getElementById("letterNav"),
    letterHeading: document.getElementById("letterHeading"),
    entryList: document.getElementById("entryList"),
    loadMoreWrap: document.getElementById("loadMoreWrap"),
    loadMoreBtn: document.getElementById("loadMoreBtn"),
    emptyState: document.getElementById("emptyState"),
    searchInput: document.getElementById("searchInput"),
    searchMeta: document.getElementById("searchMeta"),
    modal: document.getElementById("entryModal"),
    modalClose: document.getElementById("modalClose"),
    modalBackdrop: document.getElementById("modalBackdrop"),
    modalBody: document.getElementById("modalBody"),
  };

  function collectFormStrings(obj, out){
    if (!obj || typeof obj !== "object") return;
    for (const k in obj){
      const val = obj[k];
      if (typeof val === "string"){
        const trimmed = val.trim();
        if (trimmed) out.push(trimmed);
      } else if (Array.isArray(val)){
        for (const item of val){
          if (typeof item === "string"){
            const t = item.trim();
            if (t) out.push(t);
          } else if (item && typeof item === "object" && typeof item.f === "string"){
            const t = item.f.trim();
            if (t) out.push(t);
          }
        }
      } else if (typeof val === "object"){
        collectFormStrings(val, out);
      }
    }
  }

  function getEntryForms(e){
    if (e._formList !== undefined) return e._formList;
    const list = [];
    if (e.f) list.push(...e.f.split(/[,;/]\s*/).map(s => s.trim()).filter(Boolean));
    if (e.paradigm) collectFormStrings(e.paradigm, list);
    if (e.conjugation) collectFormStrings(e.conjugation, list);
    e._formList = list;
    e._formListNorm = list.map(stripAccents);
    return list;
  }

  function findMatchingForm(e, q){
    getEntryForms(e);
    const forms = e._formList;
    const formsNorm = e._formListNorm;
    for (let i = 0; i < forms.length; i++){
      if (formsNorm[i].includes(q)) return forms[i];
    }
    return null;
  }

  function initDict(data){
    DATA = data;
    byLetter = {};
    byWordLower = {};
    formsOfBase = {};

    for (const e of DATA){
      const l = deriveLetter(e.w);
      (byLetter[l] ||= []).push(e);

      const wl = e.w.toLowerCase();
      (byWordLower[wl] ||= []).push(e);

      if (e.b){
        const bl = e.b.toLowerCase();
        (formsOfBase[bl] ||= []).push(e);
      }

      e._search_w = stripAccents(e.w);
      e._search_other = ["ru","lt","lv","de","en","pl"]
        .map(k => e[k] || "")
        .join(" ")
        .toLowerCase();
    }

    if (el.totalCount) el.totalCount.textContent = DATA.length.toLocaleString("ru-RU");
    buildLetterNav();
    renderDict();
  }

  function buildLetterNav(){
    el.letterNav.innerHTML = "";
    for (const ch of LETTER_ORDER){
      const count = byLetter[ch] ? byLetter[ch].length : 0;
      if (!count) continue;
      const btn = document.createElement("button");
      btn.textContent = ch;
      btn.dataset.letter = ch;
      if (ch === dictState.letter) btn.classList.add("active");
      btn.addEventListener("click", () => {
        dictState.letter = ch;
        dictState.query = "";
        dictState.visible = PAGE_SIZE;
        el.searchInput.value = "";
        el.searchMeta.textContent = "";
        updateLetterNavActive();
        renderDict();
        window.scrollTo({ top: 0, behavior: "smooth" });
      });
      el.letterNav.appendChild(btn);
    }
  }

  function updateLetterNavActive(){
    for (const btn of el.letterNav.querySelectorAll("button")){
      btn.classList.toggle("active", btn.dataset.letter === dictState.letter && !dictState.query);
    }
  }

  function currentResults(){
    if (!dictState.query){
      return byLetter[dictState.letter] || [];
    }
    const q = stripAccents(dictState.query);
    const out = [];
    for (const e of DATA){
      let matchedForm = null;
      if (e._search_w.includes(q) || e._search_other.includes(q) || (matchedForm = findMatchingForm(e, q))){
        e._lastMatchedForm = matchedForm;
        out.push(e);
      } else {
        e._lastMatchedForm = null;
      }
    }
    return out;
  }

  function glossLine(e){
    const parts = [];
    for (const k of ["ru","lt","lv","de","en","pl"]){
      if (e[k]) parts.push(`<span class="gloss-item"><span class="lang-tag ${k}">${LANG_LABELS[k]}</span>${escapeHtml(e[k])}</span>`);
    }
    return parts.join(" ");
  }

  function renderDict(){
    const list = currentResults();
    const visibleCount = Math.min(dictState.visible, list.length);
    const visibleItems = list.slice(0, visibleCount);

    if (dictState.query){
      el.letterHeading.textContent = `Поиск: «${dictState.query}» (${list.length})`;
      el.searchMeta.textContent = `найдено ${list.length}`;
    } else {
      el.letterHeading.textContent = `${dictState.letter} (${list.length})`;
      el.searchMeta.textContent = "";
    }

    if (!list.length){
      el.entryList.innerHTML = "";
      el.emptyState.hidden = false;
      el.loadMoreWrap.hidden = true;
      return;
    }
    el.emptyState.hidden = true;

    const frag = document.createDocumentFragment();
    for (const e of visibleItems){
      const row = document.createElement("div");
      row.className = "entry-card" + (e.x ? " is-form" : "");

      let headHtml = "";
      if (e.x && e.b){
        headHtml = `<span class="entry-word"><span class="form-arrow">↳</span>${escapeHtml(e.w)}</span>`
          + `<span class="entry-base">${escapeHtml(e.b)}</span>`;
      } else {
        headHtml = `<span class="entry-word">${escapeHtml(e.w)}</span>`;
      }
      if (e.g) headHtml += `<span class="entry-grammar">${escapeHtml(e.g)}</span>`;
      if (e.s) headHtml += `<span class="entry-source">${escapeHtml(e.s)}</span>`;

      row.innerHTML = `<div class="entry-head">${headHtml}</div><div class="entry-gloss">${glossLine(e)}</div>`;
      row.addEventListener("click", () => openModal(e));
      frag.appendChild(row);
    }

    el.entryList.innerHTML = "";
    el.entryList.appendChild(frag);
    el.loadMoreWrap.hidden = visibleCount >= list.length;
  }

  function escapeHtml(s){
    if (s === null || s === undefined) return "";
    return String(s)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#039;");
  }

  function genderGridHtml(genderObj){
    let out = "";
    if (!genderObj || typeof genderObj !== "object") return out;
    for (const gender in genderObj){
      const numbers = genderObj[gender];
      if (!numbers || typeof numbers !== "object") continue;
      for (const number in numbers){
        const forms = numbers[number];
        if (!forms || typeof forms !== "object") continue;
        const cases = CASE_ORDER.filter(c => forms[c]);
        if (!cases.length) continue;
        out += `<div class="mw-para-block" style="margin-bottom:10px;">
          <div style="font-weight:600; font-size:12px; color:var(--parchment-dim); margin-bottom:4px;">${escapeHtml(GENDER_LABEL[gender] || gender)}, ${escapeHtml(NUMBER_LABEL[number] || number)}</div>
          <table class="paradigm-table">
            ${cases.map(c => `<tr><td class="case-cell">${CASE_LABEL[c] || c}</td><td>${escapeHtml(forms[c])}</td></tr>`).join("")}
          </table>
        </div>`;
      }
    }
    return out;
  }

  function paradigmHtml(paradigm){
    if (!paradigm || typeof paradigm !== "object") return "";
    const isAdjective = DEGREE_KEYS.some(k => paradigm[k]);

    if (isAdjective){
      let out = `<div class="paradigm-section"><h3>Склонение</h3>`;
      for (const deg of DEGREE_KEYS){
        if (!paradigm[deg]) continue;
        out += `<h4 style="color:var(--amber); font-size:13px; margin:6px 0;">${DEGREE_LABEL[deg]}</h4>${genderGridHtml(paradigm[deg])}`;
      }
      out += `</div>`;
      return out;
    }
    return `<div class="paradigm-section"><h3>Склонение</h3>${genderGridHtml(paradigm)}</div>`;
  }

  function pronounRowsHtml(rows){
    if (!Array.isArray(rows) || !rows.length) return "";
    return `<table class="paradigm-table">${rows.map(r => `<tr><td class="case-cell" style="width:140px;">${escapeHtml(r.p)}</td><td>${escapeHtml(r.f)}</td></tr>`).join("")}</table>`;
  }

  const TENSE_LABEL = {present:"Настоящее время", past:"Прошедшее время", perfect:"Перфект", future:"Будущее время"};

  function conjugationHtml(conj){
    if (!conj || typeof conj !== "object") return "";
    let out = `<div class="paradigm-section"><h3>Спряжение</h3>`;
    if (conj.indicative){
      out += `<h4 style="color:var(--amber); font-size:13px; margin:6px 0;">Изъявительное наклонение</h4>`;
      for (const tense of ["present","past","perfect","future"]){
        if (!conj.indicative[tense]) continue;
        out += `<div style="margin-bottom:8px;"><div style="font-size:12px; font-weight:600; color:var(--parchment-dim);">${TENSE_LABEL[tense] || tense}</div>${pronounRowsHtml(conj.indicative[tense])}</div>`;
      }
    }
    if (conj.optative){
      out += `<h4 style="color:var(--amber); font-size:13px; margin:6px 0;">Оптатив</h4><table class="paradigm-table"><tr><td>${escapeHtml(conj.optative)}</td></tr></table>`;
    }
    if (conj.imperative){
      out += `<h4 style="color:var(--amber); font-size:13px; margin:6px 0;">Императив</h4>${pronounRowsHtml(conj.imperative)}`;
    }
    if (conj.subjunctive){
      out += `<h4 style="color:var(--amber); font-size:13px; margin:6px 0;">Сослагательное наклонение</h4>${pronounRowsHtml(conj.subjunctive)}`;
    }
    out += `</div>`;
    return out;
  }

  function openModal(e){
    const rows = [];
    for (const k of ["ru","lt","lv","de","en","pl"]){
      const val = e[k];
      rows.push(`<div style="display:flex; padding:4px 0; border-bottom:1px solid var(--ink-line);"><span style="width:50px; font-family:var(--mono); font-size:11px; color:var(--parchment-dim);">${LANG_LABELS[k]}</span><span style="flex:1;">${val ? escapeHtml(val) : '<i style="color:var(--parchment-dim)">нет данных</i>'}</span></div>`);
    }

    let xrefHtml = "";
    if (e.x && e.b){
      xrefHtml = `<p style="font-size:13px; margin:8px 0; color:var(--sea);">Словоформа от: <a href="#" data-word="${escapeHtml(e.b)}" style="color:var(--amber); font-weight:600;">${escapeHtml(e.b)}</a>${e.g ? " — " + escapeHtml(e.g) : ""}</p>`;
    }
    const bl = e.w.toLowerCase();
    if (formsOfBase[bl] && formsOfBase[bl].length){
      const links = formsOfBase[bl]
        .map(f => `<a href="#" data-word="${escapeHtml(f.w)}" style="color:var(--amber);">${escapeHtml(f.w)}${f.g ? " <i>("+escapeHtml(f.g)+")</i>" : ""}</a>`)
        .join(", ");
      xrefHtml += `<p style="font-size:13px; margin:8px 0; color:var(--parchment-dim);">Словоформы: ${links}</p>`;
    }

    el.modalBody.innerHTML = `
      <h2 style="font-family:var(--serif); font-size:26px; color:var(--amber-bright); margin-bottom:4px;">${escapeHtml(e.w)}</h2>
      ${e.f ? `<p style="font-size:13px; color:var(--parchment-dim); margin-bottom:8px;">варианты: ${escapeHtml(e.f)}</p>` : ""}
      ${e.s ? `<p style="font-size:12px; color:#7a7f8d; margin-bottom:12px;">${escapeHtml(e.s)}</p>` : ""}
      ${xrefHtml}
      <div style="margin:14px 0;">${rows.join("")}</div>
      ${paradigmHtml(e.paradigm)}
      ${conjugationHtml(e.conjugation)}
    `;

    el.modalBody.querySelectorAll("a[data-word]").forEach(a => {
      a.addEventListener("click", (ev) => {
        ev.preventDefault();
        const w = a.getAttribute("data-word").toLowerCase();
        const matches = byWordLower[w];
        if (matches && matches.length) openModal(matches[0]);
      });
    });

    el.modal.hidden = false;
    document.body.style.overflow = "hidden";
  }

  function closeModal(){
    el.modal.hidden = true;
    document.body.style.overflow = "";
  }

  el.modalClose.addEventListener("click", closeModal);
  el.modalBackdrop.addEventListener("click", closeModal);
  document.addEventListener("keydown", (ev) => {
    if (ev.key === "Escape" && !el.modal.hidden) closeModal();
  });

  let searchTimeout = null;
  el.searchInput.addEventListener("input", () => {
    clearTimeout(searchTimeout);
    searchTimeout = setTimeout(() => {
      dictState.query = el.searchInput.value.trim();
      dictState.visible = PAGE_SIZE;
      updateLetterNavActive();
      renderDict();
    }, 120);
  });

  el.loadMoreBtn.addEventListener("click", () => {
    dictState.visible += PAGE_SIZE;
    renderDict();
  });

  // Загрузка словаря и оверлеев
  const OVERRIDE_META_KEYS = ["word","id","letter","forms","is_form","base_word","grammar_note","source","ru","lt","lv","de","en","pl","priority"];

  function applyOverrides(data, overrides){
    if (!Array.isArray(overrides) || !overrides.length) return data;
    const byId = {};
    const byWord = {};
    for (const e of data){
      if (e.i !== undefined && e.i !== null) byId[String(e.i)] = e;
      const w = (e.w || "").toLowerCase();
      if (w) (byWord[w] ||= []).push(e);
    }

    for (const ov of overrides){
      if (!ov || typeof ov !== "object") continue;
      const target = (ov.id !== undefined && ov.id !== null && byId[String(ov.id)])
        || (ov.word && byWord[ov.word.toLowerCase()] && byWord[ov.word.toLowerCase()][0]);

      if (target){
        if (ov.paradigm) target.paradigm = ov.paradigm;
        if (ov.conjugation) target.conjugation = ov.conjugation;
        for (const k of ["ru","lt","lv","de","en","pl","f","g","s","b"]){
          if (ov[k] !== undefined && ov[k] !== "") target[k] = ov[k];
        }
      } else if (ov.word){
        const fresh = {
          i: ov.id !== undefined ? ov.id : "ov-" + ov.word.toLowerCase(),
          w: ov.word,
          l: ov.letter || deriveLetter(ov.word),
          f: ov.forms || "",
          x: Boolean(ov.is_form),
          b: ov.base_word || "",
          g: ov.grammar_note || "",
          s: ov.source || "добавлено оверлеем",
          ru: ov.ru || "", lt: ov.lt || "", lv: ov.lv || "", de: ov.de || "", en: ov.en || "", pl: ov.pl || ""
        };
        for (const k in ov){
          if (OVERRIDE_META_KEYS.indexOf(k) !== -1) continue;
          fresh[k] = ov[k];
        }
        data.push(fresh);
        (byWord[ov.word.toLowerCase()] ||= []).push(fresh);
        if (fresh.i !== undefined && fresh.i !== null) byId[String(fresh.i)] = fresh;
      }
    }
    return data;
  }

  function loadOverrides(){
    return fetch("data/overrides/manifest.json")
      .then(r => r.ok ? r.json() : null)
      .catch(() => null)
      .then(m => {
        if (!m || !Array.isArray(m.shards) || !m.shards.length){
          return fetch("data/overrides.json").then(r => r.ok ? r.json() : []).catch(() => []);
        }
        const files = m.shards.map(s => (typeof s === "string" ? s : (s && s.file) || "")).filter(Boolean);
        return Promise.all(files.map(f =>
          fetch("data/overrides/" + f).then(r => r.ok ? r.json() : []).catch(() => [])
        )).then(lists => lists.reduce((acc, l) => acc.concat(l), []));
      })
      .then(list => Array.isArray(list) ? list : []);
  }

  fetch("data/dictionary.json")
    .then(r => r.json())
    .then(data => {
      loadOverrides()
        .then(overrides => initDict(applyOverrides(data, overrides || [])))
        .catch(() => initDict(data));
    })
    .catch(err => {
      el.entryList.innerHTML = `<p style="color:var(--danger)">Не удалось загрузить словарь: ${escapeHtml(err.message)}.</p>`;
    });


  // =========================================================================
  // 3. МОДУЛЬ ПЕРЕВОДЧИКА (PYODIDE + PYMORPHY3 + TRANSLATE_CORE)
  // =========================================================================
  const transUI = {
    loading: document.getElementById("transLoading"),
    statusText: document.getElementById("transStatusText"),
    app: document.getElementById("transApp"),
    inputLabel: document.getElementById("transInputLabel"),
    input: document.getElementById("transInput"),
    translateBtn: document.getElementById("translateBtn"),
    statsNote: document.getElementById("transStatsNote"),
    resultWrap: document.getElementById("resultWrap"),
    resultLabel: document.getElementById("resultLabel"),
    resultText: document.getElementById("resultText"),
    copyResultBtn: document.getElementById("copyResultBtn"),
    breakdownTable: document.getElementById("breakdownTable"),
    breakdownBody: document.getElementById("breakdownBody"),
    presetsList: document.getElementById("presetsList"),
    dirRuPrBtn: document.getElementById("dir-ru-pr"),
    dirPrRuBtn: document.getElementById("dir-pr-ru"),
    error: document.getElementById("transError"),
    errorText: document.getElementById("transErrorText"),
    feedbackComment: document.getElementById("feedbackComment"),
    feedbackCopy: document.getElementById("feedbackCopy"),
    feedbackCopiedNote: document.getElementById("feedbackCopiedNote"),
  };

  let transDirection = "ru-pr"; // "ru-pr" | "pr-ru"
  let pyodideInstance = null;
  let pyodideLoading = false;
  let pyodideReady = false;
  let translateFunctions = null;
  let lastTranslateResult = null;

  const PRESETS = {
    "ru-pr": [
      "Я вижу красивую девушку",
      "Мы говорим на прусском языке",
      "Человек дал книгу своему другу",
      "Они обитают в старом городе",
      "Ты знаешь это слово?"
    ],
    "pr-ru": [
      "As reggi grazzjan mērgan",
      "Mes bilāimai na prūsiskan billan",
      "Gints dāi lāiskan swajasmu ginnei",
      "Prūsai madli deiwans",
      "Tenēi buwinna ēn wāriskasmu mēstu"
    ]
  };

  function setTransDirection(dir){
    transDirection = dir;
    transUI.dirRuPrBtn.classList.toggle("active", dir === "ru-pr");
    transUI.dirPrRuBtn.classList.toggle("active", dir === "pr-ru");

    if (dir === "ru-pr"){
      transUI.inputLabel.textContent = "Фраза по-русски";
      transUI.input.placeholder = "Например: Я вижу красивую девушку";
      transUI.resultLabel.textContent = "Прусский (черновой перевод)";
    } else {
      transUI.inputLabel.textContent = "Фраза по-прусски";
      transUI.input.placeholder = "Например: As reggi grazzjan mērgan";
      transUI.resultLabel.textContent = "Русский (черновой перевод)";
    }

    renderPresets();
    transUI.resultWrap.classList.add("hidden");
  }

  function renderPresets(){
    transUI.presetsList.innerHTML = "";
    const list = PRESETS[transDirection] || [];
    for (const text of list){
      const pill = document.createElement("button");
      pill.type = "button";
      pill.className = "preset-pill";
      pill.textContent = text;
      pill.addEventListener("click", () => {
        transUI.input.value = text;
        runTranslation();
      });
      transUI.presetsList.appendChild(pill);
    }
  }

  transUI.dirRuPrBtn.addEventListener("click", () => setTransDirection("ru-pr"));
  transUI.dirPrRuBtn.addEventListener("click", () => setTransDirection("pr-ru"));
  renderPresets();

  function setTransStatus(msg){
    transUI.statusText.textContent = msg;
  }

  async function loadPyodideScript(){
    if (window.loadPyodide) return;
    return new Promise((resolve, reject) => {
      const script = document.createElement("script");
      script.src = "https://cdn.jsdelivr.net/pyodide/v0.27.3/full/pyodide.js";
      script.onload = () => resolve();
      script.onerror = () => reject(new Error("Не удалось загрузить Pyodide с CDN"));
      document.head.appendChild(script);
    });
  }

  async function fetchText(url){
    const r = await fetch(url);
    if (!r.ok) throw new Error(`${url}: HTTP ${r.status}`);
    return r.text();
  }

  async function fetchOptionalText(url, fallback){
    try {
      const r = await fetch(url);
      return r.ok ? await r.text() : fallback;
    } catch {
      return fallback;
    }
  }

  async function loadDictionaryDataForTranslator(){
    // Пробуем шардированные данные, если нет - плоские файлы
    try {
      const manifestResp = await fetch("data/shards/manifest.json", { cache: "no-cache" });
      if (manifestResp.ok){
        const manifest = await manifestResp.json();
        const loadSection = async (sectionName) => {
          const s = manifest[sectionName];
          const texts = await Promise.all(s.shards.map(sh => fetchText(`data/shards/${sh.path}`)));
          return "[" + texts.map(t => t.trim().replace(/^\[|\]$/g, "")).filter(Boolean).join(",") + "]";
        };
        const [dictText, overridesText] = await Promise.all([
          loadSection("dictionary"),
          loadSection("overrides")
        ]);
        return { dictText, overridesText, mode: "shards" };
      }
    } catch (e) {
      console.warn("Sharded dictionary failed, falling back to flat files", e);
    }

    const [dictText, overridesText] = await Promise.all([
      fetchText("data/dictionary.json"),
      fetchText("data/overrides.json")
    ]);
    return { dictText, overridesText, mode: "flat" };
  }

  async function initTranslatorIfNeeded(){
    if (pyodideReady || pyodideLoading) return;
    pyodideLoading = true;
    transUI.loading.classList.remove("hidden");

    try {
      setTransStatus("Загрузка WebAssembly среды Pyodide…");
      await loadPyodideScript();
      pyodideInstance = await window.loadPyodide();

      setTransStatus("Установка pymorphy3 для разбора русской грамматики…");
      await pyodideInstance.loadPackage("micropip");
      const micropip = pyodideInstance.pyimport("micropip");
      await micropip.install(["pymorphy3", "pymorphy3-dicts-ru"]);

      setTransStatus("Загрузка словарей и парадигм Prūsiska bilā…");
      const [dataFiles, phrasebook, priorities, propernames, coreCode] = await Promise.all([
        loadDictionaryDataForTranslator(),
        fetchOptionalText("data/phrasebook.json", "[]"),
        fetchOptionalText("data/priorities.json", "{}"),
        fetchOptionalText("data/propernames.json", "{}"),
        fetchText("translate_core.py"),
      ]);

      setTransStatus("Компиляция правил согласования и построение индексов…");
      await pyodideInstance.runPythonAsync(coreCode);
      const loadData = pyodideInstance.globals.get("load_data");
      const stats = loadData(dataFiles.dictText, dataFiles.overridesText, phrasebook, priorities, propernames).toJs({ dict_converter: Object.fromEntries });

      transUI.statsNote.textContent = `База: ${stats.words} статей · с парадигмами: ${stats.overrides} · предлогов: ${stats.prepositions} · фраз: ${stats.phrases || 0} · движок готов`;

      const translateSentenceJson = pyodideInstance.globals.get("translate_sentence_json");
      const translatePrSentenceJson = pyodideInstance.globals.get("translate_pr_sentence_json");

      translateFunctions = {
        "ru-pr": (text) => JSON.parse(translateSentenceJson(text)),
        "pr-ru": (text) => JSON.parse(translatePrSentenceJson(text)),
      };

      pyodideReady = true;
      pyodideLoading = false;
      transUI.loading.classList.add("hidden");

      if (transUI.input.value.trim()){
        runTranslation();
      }
    } catch (err){
      console.error(err);
      pyodideLoading = false;
      transUI.loading.classList.add("hidden");
      transUI.error.classList.remove("hidden");
      transUI.errorText.textContent = "Ошибка запуска переводчика: " + (err.message || err);
    }
  }

  function runTranslation(){
    const text = transUI.input.value.trim();
    if (!text){
      transUI.resultWrap.classList.add("hidden");
      return;
    }
    if (!pyodideReady){
      initTranslatorIfNeeded();
      return;
    }

    try {
      const res = translateFunctions[transDirection](text);
      lastTranslateResult = { direction: transDirection, text, res };

      transUI.resultText.textContent = res.translation || "";
      transUI.resultWrap.classList.remove("hidden");

      // Рендер таблицы разбора
      transUI.breakdownBody.innerHTML = "";
      const words = res.words || [];
      for (const w of words){
        const tr = document.createElement("tr");
        const srcTd = document.createElement("td");
        srcTd.textContent = w.src || "";
        const outTd = document.createElement("td");
        outTd.textContent = w.out || "";
        const noteTd = document.createElement("td");
        noteTd.textContent = w.note || "";

        tr.appendChild(srcTd);
        tr.appendChild(outTd);
        tr.appendChild(noteTd);
        transUI.breakdownBody.appendChild(tr);
      }
    } catch (e){
      console.error(e);
      alert("Ошибка перевода: " + e.message);
    }
  }

  transUI.translateBtn.addEventListener("click", runTranslation);
  transUI.input.addEventListener("keydown", (ev) => {
    if ((ev.ctrlKey || ev.metaKey) && ev.key === "Enter"){
      ev.preventDefault();
      runTranslation();
    }
  });

  transUI.copyResultBtn.addEventListener("click", () => {
    const text = transUI.resultText.textContent;
    if (text){
      navigator.clipboard.writeText(text).then(() => {
        const orig = transUI.copyResultBtn.textContent;
        transUI.copyResultBtn.textContent = "✓ Скопировано";
        setTimeout(() => { transUI.copyResultBtn.textContent = orig; }, 1500);
      });
    }
  });

  transUI.feedbackCopy.addEventListener("click", () => {
    if (!lastTranslateResult) return;
    const comment = transUI.feedbackComment.value.trim();
    const report = [
      "=== Отчёт об ошибке перевода Prūsiskan Wirdeīns ===",
      `Направление: ${lastTranslateResult.direction}`,
      `Входной текст: ${lastTranslateResult.text}`,
      `Результат: ${lastTranslateResult.res.translation}`,
      comment ? `Комментарий: ${comment}` : "",
      "Разбор по словам:",
      JSON.stringify(lastTranslateResult.res.words, null, 2)
    ].filter(Boolean).join("\n\n");

    navigator.clipboard.writeText(report).then(() => {
      transUI.feedbackCopiedNote.classList.remove("hidden");
      setTimeout(() => transUI.feedbackCopiedNote.classList.add("hidden"), 3000);
    });
  });

})();
