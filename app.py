from flask import session
from flask import flash
from functools import wraps
from flask import Flask, jsonify, redirect, render_template, request, session, url_for
import requests
app = Flask(__name__)
SERVER_URL = "https://mlops.morgan-coulm.fr"


def get_token(username, password):
    response = requests.post(
        f'{SERVER_URL}/auth', json={'username': username, 'password': password})
    if response.status_code == 200:
        token = response.json().get('access_token')
        print(f"Token obtained: {token}")  # Print the obtained token
        return token
    else:
        print(f"Failed to obtain token. Status code: {response.status_code}")
        return None


def check_authentication(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        token = get_token()
        if token:
            session['token'] = token
            headers = {'Authorization': f'JWT {token}'}
            response = requests.get(f'{SERVER_URL}/protected', headers=headers)
            if response.status_code == 200:
                result = response.json()
                print(result)
                return func(*args, **kwargs)
            else:
                print(
                    f"Failed to access protected resource. Status code: {response.status_code}")
        else:
            return render_template('login.html')
    return wrapper


@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        token = get_token(username, password)
        if token:
            headers = {'Authorization': f'JWT {token}'}
            response = requests.get(f'{SERVER_URL}/protected', headers=headers)
            if response.status_code == 200:
                result = response.json()
                print(result)
            else:
                print(
                    f"Failed to access protected resource. Status code: {response.status_code}")
            return render_template('dashboard.html')
            # return redirect(url_for('dashboard'))
            # ^------------------------ à décommenter pour plus tard
        else:
            print("Authentication failed")
            return render_template('login.html')
    else:
        return render_template('login.html')
        # return jsonify({'message': 'Authentication failed'}), 401
    # Si la méthode est GET, simplement afficher la page de connexion


@app.route('/register')
def register():
    return render_template('register.html')


@app.route('/dashboard')
@check_authentication
def dashboard():
    token = get_token()
    if token:
        headers = {'Authorization': f'JWT {token}'}
        response = requests.get(f'{SERVER_URL}/protected', headers=headers)
        if response.status_code == 200:
            result = response.json()
            print(result)
        else:
            print(
                f"Failed to access protected resource. Status code: {response.status_code}")
        return render_template('dashboard.html', token=session['token'])
    else:
        print("Authentication failed")
        return jsonify({'message': 'Authentication failed'}), 401


@app.route('/labelling')
@check_authentication
def labelling():
    return render_template('labelling.html')


@app.route('/logs')
@check_authentication
def logs():
    return render_template('logs.html')


@app.route('/docs')
@check_authentication
def docs():
    return render_template('docs.html')


@app.route('/help')
@check_authentication
def help():
    return render_template('help.html')


@app.route('/logout')
def logout():
    # Clear the session to log out the user
    session.clear()
    # Redirect to the login page
    return redirect(url_for('login'))


if __name__ == '__main__':
    app.run(debug=True)
