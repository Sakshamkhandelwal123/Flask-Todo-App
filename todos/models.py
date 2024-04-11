from sqlalchemy import inspect
from datetime import datetime

from .. import db

class Todo(db.Model):
  id = db.Column(db.String(50), primary_key = True, nullable=False, unique=True)
  description = db.Column(db.String(200), nullable = False)
  complete = db.Column(db.Boolean, default=False)
  user_id = db.Column(db.String(50), db.ForeignKey("user.id"))
  created_at = db.Column(db.DateTime(timezone = True), default=datetime.now)
  updated_at = db.Column(db.DateTime(timezone = True), default=datetime.now, onupdate=datetime.now)

  #Relations
  user = db.relationship("User", back_populates="todos")

  def toDict(self):
    return {c.key: getattr(self, c.key) for c in inspect(self).mapper.column_attrs}