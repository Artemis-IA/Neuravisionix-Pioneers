from flask import Flask, jsonify
import requests
app = Flask(__name__)

# Set the server URL
SERVER_URL = 'http://127.0.0.1:5000'

# Replace these credentials with a valid username and password
USERNAME = 'username'
PASSWORD = 'passw'

def get_token():
   response = requests.post(f'{SERVER_URL}/auth', json={'username': USERNAME, 'password': PASSWORD})
   if response.status_code == 200:
       token = response.json().get('access_token')
       print(f"Token obtained: {token}") # Print the obtained token
       return token
   else:
       print(f"Failed to obtain token. Status code: {response.status_code}")
       return None




def access_protected_resource(token):
    headers = {'Authorization': f'JWT {token}'}
    response = requests.get(f'{SERVER_URL}/protected', headers=headers)
    if response.status_code == 200:
        result = response.json()
        print(result)
    else:
        print(f"Failed to access protected resource. Status code: {response.status_code}")

@app.route('/')
def main():
    # Get the JWT token
    token = get_token()

    if token:
        # Access the protected resource
        access_protected_resource(token)
        return jsonify({'message': 'Successfully accessed protected resource'})
    else:
        print("Authentication failed")
        return jsonify({'message': 'Authentication failed'}), 401

if __name__ == '__main__':
    app.run(debug=True)
