# URL Fetch 전략

URL 소스별 콘텐츠 추출 전략과 성공률. 병렬 호출을 기본으로 한다.

## 목차

1. [소스 분류](#소스-분류)
2. [소스별 상세 전략](#소스별-상세-전략)
3. [병렬 실행 패턴](#병렬-실행-패턴)
4. [실패 처리](#실패-처리)

---

## 소스 분류

URL을 호스트명으로 먼저 분류한 뒤 전략 선택.

| 호스트 패턴 | 분류 | 1순위 도구 | 2순위 (보충) |
|---|---|---|---|
| `news.hada.io` | GeekNews | `webfetch` | - |
| `*.wikipedia.org` | Wikipedia | `webfetch` | - |
| `youtube.com`, `youtu.be` | YouTube | `webfetch` (제목만) | web search (설명/챕터) |
| `x.com`, `twitter.com` | X/Twitter | web search | placeholder |
| `threads.com`, `threads.net` | Threads | `webfetch` | web search |
| `github.com/*/blob/*` | GitHub 파일 | `webfetch` (raw URL 변환) | - |
| `github.com/*` (repo) | GitHub repo | `webfetch` | - |
| `medium.com`, `velog.io`, `dev.to`, `qiita.com` | 기술 블로그 | `webfetch` | - |
| `substack.com`, 개인 블로그 | 일반 블로그 | `webfetch` | web search |
| 기타 | Unknown | `webfetch` 시도 | 실패 시 web search |

---

## 소스별 상세 전략

### GeekNews (news.hada.io)

`webfetch(url, format="markdown")` 한 번으로 충분. 제목, 본문 요약, 외부 링크 모두 추출됨.

### Wikipedia

`webfetch(url, format="markdown")`. 긴 페이지는 앞부분 (개요 + 핵심 섹션)만 요약에 사용.

### YouTube

```
1. webfetch(url) → 영상 제목, 채널, 설명 일부 추출
2. (선택) web search(query="{title} {channel} video summary") → 설명/챕터 보충
```

md 본문은 제목 + 채널 + 설명 요약 + (가능하면) 주요 챕터 리스트.

### X/Twitter

X.com은 JS 렌더링 의존도가 높아 webfetch 실패율이 매우 높다.

```
1. web search(query="{tweet_url} OR 트윗 URL에서 추출한 키워드")
2. 실패 시 placeholder 생성
```

placeholder는 resource-md-template.md의 X/Twitter 섹션 참조.

### Threads

Threads는 web search 성공률이 높다. `webfetch` 먼저 시도하고 빈 본문이면 web search.

### GitHub

- 파일 URL (`/blob/`): raw URL로 변환 (`/blob/` → `raw.githubusercontent.com`) 후 webfetch
- 레포 루트: `webfetch(url)` → README 기반 요약

### 일반 블로그

`webfetch` 시도. 페이월이면 사용자에게 알림 ("페이월로 접근 불가 - HoneyCombo 제출 불가 후보").

---

## 병렬 실행 패턴

**절대로 순차 실행하지 말 것.** 하나의 메시지 내에서 모든 fetch 도구 호출을 동시에 발사한다.

```typescript
// CORRECT: 단일 메시지 내 병렬 호출
[
  webfetch(url=url1, format="markdown"),
  webfetch(url=url2, format="markdown"),
  web_search(query=youtube_query),
  webfetch(url=url4, format="markdown"),
]

// WRONG: 순차 실행
const r1 = webfetch(url1)
const r2 = webfetch(url2)  // r1 완료 후에만 실행됨 - 낭비
```

URL이 10개를 넘으면 5개 단위 배치로 나누되, 각 배치 내에서는 병렬.

---

## 실패 처리

### webfetch 빈 응답 / HTTP 에러

1. 1회 재시도 (동일 URL)
2. 여전히 실패 시 web search fallback
3. fallback도 실패 시 placeholder md 생성하고 "⚠️ 보충 필요" 목록에 추가

### Cloudflare / 봇 차단

webfetch가 "Just a moment..." 페이지를 반환하면 차단된 것. 곳바로 web search로 넘어간다.

### 타임아웃

기본 60초. 너무 느린 URL은 스킵하고 placeholder + 사용자 알림.

### 중복 URL

입력 목록 내 중복은 제거 후 1번만 처리. 사용자에게 "N개 중 M개 중복 제거" 보고.

---

## 출력 품질 체크

fetch 후 md 작성 전에 확인:

- [ ] 제목을 추출했는가? (없으면 URL에서 slug 추출)
- [ ] 본문이 200자 이상인가? (너무 짧으면 fallback 시도)
- [ ] 본문에 "error", "access denied", "403 forbidden" 같은 에러 메시지가 포함되어 있지 않은가?
- [ ] 원 페이지 메타데이터(저자, 날짜)를 확보했는가? (있으면 frontmatter에 반영 고려)
