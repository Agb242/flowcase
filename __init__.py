import os
from flask import Flask
from werkzeug.middleware.proxy_fix import ProxyFix
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_wtf import CSRFProtect
from utils import docker as docker_utils

__version__ = "develop"

db = SQLAlchemy()
migrate = Migrate()
bcrypt = Bcrypt()
login_manager = LoginManager()
login_manager.login_view = 'auth.index'  # Fixed: Use proper endpoint name

def create_app(config=None):
	app = Flask(__name__)
	
	from config.config import configure_app
	configure_app(app, config)
	
	app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_port=1)
	db.init_app(app)
	migrate.init_app(app, db)
	bcrypt.init_app(app)
	login_manager.init_app(app)
	csrf = CSRFProtect(app)
	
	docker_utils.init_docker()
	# Initialize rate limiting
	from flask_limiter import Limiter
	from flask_limiter.util import get_remote_address
	limiter = Limiter(key_func=get_remote_address)
	# Apply global rate limiting
	app.config['RATELIMIT_HEADERS_ENABLED'] = True
	limiter.init_app(app)
	
	# Register blueprints
	from routes.auth import auth_bp
	from routes.health import health_bp
	from routes.admin import admin_bp
	from routes.admin_api import admin_api_bp
	from routes.droplet import droplet_bp
	from routes.workshops import workshop_bp
	# Removed obsolete blueprints: tenant_bp, pages_bp
	# (features integrated in dashboard)
	
	app.register_blueprint(auth_bp)
	app.register_blueprint(health_bp, url_prefix='/api')
	app.register_blueprint(admin_bp, url_prefix='/api/admin')
	app.register_blueprint(admin_api_bp)
	app.register_blueprint(droplet_bp)
	app.register_blueprint(workshop_bp)
	
	@app.errorhandler(404)
	def page_not_found(e):
		from flask import render_template
		return render_template('404.html'), 404
	
	return app

def initialize_database_and_setup():
	db.create_all()
	from utils.setup import initialize_app
	from flask import current_app
	initialize_app(current_app) 