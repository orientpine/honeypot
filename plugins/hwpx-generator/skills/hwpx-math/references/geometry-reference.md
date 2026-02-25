# 도형 그래프 타입 레퍼런스 (Geometry Shapes)

> Source: Canine89/hwpxskill-math SKILL.md
> graph_generator.py가 지원하는 5가지 기하 도형 타입 전체 참조

`graph_generator.py`는 함수 그래프(polynomial, trig 등) 외에 5가지 기하 도형 타입을 지원한다.
문제 JSON의 `graph` 필드에 아래 스펙을 지정하면 도형 PNG가 자동 생성된다.

---

## triangle — 삼각형

꼭짓점 좌표 3개로 정의. 내각 표시, 각도 호, 변 길이 레이블, 보조선(중선/수선/이등분선), 외접원/내접원 지원.

```json
{
  "type": "triangle",
  "vertices": [[0, 0], [6, 0], [2, 5]],
  "labels": {"A": [2, 5], "B": [0, 0], "C": [6, 0]},
  "show_angles": [true, true, true],
  "angle_labels": ["80°", "50°", "50°"],
  "side_labels": {"AB": "5", "BC": "6", "AC": "5"},
  "equal_marks": {"AB": 1, "AC": 1},
  "show_circumcircle": false,
  "show_incircle": false,
  "auxiliary_lines": [{"type": "bisector", "vertex": "B"}]
}
```

### 필드 설명

| 필드 | 필수 | 설명 |
|------|------|------|
| `vertices` | O | 꼭짓점 좌표 3개 `[[x,y], [x,y], [x,y]]` |
| `labels` | X | 꼭짓점 이름→좌표 매핑 |
| `show_angles` | X | 각 꼭짓점별 각도 호 표시 여부 `[bool, bool, bool]` |
| `angle_labels` | X | 각도 라벨 (예: `["80°", "50°", "50°"]`) |
| `side_labels` | X | 변 이름→길이 라벨 (예: `{"AB": "5"}`) |
| `equal_marks` | X | 변 이름→등분 표시 개수 (예: `{"AB": 1, "AC": 1}`) |
| `show_circumcircle` | X | 외접원 표시 |
| `show_incircle` | X | 내접원 표시 |
| `auxiliary_lines` | X | 보조선 배열. `type`: `"median"`, `"altitude"`, `"bisector"` |

---

## circle — 원/부채꼴/호

중심, 반지름, 원 위의 점, 현, 접선, 호 강조, 중심각/원주각 표시.

```json
{
  "type": "circle",
  "center": [0, 0],
  "radius": 3,
  "show_center": true,
  "points_on_circle": [
    {"angle_deg": 30, "label": "A"},
    {"angle_deg": 150, "label": "B"}
  ],
  "chords": [["A", "B"]],
  "tangent_at": ["A"],
  "arc_highlight": {"from": "A", "to": "B", "color": "gray"},
  "central_angle": true,
  "inscribed_angle": {"vertex": "C", "arc": ["A", "B"]}
}
```

### 필드 설명

| 필드 | 필수 | 설명 |
|------|------|------|
| `center` | X | 중심 좌표 (기본: `[0,0]`) |
| `radius` | X | 반지름 (기본: 3) |
| `show_center` | X | 중심점 O 표시 |
| `points_on_circle` | X | 원 위의 점 배열 `{angle_deg, label}` |
| `chords` | X | 현 `[["A","B"]]` |
| `tangent_at` | X | 접선 그릴 점 이름 |
| `arc_highlight` | X | 호 강조 `{from, to, color}` |
| `central_angle` | X | 중심각 선분 표시 |
| `inscribed_angle` | X | 원주각 `{vertex, arc: [A, B]}` |

---

## quadrilateral — 사각형

4개 꼭짓점 좌표로 정의. 대각선, 평행 표시, 등분 표시, 직각 표시 지원.

```json
{
  "type": "quadrilateral",
  "kind": "parallelogram",
  "vertices": [[0, 0], [5, 0], [7, 3], [2, 3]],
  "labels": {"A": [0, 0], "B": [5, 0], "C": [7, 3], "D": [2, 3]},
  "show_diagonals": true,
  "diagonal_intersection_label": "O",
  "parallel_marks": {"AB_DC": 1, "AD_BC": 2},
  "equal_marks": {"AB": 1, "DC": 1},
  "show_right_angles": [],
  "side_labels": {"AB": "10", "BC": "6"}
}
```

### 필드 설명

| 필드 | 필수 | 설명 |
|------|------|------|
| `vertices` | O | 꼭짓점 좌표 4개 |
| `kind` | X | 참고용 종류명 (parallelogram, rectangle 등) |
| `labels` | X | 꼭짓점 이름→좌표 |
| `show_diagonals` | X | 대각선 점선 표시 |
| `diagonal_intersection_label` | X | 대각선 교점 라벨 |
| `parallel_marks` | X | 평행 표시 `{"AB_DC": 1}` (AB∥DC, 화살표 1개) |
| `equal_marks` | X | 등분 표시 |
| `show_right_angles` | X | 직각 표시할 꼭짓점 이름 배열 |
| `side_labels` | X | 변 길이 라벨 |

---

## coordinate — 좌표 위 도형

좌표축 + 선분/다각형/점/직선의 조합. 일차함수와 도형의 넓이 등.

```json
{
  "type": "coordinate",
  "xlim": [-1, 7],
  "ylim": [-1, 7],
  "segments": [[[0, 6], [2, 0]], [[2, 0], [6, 0]], [[0, 6], [6, 0]]],
  "points": [
    {"pos": [0, 6], "label": "(0, 6)"},
    {"pos": [2, 0], "label": "(2, 0)"}
  ],
  "fill_polygon": [[0, 6], [2, 0], [6, 0]],
  "shade_alpha": 0.15,
  "lines": [{"slope": -3, "intercept": 6, "style": "k-"}],
  "circles": [{"center": [3, 3], "radius": 2}]
}
```

### 필드 설명

| 필드 | 필수 | 설명 |
|------|------|------|
| `xlim`, `ylim` | X | 좌표축 범위 |
| `segments` | X | 선분 배열 `[[[x1,y1],[x2,y2]], ...]` |
| `points` | X | 점 배열 `{pos, label}` |
| `fill_polygon` | X | 채울 다각형 꼭짓점 좌표 |
| `shade_alpha` | X | 채우기 투명도 (기본: 0.15) |
| `lines` | X | 직선 `{slope, intercept, style}` |
| `circles` | X | 원 `{center, radius}` |

---

## solid3d — 입체도형 (2D 투영)

2D oblique projection으로 시험지 스타일 입체도형 렌더링. 점선으로 뒷면 모서리 표현.

```json
{
  "type": "solid3d",
  "kind": "cylinder",
  "params": {"radius": 2, "height": 4},
  "labels": {"r": "2", "h": "4"},
  "show_hidden": true
}
```

### 지원 kind

`cylinder`, `cone`, `sphere`, `rectangular_prism`, `triangular_prism`, `pyramid`

### 필드 설명

| 필드 | 필수 | 설명 |
|------|------|------|
| `kind` | X | 입체 종류 (기본: `"cylinder"`) |
| `params` | X | 종류별 파라미터 (radius, height, width, depth, base 등) |
| `labels` | X | 치수 라벨 (예: `{"r": "2", "h": "4"}`) |
| `show_hidden` | X | 뒷면 모서리 점선 표시 (기본: true) |

### kind별 params

| kind | params |
|------|--------|
| `cylinder` | `{radius, height}` |
| `cone` | `{radius, height}` |
| `sphere` | `{radius}` |
| `rectangular_prism` | `{width, height, depth}` |
| `triangular_prism` | `{base, height, depth}` |
| `pyramid` | `{base, height, depth}` |
