/* UseThisSI quiz. Data comes from data.csv at build time (see quiz.py). No framework.
   Results are soft-gated: the free pick shows right away; the paid and skip picks unlock after a beehiiv
   signup or a "No thanks" tap. The email form is beehiiv's own form (same id as the site), loaded in its
   slim layout with utm_source=quiz / utm_campaign=quiz-<job> set on the form URL. */
(function () {
  "use strict";
  var Q = JSON.parse(document.getElementById("qdata").textContent);
  var root = document.getElementById("quiz"), ask = document.getElementById("qask"), res = document.getElementById("qres");
  var FORM = root.getAttribute("data-form"), PUB = root.getAttribute("data-pub"), BH = "https://subscribe-forms.beehiiv.com";
  var ICON = { founder: "\uD83D\uDE80", dev: "\uD83D\uDCBB", marketer: "\uD83D\uDCE3", freelancer: "\uD83E\uDDF3", gamedev: "\uD83C\uDFAE", explore: "\uD83C\uDF93",
    "0": "\uD83C\uDD93", "20": "\uD83D\uDCB5", "50": "\uD83D\uDCB3", any: "\u2728", "new": "\uD83C\uDF31", mid: "\uD83D\uDC4D", tech: "\uD83D\uDEE0\uFE0F" };
  var st = { r: null, j: null, b: null, s: null }, preJob = false, fromHash = false, started = false;
  var qIframe = null, frameJob = null, unlocked = false, cur = null;
  function $(id) { return document.getElementById(id); }
  function P(a, b) { return "/" + a + "/" + b + "/"; }
  function esc(s) { return String(s).replace(/[&<>"']/g, function (c) { return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]; }); }
  function idx(list, k, key) { for (var i = 0; i < list.length; i++) if (list[i][key || "k"] === k) return i; return -1; }
  function fmt(v, c) { var s = (c === "EUR" ? "\u20ac" : "$") + v.toFixed(2); return s.slice(-3) === ".00" ? s.slice(0, -3) : s; }
  function short(d) { return d.replace(/, \d{4}$/, ""); }
  // Vercel Web Analytics on Hobby has no custom events, so funnel steps are virtual pageviews.
  function track(path) { try { if (window.va) window.va("pageview", { path: path }); } catch (e) {} }
  function getCookie(n) { var m = document.cookie.match(new RegExp("(?:^|; )" + n.replace(/[-.]/g, "\\$&") + "=([^;]*)")); return m ? m[1] : null; }
  function isSub() { try { if (localStorage.getItem("uts_sub")) return true; } catch (e) {} return !!(PUB && getCookie("bhv_" + PUB + "_subscribed")); }
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
  function setStarted() { if (!started) { started = true; } var h = $("qhero"); if (h) h.hidden = true; }
  function render() {
    var S = steps(), n = 0;
    while (n < S.length && st[S[n]]) n++;
    if (n >= S.length) return showResult();
    res.hidden = true; ask.hidden = false; stickyOff();
    var k = S[n], title, opts;
    if (k === "r") { title = "What do you do?"; opts = Q.roles.map(function (o) { return [o.k, o.name, ICON[o.k]]; }); }
    else if (k === "j") { title = "What do you need AI for most?"; opts = jobsFor(st.r).map(function (o) { return [o.slug, o.name, Q.icons[o.slug]]; }); }
    else if (k === "b") { title = "Monthly budget?"; opts = Q.budgets.map(function (o) { return [o.k, o.name, ICON[o.k]]; }); }
    else { title = "How handy are you with AI?"; opts = Q.skills.map(function (o) { return [o.k, o.name, ICON[o.k]]; }); }
    var pct = Math.round(n / (S.length - 1) * 100);
    ask.innerHTML = '<div class="qtop"><button type="button" class="qicon" data-back="1" aria-label="Back"' + (n ? "" : " hidden") + '>&larr;</button>' +
      '<div class="qprog" role="progressbar" aria-label="Progress" aria-valuemin="0" aria-valuemax="' + S.length + '" aria-valuenow="' + n + '"><span style="width:' + Math.max(pct, 6) + '%"></span></div>' +
      '<span class="qstepn">' + (k === "s" ? "Optional" : (n + 1) + "/" + (S.length - 1)) + "</span></div>" +
      '<div class="qstep"><h2 id="qtitle" tabindex="-1">' + title + "</h2>" +
      '<div class="qopts" role="group" aria-labelledby="qtitle">' + opts.map(function (o) {
        return '<button type="button" class="qopt" data-k="' + k + '" data-v="' + esc(o[0]) + '"><span class="qe" aria-hidden="true">' + (o[2] || "\u2728") + "</span>" + esc(o[1]) + "</button>";
      }).join("") + "</div>" + (k === "s" ? '<button type="button" class="qlink" data-skipq="1">Skip this one</button>' : "") + "</div>";
    if (started) { var t = $("qtitle"); if (t) t.focus({ preventScroll: true }); }
  }
  ask.addEventListener("click", function (e) {
    var b = e.target.closest("button"); if (!b) return;
    if (b.hasAttribute("data-v")) {
      if (!started) track("/quiz/start/");
      setStarted();
      st[b.getAttribute("data-k")] = b.getAttribute("data-v"); writeHash();
      if (st.j) loadForm(st.j);
      render(); scrollTop();
    } else if (b.hasAttribute("data-skipq")) { st.s = Q.defaultSkill; writeHash(); render(); scrollTop(); }
    else if (b.hasAttribute("data-back")) {
      var S = steps(), n = 0; while (n < S.length && st[S[n]]) n++;
      if (n > 0) st[S[n - 1]] = null; writeHash(); render();
    }
  });
  function scrollTop() { var y = root.getBoundingClientRect().top + window.pageYOffset - 70; if (window.pageYOffset > y || y - window.pageYOffset > 200) window.scrollTo({ top: Math.max(0, y), behavior: "smooth" }); }
  function chips(t, kind) {
    var a = [];
    if (kind === "free") { var m = /^Yes \(([^()]*)\)$/.exec(t.freeShort); a.push('<span class="qchip qc-free">Free' + (m ? ": " + esc(m[1]) : /^yes$/i.test(t.freeShort) ? " plan" : ": " + esc(t.freeShort.replace(/^Yes\s*/, ""))) + "</span>"); }
    else a.push('<span class="qchip">' + esc(t.price) + "</span>");
    a.push('<span class="qchip qc-date">Checked <time datetime="' + t.checked + '">' + esc(short(t.checkedNice)) + "</time></span>");
    return '<div class="qchips">' + a.join("") + "</div>";
  }
  function card(cls, label, t, why, extra) {
    if (!t) return '<article class="qcard ' + cls + '"><p class="qlabel">' + label + "</p>" + why + "</article>";
    return '<article class="qcard ' + cls + '"><p class="qlabel">' + label + '</p><h3><a href="' + P("tools", t.slug) + '">' + esc(t.tool) + "</a></h3>" +
      '<p class="qwhy">' + esc(why) + "</p>" + (extra || "") + chips(t, cls === "q-free" ? "free" : "price") + "</article>";
  }
  function note(tpl, t, paid) {
    if (!tpl || !t) return "";
    var s = tpl.replace("{price}", t.mo != null ? fmt(t.mo, t.cur) : "");
    if (paid) s = s.replace("{paidtool}", paid.tool).replace("{paidprice}", paid.mo != null ? fmt(paid.mo, paid.cur) : "");
    return s;
  }
  function showResult() {
    if (!st.s) st.s = Q.defaultSkill;
    setStarted();
    var ri = idx(Q.roles, st.r), ji = idx(Q.jobs, st.j, "slug"), bi = idx(Q.budgets, st.b), si = idx(Q.skills, st.s);
    var c = Q.combos[ri][ji][bi][si], T = Q.tools, job = Q.jobs[ji];
    var f = c[0] >= 0 ? T[c[0]] : null, p = c[1] >= 0 ? T[c[1]] : null, k = c[2] >= 0 ? T[c[2]] : null;
    cur = { f: f, p: p, k: k, c: c, job: job };
    ask.hidden = true; res.hidden = false;
    $("qmeta").innerHTML = esc(job.name) + " &middot; " + esc(Q.budgets[bi].name);
    $("qall").href = P("use-cases", job.slug);
    $("qfree").innerHTML = f ? card("q-free", "Free pick", f, f.reason + ".", Q.catch[f.kind] ? '<p class="qcatch">' + esc(Q.catch[f.kind]) + "</p>" : "")
      : card("q-free", "Free pick", null, '<h3>No verified free tier</h3><p class="qwhy">Nothing for this job has a free tier we checked in the last 30 days.</p>');
    $("qfallback").href = "https://usethissi.beehiiv.com/subscribe?utm_source=quiz&utm_medium=website&utm_campaign=quiz-" + job.slug;
    var an = $("qanchor"), ano = $("qanote");
    if (c[6] != null && c[6] >= 0) { $("qanchorv").textContent = fmt(c[6], "USD") + "/mo"; ano.textContent = "Based on list prices checked " + c[7] + "."; an.hidden = false; ano.hidden = false; }
    else { an.hidden = true; ano.hidden = true; }
    loadForm(job.slug);
    if (qIframe && qIframe.contentWindow) try { qIframe.contentWindow.postMessage({ type: "beehiiv:resize" }, "*"); } catch (e) {}
    if (unlocked || isSub()) reveal(isSub() ? "sub" : unlocked);
    else { $("qfull").hidden = true; $("qfull").innerHTML = ""; $("qlocked").hidden = false; $("qgate").hidden = false; stickyOn(); }
    var t = $("qrtitle"); if (t) t.focus({ preventScroll: true });
    scrollTop();
    if (!fromHash) track("/quiz/done/" + job.slug + "/");
    fromHash = false;
  }
  function fullCards() {
    var f = cur.f, p = cur.p, k = cur.k, c = cur.c, h;
    if (p) {
      var up = c[5] && f ? '<p class="qcatch qc-soft">Prefer ' + esc(f.tool) + "? Paid from " + fmt(f.mo, f.cur) + "/mo.</p>" : "";
      h = card("q-paid", "Paid pick", p, p.reason + ". " + note(Q.paidNotes[c[3]], p, p), up);
    } else if (st.b === "0") {
      h = card("q-paid", "Paid pick", null, '<h3>None. Stay free.</h3><p class="qwhy">Budget is $0.' + (f && f.mo != null ? " " + esc(f.tool) + " paid starts at " + fmt(f.mo, f.cur) + "/mo if you outgrow it." : "") + "</p>");
    } else {
      h = card("q-paid", "Paid pick", null, '<h3>None fits</h3><p class="qwhy">No verified price fits this budget. Stick with the free pick.</p>');
    }
    h += k ? card("q-skip", "Skip", k, note(Q.skipNotes[c[4]], k, p)) : card("q-skip", "Skip", null, '<h3>Nothing to skip</h3><p class="qwhy">The other checked tools are all fair options.</p>');
    return h;
  }
  function reveal(how) {
    unlocked = how;
    var full = $("qfull"); full.innerHTML = fullCards(); full.hidden = false; full.classList.remove("qin"); void full.offsetWidth; full.classList.add("qin");
    $("qlocked").hidden = true; stickyOff();
    if (how === "sub") { $("qgatebody").hidden = true; $("qsuccess").hidden = false; $("qgate").classList.add("qdone"); }
    else { $("qnothanks").hidden = true; $("qgh").textContent = "Want the free AI Stack Kit too?"; $("qlockline").hidden = true; $("qanchor").hidden = true; $("qanote").hidden = true; }
  }
  $("qnothanks").addEventListener("click", function () { track("/quiz/skip/"); reveal("skip"); var f = $("qfull"); f.scrollIntoView({ behavior: "smooth", block: "center" }); });
  res.addEventListener("click", function (e) {
    var b = e.target.closest("button"); if (!b) return;
    if (b.hasAttribute("data-restart")) { st = { r: null, j: preJob ? st.j : null, b: null, s: null }; writeHash(); render(); scrollTop(); }
    else if (b.hasAttribute("data-copy")) {
      var u = location.href;
      if (navigator.clipboard) navigator.clipboard.writeText(u).then(function () { b.textContent = "Link copied \u2713"; }, function () { prompt("Copy this link:", u); });
      else prompt("Copy this link:", u);
    }
  });
  // ---- beehiiv form (their slim layout: one email field + button). Same message protocol their loader.js uses.
  var wrap = null, fallbackTimer = null;
  function loadForm(job) {
    if (!FORM || frameJob === job || unlocked === "sub") return;
    frameJob = job;
    var box = $("qform"); box.innerHTML = "";
    var u = new URL(BH + "/v3/forms/" + FORM);
    u.searchParams.set("layout", "slim");
    u.searchParams.set("utm_source", "quiz"); u.searchParams.set("utm_medium", "website"); u.searchParams.set("utm_campaign", "quiz-" + job);
    u.searchParams.set("referrer", encodeURIComponent(location.origin + location.pathname));
    wrap = document.createElement("div"); wrap.className = "qframe";
    qIframe = document.createElement("iframe");
    qIframe.src = u.href; qIframe.title = "Email signup"; qIframe.setAttribute("frameborder", "0"); qIframe.setAttribute("scrolling", "no");
    qIframe.style.cssText = "width:100%;height:2000px;border:0;display:block;background:transparent";
    wrap.appendChild(qIframe); box.appendChild(wrap);
    clearTimeout(fallbackTimer);
    fallbackTimer = setTimeout(function () { if (wrap) { wrap.classList.add("qready"); qIframe.style.height = "350px"; } $("qalt").classList.add("qshow"); }, 7000);
  }
  window.addEventListener("message", function (e) {
    if (e.origin !== BH) return;
    var m = e.data || {};
    // A signup in any beehiiv form on this page (ours or the footer one) unlocks the stack.
    if (m.type === "beehiiv:submitted" && (!qIframe || e.source !== qIframe.contentWindow)) { if (unlocked !== "sub") { try { localStorage.setItem("uts_sub", "1"); } catch (x) {} track("/quiz/signup/"); if (cur) reveal("sub"); } return; }
    if (!qIframe || e.source !== qIframe.contentWindow) return;
    if (m.type === "beehiiv:child-loaded") {
      clearTimeout(fallbackTimer); qIframe.style.height = "2000px";
      requestAnimationFrame(function () { qIframe.contentWindow.postMessage({ type: "beehiiv:parent-loaded", payload: { handlesRedirect: true } }, "*"); });
    } else if (m.type === "beehiiv:styles") {
      var h = m.payload && parseFloat(m.payload.height);
      if (h > 20) { qIframe.style.height = m.payload.height; wrap.classList.add("qready"); }
    } else if (m.type === "beehiiv:challenge") {
      if (m.payload && m.payload.height) qIframe.style.height = m.payload.height; wrap.classList.add("qready");
    } else if (m.type === "beehiiv:challenge-resolved") {
      qIframe.style.height = "2000px"; qIframe.contentWindow.postMessage({ type: "beehiiv:resize" }, "*");
    } else if (m.type === "beehiiv:submitted" || m.type === "beehiiv:success-toast" || m.type === "beehiiv:redirect") {
      if (unlocked === "sub") return;
      try { localStorage.setItem("uts_sub", "1"); } catch (x) {}
      if (PUB) document.cookie = "bhv_" + PUB + "_subscribed=" + Date.now() + "; path=/; max-age=" + 365 * 86400;
      track("/quiz/signup/");
      if (cur) { reveal("sub"); $("qfull").scrollIntoView({ behavior: "smooth", block: "start" }); }
    }
  });
  // ---- slim sticky bar (mobile only via CSS) while results are locked and the form is off screen
  var bar = $("qsticky"), gateSeen = true, io = null;
  function stickyOn() {
    if (!bar || !("IntersectionObserver" in window)) return;
    if (!io) io = new IntersectionObserver(function (en) { gateSeen = en[0].isIntersecting; bar.hidden = gateSeen || !!unlocked || res.hidden; }, { threshold: 0.2 });
    io.observe($("qgate"));
  }
  function stickyOff() { if (bar) bar.hidden = true; if (io) io.disconnect(); }
  if (bar) bar.querySelector("button").addEventListener("click", function () { $("qgate").scrollIntoView({ behavior: "smooth", block: "center" }); });
  readHash();
  if (st.r && st.j && st.b) { fromHash = !!st.s; setStarted(); }
  render();
})();
