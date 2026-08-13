from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_mail import Mail
from functools import wraps
from flask import session, redirect, url_for, flash


db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = "web.login"
login_manager.login_message = "Debe iniciar sesión para continuar."
login_manager.login_message_category = "warning"
mail = Mail()


