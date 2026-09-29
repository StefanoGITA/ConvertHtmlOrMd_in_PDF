# Transform HTML & Markdown files in PDF
This utility is a small extension of [playwright](https://pypi.org/project/playwright/) that converts **HTML** files, **Markdown** files and **URLs** into PDF files.
My contribution consists of a set of wrappers that format the input properly and generate suitably formatted PDF files.

## Scope
The goal of this utility is to produce a PDF file that is as well formatted as possible, starting from any of the sources listed above.

## Use
The library can be imported into another project or invoked from the command line. 
When it uses from command line, it takes one mandatory argument, **source**, and an optional PDF file name `--output / -o`, to be used when you want a name different from the input file's. For details:

`python main.py --help`

When used as a library by another script, it exposes 4 entry points:
- `html_to_pdf` - Creates a PDF file from a URL or from an HTML file
- `md_to_pdf` - Creates a PDF file from a Markdown file
- `build_pdf` - Given a buffer holding an HTML file, returns a byte stream ready to be saved as a PDF file
- `md_to_html` - Converts a Markdown file into an HTML file

## PDF formatting
Formatting the PDF file correctly requires at least 3 parameters:
- The page size
- The page margins
- The resize factor of the HTML file

The utility ships with default values, stored in the [pdf_page_settings.json](config/pdf_page_settings.json) file.
You are free to edit that file or to pass a dictionary holding the expected keys with the values you want.
