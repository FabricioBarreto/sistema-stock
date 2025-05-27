import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

db = SQLAlchemy()
login_manager = LoginManager()

def create_app():
    """Crea y configura la aplicación Flask."""
    app = Flask(__name__)
    # Configuración segura usando variables de entorno
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'clave-secreta')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'mysql+pymysql://root:root@localhost/inventario_db')

    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'main.login'

    # Registro de blueprints
    from .routes import main
    app.register_blueprint(main)

    # Importa modelos después de inicializar la app
    from .models import Usuario

    @login_manager.user_loader
    def load_user(user_id):
        return Usuario.query.get(int(user_id))

    return app