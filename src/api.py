from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename
from src.utils.auth import require_team_auth, RateLimiter
from src.answer_generator import answer_generator
from src.document_processor import document_processor
from src.vector_store import vector_store
from src.config import config
from flask_talisman import Talisman
from datetime import datetime
import logging
import time

# Initialize Flask app
app = Flask(__name__)

# Configure upload settings
app.config['MAX_CONTENT_LENGTH'] = config.MAX_UPLOAD_SIZE_MB * 1024 * 1024

# Initialize security headers with Talisman
Talisman(app,
         force_https=config.ENABLE_HTTPS,
         strict_transport_security=True,
         session_cookie_secure=True,
         content_security_policy={
             'default-src': "'self'",
             'img-src': '*',
             'script-src': "'self'"
         }
         )

# Initialize rate limiter
rate_limiter = RateLimiter(
    window=60,  # 60 seconds window
    max_requests=100  # 100 requests per window
)

# Setup logging
logger = logging.getLogger(__name__)


@app.before_request
def before_request():
    """Pre-request processing"""
    request.start_time = time.time()


@app.after_request
def after_request(response):
    """Post-request processing"""
    duration = time.time() - request.start_time

    # Try to access JSON only if it exists, to prevent JSONDecodeError
    team_id = None
    if request.is_json:
        json_data = request.get_json(silent=True)  # silent=True prevents error if JSON is invalid
        team_id = json_data.get('team_id') if json_data else None

    # Log request details
    logger.info(
        "Request processed",
        extra={
            "path": request.path,
            "method": request.method,
            "duration": duration,
            "status_code": response.status_code,
            "team_id": request.args.get('team_id') or team_id
        }
    )

    return response


@app.errorhandler(Exception)
def handle_error(error):
    """Global error handler"""
    logger.error(
        f"Unhandled error: {str(error)}",
        exc_info=error,
        extra={
            "path": request.path,
            "method": request.method
        }
    )

    return jsonify({
        "error": "Internal server error",
        "message": str(error) if config.DEBUG else "An unexpected error occurred"
    }), 500


@app.route("/health", methods=['GET'])
def health_check():
    """System health check endpoint"""
    try:
        # Check vector store connection
        vector_store.client.get_collections()

        # Return health status
        return jsonify({
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "components": {
                "vector_store": "healthy",
                "api": "healthy"
            }
        })

    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return jsonify({
            "status": "unhealthy",
            "timestamp": datetime.utcnow().isoformat(),
            "error": str(e)
        }), 500


@app.route("/answer", methods=['POST'])
@require_team_auth
def get_answer():
    """
    Generate answer for question within team scope

    Expected JSON body:
    {
        "team_id": "string",
        "question": "string"
    }
    """
    try:
        # Validate request
        data = request.json
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400

        team_id = data.get('team_id')
        question = data.get('question')

        if not question:
            return jsonify({"error": "Question is required"}), 400

        # Check rate limit
        if not rate_limiter.is_allowed(team_id):
            return jsonify({"error": "Rate limit exceeded"}), 429

        # Generate answer
        response = answer_generator.generate_answer(team_id, question)

        return jsonify(response)

    except Exception as e:
        logger.error(
            f"Error generating answer: {str(e)}",
            extra={"team_id": data.get('team_id') if data else None}
        )
        return jsonify({"error": str(e)}), 500


@app.route("/upload", methods=['POST'])
@require_team_auth
def upload_file():
    """
    Upload and process PDF within team scope

    Form data:
    - file: PDF file
    - team_id: string
    - document_id: string
    """
    try:
        # Validate file
        if 'file' not in request.files:
            return jsonify({"error": "No file part"}), 400

        file = request.files['file']
        if file.filename == '':
            return jsonify({"error": "No selected file"}), 400

        if not file.filename.endswith('.pdf'):
            return jsonify({"error": "Only PDF files are allowed"}), 400

        # Get form data
        team_id = request.form['team_id']
        document_id = request.form['document_id']

        # Check rate limit
        if not rate_limiter.is_allowed(team_id):
            return jsonify({"error": "Rate limit exceeded"}), 429

        # Process file
        chunks = document_processor.process_pdf(
            pdf_file=file,
            team_id=team_id,
            doc_name=secure_filename(file.filename),
            document_id=document_id
        )

        return jsonify({
            "status": "success",
            "chunks_processed": len(chunks),
            "document_id": document_id,
            "filename": secure_filename(file.filename)
        })

    except Exception as e:
        logger.error(
            f"Error processing upload: {str(e)}",
            extra={"team_id": request.form.get('team_id')}
        )
        return jsonify({"error": str(e)}), 500


@app.route("/documents", methods=['GET'])
@require_team_auth
def list_documents():
    """
    List documents available for a team

    Query parameters:
    - team_id: string
    """
    try:
        team_id = request.args.get('team_id')

        # Get documents from vector store
        documents = vector_store.get_team_documents(team_id)

        return jsonify({
            "status": "success",
            "documents": documents
        })

    except Exception as e:
        logger.error(
            f"Error listing documents: {str(e)}",
            extra={"team_id": request.args.get('team_id')}
        )
        return jsonify({"error": str(e)}), 500


@app.route("/documents/<document_id>", methods=['DELETE'])
@require_team_auth
def delete_document(document_id):
    """
    Delete a document and its vectors

    Path parameters:
    - document_id: string

    Query parameters:
    - team_id: string
    """
    try:
        team_id = request.args.get('team_id')

        # Delete document vectors
        deleted_count = vector_store.delete_document(
            team_id=team_id,
            document_id=document_id
        )

        return jsonify({
            "status": "success",
            "document_id": document_id,
            "vectors_deleted": deleted_count
        })

    except Exception as e:
        logger.error(
            f"Error deleting document: {str(e)}",
            extra={
                "team_id": request.args.get('team_id'),
                "document_id": document_id
            }
        )
        return jsonify({"error": str(e)}), 500


# Optional: Add CORS support if needed
@app.after_request
def add_cors_headers(response):
    """Add CORS headers to response"""
    if config.ENABLE_CORS:
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type,Authorization'
        response.headers['Access-Control-Allow-Methods'] = 'GET,PUT,POST,DELETE'
    return response


if __name__ == "__main__":
    # Initialize vector store collection on startup
    vector_store.setup_collection()

    # Start server
    app.run(
        host='0.0.0.0',
        port=config.PORT,
        debug=config.DEBUG,
        ssl_context='adhoc' if config.ENABLE_HTTPS else None
    )