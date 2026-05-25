from flask import Flask
from flask_cors import CORS
from backend.config import DEBUG, PORT
from backend.database import db, init_db
from backend.database.models import User
from backend.auth.routes import auth_bp
from backend.api.routes import api_bp
from backend.utils.logging import setup_logging
import os


def create_app():
    """Create and configure the Flask application"""
    app = Flask(__name__, static_folder='../frontend/dist', static_url_path='/')
    
    # Enable CORS
    CORS(app, resources={r"/api/*": {"origins": "*"}, r"/auth/*": {"origins": "*"}})
    
    # Setup logging
    logger = setup_logging(app)
    logger.info("Starting MuSync 2.0")
    
    # Initialize database
    init_db(app)
    
    # Register blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(api_bp)
    
    # Initialize scheduler
    from backend.api.routes import scheduler_manager
    with app.app_context():
        scheduler_manager.initialize_jobs()
    
    # Create default user if none exists
    with app.app_context():
        if not User.query.first():
            default_user = User(
                id="default_user",
                username="default"
            )
            db.session.add(default_user)
            db.session.commit()
            logger.info("Created default user")
    
    # Serve frontend (if built)
    @app.route('/', defaults={'path': ''})
    @app.route('/<path:path>')
    def serve_frontend(path):
        if path != "" and os.path.exists(app.static_folder + '/' + path):
            return app.send_static_file(path)
        return app.send_static_file('index.html')
    
    # Shutdown handler
    import atexit
    atexit.register(scheduler_manager.shutdown)
    
    logger.info(f"MuSync 2.0 running on port {PORT}")
    return app


if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=PORT, debug=DEBUG)
