from flask_sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap
from flask_mail import Mail
from flask_debugtoolbar import DebugToolbarExtension
from flask_moment import Moment
from flask_babelex import Babel
from flask_avatars import Avatars
from flask_adminlte3 import AdminLTE3
from flask_mdbootstrap import MDBootstrap
from flask_ckeditor import CKEditor
from flask_wtf.csrf import CSRFProtect

boostrap = Bootstrap()
mail = Mail()
db = SQLAlchemy()
toolbar = DebugToolbarExtension()
moment = Moment()
babel = Babel()
avatars = Avatars()
adminlte = AdminLTE3()
mdb = MDBootstrap()
ckeditor = CKEditor()
csrf = CSRFProtect()
