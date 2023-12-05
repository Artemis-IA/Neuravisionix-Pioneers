from flask import Flask, request, jsonify
from functools import wraps
import jwt

app = Flask(__name__)
app.config['SECRET_KEY'] = 'jkdbvlqdfvqldvihviviuqvisdhfv'  # Change this to a strong, random secret key

# Dummy user for demonstration purposes
users = {
   'user_id': {
       'id': 'user_id',
       'username': 'username',
       'password': 'passw'
   }
}


# JWT authentication decorator
def jwt_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        token = request.headers.get('Authorization', '').split(' ')[1]
        try:
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
            current_user = users.get(data['identity'], None)
            if current_user:
                return fn(current_user, *args, **kwargs)
        except jwt.ExpiredSignatureError:
            return jsonify({'message': 'Token has expired'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'message': 'Invalid token'}), 401

    return wrapper

# Example protected resource
@app.route('/protected')
@jwt_required
def protected_resource(current_user):
    return jsonify({'message': 'You have access to this protected resource', 'user': current_user})



@app.route('/auth', methods=['POST'])
def auth():
   data = request.get_json()
   username = data.get('username')
   password = data.get('password')
   
   # Get the user ID using the username
   user_id = next((user['id'] for user in users.values() if user['username'] == username), None)
   
   # If the user ID is not found, return an error
   if not user_id:
       return jsonify({'message': 'Invalid username or password'}), 401
   
   user = users.get(user_id)
   print(user)
   if user and user['password'] == password:
       token = jwt.encode({'identity': user['id']}, app.config['SECRET_KEY'], algorithm='HS256')
       print(f"Token generated: {token.decode('UTF-8')}") # Print the generated token
       return jsonify({'access_token': token.decode('UTF-8')})
   else:
       return jsonify({'message': 'Invalid username or password'}), 401










if __name__ == '__main__':
    app.run(debug=True)
