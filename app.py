import json
from flask import session
from PIL import Image
from functools import wraps
from flask import Flask, jsonify, redirect, render_template, request, session, url_for, send_file, jsonify
import requests

app = Flask(__name__)
app.secret_key = '0ec5205f107e18f72f9fd8d363c04c98'
SERVER_URL = "http://equipe2.lumys.tech:5005"


def get_token(username, password):
    response = requests.post(
        f'{SERVER_URL}/auth', json={'username': username, 'password': password})
    if response.status_code == 200:
        token = response.json().get('access_token')
        return token
    else:
        print(f"Failed to obtain token. Status code: {response.status_code}")
        return None


def get_current_user():
    token = session.get('token')
    if token:
        headers = {'Authorization': f'JWT {token}'}
        response = requests.post(
            f'https://api.morgan-coulm.fr/user', headers=headers)
        response.raise_for_status()
        user_data = response.json().get('user')
        current_username = user_data.get('user_name')
        current_role = user_data.get('role')
        return current_role, current_username


def check_authentication(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        # Check if the current route is the "predict_route"
        if request.endpoint == 'predict_route':
            # Extract the token from the request's form
            token = request.form['token']
        else:
            # Check for the token in the session
            token = session.get('token')

        if token:
            # Verify the token using the get_token function
            headers = {'Authorization': f'JWT {token}'}
            response = requests.get(f'{SERVER_URL}/protected', headers=headers)
            if response.status_code == 200:
                # Do not print the result here
                pass
            else:
                print(
                    f"Failed to access protected resource. Status code: {response.status_code}")
            return func(*args, **kwargs)
        else:
            print("Authentication failed")
            return render_template('login.html')

    return wrapper


@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        token = get_token(username, password)
        if token:
            session['token'] = token  # Store the token in the session
            headers = {'Authorization': f'JWT {token}'}
            response = requests.get(f'{SERVER_URL}/protected', headers=headers)
            if response.status_code == 200:
                # Do not print the result here
                pass
                return redirect(url_for('dashboard'))
        print("Authentication failed")
        return render_template('login.html')
    else:
        return render_template('login.html')


@app.route('/register')
def register():
    return render_template('register.html')


# @app.context_processor
# def inject_user_info():
#     current_role, current_username = get_current_user()
#     return dict(current_role=current_role, current_username=current_username)


@app.route('/dashboard')
@check_authentication
def dashboard():
    token = session.get('token')

    if token:
        headers = {'Authorization': f'JWT {token}'}
        response = requests.get(f'{SERVER_URL}/protected', headers=headers)
        if response.status_code == 200:
            # Do not print the result here
            pass
        else:
            print(
                f"Failed to access protected resource. Status code: {response.status_code}")
        return render_template('dashboard.html', token=token)
    else:
        print("Authentication failed")
        return jsonify({'message': 'Authentication failed'}), 401


@app.route('/labelling')
@check_authentication
def labelling():
    id_image = '65772409edfb11a6c6d8fac9'  # image en dur
    info_image = requests.get(f'{SERVER_URL}/affiche_image/{id_image}')
    data_image = info_image.json()
    filepath = data_image['result']['path']
    print('prems : ', filepath)
    filepath = {"filepath": filepath}
    response_annotation = requests.post(
        f'http://equipe2.lumys.tech:5005/load_images', json=filepath)
    data = response_annotation.json()
    filename = [image_info['filename']
                for image_info in data['images'].values()]
    filename = filename[0]
    print(f"Image:{filename}")

    response_image = requests.post(
        f'{SERVER_URL}/image_from_server', json=filepath)

    with open(f"./image/{filename}", 'wb') as f:
        f.write(response_image.content)
    image = filename
    return render_template('labelling.html', image=image, filename=filename, data=data, id_image=id_image)


@app.route('/resultat', methods=['POST'])
def resultat():
    print("resultat")

    # Récupérer le fichier du formulaire multipart
    uploaded_file = request.files['file']
    file_content = uploaded_file.read().decode('utf-8')
    id_value = request.form['id']
    # response = requests.post(f'{SERVER_URL}/post_resultat/{id_value}')
    file_content = json.loads(file_content)
    # print(list(file_content.keys())[0])
    data = {'id': id_value, 'regions': file_content[list(file_content.keys())[
        0]]["regions"]}
    print('uplod', data)
    response = requests.post(f'{SERVER_URL}/post_resultat', json=data)
    response_json = response.json()
    return jsonify({'status': 'success', 'message': 'File uploaded successfully'})


@app.route('/get_image/<filename>')
def get_image(filename):
    image_path = f'./image/{filename}'
    with Image.open(image_path) as img:
        # Récupérer le format de l'image (par exemple, 'JPEG', 'PNG', etc.)
        image_format = img.format.lower()
        print('image sans app pls', image_path)
        # Envoyer le fichier avec le bon type MIME
        return send_file(image_path, mimetype=f'image/{image_format}')

    # return send_file(image_path, mimetype='image/png')


@app.route('/overview')
@check_authentication
def overview():
    return render_template('overview.html')


@app.route('/test')
def test():
    return render_template('test.html')


@app.route('/docs')
@check_authentication
def docs():
    return render_template('docs.html')


@app.route('/help')
@check_authentication
def help():
    return render_template('help.html')


@app.route('/admin/user_management')
@check_authentication
def user_management():
    try:
        # Remplacez l'URL par l'URL réelle de votre API pour récupérer les utilisateurs
        response = requests.get(f'{SERVER_URL}/all_user')
        response.raise_for_status()  # Gère les erreurs HTTP
        users = response.json()  # Convertit la réponse JSON en Python dict
        return render_template('user_management.html', users=users)
    except requests.exceptions.RequestException as e:
        print(f"Error fetching users: {e}")
        return []


@app.route('/admin/delete_user/<int:user_id>', methods=['POST'])
@check_authentication
def delete_user(user_id):
    token = session.get('token')
    if token:
        try:
            headers = {'Authorization': f'JWT {token}'}
            response = requests.post(
                f'{SERVER_URL}/delete_user/{user_id}', headers=headers)
            response.raise_for_status()
            return render_template('user_management.html'), 200
        except requests.exceptions.RequestException as e:
            print(f"Error deleting user: {e}")
            return jsonify({'message': f'Erreur lors de la suppression de l\'utilisateur'}), 500
    else:
        return jsonify({'message': f'L\'authentification a échoué'}), 401


@app.route('/admin/switch_role/<int:user_id>', methods=['POST'])
@check_authentication
def switch_role(user_id):
    token = session.get('token')
    if token:
        try:
            headers = {'Authorization': f'JWT {token}'}
            response = requests.get(
                f'{SERVER_URL}/user/{user_id}', headers=headers)
            response.raise_for_status()
            user_data = response.json().get('user')
            current_role = user_data.get('role')
            new_role = 'admin' if current_role == 'utilisateur' else 'utilisateur'
            data = {'role': new_role}
            response = requests.post(
                f'{SERVER_URL}/change_role/{user_id}', json=data, headers=headers)
            response.raise_for_status()
            return render_template('user_management.html'), 200
        except requests.exceptions.RequestException as e:
            print(f"Error switching role: {e}")
            print(f"Response content: {response.content}")
    else:
        return jsonify({'message': 'L\'authentification a échoué'}), 401


@app.route('/logout')
def logout():
    # Clear the session to log out the user
    session.clear()
    # Redirect to the login page
    return redirect(url_for('login'))


if __name__ == '__main__':
    app.run(debug=True)
