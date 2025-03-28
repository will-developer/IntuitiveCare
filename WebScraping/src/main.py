import requests
from bs4 import BeautifulSoup
import os

target_url = 'https://www.gov.br/ans/pt-br/acesso-a-informacao/participacao-da-sociedade/atualizacao-do-rol-de-procedimentos'

# Page fetch
page = requests.get(target_url)
soup = BeautifulSoup(page.text, 'html.parser')

# Link detection 
pdf_links = []
for link in soup.find_all('a', class_='internal-link'):
    href = link.get('href', '')
    link_text = link.text.strip()
    if href.endswith('.pdf') and ('Anexo I' in link_text or 'Anexo II' in link_text):
        pdf_links.append(href)
        #print(f'Found! {pdf_links}\n ------')
        
if not pdf_links:
    print('No Anexos found!')
    exit()

#Pdf dowloader
print("\nStart PDF downloads -----")
for link in pdf_links:
    filename = link.split('/')[-1]
    print(f"download the: {filename}")
    response = requests.get(link)
    with open(filename, 'wb') as f:
        f.write(response.content)
print("download Success")