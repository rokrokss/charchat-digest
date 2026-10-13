#!/usr/bin/env python3
"""today-items.json(오늘 항목 배열)을 digest-items.jsonl에 병합.
같은 날짜의 기존 항목은 교체, 과거 날짜는 보존. 스키마 검증 포함."""
import json
import os
import sys

DIR = os.path.expanduser("~/.claude/routines")
JSONL = os.path.join(DIR, "digest-items.jsonl")
TODAY = os.path.join(DIR, "today-items.json")

CATEGORIES = {"플랫폼 동향", "신기능·업데이트", "유저 니즈", "제작 트렌드", "영상 제작", "기타"}
IMPORTANCE = {"high", "medium", "low"}

with open(TODAY, encoding="utf-8") as f:
    new_items = json.load(f)
assert isinstance(new_items, list) and new_items, "today-items.json은 비어있지 않은 배열이어야 함"

for it in new_items:
    for key in ("date", "category", "title", "summary", "source"):
        assert isinstance(it.get(key), str) and it[key], f"필수 필드 누락: {key} — {it.get('title')}"
    assert it["category"] in CATEGORIES, f"카테고리 오류: {it['category']}"
    it.setdefault("importance", "medium")
    assert it["importance"] in IMPORTANCE, f"중요도 오류: {it['importance']}"
    it.setdefault("implication", None)
    it.setdefault("platforms", [])
    it.setdefault("links", [])
    assert all(isinstance(l, dict) and l.get("url") for l in it["links"]), f"links 형식 오류: {it['title']}"

# 롤업(주간·월간 요약) 항목은 날짜 교체 대상에서 제외 — 괄호 접두([YYYY년 M월 N주차 동향] 등)
# 기준으로 교체해, 헤드라인이 매일 달라져도 같은 기간 롤업이 중복되지 않게 한다
import re
ROLLUP = re.compile(r"^\[\d{4}년 \d+월")
rollup_key = lambda title: title.split("]")[0] + "]"
new_dates = {it["date"] for it in new_items if not ROLLUP.match(it["title"])}
new_rollup_keys = {rollup_key(it["title"]) for it in new_items if ROLLUP.match(it["title"])}
old_lines = []
canon = {"artcraft": "ArtCraft", "nomi": "Nomi"}  # 플랫폼 태그 표기 통일 (소문자 키 → 정본)
if os.path.exists(JSONL):
    with open(JSONL, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            old = json.loads(line)
            for p in old.get("platforms", []):
                canon.setdefault(p.lower(), p)
            if ROLLUP.match(old.get("title", "")):
                if rollup_key(old["title"]) not in new_rollup_keys:
                    old_lines.append(line)
            elif old.get("date") not in new_dates:
                old_lines.append(line)

for it in new_items:
    seen, normed = set(), []
    for p in it["platforms"]:
        p = canon.setdefault(p.lower(), p)
        if p not in seen:
            seen.add(p)
            normed.append(p)
    it["platforms"] = normed

tmp = JSONL + ".tmp"
with open(tmp, "w", encoding="utf-8") as f:
    for line in old_lines:
        f.write(line + "\n")
    for it in new_items:
        f.write(json.dumps(it, ensure_ascii=False) + "\n")
os.replace(tmp, JSONL)
os.remove(TODAY)
print(f"병합 완료: 신규 {len(new_items)}개 (날짜 {sorted(new_dates)}), 보존 {len(old_lines)}개")
