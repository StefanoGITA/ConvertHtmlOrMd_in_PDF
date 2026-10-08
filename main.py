import json
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urlparse

import markdown
from jinja2 import Template
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
from playwright.sync_api import sync_playwright
from pymdownx.superfences import fence_div_format


@dataclass
class PdfPageSettings:
    page_format: str
    scale: float
    margins: dict[str, str]

def wrap_md_html_in_template(
        content_html: str,
        template_str: str,
        title: str) -> str:
    template = Template(template_str)
    return template.render(content=content_html, title=title)


def md_to_html(
        stream_data: str,
        title: str,
        template_file: str | Path | None = None
) -> str:
    if not template_file:
        template_file = Path(__file__).parent / "config/template.html"

    template_str = Path(template_file).read_text(encoding="utf-8")
    md_html = markdown.markdown(
        stream_data,
        extensions=["pymdownx.arithmatex", "pymdownx.superfences", "tables", "toc", "smarty"],
        extension_configs={
            "pymdownx.arithmatex": {
                "generic": True,
            },
            "pymdownx.superfences": {
                "custom_fences": [
                    {
                        "name": "mermaid",
                        "class": "mermaid",
                        "format": fence_div_format,
                    }
                ]
            },
        },
    )
    return wrap_md_html_in_template(md_html, template_str=template_str, title=title)


def build_pdf(
    html: str,
    pdf_page_settings: PdfPageSettings | None = None,
) -> bytes:
    if not isinstance(html, str):
        raise TypeError("Source must be a buffer or an url")
    
    if not pdf_page_settings:
        pdf_page_settings_f = Path(__file__).parent / "config/pdf_page_settings.json"
        if not pdf_page_settings_f.is_file():
            raise FileNotFoundError(f"If don't pass the json with the pdf page settings of the page this app require "
                                    f"the maring file: {pdf_page_settings_f}, that was not found")
        with pdf_page_settings_f.open("r", encoding="utf-8") as f:
            pdf_page_settings = PdfPageSettings(**json.load(f))

    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        if html.startswith(('http://', 'https://')):
            page.goto(html)
        else:
            page.set_content(html, wait_until="load")
        try:
            page.wait_for_function(
                "document.documentElement.getAttribute('data-render-ready') === 'true'",
                timeout=15000,
            )
        except PlaywrightTimeoutError:
            pass

        pdf_bytes = page.pdf(
            print_background=True,
            format=pdf_page_settings.page_format,
            scale=pdf_page_settings.scale,
            margin=pdf_page_settings.margins
        )
        browser.close()
    return pdf_bytes

def html_to_pdf(
    html: str,
    output_file: str,
    pdf_page_settings: PdfPageSettings | dict[str, str] | None = None,
) -> None:
    if isinstance(pdf_page_settings, dict):
        pdf_page_settings = PdfPageSettings(**pdf_page_settings)
    pdf_bytes = build_pdf(html=html, pdf_page_settings=pdf_page_settings)
    with open(output_file, "wb") as fw:
        fw.write(pdf_bytes)
        print(f"Generated pdf file: {output_file}")


def md_to_pdf(
    stream_data: str,
    output_file: str,
    pdf_page_settings: PdfPageSettings | dict[str, str] | None = None,
    title: str | None = None
) -> None:
    if isinstance(pdf_page_settings, dict):
        pdf_page_settings = PdfPageSettings(**pdf_page_settings)

    if not title:
        title = Path(output_file).stem
    pdf_bytes = build_pdf(html=md_to_html(stream_data, title), pdf_page_settings=pdf_page_settings)
    with open(output_file, "wb") as fw:
        fw.write(pdf_bytes)
        print(f"Generated pdf file: {output_file}")


def main(
        source_url_file: str,
        output_file: str | None = None,
        pdf_page_settings: dict[str, str] | None = None,
) -> None:
    if source_url_file.startswith(('http://', 'https://')):
        # Input is an url
        if not output_file:
            parsed = urlparse(source_url_file)
            output_file = parsed.netloc + parsed.path.replace('/', '-') + '.pdf'

        func_to_call = html_to_pdf
        url = source_url_file
    else:
        # Input is an file
        source_url_file = Path(source_url_file)
        if not source_url_file.exists():
            raise FileNotFoundError(f'File {source_url_file} not found')
        if not output_file:
            output_file = source_url_file.stem + '.pdf'

        suffix = source_url_file.suffix.lower()
        url = source_url_file.read_text(encoding="utf-8")

        if suffix == '.md':
            func_to_call = md_to_pdf
        else:
            func_to_call = html_to_pdf

    func_to_call(url, output_file, pdf_page_settings)


if __name__ == "__main__":
    from typing import Annotated

    import typer

    def cli(
            source: Annotated[
                str,
                typer.Argument(help="The URL or file path to be processed")
            ],
            output_file: Annotated[
                str | None,
                typer.Option("--output", "-o", help="If You wish a output file name different from default")
            ] = None,
    ) -> None:
        main(source, output_file)

    typer.run(cli)
