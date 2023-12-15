from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib
from flask_mail import Mail, Message
import json
from flask import flash, session
from PIL import Image
from functools import wraps
from flask import Flask, jsonify, redirect, render_template, request, session, url_for, send_file, jsonify
import requests
import os
app = Flask(__name__)
app.secret_key = '0ec5205f107e18f72f9fd8d363c04c98'
# SERVER_URL = "http://equipe2.lumys.tech:5005"
SERVER_URL = "https://api.morgan-coulm.fr"
# SERVER_URL = os.environ.get("SERVER_URL")


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
            f'{SERVER_URL}/user_name', headers=headers)
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
    response = requests.get(f'{SERVER_URL}/check_db_empty')

    response = response.json()
    print(response["message"])
    if response["message"] == 'True':
        data = {
            'username': 'admin',
            'password': 'admin',
        }
        response = requests.post(f'{SERVER_URL}/first_user', json=data)
        return render_template('login.html')
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        token = get_token(username, password)
        if token:
            session['token'] = token  # Store the token in the session
            return redirect(url_for('dashboard'))
        flash("Authentication failed", "error")
        return render_template('login.html')
    else:
        return render_template('login.html')


def check_db_empty():
    response = requests.get(f'{SERVER_URL}/check_db_empty')
    if response.status_code == 200:
        is_db_empty = response.json().get('message', False)
        return is_db_empty
    else:
        print(
            f"Failed to check if the database is empty. Status code: {response.status_code}")
        return False  # Assume the database is not empty to prevent registration in case of an error


@app.route('/dashboard')
@check_authentication
def dashboard():
    token = session.get('token')
    if token:
        headers = {'Authorization': f'JWT {token}'}
        response = requests.get(f'{SERVER_URL}/protected', headers=headers)
        user_id = requests.post(f'{SERVER_URL}/user_name', headers=headers)
        username = user_id.json()['username']
        role = user_id.json()['role']
        if response.status_code == 200:
            # Do not print the result here
            pass
        else:
            print(
                f"Failed to access protected resource. Status code: {response.status_code}")
        return render_template('dashboard.html', token=token, username=username, role=role)
    else:
        print("Authentication failed")
        return jsonify({'message': 'Authentication failed'}), 401


@app.route('/labelling', methods=['GET'])
@check_authentication
def labelling():
    token = session.get('token')
    if token:
        headers = {'Authorization': f'JWT {token}'}
        id_image = request.args.get('id_image', None)
        print('is image', id_image)
        info_image = requests.post(
            f'{SERVER_URL}/affiche_image', json=id_image, headers=headers)

        data_image = info_image.json()
        filepath = data_image['result']['path']

        print('ici', data_image['result']['labels'])
        filepath = {"filepath": filepath}
        filename_2 = data_image['result']['name']
        if data_image['result']['labels'] == False:
            response_annotation = requests.post(
                f'{SERVER_URL}/load_images', json=filepath, headers=headers)
            data = response_annotation.json()
            print(data)
        else:
            data = data_image['result']['regions']
            data = {'images': {
                    f"{filename_2}{data_image['result']['size']}": {
                        'file_attributes': {},
                        'filename': data_image['result']['name'],
                        'regions': data,
                        'size': data_image['result']['size']
                    }
                    }}

        print(data)
        print(data)
        print("filename ++", data['images'].values())

        filename = [image_info['filename']
                    for image_info in data['images'].values()]
        filesize = [image_info['size']
                    for image_info in data['images'].values()]
        filename = filename[0]
        filesize = filesize[0]
        print(filesize)
        print(f"Image:{filename}")
        print(f"Image:{filename_2}")
        filename = filename_2
        response_image = requests.post(
            f'{SERVER_URL}/image_from_server', json=filepath, headers=headers)

        with open(f"./image/{filename}", 'wb') as f:
            f.write(response_image.content)
        image = filename
        return render_template('labelling.html', image=image, filename=filename, data=data, id_image=id_image, filesize=filesize)
    else:
        print("Authentication failed")
        return jsonify({'message': 'Authentication failed'}), 401


@app.route('/resultat', methods=['POST'])
def resultat():
    print("resultat")
    token = session.get('token')

    if token:
        headers = {'Authorization': f'JWT {token}'}
        # Récupérer le fichier du formulaire multipart
        uploaded_file = request.files['file']
        file_content = uploaded_file.read().decode('utf-8')
        id_value = request.form['id']
        size_value = request.form['size']
        # response = requests.post(f'{SERVER_URL}/post_resultat/{id_value}')
        file_content = json.loads(file_content)
        # print(list(file_content.keys())[0])
        data = {'id': id_value, 'regions': file_content[list(file_content.keys())[
            0]]["regions"], 'size': f'{size_value}'}
        print('uplod', data)
        response = requests.post(
            f'{SERVER_URL}/post_resultat', json=data, headers=headers)
        response_json = response.json()
        return jsonify({'status': 'success', 'message': 'File uploaded successfully'})
    else:
        print("Authentication failed")
        return jsonify({'message': 'Authentication failed'}), 401


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
    token = session.get('token')
    if token:
        headers = {'Authorization': f'JWT {token}'}
        user_id = requests.post(f'{SERVER_URL}/user_name', headers=headers)
        username = user_id.json()['username']
        role = user_id.json()['role']
        response = requests.post(
            f'{SERVER_URL}/find_all_image', headers=headers)
        response.raise_for_status()  # Gère les erreurs HTTP
        images = response.json()  # Convertit la réponse JSON en Python dict
        return render_template('overview.html', images=images, username=username, role=role)
    else:
        print("Authentication failed")
        return jsonify({'message': 'Authentication failed'}), 401


@app.route('/help', methods=['GET', 'POST'])
@check_authentication
def help():
    if request.method == 'POST':
        # Récupérer les données du formulaire
        problem_type = request.form['form_div_select1']
        comment = request.form['form_div_textarea']
        importance = request.form['form_div_select2']

        # Envoyer l'e-mail
        send_help_email(problem_type, comment, importance)

    return render_template('help.html')


def send_help_email(problem_type, comment, importance):
    sender_email = 'help.intradys@gmail.com'  # Remplacez par votre adresse e-mail
    sender_password = 'Intradys123'  # Remplacez par votre mot de passe
    # Remplacez par l'adresse e-mail du destinataire
    receiver_email = 'help.intradys@gmail.com'

    subject = 'Demande d\'aide - Intradys'
    body = f"Type de problème : {problem_type}\nCommentaire : {comment}\nImportance : {importance}"
    message = MIMEMultipart()
    message['From'] = sender_email
    message['To'] = receiver_email
    message['Subject'] = subject
    message.attach(MIMEText(body, 'plain'))

    try:
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, receiver_email, message.as_string())

        print("E-mail envoyé avec succès!")
    except Exception as e:
        print(f"Erreur lors de l'envoi de l'e-mail : {str(e)}")


# @app.route('/help')
# @check_authentication
# def help():
#     return render_template('help.html')


@app.route('/admin/user_management')
@check_authentication
def user_management():
    token = session.get('token')

    if token:
        headers = {'Authorization': f'JWT {token}'}
        user_id = requests.post(f'{SERVER_URL}/user_name', headers=headers)
        username = user_id.json()['username']
        role = user_id.json()['role']
        try:
            # Remplacez l'URL par l'URL réelle de votre API pour récupérer les utilisateurs
            response = requests.post(f'{SERVER_URL}/all_user', headers=headers)
            response.raise_for_status()  # Gère les erreurs HTTP
            users = response.json()  # Convertit la réponse JSON en Python dict
            return render_template('user_management.html', users=users, username=username, role=role)
        except requests.exceptions.RequestException as e:
            print(f"Error fetching users: {e}")
            return []
    else:
        print("Authentication failed")
        return jsonify({'message': 'Authentication failed'}), 401


@app.route('/admin/register', methods=['GET', 'POST'])
@check_authentication
def register():
    if request.method == 'POST':
        # Rest of your registration code remains unchanged
        admin_token = session.get('token')
        if admin_token:
            # Créez un nouvel utilisateur avec les données minimales
            username = request.form['username']
            password = request.form['password']
            role = request.form['role']

            headers = {'Authorization': f'JWT {admin_token}'}
            data = {
                'username': username,
                'password': password,
                'role': role
            }

            try:
                response = requests.post(
                    f'{SERVER_URL}/create_user', headers=headers, json=data)
                response.raise_for_status()

                if response.status_code == 201:
                    flash('User created successfully', 'success')
                    return redirect(url_for('user_management'))
                else:
                    error_message = response.json().get('message')
                    flash(
                        f"User creation failed. Status code: {response.status_code}, Message: {error_message}", 'error')

            except requests.exceptions.RequestException as e:
                flash(f"Error during user creation: {e}", 'error')

        else:
            flash("Admin authentication failed", 'error')
            return redirect(url_for('user_management'))

    return redirect(url_for('user_management'))


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
