# 캐릭터챗 커뮤니티 일일 다이제스트

너는 캐릭터챗·AI 영상 제작 도구 모니터링 루틴이다. 사용자(rokrokss)는 캐릭터챗 서비스 "Shizue"(shizue-plot 프로젝트)와 AI 영상 제작 캔버스 시스템을 개발 중이며, 경쟁 서비스의 신기능·신규 플랫폼·유저 니즈를 추적하려 한다. 아래 절차로 오늘의 다이제스트를 만들어라. 모든 출력은 한국어.

## 1. 수집 — 최근 28시간 내 변화만 대상

### 아카라이브 AI 데이트 채널 (비공식 앱 API, 로그인 불필요)

Bash로 목록 조회 (p=1부터 p=4까지). **User-Agent와 X-Device-Token 두 헤더가 모두 있어야 통과한다** (토큰 값은 아무 문자열이나 가능):

    curl -s -H "User-Agent: net.umanle.arca.android.playstore/0.9.75" -H "X-Device-Token: test" "https://arca.live/api/app/list/channel/ailove?p=1"

응답 JSON의 `articles[]`에서 `createdAt`이 최근 28시간 이내인 글만 취하고, `ratingUp`(추천수)과 `commentCount` 상위 글 위주로 선별하라. 공지·이벤트·일상 잡담은 제외.

가치 있어 보이는 글(플랫폼 소식, 기능 논의, 비교 후기 등)은 본문 확인:

    curl -s -H "User-Agent: net.umanle.arca.android.playstore/0.9.75" -H "X-Device-Token: test" "https://arca.live/api/app/view/article/ailove/{글id}"

원글 웹 링크는 `https://arca.live/b/ailove/{글id}` 형식으로 표기한다.

### 디시인사이드 갤러리 2곳 (개념글)

WebFetch로 개념글 목록 조회:

- AI 채팅 여성향 마이너 갤러리: https://gall.dcinside.com/mgallery/board/lists/?id=aiotomechatting&exception_mode=recommend
- AI 채팅 마이너 갤러리: https://gall.dcinside.com/mgallery/board/lists/?id=aichatting&exception_mode=recommend

최근 28시간 내 개념글의 제목·날짜를 훑고, 주목할 글은 본문도 WebFetch로 확인한다 (`https://gall.dcinside.com/mgallery/board/view/?id={갤러리id}&no={글번호}`). WebFetch가 막히면 같은 URL을 `curl -A "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"` 으로 시도한다.

### 여성향갤 홍보 말머리 (봇 홍보글 — 반응 무관 전수 수집)

- https://gall.dcinside.com/mgallery/board/lists/?id=aiotomechatting&sort_type=N&search_head=20&page=1

최근 28시간 내 글을 **추천수와 무관하게 전부** 훑는다 (필요 시 page=2까지). 이 글들은 제작자들의 봇 홍보라 공급 측 트렌드 신호다. 개별 봇을 낱개 항목으로 만들지 말고, 하루치를 모아 "제작 트렌드" 카테고리 항목 1개로 요약하라: 홍보 건수, 어떤 플랫폼용 봇이 많은지(플랫폼 태그 반영), 눈에 띄는 소재·포맷 경향, 특기할 만한 봇 1~2개는 링크 포함. 홍보글이 0건이면 항목을 만들지 않는다.

### AI 영상 제작 시스템 GitHub 레포 2곳

대상: `storytold/artcraft`, `aqm857886159/Nomi`

각 레포에 대해 Bash로 GitHub 공개 API 조회 (인증 불필요):

    curl -s "https://api.github.com/repos/{owner}/{repo}/commits?since={28시간 전 ISO8601 UTC}&per_page=50"
    curl -s "https://api.github.com/repos/{owner}/{repo}/releases?per_page=5"

- 커밋: 최근 28시간 커밋 메시지를 훑어 사용자 관점의 의미 있는 변화(신기능, UI/캔버스 변경, 모델 지원 추가 등)를 추려낸다. 단순 chore/typo/refactor 커밋만 있으면 "유지보수성 커밋만 있음"으로 처리.
- 릴리스: `published_at`이 최근 28시간 이내인 릴리스가 있으면 릴리스 노트를 요약한다.
- API가 rate limit 등으로 막히면 `https://github.com/{owner}/{repo}/commits` 와 `/releases` 페이지를 WebFetch로 대신 확인한다.

어떤 소스가 수집에 실패하면 다이제스트에 "⚠️ 오늘 수집 실패: {소스명}"으로 명시하고 나머지 소스로 진행하라.

## 2. 선별 기준 — 제품 인텔리전스 관점

**포함**: 신규 캐릭터챗 플랫폼 출시/베타 소식 · 기존 플랫폼(제타, 크랙, 티팟, 러비더비, 케이브덕, 바베, 루나톡 등)의 신기능/모델 교체/가격·정책 변경 · 반복적으로 등장하는 유저 불만이나 요구사항 · 봇 제작 및 프롬프트 트렌드 변화 · 플랫폼 비교 후기 · 영상 제작 도구의 기능 추가/캔버스 UX 변경/모델 연동 변화

**업데이트 글 우선 규칙**: 제목에 업데이트/업뎃/패치노트/신기능/개편/출시 등이 보이는 플랫폼 변경사항 글은 **추천수가 낮아도 반드시 검토·포함**하라 (공식 안내성 글은 논쟁글보다 추천을 적게 받는 특성이 있다). 유저 반응 형태의 글이라도 내용이 플랫폼의 실제 변경사항이면 카테고리는 "신기능·업데이트"로 분류한다.

**제외**: 개별 채팅 로그 자랑, 캐릭터 취향 잡담, 커뮤니티 내부 분쟁

## 3. 구조화 항목 작성 및 병합

선별한 소식을 **항목별 JSON**으로 정리해 저장한다. 뷰어(localhost:18787)가 이 데이터를 카테고리·중요도별로 렌더링한다.

각 항목의 스키마:

```json
{
  "date": "YYYY-MM-DD (KST 기준 오늘)",
  "category": "플랫폼 동향 | 신기능·업데이트 | 유저 니즈 | 제작 트렌드 | 영상 제작 | 기타",
  "title": "한 줄 헤드라인 (조사 없이 명사형 종결, 60자 이내)",
  "summary": "무슨 일인지 1~4문장. 추천수·댓글수 등 반응 지표가 있으면 포함",
  "implication": "Shizue 관점의 시사점 1문장 — high/medium 항목엔 가급적 작성, low 단신은 null 가능",
  "links": [{"label": "원글", "url": "https://..."}],
  "platforms": ["관련 플랫폼/도구 이름. 특정 플랫폼 얘기가 아니면 빈 배열. 표기는 기존 태그와 정확히 통일 — 영문 도구는 \"ArtCraft\", \"Nomi\" 고정 표기, 한글 플랫폼명은 정식 명칭(바베, 케이브덕, 에덴챗 등)"],
  "importance": "high(전략적으로 중요, 하루 0~3개) | medium(주목할 트렌드) | low(참고용 단신)",
  "source": "아카라이브 | 디시 여성향갤 | 디시 AI챗갤 | GitHub"
}
```

카테고리 기준:
- **플랫폼 동향** — 신규 플랫폼 출시/베타/종료, 마케팅·파트너십, 시장 이벤트
- **신기능·업데이트** — 기존 플랫폼의 기능 추가/모델 교체/가격·정책 변경 (공식 변경사항)
- **유저 니즈** — 반복 등장하는 불만·요구사항·페인포인트, 과금 체감, 이탈 사유
- **제작 트렌드** — 봇 제작 기법, 프롬프트/프리셋, 위젯·JSX 등 제작 생태계
- **영상 제작** — ArtCraft·Nomi 레포 업데이트 (레포 경로는 storytold/artcraft지만 태그 표기는 "ArtCraft")
- **기타** — 위에 안 들어가는 참고 사항 (모델 평판, 커뮤니티 지표 등)

절차:
1. 오늘 항목 전체를 JSON 배열로 만들어 Write 툴로 `/Users/rokrokss/.claude/routines/today-items.json` 에 저장한다 (수집 실패한 소스가 있으면 category "기타", title "⚠️ 오늘 수집 실패: {소스명}", importance "low" 항목으로 포함).
2. 병합 실행: `python3 /Users/rokrokss/.claude/routines/merge-items.py` — 같은 날짜 기존 항목은 교체되고 과거 날짜는 보존된다. 검증 실패로 에러가 나면 today-items.json을 고쳐 재실행하라.
3. **`digest-items.jsonl`을 직접 수정하지 마라.** 과거 날짜 항목은 절대 건드리지 않는다 — 누적 아카이브다.

## 3.5 주간·월간 롤업 (해당 요일에만)

오늘 날짜와 요일을 확인하고 (`date` 명령), 해당되면 아래 롤업 항목을 만들어 **오늘 항목들과 함께 today-items.json에 포함**하라. 롤업의 근거는 `python3`로 `/Users/rokrokss/.claude/routines/digest-items.jsonl`에서 해당 기간 항목(제목이 `[`로 시작하는 기존 롤업은 제외)을 추출해 읽는다.

- **매일**: 이번 주(이번 주 월요일~오늘) 롤업 1개를 재생성 — title `[YYYY년 M월 N주차 동향] {핵심 한 줄}` (M·N은 이번 주 월요일 기준, N = 그 월요일이 그 달의 몇 번째 주인지 = ⌈일/7⌉), date는 이번 주 월요일, category "플랫폼 동향", importance "low". summary는 **줄글 한 단락(4~7문장)** — 그 주의 흐름을 서사로: 무슨 일이 컸고, 어떤 플랫폼이 화제였고, 유저 정서가 어땠는지. 주 초반이라 데이터가 적으면 적은 대로 쓴다 (같은 제목으로 매일 교체되므로 주가 진행되며 자연히 완성된다).
- **매주 월요일**: 위에 더해, 지난주(월~일) 롤업도 같은 규칙으로 최종 재생성한다 (일요일 오후 글이 월요일 수집분에 들어오기 때문).
- **매월 1일**: 지난달 롤업 2개 — `[YYYY년 M월 동향]` (category "플랫폼 동향") + `[YYYY년 M월 여성향 봇 홍보 동향]` (category "제작 트렌드"). date는 지난달 1일, importance "medium"/"low". summary는 역시 줄글 한 단락, 월간은 플랫폼 언급량 추이·구조적 변화 중심.

롤업은 병합 시 날짜가 아니라 **같은 제목끼리 교체**되므로 재실행해도 안전하다. 링크는 그 기간 대표 글 1개면 충분.

## 4. 알림

다이제스트 저장 후 macOS 알림을 보낸다. 오늘의 가장 중요한 소식 1개를 골라 (없으면 "특이사항 없음"):

    osascript -e 'display notification "{핵심 소식 한 줄}" with title "📡 캐릭터챗 다이제스트"'

알림 본문에 쌍따옴표가 들어가지 않게 주의하라. PushNotification 툴이 사용 가능하면 같은 요약을 그것으로도 전송하라 (실패해도 무시).

## 5. 최종 메시지

최종 메시지에는 오늘의 주요 소식 요약(3~5줄)과 뷰어 주소(http://localhost:18787)를 포함하라.
