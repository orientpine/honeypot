import pytest  # pyright: ignore[reportMissingImports]
import yaml  # pyright: ignore[reportMissingModuleSource]
from collections.abc import Mapping
from pathlib import Path


def _mkdir(path: Path, *, parents: bool = False) -> None:
    path.mkdir(parents=parents)


def _write_text(path: Path, content: str) -> None:
    path.write_text(content, encoding="utf-8")  # pyright: ignore[reportUnusedCallResult]


@pytest.fixture  # pyright: ignore[reportUnknownMemberType, reportUntypedFunctionDecorator]
def tmp_wiki_root(tmp_path: Path) -> Path:
    wiki = tmp_path / "wiki"
    _mkdir(wiki)
    return wiki


@pytest.fixture  # pyright: ignore[reportUnknownMemberType, reportUntypedFunctionDecorator]
def tmp_source_dir(tmp_path: Path) -> Path:
    source = tmp_path / "source"
    _mkdir(source)
    return source


@pytest.fixture  # pyright: ignore[reportUnknownMemberType, reportUntypedFunctionDecorator]
def sample_sources_yaml(tmp_path: Path) -> Mapping[str, object]:
    src_a = tmp_path / "src_a" / "doc"
    src_b = tmp_path / "src_b" / "doc"
    _mkdir(src_a, parents=True)
    _mkdir(src_b, parents=True)

    _write_text(src_a / "guide.md", "---\ntitle: Guide A\n---\nContent A\n")
    _write_text(src_b / "readme.md", "---\ntitle: Readme B\n---\nContent B\n")

    data = {
        "sources": [
            {
                "name": "test_a",
                "type": "local",
                "path": str(src_a.parent),
                "doc_path": "doc/",
                "source_top": "Test",
                "source_category": "Project",
            },
            {
                "name": "test_b",
                "type": "local",
                "path": str(src_b.parent),
                "doc_path": "doc/",
                "source_top": "Test",
                "source_category": "Project",
            },
        ],
        "settings": {"entries_subdir": True, "id_strategy": "source_prefixed"},
    }

    _write_text(tmp_path / "sources.yaml", yaml.safe_dump(data, sort_keys=False))
    return data


@pytest.fixture  # pyright: ignore[reportUnknownMemberType, reportUntypedFunctionDecorator]
def sample_project_docs(tmp_path: Path) -> Path:
    project = tmp_path / "project"
    doc = project / "doc"
    _mkdir(doc, parents=True)

    _write_text(
        doc / "guide.md",
        "---\ntitle: Guide\ntags: [test]\ndate: 2026-01-15\n---\nContent\n",
    )
    _write_text(
        doc / "readme.md",
        "---\ntitle: Readme\ntags: [docs]\ndate: 2026-02-01\n---\nReadme content\n",
    )
    return project
