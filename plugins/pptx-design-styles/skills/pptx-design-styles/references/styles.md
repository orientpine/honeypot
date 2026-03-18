# 30 Modern PPTX Design Styles — Reference Guide

> Original source: [corazzon/pptx-design-styles](https://github.com/corazzon/pptx-design-styles) by TodayCode (오늘코드) — MIT License

Each style is documented with:
- **Background** — slide background color / gradient
- **Colors** — primary, secondary, accent with HEX values
- **Fonts** — title and body font recommendations with sizes
- **Layout** — slide composition approach
- **Signature Elements** — must-have design details for authenticity
- **Avoid** — common mistakes that break the style

---

## 01. Glassmorphism

**Mood**: Premium, tech, futuristic
**Best For**: SaaS, app launches, AI product decks

### Background
- Deep 3-color gradient: `#1A1A4E → #6B21A8 → #1E3A5F`
- Or deep single-tone blue: `#0F0F2D`

### Colors
| Role | Color | HEX |
|------|-------|-----|
| Glass card fill | White translucent | `#FFFFFF` @ 15–20% opacity |
| Glass card border | White translucent | `#FFFFFF` @ 25% opacity |
| Title text | White | `#FFFFFF` |
| Body text | Soft white | `#E0E0F0` |
| Accent | Cyan or violet | `#67E8F9` or `#A78BFA` |

### Fonts
- Title: **Segoe UI Light / Calibri Light**, 36–44pt, bold
- Body: **Segoe UI**, 14–16pt, regular
- KPI numbers: 52–64pt bold

### Layout
- **Card-based**: use frosted-glass rectangles as content containers
- Rounded corners (radius 12–20px equivalent)
- Layer cards slightly offset and rotated ±5° for depth
- Add large blurred circles/ellipses behind cards for glow effect

### Signature Elements
- Translucent card (fill 15–20%, white border 25%)
- Blurred glow blobs in background
- All containers use the same glass treatment

### Avoid
- White backgrounds (kills the effect)
- Fully opaque cards
- Bright saturated solid colors

---

## 02. Neo-Brutalism

**Mood**: Bold, raw, provocative, startup energy
**Best For**: Startup pitches, marketing campaigns, creative agencies

### Background
- High-saturation solid: Yellow `#F5F500`, Lime `#CCFF00`, Hot pink `#FF2D55`
- Or pure white `#FFFFFF`

### Colors
| Role | Color | HEX |
|------|-------|-----|
| Background | Primary yellow/lime | `#F5F500` or `#CCFF00` |
| Card fill | White or black | `#FFFFFF` / `#000000` |
| Border & shadow | Pure black | `#000000` |
| Accent | Red or blue | `#FF3B30` / `#0000FF` |
| Text | Black | `#000000` |

### Fonts
- Title: **Arial Black / Impact / Bebas Neue**, 40–56pt
- Body: **Courier New / Space Mono**, 13–16pt
- Numbers: 72–96pt Arial Black

### Layout
- **Thick black borders** on all elements (2–4pt solid black)
- **Hard offset shadow** bottom-right of every card (5–8pt, no blur)
- Slight intentional misalignment — tilted shapes allowed

### Signature Elements
- Hard drop shadow (no blur, pure black offset)
- Thick border on every element
- One oversized number or word breaking the layout

### Avoid
- Soft shadows or gradients
- Rounded corners
- Pastel or muted colors

---

## 03. Bento Grid

**Mood**: Modular, informational, Apple-inspired
**Best For**: Feature comparisons, product overviews, data summaries

### Background
- Near-white: `#F8F8F2` or `#F0F0F0`

### Colors
| Role | Color | HEX |
|------|-------|-----|
| Background | Off-white | `#F8F8F2` |
| Cell 1 (dark) | Deep navy | `#1A1A2E` |
| Cell 2 (accent 1) | Bright yellow | `#E8FF3B` |
| Cell 3 (accent 2) | Coral red | `#FF6B6B` |
| Cell 4 (accent 3) | Teal | `#4ECDC4` |
| Cell 5 (warm) | Warm yellow | `#FFE66D` |

### Fonts
- Cell title: **SF Pro / Inter**, 18–24pt, semibold
- Cell body: **Inter**, 12–14pt, regular
- Large stat: 48–64pt bold in dark cell

### Layout
- CSS Grid-style layout: cells of different sizes spanning columns/rows
- Gap between cells: 8–12pt equivalent
- **Asymmetric merging**: one cell spans 2 columns, one spans 2 rows
- Each cell has one focused piece of info

### Signature Elements
- Asymmetric multi-size grid
- One dark anchor cell with white text
- Color-coded cells for visual hierarchy

### Avoid
- Equal-sized cells (boring)
- Too many colors (max 5)
- Dense text inside cells

---

## 04. Dark Academia

**Mood**: Scholarly, vintage, refined, literary
**Best For**: Education, historical research, book presentations, university talks

### Background
- Deep warm dark brown: `#1A1208`
- Or `#0E0A05` for maximum drama

### Colors
| Role | Color | HEX |
|------|-------|-----|
| Background | Deep warm brown | `#1A1208` |
| Title text | Antique gold | `#C9A84C` |
| Body text | Warm parchment | `#D4BF9A` |
| Border / ornament | Dark gold | `#3D2E10` |
| Accent | Muted gold | `#8A7340` |

### Fonts
- Title: **Playfair Display Italic / Georgia Italic**, 36–48pt
- Body: **EB Garamond / Georgia**, 13–16pt
- Label: **Space Mono**, 9–11pt, wide letter-spacing

### Layout
- **Inset border frame** — thin gold border 12–20pt from slide edge
- Centered title with wide letter-spacing (6–10pt)
- Body text in serif, generous leading (1.6–1.8)
- Decorative horizontal rule line (thin, gold tint)

### Signature Elements
- Double inset border (outer + inner, slightly different widths)
- Italic serif title in gold
- Monospace footnote or date in muted gold

### Avoid
- Modern sans-serif fonts
- Bright or saturated colors
- Clean minimal layouts — add texture and decoration

---

## 05. Gradient Mesh

**Mood**: Artistic, vibrant, sensory, brand-forward
**Best For**: Brand launches, creative portfolios, music/film promotions

### Background
- Multi-point radial gradient blend (4–6 colors overlapping)
- Example: `#FF6EC7` + `#7B61FF` + `#00D4FF` + `#FFB347` bleeding into each other

### Colors
| Role | Color | HEX |
|------|-------|-----|
| Mesh node 1 | Hot pink | `#FF6EC7` |
| Mesh node 2 | Violet | `#7B61FF` |
| Mesh node 3 | Cyan | `#00D4FF` |
| Mesh node 4 | Warm orange | `#FFB347` |
| Text | Pure white | `#FFFFFF` |

### Fonts
- Title: **Bebas Neue / Barlow Condensed ExtraBold**, 48–72pt
- Body: **Outfit / Poppins Light**, 14–16pt
- All text white with subtle drop shadow for legibility

### Layout
- Full-bleed gradient as background
- Minimal text overlay — let the gradient breathe
- Large centered title, small subtitle below
- Optional: frosted glass card for body text

### Signature Elements
- Multi-radial gradient that feels painterly, not linear
- White text with drop shadow
- Large typographic element dominating

### Avoid
- Linear two-color gradients (too plain)
- Dark or muted text
- Overcrowded layouts

---

## 06. Claymorphism

**Mood**: Friendly, soft 3D, tactile, playful
**Best For**: Product launches, education, children's content, app UI decks

### Background
- Warm pastel gradient: `#FFECD2 → #FCB69F` or `#E0F7FA → #B2EBF2`

### Colors
| Role | Color | HEX |
|------|-------|-----|
| Background | Warm peach gradient | `#FFECD2` → `#FCB69F` |
| Clay element 1 | Soft teal | `#A8EDEA` |
| Clay element 2 | Blush pink | `#FED6E3` |
| Clay element 3 | Warm yellow | `#FFEAA7` |
| Shadow | Color-matched shadow | element color @ 50%, offset 8–12pt down |

### Fonts
- Title: **Nunito ExtraBold / Rounded Mplus**, 32–48pt
- Body: **Nunito / DM Sans**, 14–16pt
- Icon labels: 11–13pt medium

### Layout
- **3D rounded shapes** as primary containers (radius 20–32pt equivalent)
- Each element casts a **colored drop shadow** (same hue, shifted down, no X offset)
- Inner highlight on top edge (white, 30% opacity)
- Playful asymmetric arrangement of clay bubbles

### Signature Elements
- Colored soft shadow (not grey) matching element color
- Very high border radius
- Inner highlight stripe at top of each element

### Avoid
- Sharp corners
- Grey/neutral shadows
- Flat design elements mixed in

---

## 07. Swiss International Style

**Mood**: Functional, authoritative, timeless, corporate
**Best For**: Consulting, finance, government, institutional presentations

### Background
- Pure white: `#FFFFFF`
- Or off-white: `#FAFAFA`

### Colors
| Role | Color | HEX |
|------|-------|-----|
| Background | White | `#FFFFFF` |
| Primary text | Near-black | `#111111` |
| Accent bar | Signal red | `#E8000D` |
| Secondary text | Dark grey | `#444444` |
| Divider line | Light grey | `#DDDDDD` |

### Fonts
- Title: **Helvetica Neue Bold / Arial Bold**, 32–44pt, tight leading
- Body: **Helvetica Neue / Arial**, 12–14pt
- Labels/captions: **Space Mono**, 9–10pt, 3–4pt letter-spacing

### Layout
- Strict **5-column or 12-column grid** — every element snaps to columns
- **Vertical red rule** on left edge (4–8pt wide stripe)
- Single horizontal divider rule at mid-slide
- Circle accent element (red outline) in lower-right zone

### Signature Elements
- Left-edge vertical red bar
- Horizontal rule dividing title from content
- Grid-aligned text blocks with generous margins

### Avoid
- Decorative or illustrative elements
- Rounded corners
- More than 2 fonts

---

## 08. Aurora Neon Glow

**Mood**: Futuristic, AI, electric, otherworldly
**Best For**: AI products, cybersecurity, deep tech, innovation summits

### Background
- Near-black deep space: `#050510` or `#020208`

### Colors
| Role | Color | HEX |
|------|-------|-----|
| Background | Deep space black | `#050510` |
| Glow 1 | Neon green | `#00FF88` |
| Glow 2 | Electric violet | `#7B00FF` |
| Glow 3 | Cyan | `#00B4FF` |
| Title gradient | Green → cyan → violet | multi-stop |
| Body text | Soft white | `#D0D0F0` |

### Fonts
- Title: **Bebas Neue / Barlow Condensed**, 44–60pt, wide letter-spacing 4–8pt
- Body: **DM Mono / Space Mono**, 12–14pt
- Gradient text clip on title

### Layout
- Large blurred glow blobs (filter blur 30–50pt) in background corners
- Centered or left-aligned title with gradient text effect
- Body on semi-transparent dark panel
- Optional scan-line texture overlay (5% opacity)

### Signature Elements
- Blurred neon glow circles (not sharp shapes)
- Gradient text (green → cyan → violet)
- Dark panel for body text legibility

### Avoid
- White or light backgrounds
- Solid non-glowing colors
- Dense body text without panels

---

## 09. Retro Y2K

**Mood**: Nostalgic, pop, chaotic fun, millennium energy
**Best For**: Events, lifestyle marketing, fashion, creative campaigns

### Background
- Navy blue: `#000080`
- Or electric blue: `#0020C2`

### Colors
| Role | Color | HEX |
|------|-------|-----|
| Background | Navy | `#000080` |
| Rainbow stripe | Full spectrum | gradient: `#FF0080 → #FFFF00 → #00FF00 → #00FFFF → #0000FF → #FF00FF` |
| Title text | White | `#FFFFFF` |
| Title glow | Cyan + magenta shadow | `#00FFFF` / `#FF00FF` |
| Star accent | Yellow | `#FFFF00` |

### Fonts
- Title: **Bebas Neue / Impact**, 36–52pt
- Body: **VT323 / Space Mono**, 12–14pt
- Double text shadow: 2px cyan + 2px magenta offset

### Layout
- **Rainbow stripe bars** top and bottom (6–8pt height)
- Star/sparkle icons in corners (✦ ★)
- Title centered with double text shadow
- Optional: spinning star animation placeholder

### Signature Elements
- Rainbow gradient stripe bars
- Double-color text shadow (cyan + magenta)
- Star/sparkle motifs

### Avoid
- Minimalist layouts
- Muted or desaturated colors
- Serif fonts

---

## 10. Nordic Minimalism

**Mood**: Calm, natural, considered, Scandinavian
**Best For**: Wellness, lifestyle, non-profit, sustainable brands

### Background
- Warm cream: `#F4F1EC` or `#F0EDE8`

### Colors
| Role | Color | HEX |
|------|-------|-----|
| Background | Warm cream | `#F4F1EC` |
| Organic shape | Warm grey | `#D9CFC4` |
| Primary text | Dark warm brown | `#3D3530` |
| Secondary text | Taupe | `#8A7A6A` |
| Accent dot | Deep brown | `#3D3530` |

### Fonts
- Title: **Canela / Freight Display / DM Serif Display**, 36–52pt, light weight
- Body: **Inter Light / Lato Light**, 13–15pt
- Caption: **Space Mono**, 9–10pt, 4–6pt letter-spacing

### Layout
- **Generous whitespace** — at least 40% of slide is empty
- One organic blob shape as background texture (low opacity, grey-beige)
- Minimal dot accent (3 dots in different brown tones) top-left corner
- Thin horizontal rule near bottom, then caption text

### Signature Elements
- Organic blob background shape
- 3-dot color accent
- Wide letter-spacing caption in monospace

### Avoid
- Bright or saturated colors
- Dense text or busy layouts
- Sans-serif display fonts (use serif or editorial)

---

## 11. Typographic Bold

**Mood**: Editorial, impactful, design-driven, authoritative
**Best For**: Brand statements, manifestos, headline announcements

### Background
- Off-white linen: `#F0EDE8`
- Or pure black: `#0A0A0A` (inverted version)

### Colors
| Role | Color | HEX |
|------|-------|-----|
| Background | Off-white | `#F0EDE8` |
| Primary type | Near-black | `#1A1A1A` |
| Accent word | Signal red | `#E63030` |
| Footnote | Light grey | `#AAAAAA` |

### Fonts
- Oversized display: **Bebas Neue / Anton**, 80–120pt, tight tracking (-2pt)
- Accent word: different color, same font
- Body (if any): **Space Mono**, 9pt, wide spacing

### Layout
- **Type fills the slide** — no illustrations or photos
- 2–3 lines maximum, massive scale
- One word or phrase in accent color
- Tiny footnote/label bottom-right in monospace

### Signature Elements
- Oversized type (80pt+) as the main visual
- Single accent color word breaking the monochrome
- Almost no margins — type bleeds toward edges

### Avoid
- Images or icons (type IS the design)
- More than 3 lines of large text
- Mixing multiple font families

---

## 12. Duotone / Color Split

**Mood**: Dramatic, comparative, energetic, bold
**Best For**: Strategy decks, before/after, compare/contrast slides

### Background
- Left half: vivid orange-red `#FF4500`
- Right half: deep navy `#1A1A2E`

### Colors
| Role | Color | HEX |
|------|-------|-----|
| Left panel | Orange-red | `#FF4500` |
| Right panel | Deep navy | `#1A1A2E` |
| Divider | White | `#FFFFFF` |
| Left text | White | `#FFFFFF` |
| Right text | Matches left panel color | `#FF4500` |

### Fonts
- Panel text: **Bebas Neue**, 40–56pt, vertical writing-mode optional
- Caption: **Space Mono**, 9pt

### Layout
- Strict **50/50 vertical split** with white divider line (2–4pt)
- Each panel shows one concept, one word, or one data point
- Text in left panel = white; text in right panel = left panel color
- Optional: diagonal split instead of vertical

### Signature Elements
- Exact 50/50 split
- White divider line
- Cross-panel color echo (right text = left panel color)

### Avoid
- Three or more color panels
- Similar hues (needs strong contrast)
- Busy content — one idea per panel

---

## 13. Monochrome Minimal

**Mood**: Restrained, luxury, precise, gallery-like
**Best For**: Luxury brands, portfolio, art direction, high-end consulting

### Background
- Near-white: `#FAFAFA`
- Or jet black: `#0A0A0A` (dark variant)

### Colors
| Role | Color | HEX |
|------|-------|-----|
| Background | Near-white | `#FAFAFA` |
| Heavy type | Near-black | `#1A1A1A` |
| Thin rule/border | Light grey | `#E0E0E0` |
| Medium element | Mid grey | `#888888` |
| Footnote | Pale grey | `#CCCCCC` |

### Fonts
- Display: **Helvetica Neue Thin / Futura Light**, 24–36pt, extreme letter-spacing (8–12pt)
- Body: **Helvetica Neue**, 11–13pt, 150% line height
- Accent: **Space Mono**, 9pt

### Layout
- Single thin circle outline centered (decorative, not functional)
- Width-varying bars (120pt, 80pt, 40pt) as visual hierarchy stand-in
- All elements centered or left-aligned — never right
- Extreme negative space

### Signature Elements
- Thin circle outline as focal point
- Descending-width bars (weight hierarchy without font changes)
- Monospace caption with wide spacing

### Avoid
- Any color (pure monochrome only)
- Decorative illustration or pattern
- Crowded layouts

---

## 14. Cyberpunk Outline

**Mood**: HUD interface, sci-fi, dark tech, surveillance
**Best For**: Gaming, AI infrastructure, security, data engineering decks

### Background
- Near-black: `#0D0D0D`

### Colors
| Role | Color | HEX |
|------|-------|-----|
| Background | Near-black | `#0D0D0D` |
| Grid lines | Neon cyan | `#00FFC8` @ 6% opacity |
| Outline text | Transparent fill | stroke `#00FFC8`, 1.5pt |
| Glow | Neon cyan | `#00FFC8` @ 50% blur glow |
| Corner marks | Neon cyan | `#00FFC8` @ 60% |
| Subtext | Neon cyan | `#00FFC8` @ 50% |

### Fonts
- Title: **Bebas Neue**, 44–60pt, letter-spacing 6–8pt, **outline text** (no fill, colored stroke)
- Body: **Space Mono**, 9–11pt
- Data labels: **Space Mono**, 8pt, wider spacing

### Layout
- Subtle dot-grid or line-grid background (6% opacity)
- **Corner bracket markers** (L-shaped, 20pt, neon) in all 4 corners
- Title centered with outline stroke effect
- Bottom subtext label

### Signature Elements
- Outline (stroke-only) text for title
- Four corner bracket markers
- Grid overlay background

### Avoid
- White backgrounds
- Filled (non-outline) title text
- Bright, warm colors

---

## 15. Editorial Magazine

**Mood**: Journalistic, narrative, sophisticated
**Best For**: Annual reports, brand stories, long-form content decks

### Background
- White `#FFFFFF` with dark block

### Colors
| Role | Color | HEX |
|------|-------|-----|
| Background (main) | White | `#FFFFFF` |
| Dark block | Near-black | `#1A1A1A` |
| Title | Near-black | `#1A1A1A` |
| Rule line | Signal red | `#E63030` |
| Caption | Light grey | `#BBBBBB` |

### Fonts
- Title: **Playfair Display Italic**, 34–48pt
- Subhead: **Space Mono**, 8–9pt, 2–3pt letter-spacing
- Body: **Georgia**, 11–13pt

### Layout
- **Asymmetric two-zone layout**: left 55% white with text, right 45% dark block
- Large italic serif title upper-left
- Thin red horizontal rule (2pt) below title, 60pt wide
- Vertical label text rotated 90° in dark zone
- Column-style body text bottom-left

### Signature Elements
- Asymmetric white/dark split
- Short red rule line under title
- Rotated vertical label text in dark zone

### Avoid
- Symmetric or centered layouts
- Sans-serif display fonts
- Full-bleed colored backgrounds

---

## 16. Pastel Soft UI

**Mood**: Gentle, modern app, healthcare-friendly
**Best For**: Healthcare, beauty, education startups, consumer apps

### Background
- Soft tricolor gradient: `#FCE4F3 → #E8F4FF → #F0FCE4`

### Colors
| Role | Color | HEX |
|------|-------|-----|
| Background | Soft tricolor gradient | pink → blue → mint |
| Card fill | White semi-transparent | `#FFFFFF` @ 70% |
| Card border | White | `#FFFFFF` @ 90% |
| Dot accent 1 | Blush pink | `#F9C6E8` |
| Dot accent 2 | Sky blue | `#C6E8F9` |

### Fonts
- Title: **Nunito Bold / DM Sans Medium**, 28–36pt
- Body: **Nunito / DM Sans**, 13–15pt
- Labels: **Inter**, 11pt

### Layout
- Floating frosted-white cards on gradient background
- Large circle card (pill shape) as central element
- Small decorative blobs in opposite corners
- Cards have soft colored box-shadows (color-matched to blobs)

### Signature Elements
- Frosted white card (70% opacity, white border)
- Pastel tricolor gradient background
- Soft color-matched shadows

### Avoid
- Dark backgrounds
- Saturated or primary colors
- Hard drop shadows

---

## 17. Dark Neon Miami

**Mood**: Synthwave, 80s nostalgia, hedonistic neon
**Best For**: Entertainment, music festivals, events, nightlife brands

### Background
- Deep purple-black: `#0A0014`

### Colors
| Role | Color | HEX |
|------|-------|-----|
| Background | Deep purple-black | `#0A0014` |
| Sunset semicircle | Orange → hot pink | `#FF6B35 → #FF0080` |
| Title gradient | Orange → pink → purple | `#FF6B35 → #FF0080 → #9B00FF` |
| Grid lines | Hot pink transparent | `#FF0080` @ 15–40% |

### Fonts
- Title: **Bebas Neue**, 36–52pt, letter-spacing 6–8pt
- Body: **Space Mono**, 11–13pt
- All text white or gradient

### Layout
- **Horizon semicircle** (sunset) in lower-center third
- Perspective grid lines converging toward horizon (4–6 lines)
- Title positioned top-center
- Palm tree or geometric accent in lower corners (optional)

### Signature Elements
- Sunset semicircle gradient shape
- Converging perspective grid
- Gradient text (orange → pink → purple)

### Avoid
- Cool color palettes (blue/green dominant)
- Daylight or bright backgrounds
- Sans-serif body text

---

## 18. Hand-crafted Organic

**Mood**: Artisanal, natural, human, sustainable
**Best For**: Eco brands, food/beverage, craft studios, wellness

### Background
- Craft paper warm off-white: `#FDF6EE`

### Colors
| Role | Color | HEX |
|------|-------|-----|
| Background | Warm craft paper | `#FDF6EE` |
| Dashed circle (outer) | Light tan | `#C8A882` |
| Solid circle (inner) | Medium brown | `#A87850` |
| Title text | Dark warm brown | `#6B4C2A` |
| Leaf/flora accents | Natural greens | emoji or illustration |

### Fonts
- Title: **Playfair Display Italic / Cormorant Garamond Italic**, 22–34pt
- Body: **EB Garamond**, 13–15pt
- Caption: **Courier New**, 9pt

### Layout
- **Nested circles**: outer dashed + inner solid, slightly off-center or rotated
- Botanical emoji or line-art leaf accents in corners
- Dashed horizontal rule spanning slide
- Italic serif title centered within circles

### Signature Elements
- Dashed outer circle (imperfect, rotated 5–10°)
- Nested solid inner circle
- Botanical/leaf accent elements

### Avoid
- Clean geometric shapes
- Bright or synthetic colors
- Sans-serif fonts

---

## 19. Isometric 3D Flat

**Mood**: Technical clarity, structured, architectural
**Best For**: IT architecture, data flow, system diagrams, infrastructure

### Background
- Dark navy: `#1E1E2E`

### Colors
| Role | Color | HEX |
|------|-------|-----|
| Background | Dark navy | `#1E1E2E` |
| Top face | Mid violet | `#7C6FFF` |
| Left face | Dark violet | `#4A3FCC` |
| Right face | Medium violet | `#6254E8` |
| Top face 2 (highlight) | Light violet | `#A594FF` |

### Fonts
- Labels: **Space Mono**, 10–12pt, white
- Title: **Bebas Neue / Barlow Condensed**, 28–40pt, white

### Layout
- Isometric (30° angle) 3D block shapes — two or three stacked cubes
- Blocks assembled left-center, title upper-right
- Thin connecting lines or arrows between blocks (for diagrams)
- All shapes share the same 3-face color system (top lighter, sides darker)

### Signature Elements
- Strict isometric angle (30°/60°)
- 3-face shading system (top, left, right faces)
- Dark navy background contrast

### Avoid
- Perspective 3D (use isometric only)
- Rounded shapes
- Light or white backgrounds

---

## 20. Vaporwave

**Mood**: Dreamy, nostalgic internet aesthetics, surreal
**Best For**: Creative agencies, music/art portfolios, subculture brands

### Background
- Dark purple gradient: `#1A0533 → #2D0057 → #570038`

### Colors
| Role | Color | HEX |
|------|-------|-----|
| Background | Deep purple | `#1A0533 → #570038` |
| Sun gradient | Orange → pink → violet | `#FF9F43 → #FF6B9D → #C44DFF` |
| Grid lines | Pink transparent | `#FF64C8` @ 40% |
| Gradient text | Orange → pink → violet | same as sun |
| Ghost title | White very low opacity | `#FFFFFF` @ 8% |

### Fonts
- Ghost title: **Bebas Neue**, 38–52pt, 6pt spacing, near-invisible
- Gradient text: **Bebas Neue**, 24–34pt
- Body: **Space Mono**, 10pt

### Layout
- **Perspective grid** in lower 60% (horizontal + vertical lines converging)
- Semicircle sun top-center, sliced by 2 horizontal bars (background color)
- Ghost watermark text near sun area
- Gradient text at bottom

### Signature Elements
- Sliced sunset semicircle (sun with stripes)
- Perspective grid floor
- Ghost/watermark title text

### Avoid
- Clean or corporate layouts
- Muted or warm earth tones
- Readable "normal" typography style

---

## 21. Art Deco Luxe

**Mood**: 1920s grandeur, gilded, prestigious
**Best For**: Luxury brands, gala events, premium annual reports, high-end hospitality

### Background
- Deep black-brown: `#0E0A05`

### Colors
| Role | Color | HEX |
|------|-------|-----|
| Background | Deep black-brown | `#0E0A05` |
| Border / ornament | Antique gold | `#B8960C` |
| Title text | Rich gold | `#D4AA2A` |
| Subtitle | Muted gold | `#8A7020` |
| Diamond accent | Bright gold | `#B8960C` |

### Fonts
- Title: **Cormorant Garamond / Trajan / Didot**, 26–36pt, wide letter-spacing 6–10pt
- Caption: **Space Mono**, 9pt, 4–5pt letter-spacing
- All text uppercase

### Layout
- **Double inset gold border** frame (outer full, inner slightly inset)
- **Fan / quarter-circle ornaments** in left and right mid-edge
- Thin horizontal gold rule at vertical center
- Diamond (rotated square) at rule-center intersection
- Title centered, uppercase, wide-spaced

### Signature Elements
- Double inset border frame (two concentric rectangles)
- Fan ornaments on sides
- Diamond divider at center rule
- ALL CAPS wide letter-spaced serif

### Avoid
- Modern sans-serif fonts
- Colorful or pastel tones
- Asymmetric layouts

---

## 22. Brutalist Newspaper

**Mood**: Editorial authority, raw journalism, confrontational
**Best For**: Media companies, research institutes, content industry decks

### Background
- Aged paper off-white: `#F2EFE8`

### Colors
| Role | Color | HEX |
|------|-------|-----|
| Background | Aged paper | `#F2EFE8` |
| Masthead bar | Deep warm black | `#1A1208` |
| Masthead text | Off-white | `#F2EFE8` |
| Body text | Dark warm brown | `#3A3020` |
| Column divider | Deep warm black | `#1A1208` |

### Fonts
- Masthead: **Space Mono Bold**, 12–14pt, tight
- Headline: **Georgia Bold / Playfair Display Bold**, 20–28pt
- Body: **Georgia**, 9–11pt, 1.5 line height
- Date/label: **Space Mono**, 7–9pt, 1pt letter-spacing

### Layout
- **Dark masthead bar** full-width at top (newspaper nameplate)
- Double rule lines below masthead (3pt + 1pt)
- **Two-column layout** with vertical divider rule
- Left: headline + body text; Right: photo placeholder + caption

### Signature Elements
- Newspaper masthead bar
- Double rule below masthead
- Two-column layout with divider
- Italic serif headline

### Avoid
- Modern sans-serif fonts
- Colorful elements
- Clean white space (embrace density)

---

## 23. Stained Glass Mosaic

**Mood**: Vibrant, artistic, cathedral richness
**Best For**: Cultural institutions, museums, arts organizations, creative festivals

### Background
- Near-black grid frame: `#0A0A12`

### Colors
| Role | Color | HEX |
|------|-------|-----|
| Background | Near-black (grout) | `#0A0A12` |
| Cell 1 | Deep royal blue | `#1A3A6E` |
| Cell 2 | Crimson | `#E63030` |
| Cell 3 | Golden yellow | `#F5D020` |
| Cell 4 | Forest green | `#2A6E1A` |
| Cell 5 | Deep purple | `#6E1A4E` |
| Overlay | Dark translucent | `#000000` @ 30% |

### Fonts
- Title overlay: **Cormorant Garamond Bold / Trajan**, 16–22pt, wide spacing
- Body (below mosaic): **Georgia**, 13–15pt

### Layout
- **6×4 (or similar) mosaic grid** covering full slide — 2pt dark gap between cells
- Cells vary in color following a stained-glass color rhythm
- Semi-transparent dark overlay to darken and unify
- Slide title rendered as overlay text at bottom (light, wide-spaced)

### Signature Elements
- Dark "grout" gaps between all cells
- No two adjacent cells the same color
- Translucent overlay for text legibility

### Avoid
- Pastel or muted cell colors
- Large empty cells
- Sans-serif overlay text

---

## 24. Liquid Blob Morphing

**Mood**: Organic, fluid, living, bio-digital
**Best For**: Biotech, environmental tech, innovation labs, wellness brands

### Background
- Deep ocean gradient: `#0F2027 → #203A43 → #2C5364`

### Colors
| Role | Color | HEX |
|------|-------|-----|
| Background | Deep ocean | `#0F2027 → #2C5364` |
| Blob 1 | Teal glow | `#00D2BE` @ 35% |
| Blob 2 | Electric blue | `#0078FF` @ 30% |
| Blob 3 | Violet | `#7800FF` @ 25% |
| Title | White / near-white | `#F0FFFE` |
| Glow | Teal | `#00D2BE` radial glow |

### Fonts
- Title: **Bebas Neue**, 36–48pt, 6pt letter-spacing
- Body: **DM Mono / Space Mono**, 12–14pt
- All text white

### Layout
- 3 large blurred blob shapes positioned asymmetrically (corners + center)
- Blobs overlap with `multiply` or `screen` blend mode effect
- Title centered with teal text glow
- Optional: animated morphing border-radius effect

### Signature Elements
- Three overlapping blurred blobs (low opacity)
- Ocean-depth dark background
- Glowing white text with colored halo

### Avoid
- Sharp geometric shapes
- Bright or warm backgrounds
- Dense text content

---

## 25. Memphis Pop Pattern

**Mood**: Energetic, retro-contemporary, anti-minimalist
**Best For**: Fashion brands, lifestyle products, retail, youth marketing

### Background
- Warm off-white: `#FFF5E0`

### Colors
| Role | Color | HEX |
|------|-------|-----|
| Background | Warm off-white | `#FFF5E0` |
| Triangle accent | Crimson red | `#E8344A` |
| Circle outline | Royal blue | `#1E90FF` |
| Zigzag bar | Crimson red | `#E8344A` |
| Dot accent | Mint green | `#22BB88` |
| Star/triangle 2 | Golden yellow | `#FFD700` |

### Fonts
- Title: **Bebas Neue / Futura ExtraBold**, 32–44pt
- Body: **Futura / DM Sans**, 12–14pt

### Layout
- **Scattered geometric shapes** (triangles, circles, dots, zigzags) across slide
- No central focal point — distribute shapes with intentional asymmetry
- Title placed over a slightly cleared zone in center
- One zigzag bar cuts horizontally across the middle third

### Signature Elements
- Triangles, circles, dots, and zigzag bar all present
- Warm off-white background (not pure white or dark)
- Shapes feel random but are intentionally balanced

### Avoid
- Minimalist compositions
- Monochromatic palettes
- Modern/clean fonts

---

## 26. Dark Forest Nature

**Mood**: Mysterious, atmospheric, primal, eco-premium
**Best For**: Environmental brands, adventure/outdoor, sustainable luxury, conservation

### Background
- Radial dark gradient: `#0D2B14` center → `#060E08` edges

### Colors
| Role | Color | HEX |
|------|-------|-----|
| Background | Deep forest black | `#060E08` |
| Tree silhouettes | Dark forest green | `#0A3D1A` → `#0D4D20` |
| Moon | Pale sage glow | `#E8F4D0` → `#B8CC80` |
| Stars | Pale green-white | `#D4F0B0` |
| Mist glow | Soft mint | `#B4FFC8` @ 4% |
| Title text | Sage-white italic | `rgba(200,255,180,0.85)` |

### Fonts
- Title: **Playfair Display Italic / DM Serif Display Italic**, 20–28pt
- Body: **EB Garamond**, 13–15pt
- Caption: **Space Mono**, 9pt, wide spacing

### Layout
- **Tree silhouettes** rising from bottom — triangular/fir shapes, 3+ overlapping depths
- **Moon** top-right with soft radial glow
- Star dots scattered sparingly in upper half
- Mist gradient rising from bottom over trees
- Italic serif title near bottom (above mist)

### Signature Elements
- Layered tree silhouettes (3+ depths)
- Glowing moon top-right
- Fog/mist gradient overlay
- Italic serif text in sage-white

### Avoid
- Bright greens (use near-black forest tones)
- Hard edges on tree shapes
- Sans-serif fonts

---

## 27. Architectural Blueprint

**Mood**: Precise, technical, professional, structured
**Best For**: Architecture, urban planning, engineering, spatial design firms

### Background
- Blueprint blue: `#0D2240`

### Colors
| Role | Color | HEX |
|------|-------|-----|
| Background | Blueprint navy | `#0D2240` |
| Fine grid | Cyan-white | `#64B4FF` @ 12% |
| Major grid | Cyan-white | `#64B4FF` @ 22% |
| Shape lines | Blueprint line | `#64C8FF` @ 60% |
| Dimension text | Blueprint text | `#64C8FF` @ 60% |
| Title | Blueprint white | `#96DCFF` @ 80% |

### Fonts
- All text: **Space Mono**, 8–12pt (no exceptions — monospace only)
- Dimension annotations: 8pt
- Title: 11–13pt, 4pt letter-spacing
- Stamp: 8pt, multiline

### Layout
- **Fine grid** (20pt) + **major grid** (60pt) layered
- One or two geometric shapes with dimensions and annotation marks
- Arrow dimension lines between key points
- Circular stamp element (right side, mid-height)
- Title as full-width label at bottom

### Signature Elements
- Dual grid (fine + major)
- Dimension lines with annotation text
- Circular blueprint stamp

### Avoid
- Color or decorative elements
- Non-monospace fonts
- Photographic elements

---

## 28. Maximalist Collage

**Mood**: Chaotic energy, irreverent, advertising-bold
**Best For**: Advertising agencies, fashion brands, music promotions, editorial

### Background
- Warm antique cream: `#E8DDD0` with diagonal pattern overlay

### Colors
| Role | Color | HEX |
|------|-------|-----|
| Background | Antique cream | `#E8DDD0` |
| Block 1 | Bold red | `#E83030` |
| Block 2 | Near-black | `#1A1A1A` |
| Block 3 | Acid yellow | `#F5D020` |
| Text on red | White | `#FFFFFF` |
| Text on black | White | `#FFFFFF` |

### Fonts
- Bold word: **Bebas Neue**, 24–34pt
- Secondary: **Playfair Display Italic**, 16–22pt, vertical writing
- Giant number: **Bebas Neue**, 64–80pt (ghost/watermark at 8% opacity)
- Caption: **Space Mono**, 8pt

### Layout
- **Overlapping color blocks** (3 blocks, each slightly rotated ±2–5°)
- Each block contains one focused element (text, word, or icon)
- Diagonal stripe pattern on background (3% opacity)
- Ghost number lower-right
- Circle outline accent element (outline only, one of the bold colors)

### Signature Elements
- 3+ overlapping rotated blocks
- Giant ghost number as texture
- Circle outline accent
- Vertical text in one block

### Avoid
- Symmetric or centered compositions
- Clean uncluttered layouts
- Muted backgrounds

---

## 29. SciFi Holographic Data

**Mood**: Military HUD, quantum computing, absolute precision
**Best For**: Defense tech, AI research, quantum, advanced data engineering

### Background
- Deep space black: `#03050D`

### Colors
| Role | Color | HEX |
|------|-------|-----|
| Background | Deep space | `#03050D` |
| Ring outlines | Cyan | `#00C8FF` @ 25–60% (vary by ring) |
| Scan line | Cyan | `#00C8FF` @ 50% |
| Bar elements | Cyan gradient | `transparent → #00C8FF → transparent` |
| Text | Cyan | `#00C8FF` @ 70% |
| Center dot | Bright cyan | `#00C8FF` |

### Fonts
- All text: **Space Mono**, 9–11pt
- System labels: 10pt, 3pt letter-spacing
- Coordinates/data: 8pt

### Layout
- **3 concentric rings** (full circles, varying opacity increasing inward)
- Middle ring rotated 30° from outer ring
- **Horizontal scan line** animating top to bottom (or static at mid position)
- Horizontal bars (gradient center-glow) top and bottom
- Center dot at ring intersection
- Text labels at top-left and bottom-right

### Signature Elements
- 3 concentric circles (not uniform — one rotated)
- Scan line (animated or static)
- All elements strictly monochromatic cyan

### Avoid
- Multiple hue accents
- Warm or saturated colors
- Any decorative illustration

---

## 30. Risograph Print

**Mood**: Indie, artisanal printing, CMYK overlap, analog warmth
**Best For**: Independent publishers, music labels, art zines, boutique studios

### Background
- Aged paper: `#F7F2E8`

### Colors
| Role | Color | HEX |
|------|-------|-----|
| Background | Aged paper | `#F7F2E8` |
| Circle 1 (C) | Riso red | `#E8344A` |
| Circle 2 (M) | Riso blue | `#0D5C9E` |
| Circle 3 (Y) | Riso yellow | `#F5D020` |
| Overlap zones | Multiply blend | auto (red+blue=purple, red+yellow=orange, blue+yellow=green) |
| Ghost title | Red-tint offset | `#E8344A` @ 25%, shifted 3px |

### Fonts
- Main title: **Bebas Neue**, 34–44pt, 4pt letter-spacing
- Caption: **Space Mono**, 9pt

### Layout
- **Three overlapping circles** (CMYK primary colors) in center third
- Each circle uses `multiply` blend mode — overlaps create secondary colors naturally
- **Offset ghost text** behind main title (3–4pt shift, low opacity, accent color)
- Main title centered above circles
- Monospace caption at bottom

### Signature Elements
- Three overlapping multiply-blend circles
- Offset ghost title (registration mark error simulation)
- Warm paper background

### Avoid
- Digital-looking crisp shapes
- Dark backgrounds
- Screen-blend mode (must be multiply for authentic CMYK overlap)
