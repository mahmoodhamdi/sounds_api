"""
Swagger UI Integration for Sounds API

To enable Swagger UI, add the following to your requirements.txt:
    flask-swagger-ui

Then import and register in app/__init__.py:
    from app.swagger import register_swagger
    register_swagger(app)

Access Swagger UI at: http://localhost:5000/api/docs
"""

from flask import Blueprint, send_from_directory, current_app
import os

swagger_bp = Blueprint('swagger', __name__)

def register_swagger(app):
    """
    Register Swagger UI blueprint with the Flask app.

    Usage:
        from app.swagger import register_swagger
        register_swagger(app)
    """
    try:
        from flask_swagger_ui import get_swaggerui_blueprint

        SWAGGER_URL = '/api/docs'
        API_URL = '/swagger.yaml'

        swaggerui_blueprint = get_swaggerui_blueprint(
            SWAGGER_URL,
            API_URL,
            config={
                'app_name': "Sounds API Documentation",
                'validatorUrl': None,
                'displayRequestDuration': True,
                'docExpansion': 'list',
                'defaultModelsExpandDepth': 1,
                'defaultModelExpandDepth': 1,
                'filter': True,
                'showExtensions': True,
                'showCommonExtensions': True,
            }
        )

        app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)
        app.register_blueprint(swagger_bp)

        print(f"Swagger UI available at: http://localhost:5000{SWAGGER_URL}")

    except ImportError:
        print("flask-swagger-ui not installed. Run: pip install flask-swagger-ui")


@swagger_bp.route('/swagger.yaml')
def serve_swagger_yaml():
    """Serve the swagger.yaml file from the project root"""
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return send_from_directory(root_dir, 'swagger.yaml')


@swagger_bp.route('/swagger.json')
def serve_swagger_json():
    """
    Serve swagger spec as JSON (converted from YAML).
    Requires PyYAML: pip install pyyaml
    """
    try:
        import yaml
        import json

        root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        yaml_path = os.path.join(root_dir, 'swagger.yaml')

        with open(yaml_path, 'r', encoding='utf-8') as f:
            spec = yaml.safe_load(f)

        return current_app.response_class(
            response=json.dumps(spec, indent=2),
            status=200,
            mimetype='application/json'
        )
    except ImportError:
        return {'error': 'PyYAML not installed'}, 500
    except FileNotFoundError:
        return {'error': 'swagger.yaml not found'}, 404


# Alternative: Using flasgger (more features)
def register_flasgger(app):
    """
    Alternative: Register Flasgger for auto-generated docs from docstrings.

    Add to requirements.txt:
        flasgger

    Usage:
        from app.swagger import register_flasgger
        register_flasgger(app)
    """
    try:
        from flasgger import Swagger

        swagger_config = {
            "headers": [],
            "specs": [
                {
                    "endpoint": 'apispec',
                    "route": '/apispec.json',
                    "rule_filter": lambda rule: True,
                    "model_filter": lambda tag: True,
                }
            ],
            "static_url_path": "/flasgger_static",
            "swagger_ui": True,
            "specs_route": "/apidocs/"
        }

        template = {
            "info": {
                "title": "Sounds API",
                "description": "Educational API for language learning",
                "version": "1.0.0",
                "contact": {
                    "name": "Mahmood Hamdi",
                    "email": "hmdy7486@gmail.com"
                }
            },
            "securityDefinitions": {
                "Bearer": {
                    "type": "apiKey",
                    "name": "Authorization",
                    "in": "header",
                    "description": "JWT Authorization header using the Bearer scheme. Example: 'Bearer {token}'"
                }
            },
            "security": [
                {"Bearer": []}
            ]
        }

        Swagger(app, config=swagger_config, template=template)
        print("Flasgger available at: http://localhost:5000/apidocs/")

    except ImportError:
        print("flasgger not installed. Run: pip install flasgger")
