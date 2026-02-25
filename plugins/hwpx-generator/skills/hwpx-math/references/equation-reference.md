# 한컴 수식 스크립트 레퍼런스 (hp:equation)

> Source: Canine89/hwpxskill-math SKILL.md
> 한컴오피스 수식 편집기 스크립트 문법 전체 참조

---

## 기본 규칙

| 규칙 | 설명 |
|------|------|
| `{ }` | 그룹화 (여러 항을 하나로) |
| `~` | 공백 (1em) |
| `` ` `` | 1/4 공백 |
| `#` | 줄바꿈 (수식 내) |
| `&` | 열 정렬 (행렬, 연립방정식) |
| `"..."` | 텍스트 모드 (수식 해석 비활성) |

---

## 분수와 루트

| 수식 | 스크립트 | 예시 |
|------|----------|------|
| 분수 | `a over b` | `{x+1} over {x-1}` |
| 제곱근 | `sqrt {x}` | `sqrt {b^2 - 4ac}` |
| n제곱근 | `root n of {x}` | `root 3 of {27}` |

---

## 위·아래 첨자

| 수식 | 스크립트 |
|------|----------|
| 위첨자 | `x^2` 또는 `x SUP 2` |
| 아래첨자 | `x_i` 또는 `x SUB i` |
| 둘 다 | `x_i ^2` |

---

## 적분·합·곱

| 수식 | 스크립트 |
|------|----------|
| 정적분 | `int _{a} ^{b} f(x) dx` |
| 이중적분 | `dint f(x,y) dxdy` |
| 삼중적분 | `tint f dxdydz` |
| 급수(시그마) | `sum _{k=1} ^{n} a_k` |
| 곱(파이) | `prod _{i=1} ^{n} x_i` |

---

## 극한

| 수식 | 스크립트 |
|------|----------|
| 극한 | `lim _{x -> 0} f(x)` |
| 대문자 | `Lim _{n -> inf}` |

---

## 괄호

| 수식 | 스크립트 |
|------|----------|
| 자동 크기 소괄호 | `left ( {a over b} right )` |
| 자동 크기 대괄호 | `left [ x right ]` |
| 자동 크기 중괄호 | `left lbrace x right rbrace` |
| 절댓값 | `left | x right |` |

---

## 행렬

| 수식 | 스크립트 |
|------|----------|
| 기본 행렬 | `matrix {a & b # c & d}` |
| 소괄호 행렬 | `pmatrix {a & b # c & d}` |
| 대괄호 행렬 | `bmatrix {1 & 0 # 0 & 1}` |
| 행렬식 | `dmatrix {a & b # c & d}` |

---

## 연립방정식·조건

| 수식 | 스크립트 |
|------|----------|
| 연립방정식 | `cases {2x+y=5 # 3x-2y=4}` |
| 정렬 수식 | `eqalign {a &= b # c &= d}` |
| 수직 스택 | `pile {a # b # c}` |

---

## 장식(위·아래)

| 장식 | 스크립트 |
|------|----------|
| 모자(^) | `hat a` |
| 물결 | `tilde a` |
| 벡터 화살표 | `vec v` |
| 윗줄 | `bar x` |
| 밑줄 | `under x` |
| 점 1개 | `dot a` |
| 점 2개 | `ddot a` |

---

## 그리스 문자

### 소문자

`alpha`, `beta`, `gamma`, `delta`, `epsilon`, `zeta`, `eta`, `theta`, `iota`, `kappa`, `lambda`, `mu`, `nu`, `xi`, `pi`, `rho`, `sigma`, `tau`, `upsilon`, `phi`, `chi`, `psi`, `omega`

### 대문자

`ALPHA`, `BETA`, `GAMMA`, `DELTA` 등

### 변형

`vartheta`, `varphi`, `varepsilon`

---

## 특수 기호

| 기호 | 스크립트 |
|------|----------|
| 무한대 | `inf` |
| 편미분 | `partial` |
| 나블라 | `nabla` |
| 고로 | `therefore` |
| 왜냐하면 | `because` |
| 모든 | `forall` |
| 존재 | `exist` |
| ± | `+-` 또는 `pm` |
| ≠ | `ne` |
| ≤ | `le` 또는 `leq` |
| ≥ | `ge` 또는 `geq` |
| ≈ | `approx` |
| ≡ | `equiv` |
| ⊂ | `subset` |
| ∈ | `in` |
| → | `->` 또는 `rarrow` |
| ← | `larrow` |
| ↔ | `<->` 또는 `lrarrow` |
| ··· | `cdots` |

---

## 폰트 스타일

| 스타일 | 명령 |
|--------|------|
| 로만(정체) | `rm` |
| 이탤릭 | `it` |
| 볼드 | `bold` |
| 볼드 로만 | `rmbold` |

---

## 내장 함수 (자동 로만체)

`sin`, `cos`, `tan`, `cot`, `sec`, `csc`, `arcsin`, `arccos`, `arctan`, `log`, `ln`, `lg`, `exp`, `det`, `mod`, `gcd`, `max`, `min`, `sinh`, `cosh`, `tanh`

---

## 수식 XML 구조

section0.xml에서 수식은 다음과 같이 삽입된다:

```xml
<hp:p id="고유ID" paraPrIDRef="22" styleIDRef="0" pageBreak="0" columnBreak="0" merged="0">
  <hp:run charPrIDRef="9">
    <hp:equation id="고유ID" type="0" textColor="#000000"
                 baseUnit="1000" letterSpacing="0" lineThickness="100">
      <hp:sz width="0" height="0" widthRelTo="ABS" heightRelTo="ABS"/>
      <hp:pos treatAsChar="1" affectLSpacing="0" flowWithText="0"
              allowOverlap="0" holdAnchorAndSO="0" rgroupWithPrevCtrl="0"
              vertRelTo="PARA" horzRelTo="PARA" vertAlign="TOP" horzAlign="LEFT"
              vertOffset="0" horzOffset="0"/>
      <hp:script>x = {-b +- sqrt {b^2 - 4ac}} over {2a}</hp:script>
    </hp:equation>
  </hp:run>
</hp:p>
```

### 수식 속성

| 속성 | 값 | 설명 |
|------|----|----|
| `baseUnit` | 1000 | 기본 10pt (100 HWPUNIT = 1pt) |
| `textColor` | #000000 | 수식 색상 |
| `lineThickness` | 100 | 분수선/루트선 두께 |
| `treatAsChar` | 1 | 인라인 수식 (텍스트와 같은 줄) |

### 텍스트 + 수식 혼합

한 문단에 텍스트와 수식을 함께 배치:

```xml
<hp:p id="..." paraPrIDRef="21" ...>
  <hp:run charPrIDRef="9"><hp:t>방정식 </hp:t></hp:run>
  <hp:run charPrIDRef="9">
    <hp:equation ...>
      <hp:script>2x + 3 = 7</hp:script>
    </hp:equation>
  </hp:run>
  <hp:run charPrIDRef="9"><hp:t> 의 해를 구하라.</hp:t></hp:run>
</hp:p>
```

---

## 학년별 수식 예시

### 중학교 (중1~중3)

```
# 일차방정식
2x + 3 = 7

# 분수 방정식
{2x+1} over 3 = {x-2} over 5

# 연립방정식
cases {2x + y = 5 # 3x - 2y = 4}

# 제곱근
sqrt 12 + sqrt 27 - sqrt 48

# 부등식
3x - 5 > 2x + 1

# 이차방정식
x^2 - 5x + 6 = 0

# 피타고라스
a^2 + b^2 = c^2

# 일차함수
y = ax + b
```

### 고등학교 수학 I (고1)

```
# 지수법칙
a^m times a^n = a^{m+n}

# 로그
log _a xy = log _a x + log _a y

# 절댓값
left | x - 3 right | < 5

# 이차함수 꼭짓점
y = a(x - p)^2 + q

# 근의 공식
x = {-b +- sqrt {b^2 - 4ac}} over {2a}
```

### 고등학교 수학 II (고2)

```
# 극한
lim _{x -> 0} {sin x} over x = 1

# 미분 정의
f'(x) = lim _{h -> 0} {f(x+h) - f(x)} over h

# 정적분
int _{0} ^{pi} sin x dx = 2

# 급수
sum _{k=1} ^{n} k = {n(n+1)} over 2

# 등차수열
a_n = a_1 + (n-1)d
```

### 고등학교 확률과 통계

```
# 조합
{_n}C{_r} = {n!} over {r!(n-r)!}

# 이항정리
(a+b)^n = sum _{k=0} ^{n} {_n}C{_k} a^{n-k} b^k

# 확률
P(A cup B) = P(A) + P(B) - P(A cap B)

# 정규분포
f(x) = {1} over {sigma sqrt {2 pi}} e^{-{(x- mu)^2} over {2 sigma ^2}}
```

### 고등학교 미적분

```
# 도함수
{d} over {dx} x^n = n x^{n-1}

# 합성함수 미분
{dy} over {dx} = {dy} over {du} times {du} over {dx}

# 부분적분
int u dv = uv - int v du

# 치환적분
int f(g(x)) g'(x) dx = int f(u) du

# 테일러 급수
e^x = sum _{n=0} ^{inf} {x^n} over {n!}
```

### 고등학교 기하

```
# 벡터 내적
vec a cdot vec b = left | vec a right | left | vec b right | cos theta

# 원의 방정식
(x-a)^2 + (y-b)^2 = r^2

# 타원
{x^2} over {a^2} + {y^2} over {b^2} = 1

# 쌍곡선
{x^2} over {a^2} - {y^2} over {b^2} = 1

# 행렬 곱
pmatrix {a & b # c & d} pmatrix {x # y} = pmatrix {ax+by # cx+dy}
```

---

## 스타일 ID 맵 (수식 관련)

### charPr (글자 스타일)

| ID | 설명 | 크기 | 굵기 | 비고 |
|----|------|------|------|------|
| 9 | 문제 본문 | 10pt | 보통 | 수식 기본 |
| 11 | 선택지/보기 | 9pt | 보통 | 수식 선택지 |

### paraPr (문단 스타일)

| ID | 정렬 | 줄간격 | 용도 |
|----|------|--------|------|
| 22 | LEFT | 140% | 수식 표시 (공통) |
| 23 | LEFT | 140% | 선택지/보기 세로 |
| 27 | LEFT | 140% | 선택지 가로 (exam, tabPr=3) |

### 수식 크기 참고

| baseUnit | 크기 | 용도 |
|----------|------|------|
| 1000 | 10pt | 본문 기본 |
| 1200 | 12pt | 강조 수식 |
| 800 | 8pt | 작은 수식 |

---

## Critical Rules

1. **수식 스크립트는 `<hp:script>` 안에**: LaTeX가 아닌 한컴 수식 문법 사용
2. **ID 고유성**: 문단 ID, 수식 ID 모두 문서 내 유일해야 함
3. **charPrIDRef 정합성**: section0.xml에서 참조하는 charPr ID가 header.xml에 존재해야 함
4. **수식 크기**: `baseUnit="1000"` = 10pt (본문과 동일), 필요시 조절
5. **선택지 수식**: JSON에서 `$...$`로 감싸면 수식으로 처리. **반드시 한컴 수식 스크립트 문법** 사용
6. **hp:sz width/height 0**: 한컴오피스가 렌더링 시 자동 계산하므로 0으로 설정 가능
