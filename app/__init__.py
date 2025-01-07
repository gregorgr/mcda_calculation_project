from flask import Flask
def create_app(config_class="config.Config"):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Registracija poti
    from .routes import bp as routes_bp
    app.register_blueprint(routes_bp)
    
    return app

