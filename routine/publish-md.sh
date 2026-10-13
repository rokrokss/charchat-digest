#!/bin/bash
# 운영 파일 사본과 마크다운 다이제스트를 비공개 저장소(~/charchat-digest)에 커밋·푸시 — charchat-digest.sh가 수집 후 호출
export PATH="/Users/rokrokss/.local/bin:/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin"
SRC="/Users/rokrokss/.claude/routines"
REPO="/Users/rokrokss/charchat-digest"

echo "=== publish $(date '+%Y-%m-%d %H:%M:%S') ==="
# 운영 원본은 SRC — 저장소의 routine/·launchd/·data/는 매번 덮어쓰는 사본이다
mkdir -p "$REPO/routine/memory" "$REPO/launchd" "$REPO/data"
cp "$SRC"/{charchat-digest.sh,charchat-digest-prompt.md,merge-items.py,render-md.py,publish-md.sh,digest-server.py} "$REPO/routine/"
cp /Users/rokrokss/.claude/projects/-Users-rokrokss--claude-routines/memory/*.md "$REPO/routine/memory/"
cp /Users/rokrokss/Library/LaunchAgents/com.rokrokss.charchat-digest{,-web}.plist "$REPO/launchd/"
cp "$SRC"/{digest-items.jsonl,charchat-digest.md} "$REPO/data/"
python3 "$SRC/render-md.py" || exit 1
cd "$REPO" || exit 1
git add -A
# 변경이 없으면 커밋하지 않는다. 푸시가 실패해도(오프라인 등) 커밋은 남고 다음 실행 때 같이 올라간다
git diff --cached --quiet || git commit -q -m "digest $(date '+%Y-%m-%d')"
git push -q origin main 2>&1 || echo "push 실패 — 다음 실행 때 재시도"
