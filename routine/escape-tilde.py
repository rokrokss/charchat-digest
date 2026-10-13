#!/usr/bin/env python3
"""폴더 아래 모든 .md 파일의 물결표(~)를 \\~로 이스케이프해 GitHub에서 취소선으로 렌더링되지 않게 한다.
코드 블록·인라인 코드 안은 건드리지 않고, 이미 이스케이프된 것은 그대로 둔다 — 여러 번 돌려도 결과가 같다."""
import os
import re
import sys

FENCE = re.compile(r"^\s*(`{3,}|~{3,})")


def fix_line(line):
    parts = re.split(r"(`+[^`]*`+)", line)  # 홀수 번째 조각이 인라인 코드
    return "".join(p if i % 2 else re.sub(r"(?<!\\)~", r"\\~", p) for i, p in enumerate(parts))


def fix(text):
    out, fence = [], None
    for line in text.split("\n"):
        m = FENCE.match(line)
        if fence:
            if m and m.group(1)[0] == fence[0] and len(m.group(1)) >= len(fence):
                fence = None
            out.append(line)
        elif m:
            fence = m.group(1)
            out.append(line)
        elif re.match(r"( {4}|\t)", line):  # 들여쓴 코드 블록일 수 있다
            out.append(line)
        else:
            out.append(fix_line(line))
    return "\n".join(out)


changed = 0
for root, dirs, files in os.walk(sys.argv[1]):
    dirs[:] = [d for d in dirs if d != ".git"]
    for name in files:
        if name.endswith(".md"):
            path = os.path.join(root, name)
            with open(path, encoding="utf-8") as f:
                text = f.read()
            new = fix(text)
            if new != text:
                with open(path, "w", encoding="utf-8") as f:
                    f.write(new)
                changed += 1
print(f"물결표 이스케이프: {changed}개 파일 수정")
