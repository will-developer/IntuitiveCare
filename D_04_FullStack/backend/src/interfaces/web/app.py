import logging
from flask import Flask, jsonify, request
from flask_cors import CORS

from src.config import settings
from src.infrastructure.repositories.csv_operator_repository import CsvOperatorRepository
from src.application.use_cases.search_operators import SearchOperatorsUseCase
from src.application.repositories.operator_repository import OperatorRepository

logger = logging.getLogger(__name__)

def create_app(
    operator_repository: OperatorRepository,
    search_operators_use_case: SearchOperatorsUseCase
) -> Flask:
    app = Flask(__name__)
    CORS(app)
    logger.info("Flask app created and CORS enabled.")

    @app.route('/')
    def index():
        logger.debug("Request received for index route '/'")
        if operator_repository.is_data_loaded():
            shape = operator_repository.get_data_shape()
            response_data = {
                "message": "API is running and data is loaded.",
                "data_shape": shape
            }
            logger.info(f"Index route response (data loaded): {response_data}")
            return jsonify(response_data)
        else:
            response_data = {
                "message": "API is running, but data failed to load or is not loaded yet."
            }
            logger.warning(f"Index route response (data not loaded): {response_data}")
            return jsonify(response_data), 503

    @app.route('/api/search', methods=['GET'])
    def search():
        logger.debug(f"Request received for search route '/api/search' with args: {request.args}")
        if not operator_repository.is_data_loaded():
             logger.warning("Search request received but data is not loaded.")
             return jsonify({"error": "Data is not available for searching"}), 503

        query = request.args.get('q', default=None, type=str)
        ddd_filter = request.args.get('ddd', default=None, type=str)
        telefone_filter = request.args.get('telefone', default=None, type=str)
        logger.debug(f"Search parameters extracted - query: {query}, ddd: {ddd_filter}, telefone: {telefone_filter}")

        try:
            results = search_operators_use_case.execute(
                query=query,
                ddd=ddd_filter,
                phone=telefone_filter
            )
            logger.info(f"Search executed successfully. Found {len(results)} results for query='{query}', ddd='{ddd_filter}', phone='{telefone_filter}'.")
            return jsonify(results)

        except Exception as e:
            logger.error(f"An unexpected error occurred during search endpoint processing: {e}", exc_info=True)
            return jsonify({"error": "Internal server error during search"}), 500

    return app

def run_dev_server():
    logger.info("Initializing application dependencies for development server...")

    logger.info(f"Using CSV file path from settings: {settings.CSV_FILE_PATH}")
    csv_repo = CsvOperatorRepository(csv_file_path=settings.CSV_FILE_PATH)

    logger.info("Attempting to load data into repository...")
    csv_repo.load_data()

    if not csv_repo.is_data_loaded():
         logger.critical("*****************************************************")
         logger.critical("******** WARNING: DATA FAILED TO LOAD ***************")
         logger.critical("**** API will run but search will not function. *****")
         logger.critical("**** Check CSV path and file integrity. *************")
         logger.critical("*****************************************************")
    else:
         logger.info("Data loaded successfully into repository.")

    search_uc = SearchOperatorsUseCase(operator_repository=csv_repo)
    logger.info("SearchOperatorsUseCase initialized.")

    logger.info("Creating Flask app instance using factory...")
    flask_app = create_app(
        operator_repository=csv_repo,
        search_operators_use_case=search_uc
    )
    logger.info("Flask app instance created.")

    logger.info(f"Starting Flask development server on {settings.FLASK_HOST}:{settings.FLASK_PORT} with debug={settings.FLASK_DEBUG}")
    try:
        flask_app.run(
            host=settings.FLASK_HOST,
            port=settings.FLASK_PORT,
            debug=settings.FLASK_DEBUG
        )
    except Exception as e:
        logger.critical(f"Failed to run Flask development server: {e}", exc_info=True)