import requests
from pathlib import Path
import os

#Create Dir for place data
def create_data_dir():
    local_dir = Path(os.path.dirname(os.path.abspath(__file__)))
    data_dir = local_dir.parent / "data" / "operations"
    data_dir.mkdir(parents=True, exist_ok=True)
    return data_dir

url = "https://dadosabertos.ans.gov.br/FTP/PDA/operadoras_de_plano_de_saude_ativas/Relatorio_cadop.csv"

try:
    response = requests.get(url)
    response.raise_for_status()
    print(f"Successful Request: (status {response.status_code})")
    create_data_dir() 
except requests.exceptions.RequestException as e:
    print(f"Download failed: {str(e)}")