import requests
from pathlib import Path
import os
import logging

#Log Configuration
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

#Create Dir for place data
def create_data_dir():
    local_dir = Path(os.path.dirname(os.path.abspath(__file__)))
    data_dir = local_dir.parent / "data" / "download"
    data_dir.mkdir(parents=True, exist_ok=True)
    return data_dir

url = "https://dadosabertos.ans.gov.br/FTP/PDA/operadoras_de_plano_de_saude_ativas/Relatorio_cadop.csv"

try:
    response = requests.get(url)
    response.raise_for_status()
    print(f"\nSuccessful Request: (status {response.status_code})")

    data_dir = create_data_dir() 

    if 'text/csv' not in response.headers.get('Content-Type', ''):
            print("\n Error in content type")
    else:
        # Save file
        output_path = data_dir / "archive.csv"
        output_path.write_bytes(response.content)
        print(f"\nSuccessful saved ({len(response.content)} bytes)")

except requests.exceptions.RequestException as e:
    print(f"Download failed: {str(e)}")