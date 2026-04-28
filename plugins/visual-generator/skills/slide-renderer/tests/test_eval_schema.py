from __future__ import annotations

# pyright: reportUnknownParameterType=false, reportMissingParameterType=false, reportUnknownArgumentType=false, reportUnknownMemberType=false

import json
from pathlib import Path
from types import SimpleNamespace


def _write_test_image(module, tmp_path: Path) -> Path:
    path = tmp_path / "sample.png"
    image = module.PILImage.new("RGB", (8, 8), color="white")
    image.save(path, format="PNG")
    return path


def test_evaluation_schema_matches_responses_text_format(openai_renderer_module):
    fmt = openai_renderer_module.EVALUATION_SCHEMA["format"]

    assert fmt["type"] == "json_schema"
    assert fmt["name"] == "ImageQualityEvaluation"
    assert fmt["strict"] is True
    assert "json_schema" not in fmt
    assert fmt["schema"]["additionalProperties"] is False
    assert set(fmt["schema"]["properties"].keys()) == {
        "korean_text_readability",
        "korean_hallucination_detection",
        "content_reference_accuracy",
        "layout_suitability",
        "color_palette_compliance",
        "overall_score",
        "feedback",
    }


def test_evaluate_image_quality_sends_schema_via_text_parameter(
    openai_renderer_module, monkeypatch, tmp_path
):
    image_path = _write_test_image(openai_renderer_module, tmp_path)
    monkeypatch.setattr(
        openai_renderer_module, "_resolve_eval_model", lambda *_: "gpt-5.5"
    )

    payload = {
        "korean_text_readability": 8,
        "korean_hallucination_detection": 9,
        "content_reference_accuracy": 8,
        "layout_suitability": 7,
        "color_palette_compliance": 8,
        "overall_score": 8,
        "feedback": "ok",
    }
    captured = {}

    class DummyResponses:
        def create(self, **kwargs):
            captured.update(kwargs)
            return SimpleNamespace(output_text=json.dumps(payload))

    client = SimpleNamespace(responses=DummyResponses())

    result = openai_renderer_module.evaluate_image_quality(client, str(image_path))

    assert captured["model"] == "gpt-5.5"
    assert captured["text"] == openai_renderer_module.EVALUATION_SCHEMA
    assert result["score"] == 8.0
