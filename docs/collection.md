# 수집

지침(`routine/charchat-digest-prompt.md`)에 적힌 방법과 루틴이 실제로 쓰는 방법은 다르다. 수집 스크립트가 따로 저장돼 있지 않기 때문이다.

- 루틴은 실행할 때마다 `/tmp/dgNN/`에 수집 스크립트를 새로 짠다.
- 실행하며 알게 된 요령은 자기 Claude Code 메모리 [`routine/memory/digest-collection-quirks.md`](../routine/memory/digest-collection-quirks.md)에 덧붙인다. 다음 실행은 이 메모를 먼저 읽는다.
- 실제 수집 방법의 기준은 지침이 아니라 이 메모다. 아래 "실제" 칸은 2026-10-13 실행 기록을 기준으로 정리했다.

**수집 범위:** 최근 28시간이다. 하루 한 번 실행하므로 앞쪽 4시간쯤은 전날 수집분과 겹친다. 겹치는 구간의 글은 새 항목으로 만들지 않는다. 지난 날짜를 나중에 다시 수집할 방법은 없다.

## 아카라이브 AI 데이트 채널 (`ailove`)

| | 지침 | 실제 |
|---|---|---|
| 경로 | 앱용 비공개 API `arca.live/api/app/…` | 같음 |
| 헤더 | `User-Agent: net.umanle.arca.android.playstore/0.9.75`, `X-Device-Token`(아무 값) | 같음 |
| 목록 | `list/channel/ailove?p=1`\~`4` | 28시간 전 글이 나올 때까지 계속 넘긴다. 하루 18\~24페이지, 800\~1,070건 |
| 본문 | `view/article/ailove/{id}` | 같음. 하루 20\~30건 |
| 댓글 | 없음 | `list/comment/ailove/{id}` |
| 기타 | 없음 | 앱 API 검색(`target=all&keyword=…`)도 쓴다. 이미지로만 올라온 공지는 `Referer: https://arca.live/` 헤더로 이미지를 받아 모델이 읽는다 |

후보는 세 가지 기준으로 고른다.
- 추천·댓글 상위 글
- 제목에 업데이트, 가격, 모델명 같은 키워드가 있는 글
- `공식`, `정보` 등의 카테고리 글

`홍보`, `창작마당` 카테고리는 일반 후보에서 뺀다. 홍보 글은 제작 트렌드 집계에만 쓴다.

## 디시인사이드 (`aiotomechatting` 여성향 갤, `aichatting` AI채팅 갤)

| | 지침 | 실제 |
|---|---|---|
| 도구 | WebFetch를 쓰고, 막히면 Chrome User-Agent curl | 처음부터 Chrome User-Agent curl을 쓴다 (2026-10-13 WebFetch 호출 0회) |
| 목록 | 개념글 목록 | 개념글 목록과 전체 글 목록(`list_num=100`)을 28시간 범위 끝까지 받는다. HTML의 `tr.ub-content` 행을 정규식으로 파싱한다 |
| 본문 | view 페이지 | 같음. 본문 `write_div`를 `if(window.OutLink` 앞에서 자른다 |
| 댓글 | 없음 | 페이지에서 `e_s_n_o` 토큰을 뽑아 `POST /board/comment/`로 받는다 (`X-Requested-With`, `Referer` 헤더 포함) |
| 홍보 말머리 | 여성향 갤 `search_head=20` 1\~2페이지 전수 | 같음. 하루치를 "제작 트렌드" 항목 1개로 요약한다 |
| 성인 인증 글 | 없음 | `/error/adult/`로 넘어가서 제목만 쓴다 |

## GitHub (`storytold/artcraft`, `aqm857886159/Nomi`)

공개 REST API를 인증 없이 호출한다.
- **커밋:** `commits?since=`로 받는다. Nomi는 하루 커밋이 150개를 넘기도 해서 여러 페이지를 받는다.
- **릴리스:** `releases`를 본다.
- **스타 증가:** 커밋이 없는 날에도 `events`의 WatchEvent로 확인한다.
- **PR 상세:** 필요하면 PR 상세를 받는다. 전날과 겹치는 커밋은 PR의 `merged_at`으로 걸러 낸다.

태그 표기는 `ArtCraft`, `Nomi`로 고정한다.

## 리스크

이 루틴을 비공개로 돌리는 이유이자, 공개하거나 남에게 배포하기 전에 정리해야 할 것들이다.

- **아카라이브:** 공개 API가 없어서, 앱 User-Agent와 임의 토큰으로 앱인 척 호출한다.
- **디시:** 브라우저 User-Agent로 위장하고, 내부 댓글 엔드포인트를 토큰을 뽑아 호출한다. 이미지도 `Referer`를 붙여 받는다. 요청 사이에 대기 시간이 없다. 디시 robots.txt는 일반 봇은 허용하지만, ClaudeBot·anthropic-ai 등 Anthropic 이름의 크롤러는 명시적으로 막는다.
- **결과물:** 커뮤니티 글 요약, 실명 회사에 대한 확인되지 않은 의혹, 개별 제작자 홍보글 요약이 들어 있다.
- **에이전트 권한:** 에이전트가 누구나 쓸 수 있는 커뮤니티 글을 읽으면서 `Bash(curl:*)`, `Bash(python3:*)`, `Write`, `Edit` 권한을 가진다. `python3:*`는 사실상 임의 코드 실행이어서, 글에 심어 둔 지시문(프롬프트 인젝션)에 취약하다. git 푸시를 에이전트가 아닌 `publish-md.sh`가 하는 것도 이 때문이다.
