import requests
from bs4 import BeautifulSoup

target_url = 'https://www.gov.br/ans/pt-br/acesso-a-informacao/participacao-da-sociedade/atualizacao-do-rol-de-procedimentos'

# Page fetch
page = requests.get(target_url)
soup = BeautifulSoup(page.text, 'html.parser')

# Simple link detection 
pdf_links = []
for link in soup.find_all('a', class_='internal-link'):
    href = link.get('href', '')
    link_text = link.text.strip()
    if href.endswith('.pdf') and ('Anexo I' in link_text or 'Anexo II' in link_text):
        pdf_links.append(href)
        print(f'Found! {pdf_links}\n ------')

if not pdf_links:
    print('No Anexos found!')
    exit()