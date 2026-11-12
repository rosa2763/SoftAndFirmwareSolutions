from flask import Flask
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
DB_NAME = 'users_tt.db'

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = '2763'
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}' 

    db.init_app(app)

    from .main import main
    from .tt_entry import tt_entry
    from .tt_display import tt_display
    from .tt_DELETEdata import tt_DELETEdata

    app.register_blueprint(main,url_prefix='/')
    app.register_blueprint(tt_entry,url_prefix='/')
    app.register_blueprint(tt_display,url_prefix='/')
    app.register_blueprint(tt_DELETEdata,url_prefix='/')

    from .models import User,TTData

    create_database(app)

    return app
 
def create_database(app):
    with app.app_context():
        db.create_all()
