# Draft: HWPX 통합 플러그인 (3개 레포 취합)

## Requirements (confirmed)
- 3개 GitHub 레포의 장점만 취합하여 새 플러그인 생성
- plugins/ 디렉토리에 추가
- 기존 honeypot 프로젝트 양식(AGENTS.md 규칙) 기초

## 3개 레포 분석 결과

### Repo 1: Canine89/hwpxskill (XML-first)
**접근방식**: XML 직접 작성 중심 (python-hwpx API 버그 우회)
**핵심 장점**:
- ★★★ `build_hwpx.py` — 템플릿 + XML → HWPX 조립 (핵심 빌더)
- ★★★ `analyze_template.py` — 레퍼런스 HWPX 심층 분석 (역공학)
- ★★★ `unpack.py`/`pack.py` — 기존 문서 편집 (HWPX↔디렉토리)
- ★★★ `validate.py` — HWPX 구조 검증
- ★★★ `text_extract.py` — 텍스트 추출 (Markdown/테이블 포함)
- ★★★ 5개 템플릿 (base, gonmun, report, minutes, proposal) — 스타일 ID 완비
- ★★★ 상세 section0.xml/header.xml 작성 가이드
- ★★★ 표(table) 작성법 + 크기 계산 (A4 본문폭 42520 기준)
- ★★★ 레퍼런스 기반 문서 생성 워크플로우 (분석→추출→작성→빌드)
- ★★ 단위 변환표 (pt/mm/cm/HWPUNIT)
- ★★ `references/hwpx-format.md` — OWPML XML 요소 레퍼런스

**5가지 워크플로우**: 생성, 편집, 읽기, 검증, 레퍼런스 기반 생성

### Repo 2: Canine89/gonggong_hwpxskills (공공문서 특화)
**접근방식**: python-hwpx 라이브러리 + ZIP-level 치환
**핵심 장점**:
- ★★★ ZIP-level 텍스트 치환 (python-hwpx API보다 안전하고 호환성 높음)
- ★★★ `fix_namespaces.py` — 네임스페이스 후처리 (없으면 빈 페이지!)
- ★★★ 양식 우선 정책 (사용자 업로드 > 기본양식 > new())
- ★★ `ObjectFinder` 활용 텍스트 전수 조사
- ★★ 순차 치환 (동일 플레이스홀더를 다른 값으로)
- ★★ 보고서 템플릿 (표지+목차+섹션바+계층본문)
- ★★ 본문 기호 체계 (□→○→―→※, 각각 다른 폰트/크기)
- ★★ 공문서 날짜 형식 규칙 (2026. 2. 13.)
- ★ 문서 유형별 스타일 가이드 (report-style.md, official-doc-style.md)

**핵심 워크플로우**: 양식복사 → ObjectFinder조사 → ZIP치환 → 네임스페이스 → 검증

### Repo 3: Canine89/hwpxskill-math (수학 수식 문제지)
**접근방식**: JSON → HWPX (모듈화된 Python 빌더)
**핵심 장점**:
- ★★★ 수학 수식 지원 (hp:equation + 한컴 수식 스크립트)
- ★★★ 한컴 수식 스크립트 완전 레퍼런스 (분수/루트/적분/행렬/그리스문자 등)
- ★★★ 수식 XML 구조 (hp:equation, hp:script 태그)
- ★★ 2열 문제지 레이아웃 (colCount=2, NEWSPAPER)
- ★★ 학력평가/수능 시험지 형식 (헤더, 배점, 가로선택지, 페이지번호)
- ★★ 단 전환 기법 (1단→2단→1단 within section)
- ★★ 그래프/도형 생성 (triangle, circle, quadrilateral, coordinate, solid3d)
- ★★ 모듈화된 코드 (xml_primitives → exam_helpers → table_layout → section_generators → build)
- ★ 학년별 수식 예시 (중1~고3)
- ★ 리그레션 테스트

### 기존 plugins/hwpx-converter (pypandoc-hwpx)
**접근방식**: pypandoc-hwpx CLI wrapper
**현재 상태**: 매우 제한적
- MD→HWPX만 지원 (Pandoc 기반 단순 변환)
- XML 직접 제어 없음, 템플릿 없음, 수식 없음
- Skills: converter + setup (2개)

## 통합 전략 (초안)

### 새 플러그인에 포함할 장점 취합:

| 기능 | 출처 | 우선순위 |
|------|------|----------|
| XML-first 빌드 파이프라인 (build_hwpx.py) | hwpxskill | 핵심 |
| 5개 템플릿 + 스타일 ID 맵 | hwpxskill | 핵심 |
| unpack/pack/validate/extract 유틸 | hwpxskill | 핵심 |
| 레퍼런스 기반 역분석 (analyze_template.py) | hwpxskill | 핵심 |
| section0.xml/header.xml 작성 가이드 | hwpxskill | 핵심 |
| ZIP-level 텍스트 치환 함수 | gonggong | 핵심 |
| fix_namespaces.py 후처리 | gonggong | 핵심 (Critical) |
| 양식 우선 정책 + ObjectFinder | gonggong | 핵심 |
| 공공문서 스타일/기호체계 | gonggong | 높음 |
| 수학 수식 지원 (hp:equation) | math | 핵심 |
| 한컴 수식 스크립트 레퍼런스 | math | 핵심 |
| JSON→HWPX 빌더 (수학문제지) | math | 높음 |
| 그래프/도형 생성 | math | 높음 |
| 2열 레이아웃 + 단전환 | math | 높음 |

## Open Questions
- 플러그인 이름? (hwpx-document / hwpx-studio / hwpx-generator 등)
- 기존 hwpx-converter 대체? 병존?
- 에이전트 포함? (agent+skill vs skill-only)
- 커맨드(오케스트레이터) 필요?
- Python 스크립트 전부 포함? (build, analyze, unpack, pack, validate, extract, fix_namespaces, graph_generator 등)
- 템플릿 HWPX/XML 파일 전부 포함?

## Scope Boundaries
- INCLUDE: [TBD]
- EXCLUDE: [TBD]

## Technical Decisions
- [TBD after interview]
