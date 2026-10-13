# 운영

## launchd 작업

| 라벨 | 실행 | 주기 |
|---|---|---|
| `com.rokrokss.charchat-digest` | `/bin/bash ~/.claude/routines/charchat-digest.sh` | 매일 09:05 |
| `com.rokrokss.charchat-digest-web` | `/usr/bin/python3 ~/.claude/routines/digest-server.py` | 로그인할 때 시작하고, 죽으면 다시 띄운다 |

- **09:05는 시스템 시간대 기준이다.** 2026-10-13 저녁에 시스템 시간대가 Asia/Seoul로 바뀌었다. 그전까지는 실제로 KST 14:05쯤 돌았다.
- **Mac이 잠들어 있으면** 깨어날 때 실행된다. 꺼져 있었으면 그날은 건너뛴다.

상태는 다음 명령으로 확인한다. `runs`와 `last exit code`는 launchd가 다시 로드된 뒤(재부팅 등)부터 센다.

```bash
launchctl print gui/$(id -u)/com.rokrokss.charchat-digest
```

**즉시 실행:** 대시보드의 "지금 수집 실행" 버튼은 `launchctl kickstart gui/<uid>/com.rokrokss.charchat-digest`를 실행한다.
- 한 번에 15분 안팎 걸린다.
- 같은 날 다시 돌리면 그날 항목이 새 결과로 교체된다.

대시보드가 살아 있는지는 다음으로 확인한다. 응답의 `mtime`이 jsonl의 마지막 갱신 시각이다.

```bash
curl -s localhost:18787/status
```

## 로그

하루치 실행 기록은 `~/.claude/routines/logs/charchat-digest-YYYYMMDD.log` 하나에 남고, 30일이 지나면 지워진다.

```
=== run <시작 시각> ===
<claude의 최종 메시지: 오늘의 주요 소식 요약>
=== exit <claude 종료 코드> <끝난 시각> ===
=== publish <시각> ===
렌더링 완료: 일별 N개, 롤업 N개, 최신 YYYY-MM-DD
```

claude가 실행 중에 어떤 도구를 불렀는지는 이 로그에 없다. 전체 대화 기록은 `~/.claude/projects/-Users-rokrokss--claude-routines/<세션 id>.jsonl`에 있다.

## 실패 감지

**종료 코드만 믿으면 안 된다.** 2026-10-07처럼 실패했는데 exit 0이 남은 적이 있다. 대신 다음 둘 중 하나로 확인한다.
- GitHub [digest/README.md](../digest/README.md)의 "최신" 날짜가 오늘인지 본다.
- 로그에 `렌더링 완료 … 최신 <오늘>`이 있는지 본다.

```bash
grep -A3 '=== publish' ~/.claude/routines/logs/charchat-digest-$(date +%Y%m%d).log
```

지금까지 겪은 실패는 다음과 같다. 빠진 날짜는 다시 채울 수 없다(수집 범위가 최근 28시간뿐이다).

| 날짜 | 로그 | 원인 |
|---|---|---|
| 2026-09-11 ~ 09-24 | `Failed to authenticate: OAuth session expired and could not be refreshed`, exit 1 | Claude Code 로그인 만료. 9/25부터 정상. 9/11·9/12 로그는 보관 기한이 지나 지워졌지만, 그 날짜 항목도 없다 |
| 2026-10-07 | `Background tasks still running after 600s; terminating.`, **exit 0** | `claude -p`에서 백그라운드 서브에이전트가 600초에 강제 종료돼 병합까지 가지 못했다. 이후 루틴 메모에 "서브에이전트를 쓰지 말거나 포그라운드로 돌릴 것"이 기록됐다 |
| 2026-10-08 | `API Error: Can't reach the API server … (ENOTFOUND)`, exit 1 | 네트워크·DNS 문제. 재시도 장치는 없다 |

PushNotification은 Remote Control이 꺼져 있으면 전송되지 않는다. 알림은 macOS 알림만 믿으면 된다.

## GitHub 푸시

`publish-md.sh`는 수집 성공 여부와 상관없이 매 실행 뒤 돈다. 순서는 이렇다.
1. 사본을 복사한다.
2. 마크다운을 렌더링한다.
3. 변경이 있을 때만 `digest YYYY-MM-DD`로 커밋한다.
4. 푸시한다.

**인증 순서:**
1. git의 macOS 키체인 자격 증명이 먼저 쓰인다.
2. 저장소 로컬 설정 `credential.helper = !/opt/homebrew/bin/gh auth git-credential`이 예비다. 전역 git 설정은 건드리지 않는다.

2026-10-14에 launchd 환경에서 푸시 인증과 커밋 작성자 정보가 정상인 것을 확인했다.

**푸시가 실패하면:**
- **네트워크 문제:** 로그에 `push 실패 — 다음 실행 때 재시도`가 남는다. 커밋은 로컬에 남아 있다가 다음 실행 때 같이 올라간다.
- **키체인 자격 증명이 만료됐을 때:** 그날 푸시만 실패한다. git이 그 자격 증명을 지우므로, 다음 실행은 `gh`로 인증한다.

## 코드 수정

1. `~/.claude/routines/`의 원본을 고친다. 저장소의 `routine/`은 다음 게시 때 덮어써진다.
2. `digest-server.py`를 고쳤다면 대시보드를 다시 띄워야 반영된다. launchd가 KeepAlive로 관리하므로 다음 명령으로 재시작한다(이 명령은 아직 직접 실행해 보지 않았다).
   ```bash
   launchctl kickstart -k gui/$(id -u)/com.rokrokss.charchat-digest-web
   ```
3. 다음 정기 실행을 기다리거나, 바로 올린다.
   ```bash
   bash ~/.claude/routines/publish-md.sh
   ```

수집 지침(`charchat-digest-prompt.md`)을 고칠 때는 [collection.md](collection.md)를 먼저 본다. 실제 수집 방법은 루틴 메모 쪽에 있으므로 두 곳이 서로 어긋나지 않게 해야 한다.

## 복구 (이 Mac을 잃었을 때)

**아직 실행해 본 적 없는 절차다.** 스크립트와 plist에 `/Users/rokrokss` 경로가 박혀 있어서, 사용자 이름이 다르면 경로를 고쳐야 한다.

1. 이 저장소를 `~/charchat-digest`에 clone한다.
2. 파일을 원래 자리로 복사한다.
   - `routine/`의 스크립트·지침 6개와 `data/`의 파일 2개 → `~/.claude/routines/`. 같은 폴더에 `logs/`도 만든다.
   - `routine/memory/`의 파일 → `~/.claude/projects/-Users-rokrokss--claude-routines/memory/`
   - `launchd/*.plist` → `~/Library/LaunchAgents/`
3. plist를 각각 등록한다.
   ```bash
   launchctl bootstrap gui/$(id -u) ~/Library/LaunchAgents/com.rokrokss.charchat-digest.plist
   launchctl bootstrap gui/$(id -u) ~/Library/LaunchAgents/com.rokrokss.charchat-digest-web.plist
   ```
4. 필요한 것이 다 있는지 확인한다.
   - `~/.local/bin/claude`에 Claude Code가 설치돼 있고 로그인돼 있어야 한다.
   - `gh`가 로그인돼 있어야 한다. 저장소 로컬 `credential.helper`도 다시 설정한다.
   - python3가 있어야 한다. 표준 라이브러리만 쓴다.
