#!/usr/bin/env python3
"""
Gemini API를 사용하여 슬라이드 프롬프트 파일에서 이미지를 생성하는 스크립트

사용법:
    python generate_slide_images.py --prompts-dir [프롬프트 폴더] --output-dir [출력 폴더]

설정:
    - 모델: gemini-3-pro-image-preview
    - 해상도: 4K
    - 비율: 16:9
    - 사고모드: 활성화
    - 고급 텍스트 렌더링: 활성화

입력: slide-prompt-generator로 생성된 슬라이드 프롬프트 (.md)
출력: 정부/공공기관 발표용 고해상도 슬라이드 이미지 (.png)
"""

import os
import sys
import time
import json
import re
import shutil
import argparse
from pathlib import Path

from google import genai
from google.genai import types

# API 설정
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
MODEL_NAME = "gemini-3-pro-image-preview"
SYSTEM_INSTRUCTION = """You are an expert visual designer creating high-quality presentation slides. Follow these quality requirements strictly:

Korean Typography: All Korean text must be rendered with crisp, perfectly formed characters using heavy-weight Gothic-style sans-serif fonts (Bold/ExtraBold weight 700+). Each Korean syllable block must be complete and legible. Never use thin or light Korean serif fonts.

Visual Composition: Maintain clear visual hierarchy with distinct foreground, midground, and background depth layers. Apply rule of thirds for focal point placement. Ensure primary information elements capture immediate attention.

Negative Rendering Constraints: Never render watermarks, blurry text, numbered lists as visual elements, placeholder text, artifacts, meta-labels like 'Data:' or 'Note:', or any decorative elements not specified in the prompt. Never render hex color codes (e.g., #1E3A5F, #FFFFFF) as visible text in the image. Color codes are configuration-only and must never appear as text elements.

White Space: Maintain 30-40% negative space for visual breathing room and readability. Do not overcrowd the composition with excessive elements.

Text Contrast: All text placed over images must have sufficient contrast for legibility. Use text-shadow, outline, or semi-transparent backing when text overlaps complex or busy backgrounds. Ensure WCAG-level contrast aesthetically.

Zero-Text Rendering: If the prompt specifies a Kurzgesagt-style illustration or explicitly requests zero text rendering, render NO text elements whatsoever in the image. Treat any text-like strings in the prompt as visual element descriptions, not as text to render.
"""
QUALITY_THRESHOLD = 7.0
MAX_QUALITY_RETRIES = 2

if not GEMINI_API_KEY:
    print("[에러] GEMINI_API_KEY 환경변수가 설정되지 않았습니다.")
    print("  export GEMINI_API_KEY='your-api-key' 또는 .env 파일에 설정하세요.")
    sys.exit(1)


def extract_prompt_content(md_file_path: str) -> str:
    """
    슬라이드 프롬프트 파일 전체 내용 반환

    slide-prompt-generator 형식:
    - 목적, 톤앤매너, 스타일, 색상, 조명, 해상도
    - 슬라이드 레이아웃, 상단 타이틀, 메인 콘텐츠 섹션들
    - 인포그래픽 디테일, 금지 요소, 최종 결과물 목표

    (제외 섹션 없이 전체 사용)
    """
    with open(md_file_path, "r", encoding="utf-8") as f:
        return f.read().strip()


def generate_image(
    client, prompt_text: str, output_path: str, max_retries: int = 3
) -> bool:
    """
    Gemini API를 호출하여 슬라이드 이미지 생성

    Args:
        client: Gemini API 클라이언트
        prompt_text: 슬라이드 이미지 생성용 프롬프트
        output_path: 이미지 저장 경로
        max_retries: 최대 재시도 횟수

    Returns:
        bool: 생성 성공 여부
    """

    def _request_image(current_prompt: str, save_path: str) -> bool:
        for attempt in range(max_retries):
            try:
                response = client.models.generate_content(
                    model=MODEL_NAME,
                    contents=current_prompt,
                    config=types.GenerateContentConfig(
                        response_modalities=["TEXT", "IMAGE"],
                        image_config=types.ImageConfig(
                            aspect_ratio="16:9", image_size="4K"
                        ),
                        temperature=0.7,
                        top_p=0.9,
                        system_instruction=SYSTEM_INSTRUCTION,
                    ),
                )

                # 사고 과정 출력 (있는 경우)
                for part in response.parts:
                    if hasattr(part, "thought") and part.thought:
                        if part.text:
                            print(f"  [사고 과정] {part.text[:100]}...")

                # 이미지 저장
                for part in response.parts:
                    if part.inline_data is not None:
                        image = part.as_image()
                        image.save(save_path)
                        return True

                print(
                    f"  [경고] 이미지 데이터 없음, 재시도 {attempt + 1}/{max_retries}"
                )

            except Exception as e:
                print(f"  [에러] {e}, 재시도 {attempt + 1}/{max_retries}")
                if attempt < max_retries - 1:
                    time.sleep(5)

        return False

    total_quality_attempts = MAX_QUALITY_RETRIES + 1
    best_score = -1.0
    best_image_path = None
    current_prompt = prompt_text

    for quality_attempt in range(total_quality_attempts):
        candidate_output_path = output_path
        if total_quality_attempts > 1:
            candidate_output_path = (
                f"{output_path}.quality_attempt_{quality_attempt + 1}.png"
            )

        if not _request_image(current_prompt, candidate_output_path):
            return False

        quality_result = evaluate_image_quality(client, candidate_output_path)
        criteria = quality_result.get("criteria", {})
        score = float(quality_result.get("score", 0.0))
        feedback = quality_result.get("feedback", "")

        korean_score = int(round(criteria.get("korean_text_readability", 0)))
        layout_score = int(round(criteria.get("layout_suitability", 0)))
        color_score = int(round(criteria.get("color_palette_compliance", 0)))

        if score > best_score:
            best_score = score
            best_image_path = candidate_output_path

        if score >= QUALITY_THRESHOLD:
            print(
                f"[품질 평가] 시도 {quality_attempt + 1}/{total_quality_attempts}: "
                f"평균 {score:.1f} (한글:{korean_score}, 레이아웃:{layout_score}, 색상:{color_score}) → 통과"
            )
            if candidate_output_path != output_path:
                shutil.copyfile(candidate_output_path, output_path)
            break

        print(
            f"[품질 평가] 시도 {quality_attempt + 1}/{total_quality_attempts}: "
            f"평균 {score:.1f} (한글:{korean_score}, 레이아웃:{layout_score}, 색상:{color_score}) → 재시도"
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
        temp_path = Path(f"{output_path}.quality_attempt_{cleanup_attempt + 1}.png")
        if temp_path.exists():
            temp_path.unlink()

    return True


def evaluate_image_quality(client, image_path: str) -> dict:
    """
    Gemini 비전 모델로 생성된 이미지 품질 평가
    Returns: {"score": float, "feedback": str, "criteria": dict}
    """
    evaluation_prompt = """아래 이미지를 엄격하게 평가하세요. 반드시 JSON만 출력하세요.

평가 기준(각 0~10, 소수점 허용):
1) korean_text_readability: 한글 텍스트 가독성
2) layout_suitability: 레이아웃 구성 적합성
3) color_palette_compliance: 지정 팔레트 준수 여부

출력 형식(JSON only):
{
  "korean_text_readability": 0,
  "layout_suitability": 0,
  "color_palette_compliance": 0,
  "feedback": "재생성을 위한 구체적 개선 지침 1~3문장"
}
"""

    try:
        image_bytes = Path(image_path).read_bytes()
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=[
                types.Part.from_text(text=evaluation_prompt),
                types.Part.from_bytes(data=image_bytes, mime_type="image/png"),
            ],
            config=types.GenerateContentConfig(
                response_modalities=["TEXT"],
                temperature=0.1,
                top_p=0.1,
            ),
        )

        response_text = ""
        if hasattr(response, "text") and response.text:
            response_text = response.text
        elif hasattr(response, "parts"):
            response_text = "\n".join(
                part.text
                for part in response.parts
                if hasattr(part, "text") and part.text
            )

        json_match = re.search(r"\{[\s\S]*\}", response_text)
        payload = json.loads(json_match.group(0)) if json_match else {}

        def _score(value):
            try:
                return max(0.0, min(10.0, float(value)))
            except (TypeError, ValueError):
                return 0.0

        criteria = {
            "korean_text_readability": _score(
                payload.get("korean_text_readability", 0)
            ),
            "layout_suitability": _score(payload.get("layout_suitability", 0)),
            "color_palette_compliance": _score(
                payload.get("color_palette_compliance", 0)
            ),
        }
        avg_score = sum(criteria.values()) / 3.0
        feedback = str(payload.get("feedback", ""))

        return {"score": avg_score, "feedback": feedback, "criteria": criteria}

    except Exception as e:
        return {
            "score": 0.0,
            "feedback": f"품질 평가 실패: {e}",
            "criteria": {
                "korean_text_readability": 0.0,
                "layout_suitability": 0.0,
                "color_palette_compliance": 0.0,
            },
        }


def process_prompts(prompts_dir: str, output_dir: str) -> dict:
    """
    슬라이드 프롬프트 폴더의 모든 .md 파일을 처리하여 이미지 생성

    Args:
        prompts_dir: 슬라이드 프롬프트 파일이 있는 폴더 경로
        output_dir: 생성된 이미지를 저장할 폴더 경로

    Returns:
        dict: {"success": [...], "failed": [...]} 형태의 결과
    """
    prompts_path = Path(prompts_dir)
    output_path = Path(output_dir)

    # 출력 폴더 생성
    output_path.mkdir(parents=True, exist_ok=True)

    # 프롬프트 파일 목록 (메타/인덱스 파일 제외)
    exclude_files = [
        "prompt_index.md",
        "공통및특화작업구조설명.md",
        "style_sheet.md",
        "validation_result.md",
    ]
    # 화이트리스트 방식: 숫자로 시작하는 파일만 렌더링 대상 (01_, 02_, 10_, 11_ 등)
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

    print(f"[시작] {len(prompt_files)}개 슬라이드 프롬프트 처리")
    print(f"  - 프롬프트 폴더: {prompts_dir}")
    print(f"  - 출력 폴더: {output_dir}")
    print(f"  - 모델: {MODEL_NAME}")
    print("  - 설정: 4K, 16:9, 사고모드 활성화, 고급 텍스트 렌더링")
    print()

    # API 클라이언트 초기화
    client = genai.Client(api_key=GEMINI_API_KEY)

    results = {"success": [], "failed": []}

    for i, prompt_file in enumerate(prompt_files, 1):
        # 파일명에서 슬라이드명 추출 (01_연구비전_최종목표.md -> 01_연구비전_최종목표)
        slide_name = prompt_file.stem
        output_file = output_path / f"{slide_name}.png"

        print(f"[{i}/{len(prompt_files)}] {slide_name}")

        # 이미 생성된 파일이 있으면 스킵
        if output_file.exists():
            print(f"  [SKIP] Already exists: {output_file}")
            results["success"].append(slide_name)
            continue

        # 프롬프트 내용 추출 (전체 사용)
        prompt_content = extract_prompt_content(str(prompt_file))

        # 이미지 생성 (개별 파일 실패 시 해당 파일만 스킵하고 계속 진행)
        try:
            if generate_image(client, prompt_content, str(output_file)):
                print(f"  [OK] Saved: {output_file}")
                results["success"].append(slide_name)
            else:
                print(f"  [FAIL] Failed: {slide_name}")
                results["failed"].append(slide_name)
        except Exception as e:
            print(f"  [ERROR] Unexpected error for {slide_name}: {e}")
            results["failed"].append(slide_name)

        # API 호출 간 대기 (rate limit 방지)
        if i < len(prompt_files):
            time.sleep(2)

    # 결과 요약
    print()
    print("=" * 50)
    print(f"[완료] 성공: {len(results['success'])}, 실패: {len(results['failed'])}")
    if results["failed"]:
        print(f"[실패 목록] {', '.join(results['failed'])}")

    return results


def main():
    parser = argparse.ArgumentParser(
        description="Gemini API를 사용하여 슬라이드 프롬프트에서 이미지 생성"
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

    args = parser.parse_args()

    if not os.path.isdir(args.prompts_dir):
        print(f"[에러] 프롬프트 폴더가 존재하지 않습니다: {args.prompts_dir}")
        sys.exit(1)

    results = process_prompts(args.prompts_dir, args.output_dir)

    # 실패가 있으면 exit code 1
    sys.exit(1 if results["failed"] else 0)


if __name__ == "__main__":
    main()
