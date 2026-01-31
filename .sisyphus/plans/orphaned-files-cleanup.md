# Orphaned Files Cleanup Plan

## TL;DR

> **Quick Summary**: honeypot 플러그인 전체에서 orphaned 파일 13개 삭제 및 1개 참조 통합
> 
> **Deliverables**:
> - 13개 orphaned 파일 삭제
> - 1개 파일 참조 추가 (fund-portfolio.md)
> - 6개 빈 폴더 정리
> 
> **Estimated Effort**: Quick (단순 삭제 + 1개 통합)
> **Parallel Execution**: YES - 5개 플러그인 병렬 처리 가능

---

## Context

### 완료된 선행 작업 (참조용)
| Commit | 작업 내용 |
|--------|----------|
| 43d8360 | isd-generator: writing_patterns 5개 파일 참조 통합 |
| 78a22ae | visual-generator: SKILL.md self-contained 변경 |
| 6292379 | report-generator: agent files self-contained 변경 |
| 1dbdc5a | investments-portfolio: 파일 참조 업데이트 |
| 83efe38 | hwpx-converter: SKILL.md 참조 업데이트 |

### 남은 작업
선행 작업에서 SKILL.md/agent 파일을 self-contained로 변경했으나, 기존 orphaned 파일들은 삭제되지 않음.
본 계획은 해당 파일들을 정리하는 것.

---

## Work Objectives

### Core Objective
orphaned 파일 삭제 및 필수 참조 통합으로 플러그인 구조 정리

### Concrete Deliverables
1. 13개 orphaned 파일 삭제
2. fund-portfolio.md에 output-template 참조 추가
3. 빈 폴더 6개 정리

### Definition of Done
- [ ] 모든 orphaned 파일 삭제됨
- [ ] `grep -r "파일명" honeypot/plugins/` 결과 없음
- [ ] 빈 폴더 없음

### Must NOT Have
- 사용 중인 파일 삭제 금지 (paper_utils.py, linguistic_patterns.json, macro-synthesizer-template.md)
- 참조가 있는 파일 삭제 금지

---

## Execution Strategy

### Parallel Execution Waves

```
Wave 1 (참조 통합 - 먼저 실행):
└── Task 1: investments-portfolio fund-portfolio.md 참조 추가

Wave 2 (파일 삭제 - 병렬 실행):
├── Task 2: visual-generator 3개 파일 삭제
├── Task 3: report-generator 5개 파일 삭제  
├── Task 4: investments-portfolio 2개 파일 삭제
├── Task 5: paper-style-generator 2개 파일 삭제
└── Task 6: hwpx-converter 1개 파일 삭제

Wave 3 (검증):
└── Task 7: 전체 검증

Wave 4 (커밋):
└── Task 8: Git 커밋
```

---

## TODOs

### Task 1: investments-portfolio 참조 추가 (HIGH)

**What to do**:
fund-portfolio.md에 output-template 참조 추가 (writing_patterns 패턴 참조)

**변경 내용**:
```markdown
# fund-portfolio.md의 Resources 섹션에 추가

### references/ (Read 도구로 로드)

- `plugins/investments-portfolio/references/fund-portfolio-output-template.md`: 출력 구조, Markdown 템플릿, 품질 체크리스트
```

**Acceptance Criteria**:
- [ ] fund-portfolio.md에 참조 추가됨
- [ ] `grep "fund-portfolio-output-template" fund-portfolio.md` 결과 있음

---

### Task 2: visual-generator 파일 삭제 (MEDIUM)

**What to do**:
3개 prompt_style_guide.md 파일 및 빈 references 폴더 삭제

**Commands**:
```bash
rm honeypot/plugins/visual-generator/skills/prompt-concept/references/prompt_style_guide.md
rm honeypot/plugins/visual-generator/skills/prompt-gov/references/prompt_style_guide.md
rm honeypot/plugins/visual-generator/skills/prompt-seminar/references/prompt_style_guide.md
rmdir honeypot/plugins/visual-generator/skills/prompt-concept/references
rmdir honeypot/plugins/visual-generator/skills/prompt-gov/references
rmdir honeypot/plugins/visual-generator/skills/prompt-seminar/references
```

**Acceptance Criteria**:
- [ ] 3개 파일 삭제됨
- [ ] 3개 빈 폴더 삭제됨
- [ ] `ls honeypot/plugins/visual-generator/skills/*/references` 결과 없음

---

### Task 3: report-generator 파일 삭제 (MEDIUM)

**What to do**:
5개 orphaned 파일 및 빈 폴더 삭제

**Commands**:
```bash
rm honeypot/plugins/report-generator/references/field_keywords/ros2_keywords.json
rm honeypot/plugins/report-generator/references/field_keywords/general_keywords.json
rm honeypot/plugins/report-generator/references/field_keywords/ai_ml_keywords.json
rm honeypot/plugins/report-generator/references/document_templates/four_step_pattern.md
rm honeypot/plugins/report-generator/references/document_templates/chapter_structure.md
rmdir honeypot/plugins/report-generator/references/field_keywords
rmdir honeypot/plugins/report-generator/references/document_templates
rmdir honeypot/plugins/report-generator/references
```

**Acceptance Criteria**:
- [ ] 5개 파일 삭제됨
- [ ] references 폴더 완전 삭제됨
- [ ] `ls honeypot/plugins/report-generator/references` 결과 없음

---

### Task 4: investments-portfolio 파일 삭제 (MEDIUM)

**What to do**:
web-search-verifier의 2개 참조 파일 및 빈 폴더 삭제

**Commands**:
```bash
rm honeypot/plugins/investments-portfolio/skills/web-search-verifier/references/search-patterns.md
rm honeypot/plugins/investments-portfolio/skills/web-search-verifier/references/allowed-sources.md
rmdir honeypot/plugins/investments-portfolio/skills/web-search-verifier/references
```

**Acceptance Criteria**:
- [ ] 2개 파일 삭제됨
- [ ] references 폴더 삭제됨

---

### Task 5: paper-style-generator 파일 삭제 (MEDIUM)

**What to do**:
2개 references 파일 및 빈 폴더 삭제

**Commands**:
```bash
rm honeypot/plugins/paper-style-generator/references/output_structure.md
rm honeypot/plugins/paper-style-generator/references/analysis_schema.md
rmdir honeypot/plugins/paper-style-generator/references
```

**Acceptance Criteria**:
- [ ] 2개 파일 삭제됨
- [ ] references 폴더 삭제됨

---

### Task 6: hwpx-converter 파일 삭제 (MEDIUM)

**What to do**:
installation.md 파일 및 빈 폴더 삭제

**Commands**:
```bash
rm honeypot/plugins/hwpx-converter/skills/converter/references/installation.md
rmdir honeypot/plugins/hwpx-converter/skills/converter/references
```

**Acceptance Criteria**:
- [ ] 1개 파일 삭제됨
- [ ] references 폴더 삭제됨

---

### Task 7: 전체 검증 (HIGH)

**What to do**:
삭제된 파일에 대한 참조가 남아있지 않은지 확인

**Commands**:
```bash
# 삭제된 파일명으로 검색
grep -r "prompt_style_guide" honeypot/plugins/ --include="*.md" || echo "OK: no references"
grep -r "ros2_keywords\|general_keywords\|ai_ml_keywords" honeypot/plugins/ --include="*.md" || echo "OK: no references"
grep -r "four_step_pattern\|chapter_structure" honeypot/plugins/ --include="*.md" || echo "OK: no references"
grep -r "search-patterns\|allowed-sources" honeypot/plugins/ --include="*.md" || echo "OK: no references"
grep -r "output_structure\|analysis_schema" honeypot/plugins/ --include="*.md" || echo "OK: no references"
grep -r "installation\.md" honeypot/plugins/ --include="*.md" || echo "OK: no references"
```

**Acceptance Criteria**:
- [ ] 모든 grep 결과 없음 (또는 "OK: no references")

---

### Task 8: Git 커밋 (HIGH)

**Commit Message**:
```
chore(honeypot): remove orphaned reference files across 5 plugins

Plugins cleaned:
- visual-generator: 3 prompt_style_guide.md (content already in SKILL.md)
- report-generator: 5 files (keywords.json, templates.md - inline in agents)
- investments-portfolio: 2 web-search-verifier refs (duplicated in SKILL.md)
- paper-style-generator: 2 references (duplicated in agents)
- hwpx-converter: 1 installation.md (covered by SKILL.md + setup skill)

Also integrated:
- fund-portfolio.md: Added reference to output-template.md

Total: 13 files deleted, 1 reference added, 6 empty folders removed

Resolves: Orphaned files cleanup task
```

---

## Success Criteria

### Verification Commands
```bash
# 모든 orphaned 파일 삭제 확인
find honeypot/plugins -name "prompt_style_guide.md" | wc -l  # Expected: 0
find honeypot/plugins/report-generator/references -type f | wc -l  # Expected: error (folder not exist)

# 참조 추가 확인
grep -c "fund-portfolio-output-template" honeypot/plugins/investments-portfolio/agents/fund-portfolio.md  # Expected: 1

# 빈 폴더 없음 확인
find honeypot/plugins -type d -empty | wc -l  # Expected: 0
```

### Final Checklist
- [ ] 13개 orphaned 파일 삭제됨
- [ ] 1개 참조 추가됨 (fund-portfolio.md)
- [ ] 6개 빈 폴더 삭제됨
- [ ] 삭제된 파일에 대한 참조 없음
- [ ] Git 커밋 완료
