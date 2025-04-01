import os

BASE_URL = 'https://www.gov.br/ans/pt-br/acesso-a-informacao/participacao-da-sociedade/atualizacao-do-rol-de-procedimentos'
DOWNLOAD_DIR = 'pdfs'
ZIP_FILENAME = 'Anexos.zip'
ZIP_FILEPATH = os.path.join(DOWNLOAD_DIR, ZIP_FILENAME)

LINK_SELECTOR = 'a.internal-link' 
LINK_TEXT_KEYWORDS = ['Anexo I', 'Anexo II']
LINK_SUFFIX = '.pdf'

REQUEST_TIMEOUT = 10 