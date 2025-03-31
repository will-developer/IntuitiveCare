from flask import Flask, jsonify
from flask_cors import CORS
import pandas as pd
import os

app = Flask(__name__)
CORS(app)

df = pd.DataFrame()

try:
    script_dir = os.path.dirname(os.path.abspath(__file__))
    relative_csv_path = '../CSV/Relatorio_cadop.csv'
    csv_path = os.path.normpath(os.path.join(script_dir, relative_csv_path))

    print(f"Attempting to load CSV from: {csv_path}")
    df = pd.read_csv(csv_path, sep=';', low_memory=False)
    print(f"CSV loaded successfully. Shape: {df.shape}")

except FileNotFoundError:
    print(f"Error: CSV file not found at {csv_path}. DataFrame remains empty.")
except Exception as e:
    print(f"An error occurred during CSV loading: {e}")
    df = pd.DataFrame()

@app.route('/')
def index():
    if df.empty:
        return jsonify({"message": "API is running, but data is not loaded."})
    return jsonify({"message": "API is running and data loaded.", "shape": df.shape})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)