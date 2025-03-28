import requests
from bs4 import BeautifulSoup

target_url = 'https://www.gov.br/ans/pt-br/acesso-a-informacao/participacao-da-sociedade/atualizacao-do-rol-de-procedimentos'

# Page fetch
page = requests.get(target_url)
soup = BeautifulSoup(page.text, 'html.parser')

# Simple link detection 
pdf_links = []
for link in soup.find_all('a'):
    href = link.get('href', '')
    if href.endswith('.pdf'):
        pdf_links.append(href)

print(f'Found {len(pdf_links)} PDF links')