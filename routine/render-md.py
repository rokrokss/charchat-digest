#!/usr/bin/env python3
"""digest-items.jsonl을 마크다운으로 렌더링해 ~/charchat-digest/digest(비공개 GitHub 저장소)에 쓴다.
매번 전체를 다시 만든다 — 같은 데이터면 같은 결과가 나와 커밋할 변경이 생기지 않는다."""
import collections
import datetime
import glob
import json
import os
import re

DIR = os.path.expanduser("~/.claude/routines")
JSONL = os.path.join(DIR, "digest-items.jsonl")
OUT = os.path.expanduser("~/charchat-digest/digest")
DAYS = os.path.join(OUT, "days")

ROLLUP = re.compile(r"^\[\d{4}년 \d+월")
IMP_ORD = {"high": 0, "medium": 1, "low": 2}
IMP_DOT = {"high": "🔴", "medium": "🟡", "low": "⚪"}
DOW = "월화수목금토일"


def esc(s):
    """GFM 서식으로 해석되지 않게 이스케이프 — 특히 '1~3장' 같은 물결표가 취소선이 되지 않게."""
    s = re.sub(r"([\\`*_~\[\]])", r"\\\1", s or "").replace("<", "&lt;")
    s = re.sub(r"^([#>+-])", r"\\\1", s)
    return re.sub(r"^(\d+)([.)])", r"\1\\\2", s)


def day_label(d):
    return f"{d} ({DOW[datetime.date.fromisoformat(d).weekday()]})"


def links(i):
    return " · ".join(f"[{esc(l.get('label') or '원글')}]({l['url']})" for l in i.get("links", []))


def item_md(i):
    meta = " · ".join([f"**{esc(i['category'])}**", *map(esc, i.get("platforms", [])), esc(i["source"])])
    out = [f"### {IMP_DOT.get(i['importance'], '')} {esc(i['title'])}", meta, "", esc(i["summary"])]
    if i.get("implication"):
        out += ["", f"> 💡 {esc(i['implication'])}"]
    if i.get("links"):
        out += ["", links(i)]
    return "\n".join(out) + "\n"


def rollup_md(i):
    out = [f"### {esc(i['title'])}", "", esc(i["summary"])]
    if i.get("links"):
        out += ["", links(i)]
    return "\n".join(out) + "\n"


def write(path, text):
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)


items = [json.loads(l) for l in open(JSONL, encoding="utf-8") if l.strip()]
rollups = [i for i in items if ROLLUP.match(i["title"])]
by_day = collections.defaultdict(list)
for i in items:
    if not ROLLUP.match(i["title"]):
        by_day[i["date"]].append(i)
for v in by_day.values():
    v.sort(key=lambda i: IMP_ORD.get(i["importance"], 3))

os.makedirs(DAYS, exist_ok=True)
for f in glob.glob(os.path.join(DAYS, "*.md")):
    os.remove(f)
for d, its in by_day.items():
    cnt = collections.Counter(i["importance"] for i in its)
    tally = " · ".join(f"{IMP_DOT[k]} {cnt[k]}" for k in IMP_ORD if cnt[k])
    body = "\n".join(item_md(i) for i in its)
    write(os.path.join(DAYS, f"{d}.md"),
          f"# {day_label(d)}\n\n{len(its)}건 · {tally} · [목록](../README.md)\n\n{body}")

weekly = sorted((i for i in rollups if "주차" in i["title"]), key=lambda i: i["date"], reverse=True)
monthly = sorted((i for i in rollups if "주차" not in i["title"]), key=lambda i: (i["date"], i["title"]), reverse=True)
write(os.path.join(OUT, "rollups.md"),
      "# 주간·월간 동향\n\n[목록](README.md)\n\n## 월간\n\n" + "\n".join(map(rollup_md, monthly))
      + "\n## 주간\n\n" + "\n".join(map(rollup_md, weekly)))

latest = max(by_day)
readme = ["# 캐릭터챗 다이제스트", "",
          f"최신 {day_label(latest)} · 누적 {len(items)}건 · 매일 로컬 루틴이 갱신 · [주간·월간 동향](rollups.md) · [프로젝트 설명](../README.md)", ""]
if weekly:
    readme += ["## 이번 주 동향", "", rollup_md(weekly[0])]
readme += ["## 날짜별", ""]
month = None
for d in sorted(by_day, reverse=True):
    if d[:7] != month:
        month = d[:7]
        readme += [f"### {int(d[:4])}년 {int(d[5:7])}월", ""]
    top = by_day[d][0]
    readme.append(f"- [{day_label(d)}](days/{d}.md) — {len(by_day[d])}건 · "
                  f"{IMP_DOT.get(top['importance'], '')} {esc(top['title'])}")
write(os.path.join(OUT, "README.md"), "\n".join(readme) + "\n")
print(f"렌더링 완료: 일별 {len(by_day)}개, 롤업 {len(rollups)}개, 최신 {latest}")
