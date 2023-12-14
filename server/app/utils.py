from functools import wraps
import jwt
from flask import request, jsonify
from app import app
from app.models import User

def jwt_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        print("warpper jwt")
        try:
            token = request.headers.get('Authorization', '').split(' ')[1]
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
            return fn(*args, current_user_id=data['identity'], **kwargs)
        except jwt.ExpiredSignatureError:
            return jsonify({'message': 'Token has expired'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'message': 'Invalid token'}), 401

    return wrapper

def login(data):
    username = data.get('username')
    password = data.get('password')
    user = User.query.filter_by(username=username).first()

    if user and user.check_password(password):
        return user
    else:
        return None