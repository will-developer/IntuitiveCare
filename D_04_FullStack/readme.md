# Search API FullStack

This project implements a web interface for searching a dataset of Brazilian National Supplementary Health Agency (ANS) registered operators. It consists of a Python Flask backend providing a search API and a Vue.js frontend for user interaction and data display.

## Features

- **Textual Search API:** A Python Flask backend exposes a `/api/search` endpoint that performs textual searches across multiple fields of operator data loaded from a CSV file.
- **Specific Filters:** The API supports filtering by DDD and Telephone number for more targeted searches.
- **Vue.js Frontend:** A user-friendly web interface built with Vue.js allows users to input search queries and view results dynamically.
- **Debounced Search:** The frontend implements debouncing on the search input to minimize API requests during typing.
- **Loading and Error States:** The frontend UI provides clear feedback on loading and error conditions during API requests.
- **Display of Operator Details:** Search results are presented in a structured format, displaying key information for each operator.
- **Postman Collection (for API Testing):** A Postman collection is included to demonstrate and test the API endpoints.

## Setup

To run the project locally, follow these steps:

**1. Backend Setup (Python Flask):**

- Navigate to the `backend` directory:

```bash
  cd backend
```

- Create a virtual environment (recommended):

```bash
python -m venv venv
```

- Activate the virtual environment: (If you have already done it, skip this)

- On Linux/macOS:

```bash
source venv/bin/activate
```

- On Windows wish bash:

```bash
source venv\Scripts\activate
```

- Install Python dependencies: (If you have already done it, skip this)

```bash
pip install -r requirements.txt
```

- Run the Flask backend application:

```bash
cd backend/
python -m src.main
```

- The backend will start running at `http://0.0.0.0:5000/` (accessible on your network) or `http://127.0.0.1:5000` (localhost only).

**2. Frontend Setup (Vue.js with Vite):**

- Open a new terminal window.
- Navigate to the `frontend` directory:

```bash
cd frontend
```

- Install Node.js dependencies:

```bash
npm install
```

- Run the Vue.js development server:

```bash
npm run dev
```

- The frontend application will be accessible in your browser at a URL like `http://localhost:5173` (the port might vary).

**3. CSV Data File:**

- Ensure you have the `Relatorio_cadop.csv` file.
- Place the `Relatorio_cadop.csv` file in a directory named `CSV` at the root of the project, alongside the `backend` and `frontend` folders. The project expects the following structure:

```
D__04_FullStack/
├── backend/
├── frontend/
├── CSV/
│   └── Relatorio_cadop.csv
└── README.md
└── postman/
```

## API Endpoint

### `GET /api/search`

This endpoint is the core of the search functionality. It accepts the following optional query parameters to filter and search operator data:

- **`q` (General Text Query):**
  - Parameter Name: `q`
  - Type: String
  - Optional: Yes
  - Description: Performs a case-insensitive textual search across the following columns: `Razao_Social`, `Nome_Fantasia`, `Registro_ANS`, `CNPJ`, `Cidade`, `UF`, `CEP`, `Modalidade`, `Logradouro`, `Bairro`, `Telefone`, `Endereco_eletronico`, `Representante`. Returns records that contain the query term in any of these columns.

## Postman Collection

To facilitate testing and exploration of the API, a Postman collection should be created. This collection can be exported and shared separately, allowing users to easily send requests to the `/api/search` endpoint with various parameters and examine the responses.
