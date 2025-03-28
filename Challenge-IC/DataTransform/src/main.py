import zipfile
import os
import tempfile
import tabula

# paths
zip_path = os.path.join(os.path.dirname(__file__), '..', '..', 'WebScraping', 'pdfs', 'Anexos.zip')

with tempfile.TemporaryDirectory() as temp_dir:
    # Extract
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        # The file exist?
        anexo_file = next((f for f in zip_ref.namelist() if 'Anexo_I' in f), None)
        if not anexo_file:
            raise ValueError("Anexo I not found in ZIP")
        
        zip_ref.extract(anexo_file, temp_dir)
        print(f"Successfully extracted {anexo_file}")
    
    anexo_path = os.path.join(temp_dir, anexo_file)

    # PDF extraction
    print("Extracting tables from PDF ------")
    try:
        dfs = tabula.read_pdf(
            anexo_path,
            pages='1',
            lattice=True,
        )
        print(f"Found {len(dfs)} tables")
            
    except Exception as e:
        print(f"Extraction failed: {str(e)}")
        
    # extract tables    
    processed_dfs = []
    for df in dfs:
        # Initial cleaning
        df = df.dropna(axis=1, how='all')
        
        if not df.empty:
            print(f"🔄 Processing table with {df.shape[0]} rows")
            processed_dfs.append(df)

    print(f"Cleaned {len(processed_dfs)} tables")