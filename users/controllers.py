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
from ..mail_template import send_email
from ..helpers import generate_otp
from ..exceptions import CustomException
from ..logger import logger

@app.route('/user/signup', methods=['POST'])
def signup():
  try:
    data = request.get_json()

    email = data['email']
    password = data['password']

    user = User.query.filter_by(email=email).first()

    if not user:
      hashed_password = generate_password_hash(password, method="sha256")
      otp = generate_otp()

      user = User(id=str(uuid.uuid4()), email=email, password=hashed_password, name=data['name'], age=data['age'], otp=otp)
      db.session.add(user)
      db.session.commit()

      send_email(email, otp, 'Thanks for signing up!!!')

      return jsonify({"message": "User created successfully"}), 201

    raise CustomException("User already exists", 409)
  except CustomException as ce:
    logger.error(ce)
    return jsonify({"message": ce.args[0]}), ce.status_code
  except Exception as e:
    logger.error(e)
    return jsonify({"message": f"An error occurred: {str(e)}"}), 500

@app.route('/user/verify-email', methods=['POST'])
def verify_email():
  try:
    data = request.get_json()

    email = data['email']
    otp = data['otp']

    user = User.query.filter_by(email = email).first()

    if not user:
      raise CustomException("User not found", 404)
    
    if user.is_email_verified == True:
      raise CustomException("Email already verified", 400)
    
    if user.otp == otp:
      user.otp = None
      user.is_email_verified = True
      db.session.commit()

      token = jwt.encode({
        "email": user.email,
        "exp": datetime.utcnow() + timedelta(minutes=120)
      }, os.getenv("SECRET_KEY"))

      token = token.decode("utf-8")

      decoded_token = jwt.decode(token, os.getenv("SECRET_KEY"))

      expiration_time = decoded_token.get("exp")

      return jsonify({"token": token, "expires_in": datetime.utcfromtimestamp(expiration_time)}), 200
    
    raise CustomException("Invalid OTP", 401)
  except CustomException as ce:
    logger.error(ce)
    return jsonify({"message": ce.args[0]}), ce.status_code
  except Exception as e:
    logger.error(e)
    return jsonify({"message": f"An error occurred: {str(e)}"}), 500

@app.route('/user/resend-verification-email', methods=['POST'])
def resend_verification_email():
  try:
    data = request.get_json()

    email = data['email']

    user = User.query.filter_by(email = email).first()

    if not user:
      raise CustomException("User not found", 404)
    
    user.otp = generate_otp()
    user.is_email_verified = False

    db.session.commit()

    send_email(email, user.otp, 'Thanks for signing up!!!')

    return jsonify({"message": "Email sent successfully"}), 200
  except CustomException as ce:
    logger.error(ce)
    return jsonify({"message": ce.args[0]}), ce.status_code
  except Exception as e:
    logger.error(e)
    return jsonify({"message": f"An error occurred: {str(e)}"}), 500

@app.route("/user/login", methods=["POST"])
def login():
  try:
    auth = request.get_json()

    if not auth or not auth["email"] or not auth["password"]:
      raise CustomException("Please provide email and password", 400)
    
    user = User.query.filter_by(email = auth["email"]).first()

    if not user:
      raise CustomException("User not found", 404)
    
    if user.is_email_verified == False:
      raise CustomException("Please verify your email", 401)
    
    if check_password_hash(user.password, auth["password"]):
      token = jwt.encode({
        "email": user.email,
        "exp": datetime.utcnow() + timedelta(minutes=120)
      }, os.getenv("SECRET_KEY"))

      token = token.decode("utf-8")

      decoded_token = jwt.decode(token, os.getenv("SECRET_KEY"))

      expiration_time = decoded_token.get("exp")

      return jsonify({"token": token, "expires_in": datetime.utcfromtimestamp(expiration_time)}), 200
    
    raise CustomException("Invalid password", 401)
  except CustomException as ce:
    logger.error(ce)
    return jsonify({"message": ce.args[0]}), ce.status_code
  except Exception as e:
    logger.error(e)
    return jsonify({"message": f"An error occurred: {str(e)}"}), 500
  
@app.route("/user/forgot-password", methods=["POST"])
def forgot_password():
  try:
    data = request.get_json()

    email = data['email']

    user = User.query.filter_by(email = email).first()

    if not user:
      raise CustomException("User not found", 404)
    
    user.otp = generate_otp()

    db.session.commit()

    send_email(email, user.otp, 'Request For Changing Password!!!')

    return jsonify({"message": "Email sent successfully"}), 200
  except CustomException as ce:
    logger.error(ce)
    return jsonify({"message": ce.args[0]}), ce.status_code
  except Exception as e:
    logger.error(e)
    return jsonify({"message": f"An error occurred: {str(e)}"}), 500
  
@app.route("/user/verify-password", methods=["POST"])
def verify_password():
  try:
    data = request.get_json()

    email = data['email']
    otp = data['otp']
    new_password = data['newPassword']

    user = User.query.filter_by(email = email).first()

    if not user:
      raise CustomException("User not found", 404)
    
    if user.otp != otp:
      raise CustomException("Invalid OTP", 401)
    
    hashed_password = generate_password_hash(new_password, method="sha256")

    user.password =  hashed_password
    user.otp = None

    db.session.commit()

    return jsonify({"message": "Password changed successfully"}), 200
  except CustomException as ce:
    logger.error(ce)
    return jsonify({"message": ce.args[0]}), ce.status_code
  except Exception as e:
    logger.error(e)
    return jsonify({"message": f"An error occurred: {str(e)}"}), 500

@app.route("/user/me", methods=["GET"])
@token_required
def get_user(current_user):
  try:
    user = User.query.filter_by(id = current_user.id).first()

    if not user:
      raise CustomException("User not found", 404)
    
    user_data = {}

    user_data["id"] = user.id
    user_data["name"] = user.name
    user_data["age"] = user.age
    user_data["email"] = user.email
    user_data["is_email_verified"] = user.is_email_verified
    user_data["created_at"] = user.created_at
    user_data["updated_at"] = user.updated_at
    
    return jsonify({ "user": user_data }), 200
  except CustomException as ce:
    logger.error(ce)
    return jsonify({"message": ce.args[0]}), ce.status_code
  except Exception as e:
    logger.error(e)
    return jsonify({"message": f"An error occurred: {str(e)}"}), 500

@app.route("/user/me", methods=["PUT"])
@token_required
def update_user(current_user):
  try:
    user = User.query.filter_by(id = current_user.id).first()

    if not user:
      raise CustomException("User not found", 404)
    
    data = request.get_json()

    if data["email"] != user.email:
      user.email = data["email"]
      user.otp = generate_otp()
      user.is_email_verified = False

      send_email(user.email, user.otp, 'Request For Changing Email!!!')

    user.name = data["name"]
    user.age = data["age"]

    db.session.commit()

    user = User.query.get(user.id)

    user_data = {}

    user_data["id"] = user.id
    user_data["name"] = user.name
    user_data["age"] = user.age
    user_data["email"] = user.email
    user_data["is_email_verified"] = user.is_email_verified
    user_data["created_at"] = user.created_at
    user_data["updated_at"] = user.updated_at
    
    return jsonify({ "user": user_data }), 200
  except CustomException as ce:
    logger.error(ce)
    return jsonify({"message": ce.args[0]}), ce.status_code
  except Exception as e:
    logger.error(e)
    return jsonify({"message": f"An error occurred: {str(e)}"}), 500

@app.route("/user/me", methods=["DELETE"])
@token_required
def delete_user(current_user):
  try:
    user = User.query.filter_by(id = current_user.id).first()

    if not user:
      raise CustomException("User not found", 404)
    
    db.session.delete(user)
    db.session.commit()

    return jsonify({"message": "User deleted successfully"}), 200
  except CustomException as ce:
    logger.error(ce)
    return jsonify({"message": ce.args[0]}), ce.status_code
  except Exception as e:
    logger.error(e)
    return jsonify({"message": f"An error occurred: {str(e)}"}), 500
