from flask import Flask, session
from flask_login import current_user
from flask_sqlalchemy import models_committed
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
from .controllers.analyser import analyse_blueprint

flask_app.register_blueprint(home_blueprint, url_prefix='')
flask_app.register_blueprint(user_blueprint, url_prefix='/user')
flask_app.register_blueprint(financing_blueprint, url_prefix='/invest')
flask_app.register_blueprint(analyse_blueprint, url_prefix='/analyse')


@flask_app.before_request
def load_avatar():
    if 'user_id' in session and 'avatar' not in session:
        session['avatar'] = current_user.avatar


@models_committed.connect_via(flask_app)
def update_cache(sender, changes):
    try:
        for model, operation in changes:
            print(model.__dict__, operation)
            model.clear_cache()
    except AttributeError:
        pass
