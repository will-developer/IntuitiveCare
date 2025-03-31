from flask import Flask, jsonify, request
from flask_cors import CORS
import pandas as pd
import os
import traceback

app = Flask(__name__)
CORS(app)

df = pd.DataFrame()

try:
    script_dir = os.path.dirname(os.path.abspath(__file__))
    relative_csv_path = '../CSV/Relatorio_cadop.csv'
    csv_path = os.path.normpath(os.path.join(script_dir, relative_csv_path))

    if not os.path.exists(csv_path):
        print(f"Error: CSV file not found at calculated path: {csv_path}")
    else:
        print(f"Attempting to load CSV from: {csv_path}")
        df = pd.read_csv(
            csv_path,
            sep=';',
            encoding='utf-8',
            dtype={'CEP': str,
                   'CNPJ': str,
                   'Registro_ANS': str,
                   'DDD': str,
                   'Telefone': str,
                   'Fax': str
                   },
            low_memory=False,
            on_bad_lines='warn'
        )
        print(f"CSV loaded successfully. Shape: {df.shape}")

except FileNotFoundError:
    print(f"Error: FileNotFoundError caught for path: {csv_path}")
    df = pd.DataFrame()
except pd.errors.ParserError as e:
    print(f"Error parsing CSV: {e}. Check separator, encoding, file integrity.")
    df = pd.DataFrame()
except Exception as e:
    print(f"An unexpected error occurred during CSV loading: {e}")
    print(traceback.format_exc())
    df = pd.DataFrame()


@app.route('/')
def index():
    if df.empty:
        return jsonify({"message": "API is running, but data is not loaded."})
    else:
        return jsonify({"message": "API is running and data loaded.", "shape": df.shape})

@app.route('/api/search', methods=['GET'])
def search():
    if df.empty:
        print("Search attempt failed: DataFrame is empty or not loaded.")
        return jsonify({"error": "Data not loaded or CSV empty"}), 500

    query = request.args.get('q', default='', type=str).lower().strip()
    print(f"Received search query: {query}")

    if not query:
        return jsonify([])

    try:
        columns_to_search = [
            'Razao_Social', 'Nome_Fantasia', 'Registro_ANS',
            'CNPJ', 'Cidade', 'UF'
        ]

        existing_columns = [col for col in columns_to_search if col in df.columns]
        if not existing_columns:
             print("Warning: None of the specified search columns exist.")
             return jsonify([])

        print(f"Searching in columns: {existing_columns}")

        mask = df[existing_columns].apply(
            lambda col: col.astype(str).str.lower().str.contains(query, na=False)
        ).any(axis=1)

        filtered_df = df.loc[mask]
        limited_df = filtered_df.head(50)

        results_df_filled = limited_df.fillna('')

        results = results_df_filled.to_dict(orient='records')

        return jsonify(results)

    except Exception as e:
        print(f"An error occurred during search: {e}")
        print(traceback.format_exc())
        return jsonify({"error": "Internal server error during search"}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)