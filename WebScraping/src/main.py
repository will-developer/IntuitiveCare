import requests
from bs4 import BeautifulSoup
import os
import zipfile

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
if not os.path.exists('pdfs'):
    os.makedirs('pdfs')

downloaded_files = []
failure_count = 0

print("\nStart PDF downloads -----")
for link in pdf_links:
    filename = link.split('/')[-1]
    print(f"download the: {filename}")

    try:
        response = requests.get(link, timeout=10)
        response.raise_for_status()
        
        filepath = os.path.join('pdfs', filename)
        with open(filepath, 'wb') as f:
            f.write(response.content)
            
        downloaded_files.append(filename)
        print(f"Success: {filename}")
        
    except Exception as e:
        failure_count += 1
        print(f"Failed: {filename}")
        print(f"Error: {str(e)}")

print(f"\nDownloads: {len(downloaded_files)} succeeded, {failure_count} failed")

# Zip files
if downloaded_files:
    with zipfile.ZipFile('Pdfs.zip', 'w') as zipf:
        for file in downloaded_files:
            filepathzip = os.path.join('pdfs', file)
            zipf.write(filepathzip, os.path.basename(filepathzip))
            os.remove(filepathzip)
    print(f'Zip created: Pdfs.zip in {os.path('pdfs')}')
else:
    print('No files downloaded')