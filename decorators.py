from flask import request, jsonify
from functools import wraps
from .users.models import User

import jwt
import os

def token_required(f):
  @wraps(f)
  def decorated(*args, **kwargs):
    token = None
    if 'x-access-token' in request.headers:
      token = request.headers['x-access-token']
    if not token:
      return jsonify({"message": "Please provide a valid token"}), 401
    
    try:
      data = jwt.decode(token, os.getenv('SECRET_KEY'))
      current_user = User.query.filter_by(email = data['email']).first()
    except:
      return jsonify({"message": "Please provide a valid token"}), 401
    return f(current_user, *args, **kwargs)
  return decorated
