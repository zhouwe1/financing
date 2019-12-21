from flask import Flask
from .extentions import db, alembic, login_manager
from .config import Config
from .models import *

flask_app = Flask(__name__)
flask_app.config.from_object(Config)

db.init_app(flask_app)
alembic.init_app(flask_app)
login_manager.init_app(flask_app)

from .controllers.home import home_blueprint
from .controllers.user import user_blueprint
from .controllers.financing import financing_blueprint

flask_app.register_blueprint(home_blueprint, url_prefix='')
flask_app.register_blueprint(user_blueprint, url_prefix='/user')
flask_app.register_blueprint(financing_blueprint, url_prefix='/invest')