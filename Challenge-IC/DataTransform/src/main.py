import zipfile
import os
import tempfile
import tabula
import pandas

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
        data = tabula.read_pdf(
            anexo_path,
            pages='all',
            lattice=True,
        )
        print(f"Found {len(data)} tables")
            
    except Exception as e:
        print(f"Extraction failed: {str(e)}")
        
    # extract tables    
    processed_data = []
    for df in data:
        # Initial cleaning empty tables
        df = df.dropna(axis=1, how='all')
        
        if not df.empty:
            processed_data.append(df)

    print(f"Cleaned {len(processed_data)} empty tables tables")

    if processed_data:
        combined_df = pandas.concat(processed_data).reset_index(drop=True)
        combined_df.rename(columns={
        'OD': 'Seg. Odontológica',
        'AMB': 'Seg. Ambulatorial',
    }, inplace=True)
        
        print("Combined dataframe shape:", combined_df.shape)
    else:
        print("No valid tables found after cleaning.")