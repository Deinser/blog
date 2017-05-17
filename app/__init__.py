from flask import Flask,render_template
from flask_bootstrap import Bootstrap
from flask_mail import Mail
from flask_sqlalchemy import SQLAlchemy
from flask_moment import Moment
from config import config
from flask_login import LoginManager
from flask_pagedown import PageDown

bootstrap=Bootstrap()
mail=Mail()
db=SQLAlchemy()
moment=Moment()
login_manager=LoginManager()
login_manager.session_protection='strong'
login_manager.login_view='auth.login'
pagedown=PageDown()

def create_app(config_name):
	app=Flask(__name__)
	app.config.from_object(config[config_name])
	config[config_name].init_app(app)
	
	bootstrap.init_app(app)
	mail.init_app(app)
	db.init_app(app)
	moment.init_app(app)
	login_manager.init_app(app)
	pagedown.init_app(app)
	
	from .main import main as main_blueprint #from貌似必须放到这里，放在头部导致在models.py里面不能导入
	app.register_blueprint(main_blueprint)   #本模块的内容，移下来之后正常 
	
	from .auth import auth as auth_blueprint
	app.register_blueprint(auth_blueprint,url_prefix='/auth')
	
	return app