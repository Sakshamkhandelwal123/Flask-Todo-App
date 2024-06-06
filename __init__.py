from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_mail import Mail, Message

from .config import config

db = SQLAlchemy()
migrate = Migrate()
mail = Mail()

def create_app(config_mode):
  app = Flask(__name__)
  app.config.from_object(config[config_mode])

  db.init_app(app)
  migrate.init_app(app, db)

  mail.init_app(app)

  return app