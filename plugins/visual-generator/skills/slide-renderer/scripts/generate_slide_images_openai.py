#!/usr/bin/env python3
# pyright: reportMissingImports=false
"""
OpenAI gpt-image-2 API를 사용하여 슬라이드 프롬프트 파일에서 이미지를 생성하는 스크립트

사용법:
    python generate_slide_images_openai.py --prompts-dir [프롬프트 폴더] --output-dir [출력 폴더]

설정 (CLI 옵션으로 오버라이드 가능):
    - 생성 모델: gpt-image-2 (--model)
    - 평가 모델: gpt-5.5 → gpt-5 → gpt-4o (런타임 fallback chain, --eval-model)
    - 해상도: 3840x2160 (4K, --size)
    - 품질: high (--quality)
    - 출력 형식: JPEG

입력: slide-prompt-generator로 생성된 슬라이드 프롬프트 (.md)
출력: 발표용 고해상도 슬라이드 이미지 (.jpg)

비용은 OpenAI 콘솔(https://platform.openai.com/usage)에서 확인하세요.
"""

import os
import sys
import time
import json
import re
import io
import base64
import shutil
import argparse
from pathlib import Path

# Lazy-load openai SDK so --help works without the package installed.
# Real import happens inside _make_client() and _resolve_eval_model().
from PIL import Image as PILImage

DEFAULT_IMAGE_MODEL = "gpt-image-2"
DEFAULT_EVAL_MODEL = "gpt-5.5"
DEFAULT_IMAGE_SIZE = "3840x2160"
DEFAULT_IMAGE_QUALITY = "high"
OUTPUT_FORMAT = "jpeg"

# 평가 모델 fallback chain (intra-OpenAI only — AGENTS.md anti-pattern: no Gemini fallback)
EVAL_FALLBACK_TAIL = ["gpt-5", "gpt-4o"]

# 알려진 테마 화이트리스트 (concept만 한글 면제 자격이 있음)
KNOWN_THEMES = ("concept", "gov", "seminar", "whatif", "pitch", "comparison")
VALID_THEME_VALUES = KNOWN_THEMES + ("auto",)

QUALITY_THRESHOLD = 7.0
KOREAN_MIN_THRESHOLD = 5.0
MAX_QUALITY_RETRIES = 2

API_RETRY_COUNT = 3
API_RETRY_DELAY = 5
INTER_CALL_DELAY = 2
DEFAULT_MAX_IMAGES = 30

# gpt-image-2 size 제약 조건
GPT_IMAGE_2_MAX_EDGE = 3840
GPT_IMAGE_2_EDGE_MULTIPLE = 16
GPT_IMAGE_2_MAX_TOTAL_PIXELS = 8_294_400

VALID_QUALITY_VALUES = ("low", "medium", "high", "auto")

SYSTEM_INSTRUCTION = """You are an expert visual designer creating high-quality presentation slides. Follow these quality requirements strictly:

Korean Typography: All Korean text must be rendered with crisp, perfectly formed characters using heavy-weight Gothic-style sans-serif fonts (Bold/ExtraBold weight 700+). Each Korean syllable block must be complete and legible. Never use thin or light Korean serif fonts.

Visual Composition: Maintain clear visual hierarchy with distinct foreground, midground, and background depth layers. Apply rule of thirds for focal point placement. Ensure primary information elements capture immediate attention.

Negative Rendering Constraints: Never render watermarks, blurry text, numbered lists as visual elements, placeholder text, artifacts, meta-labels like 'Data:' or 'Note:', or any decorative elements not specified in the prompt. Never render hex color codes (e.g., #1E3A5F, #FFFFFF) as visible text in the image. Color codes are configuration-only and must never appear as text elements.

White Space: Maintain 30-40% negative space for visual breathing room and readability. Do not overcrowd the composition with excessive elements.

Text Contrast: All text placed over images must have sufficient contrast for legibility. Use text-shadow, outline, or semi-transparent backing when text overlaps complex or busy backgrounds. Ensure WCAG-level contrast aesthetically.

Zero-Text Rendering: If the prompt specifies a Kurzgesagt-style illustration or explicitly requests zero text rendering, render NO text elements whatsoever in the image. Treat any text-like strings in the prompt as visual element descriptions, not as text to render.

Korean Text Hallucination Prevention: Never generate gibberish or randomly formed Korean characters to fill empty space in the image. If a content area appears empty, fill it with flat icons, isometric illustrations, or decorative visual elements rather than fabricated Korean text. Every Korean character rendered in the final image must correspond to a specific text item from the prompt's CONTENT section. Do not infer, translate, or generate any Korean text beyond what is explicitly provided in the prompt.
"""

EVALUATION_SCHEMA = {
    "format": {
        "type": "json_schema",
        "name": "ImageQualityEvaluation",
        "strict": True,
        "schema": {
            "type": "object",
            "properties": {
                "korean_text_readability": {"type": "number"},
                "korean_hallucination_detection": {"type": "number"},
                "content_reference_accuracy": {"type": "number"},
                "layout_suitability": {"type": "number"},
                "color_palette_compliance": {"type": "number"},
                "overall_score": {"type": "number"},
                "feedback": {"type": "string"},
            },
            "required": [
                "korean_text_readability",
                "korean_hallucination_detection",
                "content_reference_accuracy",
                "layout_suitability",
                "color_palette_compliance",
                "overall_score",
                "feedback",
            ],
            "additionalProperties": False,
        },
    }
}


def _validate_size(value: str) -> str:
    """gpt-image-2 size 제약 검증.

    제약:
    - WIDTHxHEIGHT 형식
    - 양변 모두 GPT_IMAGE_2_EDGE_MULTIPLE(16)의 배수
    - max edge <= GPT_IMAGE_2_MAX_EDGE(3840)
    - total pixels <= GPT_IMAGE_2_MAX_TOTAL_PIXELS(8,294,400)
    """
    m = re.fullmatch(r"(\d+)x(\d+)", value.strip())
    if not m:
        raise argparse.ArgumentTypeError(f"--size 형식 오류: '{value}' (예: 3840x2160)")
    w, h = int(m.group(1)), int(m.group(2))
    if w <= 0 or h <= 0:
        raise argparse.ArgumentTypeError(f"--size 양수 필요: {value}")
    if w % GPT_IMAGE_2_EDGE_MULTIPLE != 0 or h % GPT_IMAGE_2_EDGE_MULTIPLE != 0:
        raise argparse.ArgumentTypeError(
            f"--size 양변은 {GPT_IMAGE_2_EDGE_MULTIPLE}의 배수여야 합니다: {w}x{h}"
        )
    if max(w, h) > GPT_IMAGE_2_MAX_EDGE:
        raise argparse.ArgumentTypeError(
            f"--size 한 변이 {GPT_IMAGE_2_MAX_EDGE}px를 초과합니다: {w}x{h}"
        )
    if w * h > GPT_IMAGE_2_MAX_TOTAL_PIXELS:
        raise argparse.ArgumentTypeError(
            f"--size 총 픽셀이 {GPT_IMAGE_2_MAX_TOTAL_PIXELS:,}을 초과합니다: {w}x{h} = {w * h:,}"
        )
    return f"{w}x{h}"


def _validate_quality(value: str) -> str:
    if value not in VALID_QUALITY_VALUES:
        raise argparse.ArgumentTypeError(
            f"--quality 유효값: {VALID_QUALITY_VALUES}, 입력: {value!r}"
        )
    return value


def _check_api_key() -> str:
    key = os.environ.get("OPENAI_API_KEY")
    if not key:
        print("[에러] OPENAI_API_KEY 환경변수가 설정되지 않았습니다.")
        print("  $env:OPENAI_API_KEY='your-api-key' 또는 .env 파일에 설정하세요.")
        sys.exit(1)
    return key


def _make_client(api_key: str):
    from openai import OpenAI  # noqa: PLC0415

    return OpenAI(api_key=api_key)


# 모듈 캐시: 한 번 해결된 평가 모델은 이후 호출에서 재사용
_resolved_eval_model: str | None = None
_eval_first_success_logged = False


def _preview_text(value: object, limit: int = 120) -> str:
    text = str(value).replace("\n", " ").replace("\r", " ").strip()
    return text[:limit]


def _zero_score_result(feedback: str, *, is_concept: bool) -> dict[str, object]:
    base_criteria = {
        "korean_text_readability": 0.0,
        "korean_hallucination_detection": 0.0,
        "content_reference_accuracy": 0.0,
        "layout_suitability": 0.0,
        "color_palette_compliance": 0.0,
    }
    if is_concept:
        base_criteria["korean_text_readability"] = 10.0
        base_criteria["korean_hallucination_detection"] = 10.0
    return {
        "score": 0.0,
        "feedback": feedback[:200],
        "criteria": base_criteria,
    }


_THEME_FROM_FILENAME_RE = re.compile(r"^\d+_theme_([a-zA-Z]+)")


def _normalize_theme(value: str | None) -> str | None:
    """입력 문자열을 알려진 테마 6종 중 하나로 정규화."""
    if value is None:
        return None
    candidate = str(value).strip().lower()
    if not candidate or candidate == "auto":
        return None
    if candidate in KNOWN_THEMES:
        return candidate
    return None


def _extract_theme_from_filename(name: str) -> str | None:
    """`01_theme_concept.md` 같은 표준 파일명에서 테마 추출."""
    if not name:
        return None
    stem = Path(name).stem
    match = _THEME_FROM_FILENAME_RE.match(stem)
    if not match:
        return None
    return _normalize_theme(match.group(1))


def _resolve_theme(
    *,
    explicit_theme: str | None,
    prompt_filename: str | None,
    prompt_text: str,
    default_theme: str | None = None,
) -> str | None:
    """우선순위 기반 테마 결정.

    1) explicit_theme (가장 강함, 호출자가 명시적으로 지정)
    2) prompt_filename (`01_theme_concept.md` 컨벤션)
    3) default_theme (CLI `--theme` 등에서 들어온 기본값)
    4) prompt_text 키워드 매칭은 _is_concept_via_keywords()에서 별도로 다룸
    """
    for value in (explicit_theme, _extract_theme_from_filename(prompt_filename or ""), default_theme):
        normalized = _normalize_theme(value)
        if normalized:
            return normalized
    return None


def _is_concept_via_keywords(prompt_text: str) -> bool:
    """prompt_text 키워드 기반 보조 판정 (테마 정보가 없을 때만 사용)."""
    lowered = (prompt_text or "").lower()
    return (
        "concept" in lowered
        or "zero text rendering" in lowered
        or "zero-text rendering" in lowered
        or "kurzgesagt" in lowered
    )


def _resolve_eval_model(client, preferred: str) -> str:
    """평가 모델 fallback chain 해결.

    AGENTS.md anti-pattern 준수: Gemini로의 silent fallback 절대 금지.
    Chain은 OpenAI 모델 내에서만 순회한다.

    1) preferred (e.g., gpt-5.5)
    2) gpt-5
    3) gpt-4o
    """
    global _resolved_eval_model
    if _resolved_eval_model:
        return _resolved_eval_model

    chain: list[str] = []
    for m in [preferred, *EVAL_FALLBACK_TAIL]:
        if m and m not in chain:
            chain.append(m)

    # OpenAI SDK 에러 클래스 (lazy import)
    try:
        from openai import NotFoundError  # noqa: PLC0415
    except ImportError:  # 구버전 SDK 호환
        NotFoundError = Exception  # type: ignore[assignment,misc]

    skipped: list[str] = []
    for candidate in chain:
        try:
            # 가장 가벼운 호출로 모델 존재 확인 (1×1 PNG 평가 시도 대신 retrieve 사용)
            client.models.retrieve(candidate)
        except NotFoundError as exc:
            skipped.append(f"{candidate} (NotFound: {str(exc)[:80]})")
            continue
        except Exception as exc:
            err_str = str(exc)
            if "model_not_found" in err_str or "404" in err_str:
                skipped.append(f"{candidate} (404: {err_str[:80]})")
                continue
            # 권한 등 다른 에러는 모델이 존재한다는 신호로 간주하고 사용 시도
            print(f"[eval-model] {candidate} retrieve 비치명적 에러: {err_str[:100]}")

        _resolved_eval_model = candidate
        if skipped:
            print(
                f"[eval-model] resolved to {candidate} (preferred: {preferred}, skipped: {skipped})"
            )
        else:
            print(f"[eval-model] resolved to {candidate} (preferred: {preferred})")
        return candidate

    # 모두 실패: 마지막 후보를 그대로 반환하고 호출 시점에 에러를 발생시킨다
    fallback = chain[-1]
    print(
        f"[eval-model] WARNING: 체인 전체 해결 실패, {fallback} 사용 시도 (skipped: {skipped})"
    )
    _resolved_eval_model = fallback
    return fallback


def evaluate_image_quality(
    client,
    image_path: str,
    prompt_text: str = "",
    eval_model: str = DEFAULT_EVAL_MODEL,
    *,
    theme: str | None = None,
) -> dict[str, object]:
    """OpenAI 비전 모델로 생성된 이미지 품질 평가 (5차원, Structured Outputs).

    Returns: {"score": float, "feedback": str, "criteria": dict}

    Concept 면제 (한글 차원 자동 10점) 우선순위:
    1) theme == "concept" (가장 강함, 명시적 지정)
    2) prompt_text 키워드 매칭 (concept / zero-text / kurzgesagt)
    """
    normalized_theme = _normalize_theme(theme)
    is_concept = normalized_theme == "concept" or (
        normalized_theme is None and _is_concept_via_keywords(prompt_text)
    )

    concept_clause = (
        "\n\n[테마: concept (zero-text 일러스트)] 이미지에 한국어 텍스트가 의도적으로 없습니다. "
        "korean_text_readability와 korean_hallucination_detection은 평가하지 말고 모두 10점으로 채점하세요. "
        "한글 부재로 다른 차원을 감점하지 마세요."
        if is_concept
        else ""
    )

    evaluation_prompt = (
        "아래 이미지를 엄격하게 평가하세요.\n\n"
        "평가 기준(각 0~10, 소수점 허용):\n"
        "1) korean_text_readability: 한글 텍스트의 선명도, 자모 결합 정확성, 가독성 (글자 깨짐/뭉개짐 감점)\n"
        "2) korean_hallucination_detection: CONTENT에 없는 한글이 이미지에 존재하는지 여부 (10=깨끗, 0=심각한 hallucination)\n"
        "3) content_reference_accuracy: CONTENT에 명시된 텍스트가 이미지에 정확히 렌더링되었는지\n"
        "4) layout_suitability: 레이아웃 구성 적합성 (계층, 공간 균형, 시각 흐름)\n"
        "5) color_palette_compliance: 지정 팔레트 준수 여부\n"
        "6) overall_score: 위 5차원의 종합 가중 평균\n\n"
        "feedback: 재생성을 위한 구체적 개선 지침 1~3문장 (200자 이내)"
        + concept_clause
    )

    global _eval_first_success_logged

    try:
        active_model = _resolve_eval_model(client, eval_model)
        image_bytes = Path(image_path).read_bytes()
        image_b64 = base64.b64encode(image_bytes).decode("utf-8")
    except Exception as e:
        print(f"[eval-error] prepare failed: {_preview_text(e, limit=160)}")
        return _zero_score_result(
            f"품질 평가 준비 실패 ({type(e).__name__}): {_preview_text(e, limit=160)}",
            is_concept=is_concept,
        )

    try:
        response = client.responses.create(
            model=active_model,
            input=[
                {
                    "role": "user",
                    "content": [
                        {"type": "input_text", "text": evaluation_prompt},
                        {
                            "type": "input_image",
                            "image_url": f"data:image/jpeg;base64,{image_b64}",
                            "detail": "original",
                        },
                    ],
                }
            ],
            text=EVALUATION_SCHEMA,
        )
    except Exception as e:
        print(f"[eval-error] model={active_model}: {_preview_text(e, limit=160)}")
        return _zero_score_result(
            f"품질 평가 API 오류 ({type(e).__name__}): {_preview_text(e, limit=160)}",
            is_concept=is_concept,
        )

    raw_output = getattr(response, "output_text", "")

    try:
        payload = json.loads(raw_output)
    except (TypeError, json.JSONDecodeError) as e:
        preview = _preview_text(raw_output)
        print(
            f"[eval-error] model={active_model}: structured output parse failed: {preview!r}"
        )
        return _zero_score_result(
            f"품질 평가 응답 파싱 실패 ({type(e).__name__}): {preview}",
            is_concept=is_concept,
        )

    def _score(value):
        try:
            return max(0.0, min(10.0, float(value)))
        except (TypeError, ValueError):
            return 0.0

    criteria = {
        "korean_text_readability": _score(payload.get("korean_text_readability", 0)),
        "korean_hallucination_detection": _score(
            payload.get("korean_hallucination_detection", 0)
        ),
        "content_reference_accuracy": _score(
            payload.get("content_reference_accuracy", 0)
        ),
        "layout_suitability": _score(payload.get("layout_suitability", 0)),
        "color_palette_compliance": _score(payload.get("color_palette_compliance", 0)),
    }

    if is_concept:
        criteria["korean_text_readability"] = 10.0
        criteria["korean_hallucination_detection"] = 10.0

    avg_score = _score(payload.get("overall_score", sum(criteria.values()) / 5.0))
    feedback = _preview_text(payload.get("feedback", ""), limit=200)

    if not _eval_first_success_logged:
        print(f"[eval-ok] model={active_model} score={avg_score:.1f}")
        _eval_first_success_logged = True

    return {"score": avg_score, "feedback": feedback, "criteria": criteria}


def generate_image(
    client,
    prompt_text: str,
    output_path: str,
    *,
    image_model: str = DEFAULT_IMAGE_MODEL,
    image_size: str = DEFAULT_IMAGE_SIZE,
    image_quality: str = DEFAULT_IMAGE_QUALITY,
    eval_model: str = DEFAULT_EVAL_MODEL,
    max_retries: int = API_RETRY_COUNT,
    theme: str | None = None,
) -> bool:
    """OpenAI gpt-image-2 API를 호출하여 슬라이드 이미지 생성 (5D 품질 평가 루프 포함).

    Returns: bool (성공 여부)
    """

    def _request_image(current_prompt: str, save_path: str) -> bool:
        combined_prompt = SYSTEM_INSTRUCTION + "\n\n" + current_prompt
        backoff_delays = [API_RETRY_DELAY, API_RETRY_DELAY * 3, API_RETRY_DELAY * 9]

        for attempt in range(max_retries):
            try:
                response = client.images.generate(
                    model=image_model,
                    prompt=combined_prompt,
                    size=image_size,
                    quality=image_quality,
                    output_format=OUTPUT_FORMAT,
                    n=1,
                )

                image_b64 = response.data[0].b64_json
                if not image_b64:
                    print(
                        f"  [경고] 이미지 데이터 없음, 재시도 {attempt + 1}/{max_retries}"
                    )
                    if attempt < max_retries - 1:
                        time.sleep(API_RETRY_DELAY)
                    continue

                image_bytes = base64.b64decode(image_b64)

                # OUTPUT_FORMAT=jpeg이므로 응답 바이트는 JPEG. PIL은 검증 용도로만 사용.
                try:
                    PILImage.open(io.BytesIO(image_bytes)).verify()
                except Exception as exc:
                    print(f"  [경고] PIL 검증 실패 ({exc}), 원본 바이트 그대로 저장")

                with open(save_path, "wb") as img_f:
                    img_f.write(image_bytes)
                print(f"  [저장] JPEG 직접 저장 ({len(image_bytes):,} bytes)")

                return True

            except Exception as e:
                error_str = str(e)
                if (
                    "403" in error_str
                    or "organization" in error_str.lower()
                    or "verification" in error_str.lower()
                ):
                    print(f"  [에러] OpenAI Organization 검증 필요 (HTTP 403)")
                    print(
                        f"  → 검증 페이지: https://platform.openai.com/settings/organization/general"
                    )
                    sys.exit(1)
                elif "429" in error_str:
                    delay = backoff_delays[min(attempt, len(backoff_delays) - 1)]
                    print(f"  [에러] Rate limit (429), {delay}초 대기 후 재시도")
                    time.sleep(delay)
                else:
                    print(
                        f"  [에러] {error_str[:100]}, 재시도 {attempt + 1}/{max_retries}"
                    )
                    if attempt < max_retries - 1:
                        time.sleep(API_RETRY_DELAY)

        return False

    total_quality_attempts = MAX_QUALITY_RETRIES + 1
    best_score = -1.0
    best_image_path = None
    current_prompt = prompt_text

    for quality_attempt in range(total_quality_attempts):
        candidate_output_path = output_path
        if total_quality_attempts > 1:
            candidate_output_path = (
                f"{output_path}.quality_attempt_{quality_attempt + 1}.jpg"
            )

        if not _request_image(current_prompt, candidate_output_path):
            return False

        quality_result = evaluate_image_quality(
            client,
            candidate_output_path,
            prompt_text=current_prompt,
            eval_model=eval_model,
            theme=theme,
        )
        raw_criteria = quality_result.get("criteria", {})
        criteria: dict[str, object] = (
            raw_criteria if isinstance(raw_criteria, dict) else {}
        )
        raw_score = quality_result.get("score", 0.0)
        score = float(raw_score) if isinstance(raw_score, (int, float, str)) else 0.0
        raw_feedback = quality_result.get("feedback", "")
        feedback = raw_feedback if isinstance(raw_feedback, str) else str(raw_feedback)

        korean_score = int(round(criteria.get("korean_text_readability", 0)))
        korean_hallu_score = int(
            round(criteria.get("korean_hallucination_detection", 0))
        )
        content_acc_score = int(round(criteria.get("content_reference_accuracy", 0)))
        layout_score = int(round(criteria.get("layout_suitability", 0)))
        color_score = int(round(criteria.get("color_palette_compliance", 0)))

        if score > best_score:
            best_score = score
            best_image_path = candidate_output_path

        korean_readability = criteria.get("korean_text_readability", 0)
        korean_hallu = criteria.get("korean_hallucination_detection", 0)
        passed = (
            score >= QUALITY_THRESHOLD
            and korean_readability >= KOREAN_MIN_THRESHOLD
            and korean_hallu >= KOREAN_MIN_THRESHOLD
        )

        if passed:
            print(
                f"[품질 평가] 시도 {quality_attempt + 1}/{total_quality_attempts}: "
                f"평균 {score:.1f} (한글:{korean_score}, 환각:{korean_hallu_score}, 정확도:{content_acc_score}, 레이아웃:{layout_score}, 색상:{color_score}) → 통과"
            )
            if candidate_output_path != output_path:
                shutil.copyfile(candidate_output_path, output_path)
            break

        print(
            f"[품질 평가] 시도 {quality_attempt + 1}/{total_quality_attempts}: "
            f"평균 {score:.1f} (한글:{korean_score}, 환각:{korean_hallu_score}, 정확도:{content_acc_score}, 레이아웃:{layout_score}, 색상:{color_score}) → 재시도"
        )

        if quality_attempt < MAX_QUALITY_RETRIES:
            current_prompt = f"{prompt_text}\n\n[품질 보정 힌트] {feedback}"

    if best_image_path is None:
        return False

    if best_score < QUALITY_THRESHOLD:
        if best_image_path != output_path:
            shutil.copyfile(best_image_path, output_path)
        print(f"[품질 평가] 기준 미달, 최고 점수 이미지 채택 (평균 {best_score:.1f})")

    for cleanup_attempt in range(total_quality_attempts):
        temp_path = Path(f"{output_path}.quality_attempt_{cleanup_attempt + 1}.jpg")
        if temp_path.exists():
            temp_path.unlink()

    return True


def process_prompts(
    prompts_dir: str,
    output_dir: str,
    *,
    image_model: str = DEFAULT_IMAGE_MODEL,
    image_size: str = DEFAULT_IMAGE_SIZE,
    image_quality: str = DEFAULT_IMAGE_QUALITY,
    eval_model: str = DEFAULT_EVAL_MODEL,
    max_images: int = DEFAULT_MAX_IMAGES,
    auto_confirm: bool = False,
    default_theme: str | None = None,
) -> dict[str, list[str]]:
    """슬라이드 프롬프트 폴더의 모든 .md 파일을 처리하여 이미지 생성.

    Returns: {"success": [...], "failed": [...]}
    """
    prompts_path = Path(prompts_dir)
    output_path = Path(output_dir)

    output_path.mkdir(parents=True, exist_ok=True)

    # 메타/인덱스 파일 제외
    exclude_files = [
        "prompt_index.md",
        "공통및특화작업구조설명.md",
        "style_sheet.md",
        "validation_result.md",
    ]
    # 화이트리스트: 숫자로 시작하는 파일만 (01_, 02_, 10_, 11_ ...)
    prompt_files = sorted(
        [
            f
            for f in prompts_path.glob("*.md")
            if re.match(r"^\d+_", f.name) and f.name not in exclude_files
        ]
    )

    if not prompt_files:
        print(f"[에러] 슬라이드 프롬프트 파일이 없습니다: {prompts_dir}")
        return {"success": [], "failed": []}

    total_prompts = len(prompt_files)
    if total_prompts > max_images:
        print(
            f"[경고] 프롬프트 수({total_prompts})가 --max-images({max_images})를 초과합니다."
        )
        print(
            f"  비용은 OpenAI 콘솔(https://platform.openai.com/usage)에서 확인하세요."
        )
        if auto_confirm:
            print(
                f"  [자동 중단] --yes 없이 max_images 초과 불가. 처음 {max_images}장만 처리합니다."
            )
            prompt_files = prompt_files[:max_images]
        else:
            try:
                answer = (
                    input(
                        f"  계속하려면 'yes'를 입력하세요 (처음 {max_images}장만 처리하려면 Enter): "
                    )
                    .strip()
                    .lower()
                )
                if answer != "yes":
                    prompt_files = prompt_files[:max_images]
                    print(f"  처음 {max_images}장만 처리합니다.")
            except EOFError:
                prompt_files = prompt_files[:max_images]

    print(f"[시작] {len(prompt_files)}개 슬라이드 프롬프트 처리")
    print(f"  - 프롬프트 폴더: {prompts_dir}")
    print(f"  - 출력 폴더: {output_dir}")
    print(f"  - 생성 모델: {image_model}")
    print(f"  - 평가 모델: {eval_model} (필요 시 fallback chain)")
    print(f"  - 출력 사양: {image_size} quality={image_quality} format={OUTPUT_FORMAT}")
    print(f"  - 비용은 OpenAI 콘솔(https://platform.openai.com/usage)에서 확인하세요.")
    if default_theme:
        print(f"  - 기본 테마: {default_theme} (파일명에서 테마를 추출할 수 없을 때 적용)")
    print()

    # API 클라이언트 초기화
    api_key = _check_api_key()
    client = _make_client(api_key)

    results = {"success": [], "failed": []}

    for i, prompt_file in enumerate(prompt_files, 1):
        slide_name = prompt_file.stem
        output_file = output_path / f"{slide_name}.jpg"

        print(f"[{i}/{len(prompt_files)}] {slide_name}")

        # 이미 생성된 파일 스킵
        if output_file.exists():
            print(f"  [SKIP] Already exists: {output_file}")
            results["success"].append(slide_name)
            continue

        with open(str(prompt_file), "r", encoding="utf-8") as f:
            prompt_content = f.read().strip()

        try:
            resolved_theme = _resolve_theme(
                explicit_theme=None,
                prompt_filename=prompt_file.name,
                prompt_text=prompt_content,
                default_theme=default_theme,
            )
            if resolved_theme:
                print(f"  [테마] {resolved_theme}")
            ok = generate_image(
                client,
                prompt_content,
                str(output_file),
                image_model=image_model,
                image_size=image_size,
                image_quality=image_quality,
                eval_model=eval_model,
                theme=resolved_theme,
            )
            if ok:
                print(f"  [OK] Saved: {output_file}")
                results["success"].append(slide_name)
            else:
                print(f"  [FAIL] {slide_name}: 생성 실패")
                results["failed"].append(slide_name)
        except Exception as e:
            print(f"  [FAIL] {slide_name}: {e}")
            results["failed"].append(slide_name)

        if i < len(prompt_files):
            time.sleep(INTER_CALL_DELAY)

    print()
    print("=" * 50)
    print(f"[완료] 성공: {len(results['success'])}, 실패: {len(results['failed'])}")
    if results["failed"]:
        print(f"[실패 목록] {', '.join(results['failed'])}")

    return results


def main():
    parser = argparse.ArgumentParser(
        description="OpenAI gpt-image-2 API를 사용하여 슬라이드 프롬프트에서 이미지 생성"
    )
    parser.add_argument(
        "--prompts-dir",
        "-p",
        required=True,
        help="슬라이드 프롬프트 파일이 있는 폴더 경로",
    )
    parser.add_argument(
        "--output-dir",
        "-o",
        required=True,
        help="생성된 슬라이드 이미지를 저장할 폴더 경로",
    )
    parser.add_argument(
        "--size",
        type=_validate_size,
        default=DEFAULT_IMAGE_SIZE,
        help=(
            f"이미지 해상도 WIDTHxHEIGHT (default={DEFAULT_IMAGE_SIZE}). "
            f"제약: 양변 16배수, max edge {GPT_IMAGE_2_MAX_EDGE}px, total pixels ≤ {GPT_IMAGE_2_MAX_TOTAL_PIXELS:,}"
        ),
    )
    parser.add_argument(
        "--quality",
        type=_validate_quality,
        default=DEFAULT_IMAGE_QUALITY,
        help=f"품질 (default={DEFAULT_IMAGE_QUALITY}). 유효값: {VALID_QUALITY_VALUES}",
    )
    parser.add_argument(
        "--model",
        default=DEFAULT_IMAGE_MODEL,
        help=f"이미지 생성 모델 (default={DEFAULT_IMAGE_MODEL})",
    )
    parser.add_argument(
        "--eval-model",
        default=DEFAULT_EVAL_MODEL,
        help=(
            f"평가 모델 (default={DEFAULT_EVAL_MODEL}). "
            f"런타임 fallback: {DEFAULT_EVAL_MODEL} → {' → '.join(EVAL_FALLBACK_TAIL)}"
        ),
    )
    parser.add_argument(
        "--max-images",
        type=int,
        default=DEFAULT_MAX_IMAGES,
        help=f"최대 처리 이미지 수 sanity cap (기본값: {DEFAULT_MAX_IMAGES})",
    )
    parser.add_argument(
        "--yes",
        action="store_true",
        help="max-images 초과 시 자동으로 처음 N장만 처리 (확인 없이)",
    )
    parser.add_argument(
        "--theme",
        default=None,
        help=(
            "이미지가 속한 테마 (선택, fallback 용). "
            "우선순위: 파일명 (`NN_theme_<NAME>.md`) > --theme. "
            "유효값: " + ", ".join(KNOWN_THEMES)
        ),
    )

    args = parser.parse_args()

    if not os.path.isdir(args.prompts_dir):
        print(f"[에러] 프롬프트 폴더가 존재하지 않습니다: {args.prompts_dir}")
        sys.exit(1)

    results = process_prompts(
        args.prompts_dir,
        args.output_dir,
        image_model=args.model,
        image_size=args.size,
        image_quality=args.quality,
        eval_model=args.eval_model,
        max_images=args.max_images,
        auto_confirm=args.yes,
        default_theme=_normalize_theme(args.theme),
    )

    sys.exit(1 if results["failed"] else 0)


if __name__ == "__main__":
    main()
