#CONTROLLER
from dotenv import load_dotenv
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand

import os

load_dotenv()

from application import init_app
app = init_app(__name__)

app.jinja_options['extensions'].append('jinja2.ext.loopcontrols')
app.config["DEBUG"] = True

app.config.from_object(__name__)

#from paquete.codigo import objeto
#from carperta.codigopython import objeto
from module002.module002 import module002
from wallet.views import wallet_bp

app.register_blueprint(module002, url_prefix="/module002")
app.register_blueprint(wallet_bp, url_prefix="/wallet")

SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URI")
app.config['SECRET_KEY'] = 'EstoDeflask_wtfEsLaPolla!'
app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI
app.config["SQLALCHEMY_POOL_RECYCLE"] = 299
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

from flask_bootstrap import Bootstrap
Bootstrap(app)

from admin import init_admin
admin = init_admin(app)

from models import init_db, User
db = init_db(app)

migrate = Migrate(app,db)
manager = Manager(app)
manager.add_command('db',MigrateCommand)

from flask_login import LoginManager
login_manager = LoginManager() # Creando el objeto de la clase Login
login_manager.init_app(app) # Asociando el login a la app
login_manager.login_view = 'login' # Donde voy si no estoy loggeado

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id) # flask_login no tiene porque saber de la base de datos.

import views

if __name__ == '__main__':
    manager.run()

