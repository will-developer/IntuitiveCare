from flask import Flask, jsonify
from flask_cors import CORS
import pandas as pd
import os

app = Flask(__name__)
CORS(app)

df = pd.DataFrame()
csv_path = ""

try:
    script_dir = os.path.dirname(os.path.abspath(__file__))
    relative_csv_path = '../CSV/Relatorio_cadop.csv'
    csv_path = os.path.normpath(os.path.join(script_dir, relative_csv_path))
    df = pd.read_csv(csv_path, sep=';', low_memory=False)
except FileNotFoundError:
    df = pd.DataFrame()
except Exception:
    df = pd.DataFrame()

@app.route('/')
def index():
    return jsonify({"message": "API is running"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)