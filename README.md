# Transform HTML & Markdown files in PDF
Questa utility è una piccola estensione della [playwright](https://pypi.org/project/playwright/) che consente di convertire file **htlm**, file **Markdown** ed **indirizzi url** in file PFD.   
Il mio contributo è stato quello di creare dei wrapper che consentono di formattare adeguatamente l'input e generare degli dei file PDF oportunamente formattati. 

## Scope
# todo

## Use
La libreria può essere importata in un altro progetto o può essere invocata da linea di comando e prevede un argomento obbligatorio **source** ed l'eventuale nome del file pdf "--output -o" nel caso lo si voglia diverso dal nome del file diinput, per i dettagli:

`pytohn main.py --help`
 
Usata come sorgente da un'altro script prevede 3 punti d'ingresso:
- html_to_pdf - Crea un file pdf fa un url o da un file html
- md_to_pdf - Crea un file pdf fa un file md
- build_pdf - Dato uno buffer relativo ad un file html, restitusce un stream di byte pronto da essere salvato come file PDF
- md_to_html converte un file markdown in file html

## Todo, spiegazione margins 
[pdf_page_margins.json](config/pdf_page_margins.json)


