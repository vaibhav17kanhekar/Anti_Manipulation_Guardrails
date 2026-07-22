"""
Flask API Server for Anti-Manipulation Guardrails Demo
Main entry point for the web interface
"""

import os
import sys
import json
import yaml
from datetime import datetime
from pathlib import Path

# Add the src directory to Python path
sys.path.append(str(Path(__file__).parent / 'src'))

from flask import Flask, render_template, jsonify, request, send_from_directory
from flask_cors import CORS

# Import project modules
from src.defense_strategies import DefenseStrategies
from src.evaluator import ResponseEvaluator
from src.attack_generator import AttackGenerator

def create_app():
    """Create and configure the Flask application"""
    app = Flask(__name__, 
                template_folder='templates',
                static_folder='app/static')
    
    # Enable CORS for API endpoints
    CORS(app)
    
    # Load configuration
    config_path = Path('config.yaml')
    if config_path.exists():
        with open(config_path, 'r') as f:
            app.config.update(yaml.safe_load(f))
    else:
        app.config.update({
            'SECRET_KEY': 'dev-key-change-in-production',
            'DEBUG': True,
            'MAX_CONTENT_LENGTH': 16 * 1024 * 1024,  # 16MB max file size
        })
    
    # Initialize core components
    app.defense_strategies = DefenseStrategies()
    app.evaluator = ResponseEvaluator()
    app.attack_generator = AttackGenerator()
    
    # Import routes
    from app.routes import register_routes
    register_routes(app)
    
    return app

# Create the application instance
app = create_app()

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    # Run the Flask application
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_DEBUG', 'True').lower() == 'true'
    
    print(f"""
    ============================================
    Anti-Manipulation Guardrails Web Interface
    ============================================
    Local: http://localhost:{port}
    API Documentation: http://localhost:{port}/api/docs
    
    Press Ctrl+C to stop the server
    ============================================
    """)
    
    app.run(host='0.0.0.0', port=port, debug=debug)