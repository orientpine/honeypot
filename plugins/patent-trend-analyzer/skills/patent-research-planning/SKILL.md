---
name: patent-research-planning
description: "특허 연구 영역 클러스터링, 키워드 최적화, 검색 전략 수립. Use when: (1) 새로운 특허 조사 프로젝트 시작 시, (2) KIPRIS API 호출 전 키워드 조합 최적화 시, (3) IPC 코드와 키워드 분류 체계 구성 시, (4) 다국가 특허 검색 전략 수립 시, (5) '검색 계획', 'plan patent search', 'optimize keywords', 'cluster research areas' 요청 시."
---

# patent-research-planning

특허 조사 프로젝트의 키워드 클러스터링, 검색 전략 수립, IPC 코드 매핑을 담당하는 스킬입니다.

---

## Pipeline Overview

이 스킬은 3단계 파이프라인의 **L1 (Planning)** 입니다.

```
L1 Planning (이 스킬)
    ↓  검색 전략, 키워드 목록, IPC 코드
L2 Search (patent-search-collect)
    ↓  수집된 특허 데이터 (Excel/JSON)
L3 Analysis (patent-analysis-viz)
    ↓  분류, 트렌드 분석, 시각화 대시보드
```

L1을 충분히 수행해야 L2에서 불필요한 API 호출을 줄이고 L3 결과의 정밀도를 높일 수 있습니다.

---

## Available MCP Tools

| 도구 이름 | 설명 |
|-----------|------|
| `patent_search_planner` | 연구 주제를 입력하면 검색 전략, 키워드 클러스터, IPC 코드 추천을 반환 |
| `patent_keyword_optimizer` | 초기 키워드 세트를 입력하면 동의어 확장, 불용어 제거, 조합 최적화 수행 |

---

## 5-Step Workflow

### Step 1. 연구 주제 파악

사용자의 연구 주제를 구체화합니다.

- 핵심 기술 도메인 확인 (예: "엣지 AI 추론 최적화")
- 대상 국가/언어 범위 결정 (한국 / 해외 / 전체)
- 분석 기간 설정 (예: 2019-2024)

### Step 2. 키워드 최적화

`patent_keyword_optimizer` 를 호출하여 초기 키워드를 정제합니다.

```
입력: ["엣지 컴퓨팅", "경량화", "추론"]
출력: {
  "korean": ["에지 AI", "온디바이스", "경량 모델", "추론 최적화"],
  "english": ["edge inference", "on-device AI", "model compression", "TinyML"],
  "excluded": ["LLM", "의료", "보안"]  // 도메인 제외
}
```

### Step 3. 검색 전략 수립

`patent_search_planner` 를 호출하여 구체적인 검색 계획을 생성합니다.

```
입력: 최적화된 키워드 + 연구 주제
출력: {
  "queries": [...],       // 개별 검색 쿼리 목록
  "ipc_codes": [...],     // 추천 IPC 코드
  "search_order": [...],  // 국가별 검색 순서
  "estimated_results": N  // 예상 결과 수
}
```

### Step 4. 계획 제시

사용자에게 다음 항목을 정리해 제시합니다.

- 검색 쿼리 목록 (한국어 / 영어)
- IPC 코드 매핑
- 국가별 검색 순서
- 예상 결과 수 및 소요 시간

### Step 5. 사용자 확인

계획을 확인받은 후 L2 (patent-search-collect) 로 넘어갑니다.

- 필요시 키워드 추가/제거 반영
- 범위 조정 (너무 넓으면 IPC로 좁히기, 너무 좁으면 동의어 확장)

---

## 3-Axis Classification Reference

검색 전략 수립 시 아래 3축 분류 체계를 기준으로 키워드와 IPC 코드를 매핑합니다.

### Axis 1: Processing Layer

| 레이어 | IPC 코드 | 설명 |
|--------|----------|------|
| **OnSensor** | G06N 3/065, G06N 3/067 | 센서 내 직접 처리, 초저전력 |
| **OnDevice** | G06N 3/063 | 단말기(스마트폰/MCU) 내 처리 |
| **Cloud/Other** | G06N 3/04, G06N 3/08 | 클라우드 서버 처리 또는 미분류 |

### Axis 2: Function

| 기능 | 키워드 예시 |
|------|------------|
| **Adaptive Learning** | 전이학습, federated learning, 온라인 학습 |
| **Inference** | 추론 최적화, inference engine, TinyML |
| **Lightweight** | 경량화, 양자화, pruning, knowledge distillation |
| **Training** | 학습 알고리즘, backpropagation, 최적화기 |

---

## Domain Exclusions

아래 도메인은 분석 대상에서 제외합니다. 키워드 최적화 시 자동으로 불용어 처리됩니다.

- **LLM / 생성 AI**: GPT, BERT, transformer (대형 언어 모델)
- **Medical**: 의료 진단, 영상 판독, 신약 개발
- **Security**: 침입 탐지, 사이버 보안, 암호화
- **Recommendation**: 추천 시스템, 협업 필터링
- **Analytics**: 비즈니스 분석, BI, 데이터 웨어하우스

---

## Tips

- **넓게 시작해서 좁히기**: 처음엔 상위 IPC 코드(G06N 3)로 시작하고, 결과가 많으면 하위 코드로 좁힘
- **한국 특허 특성**: OnDevice 비율이 약 52%로 높음 (대기업 중심 출원)
- **화이트 스페이스**: OnSensor 비율은 약 12%로 낮아 기회 영역으로 분류됨
- **다국어 병행**: 같은 개념도 한국어/영어 쿼리 결과가 다를 수 있으므로 병행 검색 권장
