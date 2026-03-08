---
name: layout-types
description: "visual-generator 스킬이 공유하는 24종 레이아웃 정의. 각 레이아웃의 핵심 아이디어, ASCII 시각 구성, 시각화 원칙, 권장 사양, 적합/부적합 케이스를 포함합니다."
---

# 레이아웃 유형 (Layout Types)

## 개요
모든 `visual-generator` 스킬이 공유하는 24종 레이아웃 정의입니다. 아래 요약 표에서 적합한 레이아웃을 선택한 뒤, 상세 정의는 **references/layout-catalog.md**를 참조하세요.

## 레이아웃 요약 표

| # | 레이아웃 | 영문명 | 핵심 아이디어 | 적합 케이스 |
|---|---------|--------|-------------|------------|
| 1 | 플로우 | Flow | 입력→출력 단계적 변화/이동 | 데이터 파이프라인, 업무 프로세스 |
| 2 | 구조 | Structure | 레이어/구성요소 결합 | 소프트웨어 아키텍처, 모듈 시스템 |
| 3 | 네트워크 | Network | 요소 간 관계(연결) | 협력 생태계, 시스템 연동 |
| 4 | 대비 | Contrast | 두 상태/선택지 비교 | As-Is/To-Be, A vs B |
| 5 | 진화 | Evolution | 점진적 성숙/개선 누적 | 기술 성숙도, 제품 로드맵 |
| 6 | 중심 | Central | 핵심(허브) + 주변 요소 | 플랫폼 코어, 핵심 기술 |
| 7 | 순환 | Cycle | 반복/피드백 루프 | PDCA, 데이터-모델-배포 |
| 8 | 그룹 | Group | 카테고리 분류 | 기능 카탈로그, 세그먼트 분류 |
| 9 | 동심원 | Concentric | 범위/영향/포함 관계 | 보안 범위, 서비스 영향 범위 |
| 10 | Swimlane | Swimlane | 다주체 동일 시간축 | 기관 협업, 서비스 운영 |
| 11 | 전략맵 | Strategy Map | 두 축 배치, 위치=의미 | 우선순위 매트릭스, 포지셔닝 |
| 12 | 깔때기 | Funnel | 단계별 선별/전환 | 사용자 전환, 선발 프로세스 |
| 13 | Hub-Network | Hub-Network | 1단 허브 + 2단 분기 | 플랫폼 구조, 지식 분류 |
| 14 | Section-Flow | Section-Flow | 상단 메인 + 하단 흐름 | 시스템 개요 + 처리 흐름 |
| 15 | Card-Grid | Card-Grid | 동일 카드 그리드 배치 | 기능 리스트, 사례 갤러리 |
| 16 | 피라미드 | Pyramid | 상→하 우선순위/가치 체계 | 비전→전략→실행, 성숙도 |
| 17 | 3D 분해도 | Exploded View | 코어 + 모듈 분해 | 하드웨어 구성, 모듈 아키텍처 |
| 18 | 타임라인 | Horizontal Timeline | 좌→우 시간축 마일스톤 | R&D 로드맵, 사업 일정 |
| 19 | 조직도+네트워크 | Org-Network | 책임(상단) + 협력(하단) | 컨소시엄, 다기관 협력 |
| 20 | Bento Grid | Bento Grid | 모듈형 타일 우선순위 배치 | 한 장 요약, 기능 개요 |
| 21 | Sankey | Sankey | 굵기=비중, 흐름 배분 | 예산 배분, 에너지/데이터 흐름 |
| 22 | Z-Pattern | Z-Pattern | 좌상→우상→좌하→우하 시선 | 핵심 메시지 전달, 제안서 |
| 23 | Mind Map | Mind Map | 방사형 아이디어 확장 | 브레인스토밍, 연구 주제 구조화 |
| 24 | Stacked Progress | Stacked Progress | 누적 구성(합) + 기여 | 예산 구성비, 누적 성과 |

## 레이아웃 선택 가이드

### 메시지 유형별 추천

| 전달하려는 메시지 | 추천 레이아웃 |
|------------------|-------------|
| "A에서 B로 이렇게 변한다" | Flow, Evolution, Funnel |
| "이것이 저것 위에 있다" | Structure, Pyramid, Concentric |
| "이것과 저것이 연결된다" | Network, Central, Hub-Network, Org-Network |
| "A와 B는 이렇게 다르다" | Contrast |
| "이 항목들은 이렇게 분류된다" | Group, Card-Grid, Bento Grid |
| "누가 언제 무엇을 하는가" | Swimlane, Horizontal Timeline |
| "어디에 위치하는가" | Strategy Map, Z-Pattern |
| "반복하며 개선된다" | Cycle |
| "얼마나 이동하는가" | Sankey, Stacked Progress |
| "아이디어를 확장한다" | Mind Map |
| "한 장으로 요약한다" | Section-Flow, Bento Grid, Z-Pattern |

### 부적합 조합 (피해야 할 선택)

| 상황 | 피해야 할 레이아웃 | 이유 |
|------|------------------|------|
| 반복/피드백 강조 | Flow, Evolution | 일회성 단방향 구조 |
| 3개+ 대안 비교 | Contrast | 2개 비교 전용 |
| 순서 중심 | Network, Central, Group | 비방향/비순서 구조 |
| 위계 중심 | Network | 동등 관계 전용 |

## 검증 규칙: 공간-의미 역검증 (CRITICAL)

축 기반 레이아웃(Strategy Map, Contrast, Evolution, Pyramid 등)에서는 **위치가 곧 의미**이므로, 콘텐츠 배치 후 반드시 역검증합니다.

**역검증 질문** (사분면/영역마다 1회씩):

> "이 콘텐츠가 기술하는 상태는 **{X축명}이 {High/Low}**이고 **{Y축명}이 {High/Low}**인 상황과 일치하는가?"

불일치 발견 시 콘텐츠 위치를 교정한 후 재검증합니다. 상세 예시와 적용 범위는 **references/layout-catalog.md** § 11. 전략맵 메타포를 참조하세요.

## 상세 정의

각 레이아웃의 **ASCII 시각 구성**, **시각화 원칙**, **권장 사양**, **적합/부적합 케이스**는 다음 파일을 참조하세요:

- **references/layout-catalog.md**: 24종 레이아웃 상세 정의 (핵심 아이디어, ASCII, 원칙, 사양, 케이스)
