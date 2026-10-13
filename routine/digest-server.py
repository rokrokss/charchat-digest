#!/usr/bin/env python3
"""캐릭터챗 인텔리전스 대시보드 — launchd가 상시 실행 (http://localhost:18787)"""
import datetime
import json
import os
import subprocess
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

PORT = 18787
DIR = os.path.expanduser("~/.claude/routines")
ITEMS = os.path.join(DIR, "digest-items.jsonl")
LEGACY_MD = os.path.join(DIR, "charchat-digest.md")
JOB = f"gui/{os.getuid()}/com.rokrokss.charchat-digest"

PAGE = r"""<!doctype html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>📡 캐릭터챗 인텔리전스</title>
<style>
  :root {
    color-scheme: light dark;
    --bg:#faf9f5; --card:#ffffff; --text:#1c1c1a; --muted:#6b6b66; --line:#e4e2da;
    --chip:#efede6; --chip-on:#1c1c1a; --chip-on-text:#faf9f5; --callout:#f4f1e8;
    --c-trend:#2563eb; --c-feature:#7c3aed; --c-needs:#d97706; --c-craft:#059669;
    --c-video:#db2777; --c-etc:#6b7280;
  }
  @media (prefers-color-scheme: dark) {
    :root {
      --bg:#161618; --card:#1f1f23; --text:#e8e8e6; --muted:#9a9a94; --line:#31313a;
      --chip:#2a2a30; --chip-on:#e8e8e6; --chip-on-text:#161618; --callout:#26262c;
      --c-trend:#60a5fa; --c-feature:#a78bfa; --c-needs:#fbbf24; --c-craft:#34d399;
      --c-video:#f472b6; --c-etc:#9ca3af;
    }
  }
  * { box-sizing: border-box; }
  body { margin:0; background:var(--bg); color:var(--text);
         font: 14px/1.6 -apple-system, "Apple SD Gothic Neo", sans-serif; }
  header { position:sticky; top:0; z-index:10; background:var(--bg);
           border-bottom:1px solid var(--line); padding:14px 20px 10px; }
  .hrow { max-width:860px; margin:0 auto; display:flex; gap:10px; align-items:center; flex-wrap:wrap; }
  h1 { font-size:16px; margin:0 auto 0 0; }
  .meta { font-size:12px; color:var(--muted); }
  button.run { font:12px inherit; padding:5px 12px; border-radius:8px; cursor:pointer;
               border:1px solid var(--line); background:var(--card); color:var(--text); }
  button.run:hover { border-color:var(--muted); }
  input[type=search] { font:13px inherit; padding:6px 10px; border-radius:8px;
                       border:1px solid var(--line); background:var(--card); color:var(--text); width:180px; }
  .tabs { max-width:860px; margin:10px auto 0; display:flex; gap:4px; }
  .tab { font-size:13px; padding:6px 16px; border-radius:8px 8px 0 0; cursor:pointer; user-select:none;
         color:var(--muted); border:1px solid transparent; border-bottom:none; }
  .tab.on { color:var(--text); font-weight:600; background:var(--card); border-color:var(--line); }
  .chips { max-width:860px; margin:8px auto 0; display:flex; gap:6px; flex-wrap:wrap; }
  .chip { font-size:12px; padding:4px 11px; border-radius:999px; cursor:pointer; user-select:none;
          background:var(--chip); border:1px solid transparent; }
  .chip.on { background:var(--chip-on); color:var(--chip-on-text); }
  .chip .n { opacity:.55; margin-left:4px; }
  main { max-width:860px; margin:0 auto; padding:10px 20px 90px; }
  .day { margin-top:26px; }
  .dayhead { display:flex; align-items:baseline; gap:10px; margin-bottom:10px; }
  .dayhead h2 { font-size:15px; margin:0; }
  .dayhead .cnt { font-size:12px; color:var(--muted); }
  .card { background:var(--card); border:1px solid var(--line); border-radius:12px;
          padding:14px 16px; margin-bottom:10px; }
  .card.low { padding:9px 16px; }
  .top { display:flex; gap:8px; align-items:center; flex-wrap:wrap; }
  .badge { font-size:11px; font-weight:600; padding:2px 8px; border-radius:6px; color:#fff; }
  .dot { width:8px; height:8px; border-radius:50%; flex:none; }
  .dot.high { background:#e11d48; box-shadow:0 0 6px #e11d4888; }
  .dot.medium { background:#f59e0b; }
  .dot.low { background:var(--muted); opacity:.5; }
  .title { font-weight:650; font-size:14px; }
  .card.low .title { font-weight:500; font-size:13px; }
  .tags { display:flex; gap:4px; flex-wrap:wrap; margin-left:auto; }
  .tag { font-size:11px; color:var(--muted); background:var(--chip); padding:1px 8px; border-radius:999px; }
  .summary { margin-top:7px; }
  .card.low .summary { color:var(--muted); font-size:13px; margin-top:3px; }
  .imp { margin-top:8px; padding:8px 12px; background:var(--callout); border-radius:8px; font-size:13px; }
  .imp b { color:var(--c-needs); }
  .foot { margin-top:8px; display:flex; gap:10px; flex-wrap:wrap; font-size:12px; }
  .foot a, .hl a { color:var(--c-trend); text-decoration:none; }
  .foot a:hover, .hl a:hover { text-decoration:underline; }
  .src { color:var(--muted); margin-left:auto; }
  .empty { color:var(--muted); text-align:center; padding:60px 0; }
  /* 리포트 뷰 */
  .rcard { background:var(--card); border:1px solid var(--line); border-radius:12px;
           padding:16px 18px; margin-top:18px; }
  .rhead { display:flex; align-items:baseline; gap:10px; flex-wrap:wrap; }
  .rhead h2 { font-size:15px; margin:0; }
  .rhead .cnt { font-size:12px; color:var(--muted); }
  .catbar { display:flex; height:10px; border-radius:5px; overflow:hidden; margin:10px 0 4px; }
  .catlegend { display:flex; gap:10px; flex-wrap:wrap; font-size:11px; color:var(--muted); margin-bottom:8px; }
  .catlegend i { display:inline-block; width:8px; height:8px; border-radius:2px; margin-right:4px; }
  .rollup { padding:9px 12px; background:var(--callout); border-radius:8px; font-size:13px; margin-top:8px; }
  .rollup b { display:block; margin-bottom:2px; }
  .hl { margin-top:10px; }
  .hl-row { display:flex; gap:8px; align-items:baseline; padding:3px 0; font-size:13px; }
  .hl-row .dot { position:relative; top:0; }
  .sub { font-size:12px; color:var(--muted); margin-top:10px; }
</style>
</head>
<body>
<header>
  <div class="hrow">
    <h1>📡 캐릭터챗 인텔리전스</h1>
    <span class="meta" id="meta"></span>
    <input type="search" id="q" placeholder="검색 (제목·본문·플랫폼)">
    <button class="run" id="runbtn" onclick="runNow()">지금 수집 실행</button>
  </div>
  <div class="tabs" id="tabs"></div>
  <div class="chips" id="catChips"></div>
  <div class="chips" id="subChips"></div>
</header>
<main id="main"><div class="empty">불러오는 중…</div></main>
<script>
const CAT_COLOR = {"플랫폼 동향":"var(--c-trend)","신기능·업데이트":"var(--c-feature)","유저 니즈":"var(--c-needs)",
                   "제작 트렌드":"var(--c-craft)","영상 제작":"var(--c-video)","기타":"var(--c-etc)"};
const CATS = Object.keys(CAT_COLOR);
const IMP_ORD = {high: 0, medium: 1, low: 2};
const VIEWS = [["feed","일별 피드"],["week","주간 리포트"],["month","월간 리포트"]];
let items = [], selCats = new Set(), selPlat = null, selImp = null, view = "feed";

const esc = s => (s ?? '').replace(/[&<>"]/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
const isRollup = i => /^\[\d{4}년 \d+월/.test(i.title);
const isWeekRollup = i => isRollup(i) && i.title.includes('주차');
const dow = d => ['일','월','화','수','목','금','토'][new Date(d + 'T00:00:00').getDay()];
const md = d => `${+d.slice(5,7)}/${+d.slice(8,10)}`;

async function load() {
  const [data, st] = await Promise.all([
    fetch('/items').then(r => r.json()),
    fetch('/status').then(r => r.json()).catch(() => ({}))
  ]);
  items = data;
  document.getElementById('meta').textContent =
    `${items.length}건 누적 · 마지막 갱신 ${st.mtime ?? '-'}`;
  update();
}

function chip(label, n, on, cb, color) {
  const el = document.createElement('span');
  el.className = 'chip' + (on ? ' on' : '');
  el.innerHTML = (color && !on ? `<span style="color:${color}">●</span> ` : '') + esc(label) +
                 (n != null ? `<span class="n">${n}</span>` : '');
  el.onclick = cb;
  return el;
}

function renderTabs() {
  const t = document.getElementById('tabs'); t.replaceChildren();
  VIEWS.forEach(([v, label]) => {
    const el = document.createElement('span');
    el.className = 'tab' + (view === v ? ' on' : '');
    el.textContent = label;
    el.onclick = () => { view = v; update(); };
    t.append(el);
  });
  const showFilters = view === 'feed';
  document.getElementById('catChips').style.display = showFilters ? '' : 'none';
  document.getElementById('subChips').style.display = showFilters ? '' : 'none';
  document.getElementById('q').style.display = showFilters ? '' : 'none';
}

function renderChips() {
  const cc = document.getElementById('catChips'); cc.replaceChildren();
  const counts = {};
  items.forEach(i => counts[i.category] = (counts[i.category] || 0) + 1);
  cc.append(chip('전체', items.length, selCats.size === 0, () => { selCats.clear(); update(); }));
  CATS.forEach(c => cc.append(chip(c, counts[c] || 0, selCats.has(c),
    () => { selCats.has(c) ? selCats.delete(c) : selCats.add(c); update(); }, CAT_COLOR[c])));
  const sc = document.getElementById('subChips'); sc.replaceChildren();
  [['high','🔴 high'],['medium','🟡 medium'],['low','⚪ low']].forEach(([v, l]) =>
    sc.append(chip(l, null, selImp === v, () => { selImp = selImp === v ? null : v; update(); })));
  [...new Set(items.flatMap(i => i.platforms || []))].sort().forEach(p =>
    sc.append(chip(p, null, selPlat === p, () => { selPlat = selPlat === p ? null : p; update(); })));
}

function update() {
  renderTabs();
  if (view === 'feed') { renderChips(); renderFeed(); }
  else renderReport(view);
}

function renderFeed() {
  const q = document.getElementById('q').value.trim().toLowerCase();
  const vis = items.filter(i =>
    (selCats.size === 0 || selCats.has(i.category)) &&
    (!selImp || i.importance === selImp) &&
    (!selPlat || (i.platforms || []).includes(selPlat)) &&
    (!q || (i.title + i.summary + (i.platforms || []).join(' ')).toLowerCase().includes(q)));
  const main = document.getElementById('main'); main.replaceChildren();
  if (!vis.length) { main.innerHTML = '<div class="empty">조건에 맞는 항목이 없습니다</div>'; return; }
  const byDate = {};
  vis.forEach(i => (byDate[i.date] ??= []).push(i));
  Object.keys(byDate).sort().reverse().forEach(date => {
    const day = document.createElement('div'); day.className = 'day';
    day.innerHTML = `<div class="dayhead"><h2>${date} (${dow(date)})</h2><span class="cnt">${byDate[date].length}건</span></div>`;
    byDate[date].sort((a, b) => IMP_ORD[a.importance] - IMP_ORD[b.importance]).forEach(i => day.append(card(i)));
    main.append(day);
  });
}

function card(i) {
  const c = document.createElement('div');
  c.className = 'card' + (i.importance === 'low' ? ' low' : '');
  const tags = (i.platforms || []).map(p => `<span class="tag">${esc(p)}</span>`).join('');
  const links = (i.links || []).map(l => `<a href="${esc(l.url)}" target="_blank" rel="noopener">${esc(l.label || '원글')} ↗</a>`).join('');
  c.innerHTML = `
    <div class="top">
      <span class="dot ${esc(i.importance)}"></span>
      <span class="badge" style="background:${CAT_COLOR[i.category] || 'var(--c-etc)'}">${esc(i.category)}</span>
      <span class="title">${esc(i.title)}</span>
      <span class="tags">${tags}</span>
    </div>
    <div class="summary">${esc(i.summary)}</div>
    ${i.implication ? `<div class="imp"><b>💡 시사점</b> · ${esc(i.implication)}</div>` : ''}
    <div class="foot">${links}<span class="src">${esc(i.source)}</span></div>`;
  return c;
}

function periodKey(date, mode) {
  if (mode === 'month') return date.slice(0, 7);
  const d = new Date(date + 'T00:00:00');
  d.setDate(d.getDate() - (d.getDay() + 6) % 7);  // 그 주 월요일
  return d.toISOString().slice(0, 10);
}

function periodLabel(key, mode) {
  if (mode === 'month') return `${key.slice(0,4)}년 ${+key.slice(5,7)}월`;
  const start = new Date(key + 'T00:00:00');
  const end = new Date(start); end.setDate(end.getDate() + 6);
  const e = end.toISOString().slice(0, 10);
  return `${md(key)} (월) ~ ${md(e)} (일)`;
}

function renderReport(mode) {
  const main = document.getElementById('main'); main.replaceChildren();
  const groups = {};
  items.forEach(i => (groups[periodKey(i.date, mode)] ??= []).push(i));
  const keys = Object.keys(groups).sort().reverse();
  if (!keys.length) { main.innerHTML = '<div class="empty">데이터가 없습니다</div>'; return; }

  keys.forEach(key => {
    const g = groups[key];
    const rollups = mode === 'month'
      ? g.filter(i => isRollup(i) && !isWeekRollup(i))
      : g.filter(isWeekRollup);
    const rest = g.filter(i => !isRollup(i));

    // 카테고리 분포 바
    const cc = {};
    rest.forEach(i => cc[i.category] = (cc[i.category] || 0) + 1);
    const total = rest.length || 1;
    const bar = CATS.filter(c => cc[c]).map(c =>
      `<div style="width:${100 * cc[c] / total}%;background:${CAT_COLOR[c]}" title="${esc(c)} ${cc[c]}건"></div>`).join('');
    const legend = CATS.filter(c => cc[c]).map(c =>
      `<span><i style="background:${CAT_COLOR[c]}"></i>${esc(c)} ${cc[c]}</span>`).join('');

    // 플랫폼 상위
    const pc = {};
    g.forEach(i => (i.platforms || []).forEach(p => pc[p] = (pc[p] || 0) + 1));
    const topPlat = Object.entries(pc).sort((a, b) => b[1] - a[1]).slice(0, 8)
      .map(([p, n]) => `<span class="tag">${esc(p)} ${n}</span>`).join(' ');

    // 하이라이트 (high 전부 + medium, 주간은 medium 전부 / 월간은 medium 상위 5)
    const his = rest.filter(i => i.importance === 'high');
    let meds = rest.filter(i => i.importance === 'medium');
    if (mode === 'month') meds = meds.slice(0, 5);
    const hlRow = i => {
      const url = (i.links || [])[0]?.url;
      const t = url ? `<a href="${esc(url)}" target="_blank" rel="noopener">${esc(i.title)}</a>` : esc(i.title);
      return `<div class="hl-row"><span class="dot ${esc(i.importance)}"></span>
        <span class="badge" style="background:${CAT_COLOR[i.category]}">${esc(i.category)}</span> ${t}</div>`;
    };

    const r = document.createElement('div');
    r.className = 'rcard';
    r.innerHTML = `
      <div class="rhead"><h2>${periodLabel(key, mode)}</h2><span class="cnt">${rest.length}건${rollups.length ? ' + 월간요약' : ''}</span></div>
      <div class="catbar">${bar}</div>
      <div class="catlegend">${legend}</div>
      ${topPlat ? `<div>${topPlat}</div>` : ''}
      ${rollups.map(i => `<div class="rollup"><b>${esc(i.title)}</b>${esc(i.summary)}</div>`).join('')}
      ${(his.length || meds.length) ? `<div class="hl">${his.map(hlRow).join('')}${meds.map(hlRow).join('')}</div>` : ''}
      ${mode === 'month' && rest.filter(i => i.importance === 'medium').length > 5
        ? `<div class="sub">medium ${rest.filter(i => i.importance === 'medium').length - 5}건 더 있음 — 일별 피드에서 확인</div>` : ''}`;
    main.append(r);
  });
}

async function runNow() {
  const btn = document.getElementById('runbtn');
  btn.disabled = true; btn.textContent = '실행 중… (수 분 소요)';
  await fetch('/run', {method: 'POST'});
  setTimeout(() => { btn.disabled = false; btn.textContent = '지금 수집 실행'; }, 60000);
}

document.getElementById('q').addEventListener('input', () => { if (view === 'feed') renderFeed(); });
load();
setInterval(load, 60000);
</script>
</body>
</html>"""


class Handler(BaseHTTPRequestHandler):
    def _send(self, code, body, ctype="text/html; charset=utf-8"):
        data = body.encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        if self.path == "/":
            self._send(200, PAGE)
        elif self.path == "/items":
            out = []
            if os.path.exists(ITEMS):
                with open(ITEMS, encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if line:
                            try:
                                out.append(json.loads(line))
                            except json.JSONDecodeError:
                                pass
            self._send(200, json.dumps(out, ensure_ascii=False), "application/json; charset=utf-8")
        elif self.path == "/digest.md":
            try:
                with open(LEGACY_MD, encoding="utf-8") as f:
                    self._send(200, f.read(), "text/markdown; charset=utf-8")
            except FileNotFoundError:
                self._send(404, "not found", "text/plain")
        elif self.path == "/status":
            mtime = None
            if os.path.exists(ITEMS):
                mtime = datetime.datetime.fromtimestamp(os.path.getmtime(ITEMS)).strftime("%Y-%m-%d %H:%M")
            self._send(200, json.dumps({"mtime": mtime}), "application/json")
        else:
            self._send(404, "not found", "text/plain")

    def do_POST(self):
        if self.path == "/run":
            subprocess.Popen(["launchctl", "kickstart", JOB])
            self._send(200, json.dumps({"ok": True}), "application/json")
        else:
            self._send(404, "not found", "text/plain")

    def log_message(self, *args):
        pass


if __name__ == "__main__":
    ThreadingHTTPServer(("127.0.0.1", PORT), Handler).serve_forever()
