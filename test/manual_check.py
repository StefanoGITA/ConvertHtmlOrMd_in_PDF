from pathlib import Path
import os

from main import main

os.chdir(Path(__file__).parent.parent.absolute())

main('https://it.wikipedia.org/wiki/Pagina_principale' )
main('./source/Il Fatto Quotidiano_HOME_20260928.htm')
main('./source/md_extensions.md')
