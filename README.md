# charchat-digest

**👉 [다이제스트 보기](digest/README.md)** · [주간·월간 동향](digest/rollups.md)

이 루틴은 캐릭터챗 커뮤니티(아카라이브, 디시)와 AI 영상 제작 도구 레포(ArtCraft, Nomi)를 매일 훑는다. 제품을 만드는 입장에서 쓸모 있는 소식을 골라 구조화된 항목으로 쌓는다. 내 Mac에서만 도는 개인용 도구이고, 이 저장소는 비공개 백업이자 읽기용 사본이다.

## 동작 방식

```
launchd: com.rokrokss.charchat-digest (매일 09:05)
└─ charchat-digest.sh
   ├─ claude -p < charchat-digest-prompt.md   수집·선별·요약은 Claude Code가 한다
   │   ├─ 아카라이브, 디시, GitHub를 curl로 수집
   │   ├─ 오늘 항목을 today-items.json에 쓴다
   │   ├─ merge-items.py가 검증 후 digest-items.jsonl에 병합
   │   └─ macOS 알림
   └─ publish-md.sh                           정해진 후처리 (에이전트 권한 밖)
       ├─ 운영 파일 사본을 이 저장소로 복사
       ├─ render-md.py: jsonl → digest/*.md
       └─ 변경이 있을 때만 git commit, 그다음 push

launchd: com.rokrokss.charchat-digest-web (상시 실행)
└─ digest-server.py → http://localhost:18787   digest-items.jsonl을 읽는 대시보드
```

- 수집 대상과 실제 수집 방법은 [docs/collection.md](docs/collection.md)에 있다.
- 운영, 실패 감지, 코드 수정, 복구는 [docs/operations.md](docs/operations.md)에 있다.

## 원본과 사본

운영 원본은 이 저장소가 아니라 `~/.claude/routines/`에 있다.

- 이 저장소의 `routine/`, `launchd/`, `data/`는 `publish-md.sh`가 매 실행 뒤 덮어쓰는 사본이다. 코드는 원본 쪽에서 고친다.
- `digest/`는 `render-md.py`가 매번 jsonl로부터 새로 만든다.

| 저장소 경로 | 운영 원본 | 역할 |
|---|---|---|
| `routine/charchat-digest.sh` | `~/.claude/routines/` | launchd가 실행하는 진입점 |
| `routine/charchat-digest-prompt.md` | 〃 | Claude에게 주는 수집 지침 |
| `routine/merge-items.py` | 〃 | `today-items.json` 검증·병합 |
| `routine/render-md.py` | 〃 | jsonl을 마크다운으로 변환 |
| `routine/publish-md.sh` | 〃 | 사본 복사, 렌더링, 커밋, 푸시 |
| `routine/digest-server.py` | 〃 | 대시보드 웹앱 |
| `routine/memory/` | `~/.claude/projects/-Users-rokrokss--claude-routines/memory/` | 루틴이 실행하며 스스로 쌓은 수집 요령 (Claude Code 메모리) |
| `launchd/*.plist` | `~/Library/LaunchAgents/` | 예약 실행과 대시보드 상시 실행 |
| `data/digest-items.jsonl` | `~/.claude/routines/` | 누적 항목 아카이브 |
| `data/charchat-digest.md` | 〃 | 2026-08-10 초기 마크다운 다이제스트 (대시보드의 `/digest.md`) |
| `digest/` | (생성물) | 읽기용 마크다운 |

원본 폴더에만 있고 올리지 않는 것도 있다. 실행 로그 `logs/`는 30일 보관하고, 병합 직전 임시 파일 `today-items.json`은 병합이 끝나면 지워진다.

## 항목 스키마

`digest-items.jsonl`은 한 줄에 항목 하나씩 쓰는 JSON Lines 파일이다.

| 필드 | 내용 |
|---|---|
| `date` | `YYYY-MM-DD` 수집일. 롤업은 기간의 시작일 |
| `category` | `플랫폼 동향`, `신기능·업데이트`, `유저 니즈`, `제작 트렌드`, `영상 제작`, `기타` |
| `title` | 한 줄 헤드라인 |
| `summary` | 1\~4문장 요약. 롤업은 한 단락 |
| `implication` | 내 제품 관점의 시사점 1문장. 없으면 `null` |
| `links` | `[{"label": …, "url": …}]` |
| `platforms` | 관련 플랫폼·도구 태그 |
| `importance` | `high`(하루 0\~3개), `medium`, `low` |
| `source` | `아카라이브`, `디시 여성향갤`, `디시 AI챗갤`, `GitHub` |

`merge-items.py`의 병합 규칙:
- **일반 항목은 날짜 단위로 교체된다.** 같은 날 다시 실행하면 그날 항목 전체가 새 결과로 바뀌고, 다른 날짜는 그대로 남는다.
- **롤업은 날짜가 아니라 제목의 `[…]` 접두가 같은 항목끼리 교체된다.** 제목이 `[YYYY년 M월`로 시작하는 항목이 롤업이다.
  - 주간 롤업 `[YYYY년 M월 N주차 동향]`은 매일 다시 쓰여서 주가 지나며 완성된다. 월요일에는 지난주 롤업도 최종본으로 다시 쓴다.
  - 월간 롤업 `[YYYY년 M월 동향]`과 `[YYYY년 M월 여성향 봇 홍보 동향]`은 매월 1일에 만든다.
  - 접두가 한 글자라도 틀리면 일반 항목으로 처리돼, 그 날짜의 기존 항목이 전부 교체된다.
- 플랫폼 태그는 기존 표기에 맞춰 대소문자만 통일한다. 별칭까지 통일하지는 않는다.
- 2026-10-13 이전 항목의 `implication`에 나오는 "Black Sabayon"은 지금 Shizue의 옛 이름이다.

## 보는 곳

- **대시보드:** http://localhost:18787 (이 Mac에서만 열린다)
  - 일별 피드, 주간 리포트, 월간 리포트
  - 카테고리·중요도·플랫폼 필터와 검색
  - "지금 수집 실행" 버튼
- **GitHub:** [digest/README.md](digest/README.md). 폰으로 볼 때 쓴다. 맨 위 "최신" 날짜가 오늘로 바뀌지 않았으면 그날 수집이나 푸시가 실패한 것이다.

## 왜 비공개인가

공개하지 않는 이유는 세 가지다.
- 커뮤니티 글을 요약해 다시 배포하는 셈이다.
- 실명 회사에 대한 확인되지 않은 유저 의견과 내 제품 관점의 시사점이 들어 있다.
- 수집 방식에 공식 경로가 아닌 것이 섞여 있다([리스크](docs/collection.md#리스크)).

그래서 저장소는 비공개로 두고 GitHub Pages도 쓰지 않는다. Pages는 저장소가 비공개여도 사이트 자체는 공개된다.
