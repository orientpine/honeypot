# Honeypot 플러그인 검증 프롬프트

## 사용법

1. 여러 터미널 세션을 열고 각각에서 OpenCode 실행
2. 각 세션에 아래 프롬프트 전체를 붙여넣기
3. 프롬프트 마지막 줄에 검증할 플러그인 번호 입력 (예: `1`, `2`, ... `10`)

---

## 프롬프트

```
아래 지시사항을 따라 honeypot 플러그인 검증을 수행해줘.

## 사전 작업

1. **main 브랜치 최신화**: 현재 브랜치에서 main의 최신 커밋을 merge/rebase로 반영
   ```bash
   git fetch origin
   git rebase origin/main
   ```

2. **검증 대상 브랜치 확인**: 아래 번호에 해당하는 브랜치로 전환
   - 이미 해당 브랜치에 있다면 생략
   - 브랜치가 없으면 생성 후 전환

## 플러그인 번호 매핑

| 번호 | 브랜치명 | 플러그인 경로 | 구조 |
|:----:|----------|--------------|------|
| 1 | equity-research_verify | honeypot/plugins/equity-research | agents/ |
| 2 | general-agents_verify | honeypot/plugins/general-agents | agents/ |
| 3 | hwpx-converter_verify | honeypot/plugins/hwpx-converter | skills/ |
| 4 | investments-portfolio_verify | honeypot/plugins/investments-portfolio | agents/, scripts/, skills/ |
| 5 | isd-generator_verify | honeypot/plugins/isd-generator | agents/, assets/, references/, scripts/, skills/ |
| 6 | paper-style-generator_verify | honeypot/plugins/paper-style-generator | agents/, config/, scripts/, templates/ |
| 7 | report-generator_verify | honeypot/plugins/report-generator | agents/, assets/, skills/ |
| 8 | stock-consultation_verify | honeypot/plugins/stock-consultation | agents/, materials/, skills/ |
| 9 | visual-generator_verify | honeypot/plugins/visual-generator | references/, scripts/, skills/ |
| 10 | worktree-workflow_verify | honeypot/plugins/worktree-workflow | agents/ |

## 검증 항목

### 1. 구조 검증 (Structure Validation)
- [ ] 필수 디렉토리 존재 여부 확인 (agents/, skills/ 등)
- [ ] 각 agent 파일이 올바른 .md 형식인지 확인
- [ ] 각 skill 디렉토리에 SKILL.md 파일 존재 여부 확인
- [ ] assets/ 디렉토리의 템플릿 파일 유효성 확인

### 2. 참조 무결성 검증 (Reference Integrity)
- [ ] agent가 참조하는 skill이 실제로 존재하는지 확인
- [ ] agent 간 상호 참조가 유효한지 확인
- [ ] 외부 파일 참조 (경로) 가 올바른지 확인

### 3. 누락 파일 검사 (Missing Files Detection)
- [ ] agent에서 언급되었지만 존재하지 않는 skill 목록
- [ ] skill에서 참조하지만 존재하지 않는 asset 파일
- [ ] README나 문서에서 언급되었지만 없는 파일

### 4. 미사용 파일 검사 (Orphaned Files Detection)  
- [ ] 어떤 agent도 참조하지 않는 skill
- [ ] 어떤 문서도 참조하지 않는 asset 파일
- [ ] 의미 없는 중복 파일

### 5. 에이전트 품질 검증 (Agent Quality)
- [ ] 에이전트 설명(description)이 명확한지
- [ ] 필수 섹션 포함 여부 (Role, Instructions, Output 등)
- [ ] 다른 에이전트와의 역할 중복 여부
- [ ] 실행 가능한 명확한 지시사항 포함 여부

### 6. 스킬 품질 검증 (Skill Quality)
- [ ] SKILL.md 형식 준수 여부
- [ ] 스킬 설명이 명확한지
- [ ] 사용 예시가 포함되어 있는지
- [ ] 의존성이 명시되어 있는지

### 7. 의도 부합 검증 (Intent Alignment)
- [ ] 플러그인 이름과 실제 기능이 일치하는지
- [ ] 에이전트/스킬이 플러그인 목적에 부합하는지
- [ ] 불필요한 기능이 포함되어 있지 않은지

## 출력 형식

검증 완료 후 아래 형식으로 보고서 작성:

```markdown
# [플러그인명] 검증 보고서

## 요약
- 검증일시: YYYY-MM-DD HH:MM
- 플러그인: [이름]
- 상태: PASS / FAIL / WARN

## 구조 분석
### 현재 구조
(tree 형태로 출력)

### 에이전트 목록
| 에이전트 | 역할 | 상태 |
|----------|------|------|

### 스킬 목록
| 스킬 | 용도 | 상태 |
|------|------|------|

## 발견된 문제

### Critical (즉시 수정 필요)
- [ ] 문제 설명

### Warning (검토 필요)
- [ ] 문제 설명

### Info (참고)
- [ ] 정보

## 권장 조치
1. 조치 항목
2. 조치 항목

## 누락 파일 목록
(있는 경우)

## 미사용 파일 목록
(있는 경우)
```

## 작업 규칙

1. **읽기 전용 검증**: 파일 수정 없이 검증만 수행
2. **전체 검사**: 모든 파일을 빠짐없이 검사
3. **교차 검증**: agent ↔ skill 간 상호 참조 확인
4. **문서화**: 발견된 모든 문제를 명확히 기록

---

## 검증 시작

아래 번호의 플러그인을 검증해줘:

```

---

## 플러그인별 상세 정보

### 1. equity-research
- **용도**: 주식 리서치 분석
- **agents**: equity-research-analyst.md

### 2. general-agents  
- **용도**: 범용 에이전트
- **agents**: interview.md

### 3. hwpx-converter
- **용도**: HWPX(한글) 파일 변환
- **skills**: converter/, setup/

### 4. investments-portfolio
- **용도**: 퇴직연금 포트폴리오 분석
- **agents**: compliance-checker, fund-portfolio, portfolio-coordinator, macro-synthesizer, output-critic, index-fetcher, leadership-outlook, macro-critic, material-organizer, rate-analyst, risk-analyst, sector-analyst
- **skills**: analyst-common, bogle-principles, data-updater, dc-pension-rules, file-save-protocol, fund-output-template, fund-selection-criteria, macro-output-template, web-search-verifier
- **scripts**: fund data 처리 스크립트

### 5. isd-generator
- **용도**: ISD(교육설계문서) 생성
- **agents**: orchestrator, chapter1~5, figure
- **skills**: chapter1~5-guide, data-collection-guide, figure-guide, image-reference-guide, input-template, verification-rules
- **assets**: 출력 템플릿
- **references**: 참고 자료

### 6. paper-style-generator
- **용도**: 논문 스타일 생성
- **agents**: orchestrator, pdf-converter, skill-generator, style-analyzer
- **config**: 설정 파일
- **scripts**: 처리 스크립트
- **templates**: 템플릿 파일

### 7. report-generator
- **용도**: 보고서 생성
- **agents**: orchestrator, chapter-writer, content-mapper, input-analyzer, quality-checker
- **skills**: chapter-structure, field-keywords, four-step-pattern
- **assets**: 출력 템플릿

### 8. stock-consultation
- **용도**: 주식 상담/분석
- **agents**: bear-case-critic, materials-organizer, stock-consultant, stock-critic, stock-screener, stock-valuation
- **skills**: analyst-common-stock, file-save-protocol-stock, stock-data-verifier
- **materials**: 분석 자료

### 9. visual-generator
- **용도**: 시각 자료 생성
- **skills**: layout-types, prompt-concept, prompt-gov, prompt-seminar, renderer
- **references**: 레이아웃 참고 자료
- **scripts**: 생성 스크립트

### 10. worktree-workflow
- **용도**: Git worktree 워크플로우
- **agents**: worktree.md
