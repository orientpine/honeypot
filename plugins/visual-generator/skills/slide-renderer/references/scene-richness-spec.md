# Scene Richness Specification

## Overview

This document defines the minimum quality standards for Scene Description subsections in visual slide generation. A rich scene description ensures that Gemini API renders slides with proper depth, composition, and visual hierarchy.

---

## 1. Minimum Sentence Count Requirements

### Scene Description (Standard Themes) — 최소 5문장
- **Minimum: 5 sentences**
- Each sentence must describe a distinct visual element or spatial characteristic
- Sentences should cover: surface/textures, lighting, spatial composition, atmosphere, and depth

### Scene Description (Concept Theme) — 최소 7문장
- **Minimum: 7 sentences**
- Concept slides require richer descriptions due to abstract visual metaphors
- Must include: visual metaphor explanation, spatial composition, color atmosphere, depth layering, focal point, negative space guidance, and rendering constraints

---

## 2. Scene Guide: 7 Essential Elements Checklist

Every Scene Description subsection should incorporate **at least 5 of the following 7 elements**:

| Element | Description | Example |
|---------|-------------|---------|
| **서피스 (Surface/Textures)** | Material qualities, surface finishes, 3D elements, isometric icons | "Frosted glass cards with subtle texture", "Isometric 3D icons with soft shadows" |
| **배경 (Background/Atmosphere)** | Background color, gradients, atmospheric effects, lighting direction | "Bright neutral background with subtle gradient", "Soft blue-to-white gradient creating depth" |
| **코너/경계 (Corner/Boundary)** | Edge treatments, border styles, corner radius, frame composition | "Soft-rounded card boundaries", "Clean edges with 8px border radius" |
| **연결선 (Connection Flows)** | Visual connectors, flow lines, relationship indicators | "Thin, organized flow lines connecting elements", "Subtle connecting lines showing data flow" |
| **시각장식 (Visual Decorations/Props)** | Icons, mini props, decorative elements, glass layers | "Mini props and icons scattered throughout", "Glass morphism layers with transparency" |
| **공간구성 (Spatial Composition)** | Layout structure, element positioning, editorial mixing | "Editorial mix of text and 3D objects", "Balanced composition with clear focal point" |
| **시각메타포 (Visual Metaphors)** | Conceptual visual representations, symbolic imagery | "Seminar scene as flat infographic (not 3D room)", "Factory floor represented as abstract data visualization" |

**Requirement**: Include **at least 5 of these 7 elements** in every Scene Description subsection.

---

## 3. Forbidden Phrases (Information-Void Expressions)

The following phrases are **BANNED** from Scene Description subsections because they provide no actionable visual guidance:

- ❌ "clean layout"
- ❌ "professional design"
- ❌ "modern style"
- ❌ "high quality"
- ❌ "beautiful"
- ❌ "elegant"
- ❌ "clean background"
- ❌ "nice colors"
- ❌ "good composition"
- ❌ "visually appealing"

**Why**: These phrases are vague and don't guide the image generation model. Use specific, concrete descriptions instead.

**Correct approach**: Replace with specific details:
- Instead of "clean layout" → "Organized grid layout with 24px gutters and clear visual hierarchy"
- Instead of "professional design" → "Corporate color palette with navy blue (#1E3A5F) and accent teal (#4A90A4)"
- Instead of "modern style" → "Flat design with subtle shadows and glassmorphism effects"

---

## 4. Negative Prompting Guide

Negative prompting prevents unwanted rendering artifacts. Include explicit "No..." statements in Scene Description or Canvas Settings subsections.

### Standard Negative Prompts (Always Include)

```
No watermarks, no blurry text, no numbered lists rendered as visual elements, 
no artifacts, no placeholder text, no meta-labels, no Lorem ipsum, 
no distorted characters, no rendering errors
```

### Theme-Specific Negative Prompts

**For Seminar Theme:**
```
No 3D room perspective, no photorealistic people, no actual seminar room photos,
no hand-drawn elements, no sketchy lines
```

**For Concept Theme:**
```
No literal objects, no photorealism, no text rendered as image,
no numbered lists, no bullet points as visual elements
```

**For Gov Theme:**
```
No chart artifacts, no misaligned axes, no distorted numbers,
no overlapping data labels, no rendering glitches
```

### Implementation Pattern

Place negative prompts at the end of Scene Description:

```
[5+ sentences describing positive visual elements]

Rendering constraints: No watermarks, no blurry text, no artifacts, 
no placeholder text, no meta-labels. Ensure crisp, clean rendering 
of all text elements with proper character formation.
```

---

## 5. Visual Composition Principles

Every Scene Description subsection should reflect these four composition principles:

### 5.1 Rule of Thirds (삼분할 법칙)

Divide the canvas into a 3×3 grid. Place key elements at intersections or along grid lines.

```
+-------+-------+-------+
|       |       |       |
|   ●   |       |   ●   |  ● = Focal point placement
|       |       |       |
+-------+-------+-------+
|       |       |       |
|       |   ●   |       |
|       |       |       |
+-------+-------+-------+
|   ●   |       |   ●   |
|       |       |       |
|       |       |       |
+-------+-------+-------+
```

**In scene description**: "Position the hero title in the upper-left third, with supporting visuals in the right third."

### 5.2 Visual Hierarchy (시각 위계)

Establish clear priority levels for visual elements:

1. **Primary (Hero)**: Largest, most prominent, highest contrast
2. **Secondary**: Medium size, supports primary message
3. **Tertiary**: Small, supporting details, lower contrast

**In scene description**: "Title dominates the upper area (Extra-Bold, extra-large scale), section headers are secondary (Bold, medium scale), body text is tertiary (Medium, body scale)."

### 5.3 Depth Layering (전경/중경/배경 깊이)

Create visual depth through foreground, midground, and background layers:

- **Foreground**: Interactive elements, primary content, highest contrast
- **Midground**: Supporting visuals, icons, secondary information
- **Background**: Atmospheric elements, gradients, subtle textures

**In scene description**: "Foreground: bold title and hero number. Midground: isometric 3D icons and data cards. Background: soft gradient and subtle texture."

### 5.4 Focal Point Placement (초점 배치)

Guide viewer attention to the most important element:

- Use contrast (bright vs. dark)
- Use size (large vs. small)
- Use position (center, rule of thirds intersection)
- Use color (accent color vs. neutral)

**In scene description**: "The hero number (120%) is the focal point, positioned in the upper-left quadrant with maximum contrast against the background."

---

## 6. Negative Space (White Space) Density Guide

Maintain proper balance between content and empty space.

### Recommended Density

- **30-40% negative space**: Optimal for readability and visual breathing room
- **Below 30%**: Content feels cramped, reduces readability
- **Above 50%**: Content feels sparse, loses impact

### Text Density Upper Limit

- **Maximum 8-10 text items per slide** (for seminar theme)
- **Maximum 3-5 text items per slide** (for concept theme)
- **Spacing**: Minimum 16px between text elements

### Minimum Text Density Requirements

| Slide Type | Minimum CONTENT Items |
|-----------|----------------------------------|
| Body slides (data, process, comparison, analysis) | ≥ 8 items |
| Title / Cover slides (metadata: title, subtitle, presenter, event) | ≥ 3 items |

**Note**: Theme-specific upper limits remain unchanged (seminar 25, pitch 18, etc.). Prompts that fall below minimum thresholds must be supplemented with additional data points, KPI breakdowns, or specific metrics before proceeding to the renderer.
### Implementation

```
Maintain 30-40% negative space throughout the composition. 
Text elements should be spaced with minimum 16px gutters. 
Avoid clustering more than 3 text items in any single region.
```

---

## 7. Quality Grading Criteria

Use these criteria to evaluate Scene Description subsections before rendering:

### EXCELLENT Grade ✅

**All conditions met:**
- ✅ Minimum sentence count: 5+ (7+ for concept)
- ✅ Scene elements: 5+ of the 7 elements included
- ✅ No forbidden phrases used
- ✅ Negative prompting included (No watermarks, no artifacts, etc.)
- ✅ Composition principles reflected (rule of thirds, hierarchy, depth, focal point)
- ✅ Negative space guidance provided (30-40% target)
- ✅ Specific, concrete visual descriptions (not vague)
- ✅ Text density: ≥ 8 items for body slides, ≥ 3 items for title/cover slides

**Example**: "Isometric 3D icons with frosted glass cards on a bright neutral background with subtle gradient. Soft-rounded boundaries and thin connecting flow lines organize the composition. Mini props and icons create visual interest in the midground. The hero title dominates the upper-left quadrant (rule of thirds), with supporting visuals in the right third. Foreground: bold text. Midground: 3D elements. Background: gradient. Maintain 35% negative space. No watermarks, no artifacts, no placeholder text."

### GOOD Grade ⚠️

**Most conditions met:**
- ✅ Minimum sentence count: 4-5 (6-7 for concept)
- ✅ Scene elements: 3-4 of the 7 elements included
- ⚠️ Mostly specific descriptions, some vague phrases
- ⚠️ Negative prompting partially included
- ⚠️ Some composition principles reflected

**Example**: "Clean layout with modern icons and cards. Bright background with gradient. Soft corners and connecting lines. Professional design with good composition. No watermarks."

### REJECT Grade ❌

**Conditions not met:**
- ❌ Minimum sentence count: Below 4 (below 6 for concept)
- ❌ Scene elements: Fewer than 3 elements
- ❌ Forbidden phrases used (clean layout, professional design, modern style, etc.)
- ❌ No negative prompting
- ❌ Abstract or vague descriptions only
- ❌ No composition guidance

**Example**: "Beautiful modern design with nice colors and elegant layout."

---

## 8. Golden Examples

### Example 1: Smart Factory AI Quality Control System (EXCELLENT)

**Theme**: Seminar  
**Layout**: hero_number  
**Grade**: EXCELLENT  
**Rationale**: 7 sentences, all 7 scene elements, specific descriptions, negative prompting, composition principles, 25 text items

**Scene Description:**
The composition features isometric 3D icons representing AI quality control systems, rendered with frosted glass card effects and soft shadows. A bright neutral background with a subtle blue-to-white gradient creates atmospheric depth, with the gradient flowing from upper-left to lower-right. Soft-rounded card boundaries (8px radius) define distinct content regions, while thin, organized flow lines connect related elements showing data relationships. Mini props including factory icons, checkmark symbols, and data visualization elements are scattered throughout the midground, creating visual interest without clutter. The spatial composition balances editorial text with 3D objects: hero title in the upper-left quadrant (rule of thirds), supporting visuals in the right third, and data cards in the lower region. Depth layering: foreground contains the bold hero number and title (Extra-Bold, 72pt), midground holds 3D icons and secondary headers (Bold, 36pt), background features the gradient and subtle texture. The visual metaphor represents a smart factory floor as a flat infographic slide, not a 3D room perspective. Maintain 35% negative space with 16px gutters between elements. Rendering constraints: No watermarks, no blurry text, no numbered lists rendered as visual elements, no artifacts, no placeholder text, no meta-labels, no distorted characters.

**CONTENT:**
title: "Smart Factory AI Quality Control System"
subtitle: "Real-time Defect Detection & Prevention"
hero_number: "120%"
hero_label: "Accuracy Improvement"
section_1_header: "AI Detection Engine"
section_1_item_1: "Computer Vision Analysis"
section_1_item_2: "Real-time Processing"
section_1_item_3: "99.8% Accuracy Rate"
section_2_header: "Quality Metrics"
section_2_item_1: "Defect Detection: 2.3ms"
section_2_item_2: "False Positive Rate: 0.2%"
section_2_item_3: "System Uptime: 99.99%"
section_3_header: "Implementation Benefits"
section_3_item_1: "Reduced Scrap Rate"
section_3_item_2: "Faster Production Cycles"
section_3_item_3: "Lower Labor Costs"
section_4_header: "Technology Stack"
section_4_item_1: "Deep Learning Models"
section_4_item_2: "Edge Computing"
section_4_item_3: "Cloud Integration"
footer_left: "Smart Factory Initiative"
footer_right: "Q1 2024 Results"
badge_1: "ISO 9001 Certified"
badge_2: "Industry 4.0 Ready"

**Typography:**
Bold Modern Korean Sans-serif (Gothic style, Extra-Bold weight for titles, Bold for headers, Medium for body). 
Font family: Heavy-weight Gothic-style Korean sans-serif at ExtraBold (800+) weight for titles and Bold (700) weight for headers and body text. Ensure crisp character formation with no distortion.
All Korean text must be rendered with crisp, perfectly formed characters with no distortion.
Text hierarchy: Title (Extra-Bold, extra-large scale) > Section Header (Bold, medium scale) > Body (Medium, body scale) > Footer (Regular, small scale).
Line height: 1.4 for body text, 1.2 for headers.
Letter spacing: slightly wider for titles, normal for body.

**Canvas Settings:**
3840x2160 pixels, 16:9 aspect ratio.
Color palette: Primary Navy (#1E3A5F), Secondary Teal (#4A90A4), Accent Green (#2E7D5A), Neutral Light (#F5F7FA).
Background: Bright neutral (#F5F7FA) with subtle blue-to-white gradient (upper-left to lower-right).
Texture: Minimal, subtle noise (2% opacity) for depth.

**Content Placement:**
Position "Smart Factory AI Quality Control System" as large hero text in upper-left quadrant (rule of thirds intersection).
Position "120%" as oversized hero number (extra-large scale, Extra-Bold) directly below title, left-aligned.
Position "Accuracy Improvement" as hero label (body scale, Medium) below hero number.
Position "Real-time Defect Detection & Prevention" as subtitle (medium scale, Bold) in upper-right quadrant.
Create three content cards in the middle region:
  - Left card: "AI Detection Engine" header with 3 items (Computer Vision Analysis, Real-time Processing, 99.8% Accuracy Rate)
  - Center card: "Quality Metrics" header with 3 items (Defect Detection: 2.3ms, False Positive Rate: 0.2%, System Uptime: 99.99%)
  - Right card: "Implementation Benefits" header with 3 items (Reduced Scrap Rate, Faster Production Cycles, Lower Labor Costs)
Position "Technology Stack" section in lower-left with 3 items (Deep Learning Models, Edge Computing, Cloud Integration).
Position badges "ISO 9001 Certified" and "Industry 4.0 Ready" in lower-right corner.
Position footer text: "Smart Factory Initiative" (left) and "Q1 2024 Results" (right) at bottom.
Maintain consistent gutters between all elements. Use isometric 3D icons to visually separate content regions.

---

### Example 2: Concept Theme - Abstract Data Visualization (EXCELLENT)

**Theme**: Concept  
**Layout**: full_bleed  
**Grade**: EXCELLENT  
**Rationale**: 8 sentences, all 7 scene elements, concept-specific metaphor, negative prompting, composition principles, 0 text items (concept special rule)

**Scene Description:**
The composition represents a smart factory floor as an abstract data visualization landscape, with flowing geometric shapes and interconnected nodes rather than literal objects or photorealistic elements. A sophisticated color gradient flows from deep navy (#1E3A5F) in the upper-left to teal (#4A90A4) in the center, transitioning to soft green (#2E7D5A) in the lower-right, creating a sense of data flow and energy movement. Isometric 3D geometric forms—cubes, pyramids, and flowing ribbons—represent abstract concepts of production, quality, and efficiency without depicting actual factory equipment. Thin, elegant connecting lines link the geometric elements, suggesting relationships and data pathways between different system components. The spatial composition uses the rule of thirds: primary geometric cluster in the upper-left quadrant, secondary elements in the center, and accent shapes in the lower-right. Depth layering creates visual interest: foreground features bold geometric shapes with high contrast, midground contains connecting lines and smaller accent elements, background shows subtle gradient and atmospheric texture. The visual metaphor transforms a factory floor into an abstract infographic where shapes represent processes, colors represent data states, and connections represent system relationships. Maintain 40% negative space to allow the geometric elements to breathe and create visual impact. Rendering constraints: No literal objects, no photorealism, no text rendered as image, no numbered lists, no bullet points as visual elements, no watermarks, no artifacts, no placeholder text, no meta-labels.

**CONTENT:**
(Not applicable for concept theme - no text rendering)

**Typography:**
Not applicable for concept theme (no text rendering).

**Canvas Settings:**
3840x2160 pixels, 16:9 aspect ratio.
Color palette: Primary Navy (#1E3A5F), Secondary Teal (#4A90A4), Accent Green (#2E7D5A), Neutral Light (#F5F7FA).
Background: Gradient from navy (#1E3A5F) upper-left through teal (#4A90A4) center to green (#2E7D5A) lower-right.
Texture: Subtle animated-style texture suggesting data flow and movement.

**Content Placement:**
Full-bleed composition with no text elements.
Position primary geometric cluster (large cubes and pyramids) in upper-left quadrant using rule of thirds.
Position secondary geometric elements (smaller shapes and connecting lines) in the center region.
Position accent shapes and flowing ribbons in the lower-right quadrant.
Create visual flow from upper-left to lower-right using connecting lines and gradient direction.
Maintain 40% negative space throughout, allowing geometric elements to stand out against the gradient background.
Use isometric perspective consistently across all geometric elements.

---

## 9. Implementation Checklist

Before submitting a Scene Description subsection for rendering:

- [ ] Sentence count: 5+ (7+ for concept)
- [ ] Scene elements: 5+ of the 7 elements included
- [ ] No forbidden phrases (clean layout, professional design, modern style, etc.)
- [ ] Negative prompting included (No watermarks, no artifacts, etc.)
- [ ] Composition principles reflected (rule of thirds, hierarchy, depth, focal point)
- [ ] Negative space guidance provided (30-40% target)
- [ ] Specific, concrete descriptions (not vague)
- [ ] Golden example matches theme and layout
- [ ] All 4 sections present: Scene Description, CONTENT, Typography, Canvas Settings, Content Placement

---

## 10. References

- **Agent Skills Specification**: [agentskills.io/specification](https://agentskills.io/specification)
- **Visual Generator SKILL.md**: `plugins/visual-generator/skills/slide-renderer/SKILL.md`
- **Layout Types Reference**: `plugins/visual-generator/skills/layout-types/SKILL.md`
- **Theme Guides**: `plugins/visual-generator/skills/theme-*/SKILL.md`
- **Prompt Designer Agent**: `plugins/visual-generator/agents/prompt-designer.md`

---

**Document Version**: 1.0  
**Last Updated**: 2026-03-07  
**Status**: Active
