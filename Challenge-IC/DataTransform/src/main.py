import zipfile
import os
import tempfile

# Configure paths
zip_path = os.path.join('..', '..', 'WebScraping', 'pdfs', 'Anexos.zip')

with tempfile.TemporaryDirectory() as temp_dir:
    # Extract Anexo I
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        # Basic file existence check
        anexo_file = next((f for f in zip_ref.namelist() if 'Anexo_I' in f), None)
        if not anexo_file:
            raise ValueError("Anexo I not found in ZIP")
        
        zip_ref.extract(anexo_file, temp_dir)
        print(f"Successfully extracted {anexo_file}")