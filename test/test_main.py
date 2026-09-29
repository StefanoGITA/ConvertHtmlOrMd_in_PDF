import json
from pathlib import Path

import pytest

import main as app
from main import (
    PdfPageSettings,
    build_pdf,
    html_to_pdf,
    md_to_html,
    md_to_pdf,
    wrap_md_html_in_template,
)

SETTINGS_FILE = Path(app.__file__).parent / "config" / "pdf_page_settings.json"


# ---------------------------------------------------------------- template / md
def test_wrap_md_html_in_template_renders_content_and_title():
    out = wrap_md_html_in_template("<p>x</p>", "<t>{{ title }}</t><b>{{ content }}</b>", "My title")
    assert out == "<t>My title</t><b><p>x</p></b>"


def test_md_to_html_uses_title_and_content():
    html = md_to_html("# Hello", title="My title")
    assert "My title" in html
    assert "Hello" in html


def test_md_to_html_custom_template(tmp_path):
    tpl = tmp_path / "t.html"
    tpl.write_text("[{{ title }}]{{ content }}", encoding="utf-8")
    html = md_to_html("**b**", title="T", template_file=tpl)
    assert html.startswith("[T]")
    assert "<strong>b</strong>" in html


def test_md_to_html_table_extension():
    md = "| a | b |\n|---|---|\n| 1 | 2 |\n"
    assert "<table>" in md_to_html(md, title="t")


def test_md_to_html_mermaid_fence():
    md = "```mermaid\ngraph TD; A-->B;\n```\n"
    assert 'class="mermaid"' in md_to_html(md, title="t")


def test_md_to_html_arithmatex():
    assert "arithmatex" in md_to_html("$$x^2$$", title="t")


def test_md_to_html_toc_and_smarty():
    html = md_to_html('# Title\n\n"quoted"', title="t")
    assert 'id="title"' in html
    assert "&ldquo;quoted&rdquo;" in html


# ---------------------------------------------------------------------- settings
def test_default_settings_file_builds_dataclass():
    with SETTINGS_FILE.open(encoding="utf-8") as f:
        settings = PdfPageSettings(**json.load(f))
    assert settings.page_format
    assert settings.scale > 0
    assert set(settings.margins) == {"top", "bottom", "left", "right"}


def test_settings_unknown_or_missing_keys_raise():
    with pytest.raises(TypeError):
        PdfPageSettings(page_format="A4", scale=1, margins={}, extra=1)
    with pytest.raises(TypeError):
        PdfPageSettings(page_format="A4")


# ------------------------------------------------------------------- build_pdf
def test_build_pdf_rejects_non_str():
    with pytest.raises(TypeError):
        build_pdf(b"<html></html>")  # type: ignore[arg-type]


# ------------------------------------------------------------------------ main
@pytest.fixture
def calls(monkeypatch):
    """Replace the converters used by main() and record how they are called."""
    recorded = []

    def fake(name):
        def _f(source, output_file, pdf_page_settings=None):
            recorded.append((name, source, output_file, pdf_page_settings))
        return _f

    monkeypatch.setattr(app, "html_to_pdf", fake("html"))
    monkeypatch.setattr(app, "md_to_pdf", fake("md"))
    return recorded


def test_main_missing_file_raises(tmp_path):
    with pytest.raises(FileNotFoundError):
        app.main(str(tmp_path / "nope.md"))


def test_main_md_file_dispatch(tmp_path, calls):
    src = tmp_path / "doc.md"
    src.write_text("# hi", encoding="utf-8")
    app.main(str(src))
    assert calls == [("md", "# hi", "doc.pdf", None)]


@pytest.mark.parametrize("name", ["page.html", "page.htm", "page.txt"])
def test_main_other_files_are_treated_as_html(tmp_path, calls, name):
    src = tmp_path / name
    src.write_text("<p>x</p>", encoding="utf-8")
    app.main(str(src), output_file="out.pdf")
    assert calls == [("html", "<p>x</p>", "out.pdf", None)]


def test_main_url_default_output_name(calls):
    app.main("https://example.org/wiki/Page")
    assert calls == [("html", "https://example.org/wiki/Page", "example.org-wiki-Page.pdf", None)]


def test_main_passes_settings_dict(tmp_path, calls):
    src = tmp_path / "doc.md"
    src.write_text("x", encoding="utf-8")
    settings = {"page_format": "A5", "scale": 1.0, "margins": {"top": "1mm"}}
    app.main(str(src), pdf_page_settings=settings)
    assert calls[0][3] == settings


# ---------------------------------------------------------------- integration
CUSTOM = PdfPageSettings(page_format="A5", scale=1.0, margins={"top": "5mm", "bottom": "5mm"})


@pytest.mark.slow
def test_build_pdf_inline_html_default_settings():
    pdf = build_pdf("<h1>ciao</h1>")
    assert pdf.startswith(b"%PDF")


@pytest.mark.slow
def test_html_to_pdf_accepts_dict_settings(tmp_path):
    out = tmp_path / "o.pdf"
    html_to_pdf("<h1>x</h1>", str(out), {"page_format": "A5", "scale": 1.0, "margins": {"top": "5mm"}})
    assert out.read_bytes().startswith(b"%PDF")


@pytest.mark.slow
def test_md_to_pdf_writes_file_with_custom_settings(tmp_path):
    out = tmp_path / "o.pdf"
    md_to_pdf("# Title\n\ntext", str(out), pdf_page_settings=CUSTOM)
    assert out.read_bytes().startswith(b"%PDF")
