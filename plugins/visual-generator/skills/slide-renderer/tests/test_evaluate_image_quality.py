from __future__ import annotations

# pyright: reportUnknownParameterType=false, reportMissingParameterType=false, reportUnknownArgumentType=false, reportUnknownMemberType=false

import json
from pathlib import Path
from types import SimpleNamespace


def _write_test_jpeg(module, tmp_path: Path) -> Path:
    path = tmp_path / "sample.jpg"
    image = module.PILImage.new("RGB", (16, 16), color="navy")
    image.save(path, format="JPEG")
    return path


def test_evaluate_image_quality_reports_api_errors(
    openai_renderer_module, monkeypatch, tmp_path, capsys
):
    image_path = _write_test_jpeg(openai_renderer_module, tmp_path)
    monkeypatch.setattr(
        openai_renderer_module, "_resolve_eval_model", lambda *_: "gpt-5.5"
    )

    class DummyResponses:
        def create(self, **kwargs):
            raise RuntimeError("Missing required parameter: 'text.format.name'")

    client = SimpleNamespace(responses=DummyResponses())

    result = openai_renderer_module.evaluate_image_quality(client, str(image_path))
    stdout = capsys.readouterr().out

    assert result["score"] == 0.0
    assert result["feedback"].startswith("품질 평가 API 오류")
    assert "text.format.name" in result["feedback"]
    assert "[eval-error] model=gpt-5.5:" in stdout


def test_evaluate_image_quality_reports_parse_failures(
    openai_renderer_module, monkeypatch, tmp_path, capsys
):
    image_path = _write_test_jpeg(openai_renderer_module, tmp_path)
    monkeypatch.setattr(
        openai_renderer_module, "_resolve_eval_model", lambda *_: "gpt-5.5"
    )

    class DummyResponses:
        def create(self, **kwargs):
            return SimpleNamespace(output_text="not valid json")

    client = SimpleNamespace(responses=DummyResponses())

    result = openai_renderer_module.evaluate_image_quality(client, str(image_path))
    stdout = capsys.readouterr().out

    assert result["score"] == 0.0
    assert result["feedback"].startswith("품질 평가 응답 파싱 실패")
    assert "structured output parse failed" in stdout


def test_evaluate_image_quality_preserves_concept_exemption(
    openai_renderer_module, monkeypatch, tmp_path
):
    image_path = _write_test_jpeg(openai_renderer_module, tmp_path)
    monkeypatch.setattr(
        openai_renderer_module, "_resolve_eval_model", lambda *_: "gpt-5.5"
    )

    payload = {
        "korean_text_readability": 0,
        "korean_hallucination_detection": 0,
        "content_reference_accuracy": 8,
        "layout_suitability": 8,
        "color_palette_compliance": 8,
        "overall_score": 8,
        "feedback": "clean",
    }

    class DummyResponses:
        def create(self, **kwargs):
            return SimpleNamespace(output_text=json.dumps(payload))

    client = SimpleNamespace(responses=DummyResponses())

    result = openai_renderer_module.evaluate_image_quality(
        client,
        str(image_path),
        prompt_text="concept zero text rendering",
    )

    assert result["criteria"]["korean_text_readability"] == 10.0
    assert result["criteria"]["korean_hallucination_detection"] == 10.0
    assert result["score"] == 8.0


def test_eval_ok_logs_only_once_per_module_session(
    openai_renderer_module, monkeypatch, tmp_path, capsys
):
    image_path = _write_test_jpeg(openai_renderer_module, tmp_path)
    monkeypatch.setattr(
        openai_renderer_module, "_resolve_eval_model", lambda *_: "gpt-5.5"
    )

    payload = {
        "korean_text_readability": 8,
        "korean_hallucination_detection": 8,
        "content_reference_accuracy": 8,
        "layout_suitability": 8,
        "color_palette_compliance": 8,
        "overall_score": 8,
        "feedback": "good",
    }

    class DummyResponses:
        def create(self, **kwargs):
            return SimpleNamespace(output_text=json.dumps(payload))

    client = SimpleNamespace(responses=DummyResponses())

    openai_renderer_module.evaluate_image_quality(client, str(image_path))
    openai_renderer_module.evaluate_image_quality(client, str(image_path))
    stdout = capsys.readouterr().out

    assert stdout.count("[eval-ok] model=gpt-5.5 score=8.0") == 1


def test_explicit_theme_concept_overrides_low_korean_scores(
    openai_renderer_module, monkeypatch, tmp_path
):
    image_path = _write_test_jpeg(openai_renderer_module, tmp_path)
    monkeypatch.setattr(
        openai_renderer_module, "_resolve_eval_model", lambda *_: "gpt-5.5"
    )

    # 모델이 구체적 키워드 없이도 한글 차원을 0으로 주는 상황을 재현
    payload = {
        "korean_text_readability": 0,
        "korean_hallucination_detection": 0,
        "content_reference_accuracy": 9,
        "layout_suitability": 9,
        "color_palette_compliance": 8,
        "overall_score": 9,
        "feedback": "all good",
    }

    class DummyResponses:
        def create(self, **kwargs):
            return SimpleNamespace(output_text=json.dumps(payload))

    client = SimpleNamespace(responses=DummyResponses())

    result = openai_renderer_module.evaluate_image_quality(
        client,
        str(image_path),
        # 키워드 없이 explicit theme만으로 면제되어야 함
        prompt_text="a futuristic factory illustration with no obvious flag words",
        theme="concept",
    )

    assert result["criteria"]["korean_text_readability"] == 10.0
    assert result["criteria"]["korean_hallucination_detection"] == 10.0
    # 면제되지 않은 다른 차원은 그대로 살아있어야 함
    assert result["criteria"]["content_reference_accuracy"] == 9.0


def test_explicit_theme_gov_does_not_inflate_korean_scores(
    openai_renderer_module, monkeypatch, tmp_path
):
    image_path = _write_test_jpeg(openai_renderer_module, tmp_path)
    monkeypatch.setattr(
        openai_renderer_module, "_resolve_eval_model", lambda *_: "gpt-5.5"
    )

    payload = {
        "korean_text_readability": 4,
        "korean_hallucination_detection": 5,
        "content_reference_accuracy": 8,
        "layout_suitability": 8,
        "color_palette_compliance": 8,
        "overall_score": 7,
        "feedback": "ok",
    }

    class DummyResponses:
        def create(self, **kwargs):
            return SimpleNamespace(output_text=json.dumps(payload))

    client = SimpleNamespace(responses=DummyResponses())

    result = openai_renderer_module.evaluate_image_quality(
        client,
        str(image_path),
        # prompt_text에 우연히 'concept' 단어가 있어도 explicit theme=gov가 이겼다
        prompt_text="this proposal explores the concept of digital transformation",
        theme="gov",
    )

    assert result["criteria"]["korean_text_readability"] == 4.0
    assert result["criteria"]["korean_hallucination_detection"] == 5.0


def test_extract_theme_from_filename_handles_known_and_unknown(
    openai_renderer_module,
):
    extract = openai_renderer_module._extract_theme_from_filename
    assert extract("01_theme_concept.md") == "concept"
    assert extract("05_theme_pitch.md") == "pitch"
    assert extract("03_theme_unknownish.md") is None
    assert extract("weird_name.md") is None
    assert extract("") is None


def test_resolve_theme_priority_explicit_then_filename_then_default(
    openai_renderer_module,
):
    resolve = openai_renderer_module._resolve_theme
    # explicit이 파일명보다 우선
    assert resolve(
        explicit_theme="gov",
        prompt_filename="01_theme_concept.md",
        prompt_text="",
    ) == "gov"
    # 파일명이 default보다 우선
    assert resolve(
        explicit_theme=None,
        prompt_filename="02_theme_seminar.md",
        prompt_text="",
        default_theme="gov",
    ) == "seminar"
    # 둘 다 없으면 default
    assert resolve(
        explicit_theme=None,
        prompt_filename="random.md",
        prompt_text="",
        default_theme="comparison",
    ) == "comparison"
    # 아무것도 없으면 None
    assert resolve(
        explicit_theme=None,
        prompt_filename=None,
        prompt_text="",
    ) is None


def test_normalize_theme_rejects_unknown_and_auto(openai_renderer_module):
    n = openai_renderer_module._normalize_theme
    assert n("concept") == "concept"
    assert n("GOV") == "gov"
    assert n("  whatif  ") == "whatif"
    assert n("unknown") is None
    assert n("auto") is None
    assert n(None) is None
    assert n("") is None
