# Korean Typography Specification for Slide Rendering

## Overview
This document provides comprehensive guidelines for rendering Korean text (Hangul) in slide presentations generated via Gemini API. Korean typography requires special attention to character completeness, font weight, contrast, and legibility to ensure professional-quality output.

---

## Section 1: Mandatory Typography Directive

> ⚠️ **CRITICAL: Never include specific font family names in Typography subsection.**
> Gemini renders font names as visible text in the image (e.g., "Nanum Gothic ExtraBold" appears literally in the slide).
> Use only descriptive style hints like "heavy-weight Gothic-style sans-serif Korean font at 800+ weight".

**Use this EXACT phrase in Typography subsection when describing Korean text rendering:**

> All Korean text must be rendered with crisp, perfectly formed characters using heavy-weight Gothic-style sans-serif fonts. Each Korean syllable block must be complete and legible. Use Bold weight (700+) for titles, Medium weight (500) for body text.

This phrase encapsulates the core requirements for Korean text rendering in Gemini-generated slides. Copy it verbatim when specifying typography in Typography subsection.

---

## Section 2: Jamo Separation Prevention

### Problem: 자모 분리 (Jamo Separation)
Korean text is composed of syllable blocks (음절 블록), each containing multiple jamo (자모 - individual Korean letters). When rendering fails, syllable blocks can break apart into individual jamo, resulting in illegible text.

**Example of failure:**
- Correct: `한글` (complete syllable blocks)
- Broken: `ㅎ ㅏ ㄴ ㄱ ㅡ ㄹ` (separated jamo - unreadable)

### Prevention Strategy: 완성형 한글 (Complete Hangul)
- **Always ensure**: Korean syllable blocks are rendered as complete, unified units
- **Font requirement**: Use Gothic-style sans-serif fonts (not serif/myeongjo) which handle jamo composition better
- **Prompt hint**: Include "완성형 한글" or "each syllable as a complete block" in typography descriptions

### Anti-Patterns to Avoid
1. **Thin/Light fonts**: Weights below 400 (Regular) cause jamo separation
   - ❌ `light, elegant Korean serif font`
   - ✅ `Bold Gothic-style sans-serif (weight 700+)`

2. **Serif fonts (명조체)**: Korean serif fonts are prone to jamo separation in digital rendering
   - ❌ `Korean myeongjo (serif) font`
   - ✅ `Korean Gothic sans-serif (고딕체)`

3. **Vague font hints**: Generic descriptions don't guide Gemini toward complete syllable rendering
   - ❌ `Korean text`
   - ✅ `Heavy-weight Gothic-style sans-serif Korean font at ExtraBold (800+), each syllable as a complete block`

4. **Mixed weight without hierarchy**: Causes visual confusion and potential rendering issues
   - ❌ `Korean and English at the same weight`
   - ✅ `Korean titles in ExtraBold (800+), English subtitles in Bold (700), body text in Medium (500)`

---

## Section 3: Scene Description Level Korean Text Description

When describing Korean text elements inside Scene Description subsection, use these standardized phrases to guide Gemini toward correct rendering:

### Recommended Phrases
- **"clearly legible Korean typography"** — Emphasizes readability and completeness
- **"crisp, anti-aliased Hangul characters"** — Specifies character quality and rendering method
- **"perfectly formed Korean syllable blocks"** — Ensures jamo completeness
- **"professional-grade Korean typesetting"** — Signals high-quality rendering expectations
- **"heavy-weight Gothic-style Korean text"** — Specifies font family and weight

### Example Scene Description
```
The slide features clearly legible Korean typography with crisp Hangul characters 
against a high-contrast background. The title uses perfectly formed Korean syllable 
blocks in heavy-weight Gothic style, while body text maintains professional-grade 
typesetting with sufficient spacing and contrast.
```

### Integration with Typography Subsection
- Scene Description: Describe the visual appearance and context of Korean text
- Typography: Specify technical font parameters (weight, family, rendering hints)

Both sections should work together to ensure complete Korean text rendering.

---

## Section 4: Theme-Specific Font Weight Hierarchy

### Universal Recommendation (All 6 Themes)
Apply this weight hierarchy consistently across all slide themes:

| Text Level | Weight | Font Examples | Use Case |
|-----------|--------|----------------|----------|
| **Title** | ExtraBold / 800+ | Heavy-weight Korean Gothic sans-serif at ExtraBold (800+) | Main slide title, section headers |
| **Section Header** | Bold / 700 | Heavy-weight Korean Gothic sans-serif at Bold (700) | Subsection titles, card headers |
| **Body Text** | Medium / 500 | Korean Gothic sans-serif at Medium (500) | Main content, descriptions, labels |
| **Caption / Small Text** | Regular / 400 | Korean Gothic sans-serif at Regular (400) | Footnotes, source attribution, fine print |

### Critical Constraint: Minimum Weight = 500 (Medium)
- **Rendered text below weight 400 (Regular) may become illegible** in Gemini API output
- For body text, use weight 500 (Medium) as the minimum
- For captions, weight 400 (Regular) is acceptable only if contrast is very high
- **Never use weights below 300** (Light) for any Korean text in slides

### Font Family Recommendations
**Preferred (Heavy Gothic Sans-Serif):**
- Heavy-weight Korean Gothic sans-serif at ExtraBold (800+)
- Heavy-weight Korean Gothic sans-serif at ExtraBold (800+)
- Heavy-weight Korean Gothic sans-serif at Bold (700)
- Korean Gothic sans-serif at Bold (700)

**Avoid (Thin/Light Serif):**
- Korean myeongjo (명조체) fonts
- Any font with weight < 400
- Thin or Light variants of any Korean font

### Theme Application
Apply this hierarchy to all 6 themes:
1. **Seminar Theme**: Title (ExtraBold), Section Header (Bold), Body (Medium)
2. **Corporate Theme**: Title (ExtraBold), Section Header (Bold), Body (Medium)
3. **Academic Theme**: Title (ExtraBold), Section Header (Bold), Body (Medium)
4. **Creative Theme**: Title (ExtraBold), Section Header (Bold), Body (Medium)
5. **Minimal Theme**: Title (ExtraBold), Section Header (Bold), Body (Medium)
6. **Dark Theme**: Title (ExtraBold), Section Header (Bold), Body (Medium)

---

## Section 5: Text Legibility and Contrast Guide

### Text on Dark Background
**Requirement**: Use white or very light colors for maximum contrast

- **Recommended colors**: `#F5F7FA` (off-white), `#FFFFFF` (pure white)
- **Enhancement**: Add text-shadow or glow effect
  - Example: `"with subtle outer glow for legibility"`
  - Prompt hint: `"white Korean text with subtle outer glow against dark background"`
- **Minimum contrast ratio**: WCAG AA standard (4.5:1 for normal text, 3:1 for large text)

### Text on Light Background
**Requirement**: Use dark text for contrast

- **Recommended colors**: `#1E3A5F` (dark blue), `#2C3E50` (dark gray), `#1A1A2E` (near black)
- **Enhancement**: Ensure sufficient spacing and line-height for readability
- **Prompt hint**: `"dark Korean text on light background with professional spacing"`

### Text on Busy/Complex Background
**Requirement**: Use outline or shadow to separate text from background

- **Techniques**:
  - Drop shadow: `"with strong drop shadow for legibility"`
  - Semi-transparent backing: `"with semi-transparent backing panel behind text"`
  - Text outline: `"with subtle outline to separate from background"`
- **Prompt hint**: `"Korean text with strong drop shadow and semi-transparent backing against complex background"`

### Contrast Specification Patterns
Always explicitly specify contrast in typography prompts:

| Scenario | Prompt Pattern |
|----------|----------------|
| Dark background + light text | `"white Korean text with high contrast against dark background"` |
| Light background + dark text | `"dark Korean text with high contrast against light background"` |
| Complex background | `"Korean text with strong drop shadow and semi-transparent backing ensuring legibility"` |
| General requirement | `"Text must have sufficient contrast against background for legibility"` |
| WCAG compliance | `"high-contrast text placement ensuring WCAG AA compliance aesthetically"` |

### Minimum Contrast Ratio Guideline
- **Normal text (< 18pt)**: 4.5:1 contrast ratio (WCAG AA)
- **Large text (≥ 18pt)**: 3:1 contrast ratio (WCAG AA)
- **For Korean text in slides**: Aim for 5:1+ to account for rendering variations

---

## Section 6: Phonetic Anchoring Technique

### Definition
Phonetic anchoring is a technique where Korean text is paired with its romanized pronunciation to help Gemini render Hangul characters more accurately. This is especially useful for complex technical terms or domain-specific vocabulary.

### Format
```
한글 용어(Romanized Pronunciation)
```

**Examples:**
- `혁신적인 기술(Hyeok-sin-jeok-in Gi-sul)` — innovative technology
- `스마트 팩토리(Seu-ma-teu Paek-to-ri)` — smart factory
- `품질 관리(Pum-jil Gwal-li)` — quality control
- `자율주행(Ja-yul-ju-haeng)` — autonomous driving

### Use Cases
- **Technical/Scientific Terms**: Complex Korean vocabulary that might be rendered incorrectly
- **Domain-Specific Vocabulary**: Industry jargon in Korean
- **Compound Korean Words**: Multi-syllable words that are prone to jamo separation
- **Proper Nouns**: Company names, product names in Korean

### Placement in Prompts
1. **In Typography subsection**: Include phonetic hints for key terms
    ```
    Heavy-weight Gothic-style sans-serif Korean font at ExtraBold (800+).
    Key terms: 스마트 팩토리(Seu-ma-teu Paek-to-ri), 품질 관리(Pum-jil Gwal-li)
    ```

2. **In Scene Description**: Use phonetic anchoring for important Korean text elements
    ```
    The slide title reads "스마트 팩토리(Seu-ma-teu Paek-to-ri)" in large, bold Korean text.
    ```

### Theme-Specific Examples

**Seminar Theme:**
- `혁신적인 기술(Hyeok-sin-jeok-in Gi-sul)` — innovative technology
- `연구 결과(Yeon-gu Gyeol-gwa)` — research results

**Corporate Theme:**
- `스마트 팩토리(Seu-ma-teu Paek-to-ri)` — smart factory
- `디지털 혁신(Di-ji-tal Hyeok-sin)` — digital transformation

**Quality/Manufacturing Theme:**
- `품질 관리(Pum-jil Gwal-li)` — quality control
- `공정 최적화(Gong-jeong Choe-jeok-hwa)` — process optimization

**Autonomous Driving Theme:**
- `자율주행(Ja-yul-ju-haeng)` — autonomous driving
- `센서 기술(Sen-seo Gi-sul)` — sensor technology

---

## Section 7: Korean Rendering Anti-Pattern Examples

### Anti-Pattern 1: Generic Font Hint
**Problem**: Too vague, doesn't guide Gemini toward correct rendering

| ❌ Incorrect | ✅ Correct |
|-------------|-----------|
| `Korean text` | `Heavy-weight Gothic-style sans-serif Korean font at ExtraBold (800+)` |
| `Korean font` | `Korean Sans-serif (Gothic style, weight 700+), each syllable as a complete block` |
| `nice Korean typography` | `Professional-grade Korean typography with crisp, anti-aliased Hangul characters` |

### Anti-Pattern 2: Thin Font Request
**Problem**: Causes 자모 분리 (jamo separation) and illegibility

| ❌ Incorrect | ✅ Correct |
|-------------|-----------|
| `light, elegant Korean serif font` | `Bold Gothic-style sans-serif (weight 700+), professional and legible` |
| `thin Korean text` | `Heavy-weight Korean text (weight 500+) for clarity` |
| `delicate Korean typography` | `Crisp, bold Korean typography with complete syllable blocks` |

### Anti-Pattern 3: Mixed Language Without Hierarchy
**Problem**: Korean and English at same weight causes visual confusion and rendering issues

| ❌ Incorrect | ✅ Correct |
|-------------|-----------|
| `Korean and English text at the same size and weight` | `Korean title in ExtraBold (800+), English subtitle in Bold (700), body text in Medium (500)` |
| `bilingual text with equal emphasis` | `Korean text emphasized with heavier weight (700+), English text in supporting weight (500)` |

### Anti-Pattern 4: No Contrast Specification
**Problem**: Text becomes unreadable against background

| ❌ Incorrect | ✅ Correct |
|-------------|-----------|
| `Korean text on background` | `White Korean text with high contrast against dark background` |
| `text over image` | `Korean text with strong drop shadow and semi-transparent backing against complex background` |
| `readable Korean text` | `Dark Korean text with 5:1 contrast ratio against light background` |

### Anti-Pattern 5: Missing Syllable Completeness Hint
**Problem**: Korean characters appear as broken jamo (individual letters)

| ❌ Incorrect | ✅ Correct |
|-------------|-----------|
| `Korean text` | `Korean text with each syllable as a complete block (완성형 한글)` |
| `Hangul characters` | `Perfectly formed Korean syllable blocks (완성형 한글), each jamo properly combined` |
| `Korean typography` | `Complete Hangul typography (완성형 한글) with crisp, anti-aliased characters` |

### Anti-Pattern 6: Inconsistent Weight Hierarchy
**Problem**: Causes visual confusion and potential rendering inconsistencies

| ❌ Incorrect | ✅ Correct |
|-------------|-----------|
| `all Korean text in bold` | `Title in ExtraBold (800+), body in Medium (500), caption in Regular (400)` |
| `varying weights without pattern` | `Consistent hierarchy: Title > Section Header > Body > Caption with defined weights` |

---

## Summary: Quick Reference

### For Prompt Designers
When creating Typography subsections for Korean text:
1. **Always include**: Font weight (700+), font family (Gothic/sans-serif), syllable completeness hint
2. **Always specify**: Contrast level, background color context
3. **Consider adding**: Phonetic anchoring for technical terms
4. **Use exact phrase**: "All Korean text must be rendered with crisp, perfectly formed characters using heavy-weight Gothic-style sans-serif fonts..."

### For Renderer Agents
When rendering Korean text:
1. **Check**: Font weight ≥ 500 (Medium) for body text, ≥ 700 (Bold) for titles
2. **Verify**: Contrast ratio ≥ 4.5:1 for normal text
3. **Ensure**: Syllable blocks are complete (완성형 한글)
4. **Apply**: Phonetic anchoring for complex terms
5. **Test**: Rendered output for jamo separation or illegibility

### For Theme Developers
When defining theme typography:
1. **Specify**: Weight hierarchy (ExtraBold → Bold → Medium → Regular)
2. **Recommend**: Gothic-style sans-serif fonts with heavy weights (800+ for titles, 700+ for headers, 500+ for body)
3. **Avoid**: Serif fonts and weights below 400
4. **Document**: Contrast requirements for each background type
5. **Include**: Phonetic anchoring examples for domain-specific terms

---

## References
- [Korean Typography Best Practices](https://www.unicode.org/reports/tr37/) — Unicode Hangul Syllables
- [WCAG 2.1 Contrast Requirements](https://www.w3.org/WAI/WCAG21/Understanding/contrast-minimum.html)
- [Gemini API Image Generation Guide](https://ai.google.dev/tutorials/image_generation)
- [Korean Font Rendering in Web](https://www.w3.org/TR/css-fonts-3/)
