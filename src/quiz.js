/* UseThisSI quiz. Data is generated at build time from data.csv (see quiz.py). No framework, no cookies of our own. */
(function () {
  "use strict";
  var Q = JSON.parse(document.getElementById("qdata").textContent);
  var root = document.getElementById("quiz");
  var FORM = root.getAttribute("data-form");
  var BH = "https://subscribe-forms.beehiiv.com";
  var st = { r: null, j: null, b: null, s: null }, preJob = false, fromHash = false, started = false, formLoaded = false, qIframe = null;
  function el(h) { var d = document.createElement("div"); d.innerHTML = h; return d.firstElementChild; }
  function esc(s) { return String(s).replace(/[&<>"']/g, function (c) { return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]; }); }
  function P(a, b) { return "/" + a + "/" + b + "/"; }
  function idx(list, k, key) { for (var i = 0; i < list.length; i++) if (list[i][key || "k"] === k) return i; return -1; }
  function fmt(v, cur) { var s = (cur === "EUR" ? "\u20ac" : "$") + v.toFixed(2); return s.slice(-3) === ".00" ? s.slice(0, -3) : s; }
  // Vercel Web Analytics (Hobby has no custom events): count funnel steps as virtual pageviews.
  function track(path) { try { if (window.va) window.va("pageview", { path: path }); } catch (e) {} }
  function readHash() {
    var h = {}; location.hash.replace(/^#/, "").split("&").forEach(function (p) { var kv = p.split("="); if (kv[0]) h[kv[0]] = decodeURIComponent(kv[1] || ""); });
    if (idx(Q.jobs, h.j, "slug") >= 0) { st.j = h.j; preJob = true; }
    if (idx(Q.roles, h.r) >= 0) st.r = h.r;
    if (idx(Q.budgets, h.b) >= 0) st.b = h.b;
    if (idx(Q.skills, h.s) >= 0) st.s = h.s;
  }
  function writeHash() {
    var p = []; ["r", "j", "b", "s"].forEach(function (k) { if (st[k]) p.push(k + "=" + encodeURIComponent(st[k])); });
    history.replaceState(null, "", location.pathname + location.search + (p.length ? "#" + p.join("&") : ""));
  }
  function steps() { var s = ["r"]; if (!preJob) s.push("j"); s.push("b", "s"); return s; }
  function jobsFor(r) {
    var ri = idx(Q.roles, r), first = ri >= 0 ? Q.roles[ri].jobs : [], out = [];
    first.forEach(function (j) { var i = idx(Q.jobs, j, "slug"); if (i >= 0) out.push(Q.jobs[i]); });
    Q.jobs.forEach(function (j) { if (first.indexOf(j.slug) < 0) out.push(j); });
    return out;
  }
  function render() {
    var S = steps(), n = 0;
    while (n < S.length && st[S[n]]) n++;
    if (n >= S.length) return showResult();
    var k = S[n], title, opts, hint = "";
    if (k === "r") { title = "What do you do?"; opts = Q.roles.map(function (o) { return [o.k, o.name]; }); }
    else if (k === "j") { title = "What's the main job you want AI for?"; opts = jobsFor(st.r).map(function (o) { return [o.slug, o.name]; }); hint = "Most common for you first."; }
    else if (k === "b") { title = "What's your monthly budget for this?"; opts = Q.budgets.map(function (o) { return [o.k, o.name]; }); }
    else { title = "How comfortable are you with AI tools?"; opts = Q.skills.map(function (o) { return [o.k, o.name]; }); hint = "Optional."; }
    var pct = Math.round(n / S.length * 100);
    var h = '<div class="qstep"><div class="qprog" role="progressbar" aria-valuemin="0" aria-valuemax="' + S.length + '" aria-valuenow="' + n + '"><span style="width:' + pct + '%"></span></div>' +
      '<p class="qcount">Question ' + (n + 1) + " of " + S.length + (preJob ? ' &middot; job: <b>' + esc(Q.jobs[idx(Q.jobs, st.j, "slug")].name) + "</b>" : "") + "</p>" +
      '<h2 id="qtitle" tabindex="-1">' + title + "</h2>" + (hint ? '<p class="qhint">' + hint + "</p>" : "") +
      '<div class="qopts" role="group" aria-labelledby="qtitle">' + opts.map(function (o) { return '<button type="button" class="qopt" data-k="' + k + '" data-v="' + esc(o[0]) + '">' + esc(o[1]) + "</button>"; }).join("") + "</div>" +
      '<div class="qnav">' + (n > 0 ? '<button type="button" class="qback" data-back="1">&larr; Back</button>' : "") + (k === "s" ? '<button type="button" class="qback" data-skip="1">Skip this question &rarr;</button>' : "") + "</div></div>";
    root.innerHTML = h;
    if (started) { var t = document.getElementById("qtitle"); if (t) t.focus({ preventScroll: true }); }
  }
  root.addEventListener("click", function (e) {
    var b = e.target.closest("button"); if (!b) return;
    if (b.hasAttribute("data-v")) {
      if (!started) { started = true; track("/quiz/start/"); }
      st[b.getAttribute("data-k")] = b.getAttribute("data-v"); writeHash(); render();
    } else if (b.hasAttribute("data-skip")) { st.s = Q.defaultSkill; writeHash(); render(); }
    else if (b.hasAttribute("data-back")) {
      var S = steps(), n = 0; while (n < S.length && st[S[n]]) n++;
      if (n > 0) st[S[n - 1]] = null; writeHash(); render();
    } else if (b.hasAttribute("data-restart")) {
      st = { r: null, j: preJob ? st.j : null, b: null, s: null }; writeHash(); render(); root.scrollIntoView({ behavior: "smooth", block: "start" });
    } else if (b.hasAttribute("data-copy")) {
      var u = location.href;
      if (navigator.clipboard) navigator.clipboard.writeText(u).then(function () { b.textContent = "Link copied"; }, function () { prompt("Copy this link:", u); });
      else prompt("Copy this link:", u);
    }
  });
  function card(cls, label, t, why, extra) {
    if (!t) return '<article class="qcard ' + cls + '"><p class="qlabel">' + label + "</p>" + why + "</article>";
    return '<article class="qcard ' + cls + '"><p class="qlabel">' + label + '</p><h3><a href="' + P("tools", t.slug) + '">' + esc(t.tool) + "</a></h3>" +
      '<p class="qwhy">' + esc(why) + "</p>" + (extra || "") +
      '<ul class="qfacts"><li><span>Free tier</span> ' + esc(t.freeShort) + '</li><li><span>Paid from</span> ' + esc(t.price) + '</li><li><span>Checked</span> <time datetime="' + t.checked + '">' + esc(t.checkedNice) + "</time></li></ul>" +
      '<a class="qmore" href="' + P("tools", t.slug) + '">Full details &rarr;</a></article>';
  }
  function note(tpl, t, paid) {
    if (!tpl || !t) return "";
    var s = tpl.replace("{price}", t.mo != null ? fmt(t.mo, t.cur) : "");
    if (paid) s = s.replace("{paidtool}", paid.tool).replace("{paidprice}", paid.mo != null ? fmt(paid.mo, paid.cur) : "");
    return s;
  }
  function showResult() {
    if (!st.s) st.s = Q.defaultSkill;
    var ri = idx(Q.roles, st.r), ji = idx(Q.jobs, st.j, "slug"), bi = idx(Q.budgets, st.b), si = idx(Q.skills, st.s);
    var c = Q.combos[ri][ji][bi][si], T = Q.tools;
    var f = c[0] >= 0 ? T[c[0]] : null, p = c[1] >= 0 ? T[c[1]] : null, k = c[2] >= 0 ? T[c[2]] : null, job = Q.jobs[ji];
    var fwhy = f ? f.reason + "." : "";
    var fextra = f && Q.catch[f.kind] ? '<p class="qcatch">Catch: ' + esc(Q.catch[f.kind]) + "</p>" : "";
    var pcard;
    if (p) {
      var up = c[5] && f ? '<p class="qcatch">Happy with ' + esc(f.tool) + "? Its paid plan starts at " + fmt(f.mo, f.cur) + "/mo.</p>" : "";
      pcard = card("q-paid", "Paid pick worth it", p, p.reason + ". " + note(Q.paidNotes[c[3]], p, p), up);
    } else if (st.b === "0") {
      pcard = card("q-paid", "Paid pick", null, "<h3>None. Stay free.</h3><p class=\"qwhy\">Your budget is $0, so we won't push a paid plan." + (f && f.mo != null ? " If you outgrow " + esc(f.tool) + ", its paid plan starts at " + fmt(f.mo, f.cur) + "/mo." : "") + "</p>");
    } else {
      pcard = card("q-paid", "Paid pick", null, '<h3>None that fits.</h3><p class="qwhy">No tool with a verified price fits this budget. The free pick is your best move.</p>');
    }
    var kcard = k ? card("q-skip", "Skip", k, note(Q.skipNotes[c[4]], k, p)) : card("q-skip", "Skip", null, '<h3>Nothing to skip.</h3><p class="qwhy">Every other checked tool for this job is a reasonable fit. Start with the free pick.</p>');
    var fcard = f ? card("q-free", "Free pick", f, fwhy, fextra) : card("q-free", "Free pick", null, '<h3>No verified free tier.</h3><p class="qwhy">None of this job\'s tools has a free tier we checked in the last 30 days.</p>');
    var free = Q.freeJobs.indexOf(job.slug) >= 0 ? ' or only the <a href="' + P("free", job.slug) + '">free options</a>' : "";
    root.innerHTML = '<div class="qresult"><p class="qcount">Your stack for <b>' + esc(job.name.toLowerCase()) + "</b> &middot; " + esc(Q.budgets[bi].name) + '</p><h2 id="qtitle" tabindex="-1">Your 3 picks</h2>' +
      '<div class="qcards">' + fcard + pcard + kcard + "</div>" +
      '<p class="qsmall">Picked by rules, not by who pays: only tools we checked in the last 30 days, with the price and free tier from the vendor\'s own page. Prices change, so confirm before you buy. See <a href="' + P("use-cases", job.slug) + '">every option for this job</a>' + free + ".</p>" +
      '<div class="qnav"><button type="button" class="qback" data-copy="1">Copy link to these picks</button><button type="button" class="qback" data-restart="1">Start over</button></div></div>';
    var t = document.getElementById("qtitle"); if (t) t.focus({ preventScroll: true });
    root.scrollIntoView({ behavior: "smooth", block: "start" });
    if (!fromHash) track("/quiz/done/" + job.slug + "/");
    fromHash = false;
    showCapture(job.slug);
  }
  function getCookie(n) { var m = document.cookie.match(new RegExp("(?:^|; )" + n + "=([^;]*)")); return m ? m[1] : null; }
  function showCapture(job) {
    var cap = document.getElementById("qcap"); cap.hidden = false;
    var fb = document.getElementById("qfallback");
    fb.href = "https://usethissi.beehiiv.com/subscribe?utm_source=quiz&utm_medium=website&utm_campaign=quiz-" + job;
    if (formLoaded || !FORM) return;
    formLoaded = true;
    // beehiiv's loader reads utm_* from the page URL when it builds the form iframe and stores them in the
    // bhv_attribution cookie. Put the quiz UTMs on the URL just for that moment, then restore the URL and the
    // visitor's original attribution cookie, so only this form's signups are tagged as quiz.
    var oldSearch = location.search, oldCookie = getCookie("bhv_attribution");
    var u = new URL(location.href);
    u.searchParams.set("utm_source", "quiz"); u.searchParams.set("utm_medium", "website"); u.searchParams.set("utm_campaign", "quiz-" + job);
    history.replaceState(null, "", u.pathname + u.search + u.hash);
    var box = document.getElementById("qform"), done = false;
    function restore() {
      if (done) return; done = true;
      history.replaceState(null, "", location.pathname + oldSearch + location.hash);
      if (oldCookie) document.cookie = "bhv_attribution=" + oldCookie + "; path=/; max-age=" + 30 * 86400;
      else document.cookie = "bhv_attribution=; path=/; max-age=0";
    }
    var mo = new MutationObserver(function () { var f = box.querySelector("iframe"); if (f) { qIframe = f; mo.disconnect(); restore(); } });
    mo.observe(box, { childList: true, subtree: true });
    setTimeout(restore, 8000);
    var s = document.createElement("script"); s.async = true; s.src = BH + "/v3/loader.js"; s.setAttribute("data-beehiiv-form", FORM);
    box.appendChild(s);
  }
  window.addEventListener("message", function (e) {
    if (e.origin !== BH || !qIframe || e.source !== qIframe.contentWindow) return;
    if (e.data && e.data.type === "beehiiv:submitted") { track("/quiz/signup/"); var d = document.getElementById("qdone"); if (d) d.hidden = false; }
  });
  readHash();
  if (st.r && st.j && st.b) { started = true; fromHash = !!st.s; }
  render();
})();
