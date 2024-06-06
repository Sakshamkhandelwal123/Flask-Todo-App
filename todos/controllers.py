from flask import request, jsonify
import uuid

from ..app import app
from .. import db
from .models import Todo
from ..users.models import User
from ..decorators import token_required
from ..exceptions import CustomException
from ..logger import logger

@app.route('/todo', methods=['GET'])
@token_required
def get_all_todos(current_user):
  try:
    user = User.query.filter_by(id = current_user.id).first()

    if not user:
      raise CustomException("User not found", 404)
    
    todos = Todo.query.filter_by(user_id = user.id).all()

    output = []

    for todo in todos:
      output.append(todo.toDict())

    return jsonify({"todos": output})
  except CustomException as ce:
    logger.error(ce)
    return jsonify({"message": ce.args[0]}), ce.status_code
  except Exception as e:
    return jsonify({"message": f"An error occurred: {str(e)}"}), 500

@app.route('/todo/<todo_id>', methods=['GET'])
@token_required
def get_todo(current_user, todo_id):
  try:
    user = User.query.filter_by(id = current_user.id).first()

    if not user:
      raise CustomException("User not found", 404)
    
    todo = Todo.query.filter_by(id = todo_id, user_id = user.id).first()

    if not todo:
      raise CustomException("Todo not found", 404)
    
    return jsonify({"todo": todo.toDict()})
  except CustomException as ce:
    logger.error(ce)
    return jsonify({"message": ce.args[0]}), ce.status_code
  except Exception as e:
    return jsonify({"message": f"An error occurred: {str(e)}"}), 500

@app.route('/todo', methods=['POST'])
@token_required
def create_todo(current_user):
  try:
    user = User.query.filter_by(id = current_user.id).first()

    if not user:
      raise CustomException("User not found", 404)
    
    data = request.get_json()

    new_todo = Todo(
      id = str(uuid.uuid4()),
      description = data["description"],
      complete = False,
      user_id = user.id
    )

    db.session.add(new_todo)
    db.session.commit()

    todo = Todo.query.get(new_todo.id).toDict()

    return jsonify({"todo": todo})
  except CustomException as ce:
    logger.error(ce)
    return jsonify({"message": ce.args[0]}), ce.status_code
  except Exception as e:
    return jsonify({"message": f"An error occurred: {str(e)}"}), 500

@app.route('/todo/<todo_id>', methods=['PUT'])
@token_required
def update_todo(current_user, todo_id):
  try:
    user = User.query.filter_by(id = current_user.id).first()

    if not user:
      raise CustomException("User not found", 404)
    
    todo = Todo.query.filter_by(id = todo_id, user_id = user.id).first()

    if not todo:
      raise CustomException("Todo not found", 404)
    
    todo.complete = True

    db.session.commit()

    return jsonify({"message": "Todo completed successfully"})
  except CustomException as ce:
    logger.error(ce)
    return jsonify({"message": ce.args[0]}), ce.status_code
  except Exception as e:
    return jsonify({"message": f"An error occurred: {str(e)}"}), 500

@app.route('/todo/<todo_id>', methods = ['DELETE'])
@token_required
def delete_todo(current_user, todo_id):
  try:
    user = User.query.filter_by(id = current_user.id).first()

    if not user:
      raise CustomException("User not found", 404)
    
    todo = Todo.query.filter_by(id = todo_id, user_id = user.id).first()

    if not todo:
      raise CustomException("Todo not found", 404)
    
    db.session.delete(todo)
    db.session.commit()

    return jsonify({"message": "Todo deleted successfully"})
  except CustomException as ce:
    logger.error(ce)
    return jsonify({"message": ce.args[0]}), ce.status_code
  except Exception as e:
    return jsonify({"message": f"An error occurred: {str(e)}"}), 500
