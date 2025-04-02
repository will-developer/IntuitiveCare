from flask import Flask, jsonify, request
from flask_cors import CORS
import logging

from src.application.repositories.operator_repository import OperatorRepository
from src.application.use_cases.search_operators import SearchOperatorsUseCase

logger = logging.getLogger(__name__)

def create_app(
    operator_repository: OperatorRepository,
    search_operators_use_case: SearchOperatorsUseCase
) -> Flask:
    app = Flask(__name__)
    CORS(app)

    @app.route('/')
    def index():
        if operator_repository.is_data_loaded():
            shape = operator_repository.get_data_shape()
            return jsonify({
                "message": "API is running and data is loaded.",
                "data_shape": shape
            })
        else:
            return jsonify({
                "message": "API is running, but data failed to load or is not loaded yet."
             }), 503

    @app.route('/api/search', methods=['GET'])
    def search():
        if not operator_repository.is_data_loaded():
             logger.warning("Search request received but data is not loaded.")
             return jsonify({"error": "Data is not available for searching"}), 503

        query = request.args.get('q', default=None, type=str)
        ddd_filter = request.args.get('ddd', default=None, type=str)
        telefone_filter = request.args.get('telefone', default=None, type=str)

        try:
            results = search_operators_use_case.execute(
                query=query,
                ddd=ddd_filter,
                phone=telefone_filter
            )
            return jsonify(results)

        except Exception as e:
            logger.error(f"Error processing search request: {e}", exc_info=True)
            return jsonify({"error": "Internal server error during search"}), 500

    logger.debug("Flask app instance created.")
    return app