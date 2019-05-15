from flask import Flask, request, jsonify, Blueprint
import uuid
from werkzeug.security import generate_password_hash, check_password_hash
from inventory import db
from inventory.models import Post, User
from flask_login import current_user, login_required

api = Blueprint('api', __name__)

@api.route('/users', methods=['GET'])
@login_required
def get_all_users():
    if not current_user.admin:
        return jsonify({'message' : 'Cannot perform that function!'})
    users = User.query.all()
    output = []
    for user in users:
        user_data = {}
        user_data['id'] = user.id
        user_data['public_id'] = user.public_id
        user_data['username'] = user.username
        user_data['email'] = user.email
        user_data['password'] = user.password
        user_data['admin'] = user.admin
        user_data['active'] = user.active
        output.append(user_data)
    return jsonify({'users' : output})

@api.route('/users/<public_id>', methods=['GET'])
@login_required
def get_one_user(public_id):
    if not current_user.admin:
        return jsonify({'message' : 'Cannot perform that function!'})
    user = User.query.filter_by(public_id=public_id).first()
    if not user:
        return jsonify({'message' : 'No user found!'})
    user_data = {}
    user_data['public_id'] = user.public_id
    user_data['username'] = user.username
    user_data['email'] = user.email
    user_data['password'] = user.password
    user_data['admin'] = user.admin
    user_data['active'] = user.active
    return jsonify({'user' : user_data})

@api.route('/promote/user/<public_id>', methods=['PUT'])
@login_required
def promote(public_id):
    if not current_user.admin:
        return jsonify({'message' : 'Cannot perform that function!'})
    user = User.query.filter_by(public_id=public_id).first()
    if not user:
        return jsonify({'message' : 'No user found!'})
    user.admin = True
    db.session.commit()
    return jsonify({'message' : 'The user has been promoted!'})

@api.route('/demote/user/<public_id>', methods=['PUT'])
@login_required
def demote(public_id):
    if not current_user.admin:
        return jsonify({'message' : 'Cannot perform that function!'})
    user = User.query.filter_by(public_id=public_id).first()
    if not user:
        return jsonify({'message' : 'No user found!'})
    user.admin = False
    db.session.commit()
    return jsonify({'message' : 'The user has been demoted!'})

# @api.route('/posts', methods=['GET'])
# def get_all_posts():
#     posts = Post.query.all()

#     output = []

#     for post in posts:
#         post_data = {}
#         post_data['id'] = post.id
#         post_data['title'] = post.title
#         post_data['content'] = post.content
#         post_data['timestamp'] = post.timestamp
#         post_data['user_id'] = post.user_id
#         output.append(post_data)

#     return jsonify({'posts' : output})

# @app.route('/posts/<post_id>', methods=['GET'])
# def get_one_todo(current_user, todo_id):
#     todo = Todo.query.filter_by(id=todo_id, user_id=current_user.id).first()

#     if not todo:
#         return jsonify({'message' : 'No todo found!'})

#     todo_data = {}
#     todo_data['id'] = todo.id
#     todo_data['text'] = todo.text
#     todo_data['complete'] = todo.complete

#     return jsonify(todo_data)