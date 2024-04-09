from flask import request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import uuid
import jwt
import os

from .models import User
from .. import db
from ..app import app
from ..decorators import token_required

@app.route('/user/signup', methods=['POST'])
def signup():
  data = request.get_json()

  email = data['email']
  password = data['password']

  user = User.query.filter_by(email=email).first()

  if not user:
    hashed_password = generate_password_hash(password, method="sha256")

    user = User(id=str(uuid.uuid4()), email=email, password=hashed_password, name=data['name'], age=data['age'])
    db.session.add(user)
    db.session.commit()

    return jsonify({"message": "User created successfully"}), 201
  
  return jsonify({"message": "User already exists"})

@app.route("/user/login", methods=["POST"])
def login():
  auth = request.get_json()

  if not auth or not auth["email"] or not auth["password"]:
    return jsonify({"message": "Please provide email and password"}), 400
  
  user = User.query.filter_by(email = auth["email"]).first()

  if not user:
    return jsonify({"message": "User not found"}), 404
  
  if check_password_hash(user.password, auth["password"]):
    token = jwt.encode({
      "email": user.email,
      "exp": datetime.utcnow() + timedelta(minutes=60)
    }, os.getenv("SECRET_KEY"))

    return jsonify({"token": token.decode("utf-8")}), 200
  
  return jsonify({"message": "Invalid password"}), 401

@app.route("/user/me", methods=["GET"])
@token_required
def get_user(current_user):
  user = User.query.filter_by(id = current_user.id).first()

  if not user:
    return jsonify({"message": "User not found"}), 404
  
  user_data = {}

  user_data["id"] = user.id
  user_data["name"] = user.name
  user_data["age"] = user.age
  user_data["email"] = user.email
  user_data["created_at"] = user.created_at
  user_data["updated_at"] = user.updated_at
  
  return jsonify({ "user": user_data }), 200

@app.route("/user/me", methods=["PUT"])
@token_required
def update_user(current_user):
  user = User.query.filter_by(id = current_user.id).first()

  if not user:
    return jsonify({"message": "User not found"}), 404
  
  data = request.get_json()

  user.name = data["name"]
  user.age = data["age"]
  user.email = data["email"]

  db.session.commit()

  user = User.query.get(user.id)

  user_data = {}

  user_data["id"] = user.id
  user_data["name"] = user.name
  user_data["age"] = user.age
  user_data["email"] = user.email
  user_data["created_at"] = user.created_at
  user_data["updated_at"] = user.updated_at
  
  return jsonify(user_data), 200