import os

class Config:
  SQLALCHEMY_TRACK_MODIFICATIONS = True
  SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')
  SECRET_KEY = os.getenv('SECRET_KEY')
  MAIL_SERVER = 'smtp.sendgrid.net'
  MAIL_PORT = 587
  MAIL_USE_TLS = True
  MAIL_USERNAME = 'apikey'
  MAIL_PASSWORD = os.getenv('SENDGRID_API_KEY')
  MAIL_DEFAULT_SENDER = os.getenv('MAIL_DEFAULT_SENDER')
  
class DevelopmentConfig(Config):
  DEVELOPMENT = True
  DEBUG = True
class ProductionConfig(Config):
  DEBUG = False

config = {
  "development": DevelopmentConfig,
  "production": ProductionConfig
}