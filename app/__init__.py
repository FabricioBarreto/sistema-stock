from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

db = SQLAlchemy()
login_manager = LoginManager()

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'clave-secreta'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:root@localhost/inventario_db'

    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'main.login'  # redirige al login si no está logueado

    from .routes import main
    app.register_blueprint(main)

    return app

from .models import Usuario

@login_manager.user_loader
def load_user(user_id):
    return Usuario.query.get(int(user_id))
