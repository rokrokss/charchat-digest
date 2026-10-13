#!/bin/bash
# 캐릭터챗 커뮤니티 일일 다이제스트 — launchd가 매일 아침 실행
export PATH="/Users/rokrokss/.local/bin:/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin"
ROUTINE_DIR="/Users/rokrokss/.claude/routines"
LOG="$ROUTINE_DIR/logs/charchat-digest-$(date +%Y%m%d).log"

cd "$ROUTINE_DIR" || exit 1
echo "=== run $(date '+%Y-%m-%d %H:%M:%S') ===" >> "$LOG"

cat "$ROUTINE_DIR/charchat-digest-prompt.md" | /Users/rokrokss/.local/bin/claude -p \
  --allowedTools "Bash(curl:*)" "Bash(osascript:*)" "Bash(date:*)" "Bash(python3:*)" "WebFetch" "Read" "Write" "Edit" "PushNotification" "ToolSearch" \
  >> "$LOG" 2>&1

echo "=== exit $? $(date '+%Y-%m-%d %H:%M:%S') ===" >> "$LOG"

# 마크다운으로 렌더링해 비공개 GitHub 저장소(rokrokss/charchat-digest)에 푸시
bash "$ROUTINE_DIR/publish-md.sh" >> "$LOG" 2>&1

# 30일 지난 로그 정리
find "$ROUTINE_DIR/logs" -name "charchat-digest-*.log" -mtime +30 -delete
