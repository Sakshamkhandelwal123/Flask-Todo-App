from datetime import datetime

from .. import db

class User(db.Model):
  id = db.Column(db.String(50), primary_key = True, nullable = False, unique = True)
  name = db.Column(db.String(100), nullable = False)
  email = db.Column(db.String(100), nullable = False, unique = True)
  password = db.Column(db.String(100), nullable = False)
  age = db.Column(db.Integer, nullable = False)
  created_at = db.Column(db.DateTime(timezone = True), default=datetime.now)
  updated_at = db.Column(db.DateTime(timezone = True), default=datetime.now, onupdate=datetime.now)

  #Relations
  todos = db.relationship("Todo", back_populates='user')