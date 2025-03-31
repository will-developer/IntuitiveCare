from flask import Flask, jsonify
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

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)