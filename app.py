import os
import json
import requests
from PIL import Image
from functools import wraps
from ultralytics import YOLO
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from flask import Flask, jsonify, redirect, render_template, request, url_for, flash, session

app = Flask(__name__)
app.secret_key = 'SECRET_KEY'
SERVER_URL = "https://api.morgan-coulm.fr"


class PredictorLabeller:
    def __init__(self):
        self.image_directory = "./images"
        self.device = "cpu"
        self.model = YOLO('yolov8n.pt')

    def predict_single_image(self, image_path):
        results = self.model(image_path, save=True)
        class_names = self.model.names
        annotations = {}

        for idx, result in enumerate(results):
            filename = image_path.split("/")[-1]
            file_size = os.path.getsize(image_path)
            unique_key = f"{filename}{file_size}"
        
            with Image.open(image_path) as img:
                width, height = img.size

            size = width * height
            regions = []

            for i, box in enumerate(result.boxes.xyxy.tolist()):
                class_index = int(result.boxes.cls[i])
                label = class_names[class_index]
                x_abs = int(box[0])
                y_abs = int(box[1])
                width_abs = int((box[2] - box[0]))
                height_abs = int((box[3] - box[1]))

                shape_attributes = {
                    'name': 'rect',
                    'x': x_abs,
                    'y': y_abs,
                    'width': width_abs,
                    'height': height_abs
                }

                region_attributes = {
                    'label': label
                }

                regions.append({
                    'shape_attributes': shape_attributes,
                    'region_attributes': region_attributes
                })

                if unique_key not in annotations:
                    annotations[unique_key] = {
                        'filename': filename,
                        'size': file_size,
                        'regions': regions,
                        'file_attributes': {}
                    }

        return annotations

    def predict_multiple_images(self, images):
        all_annotations = []

        for image_path in images:
            annotations = self.predict_single_image(image_path)
            all_annotations.append(annotations)

        return all_annotations

    def list_images_in_directory(self, directory_path):
        images = []

        if os.path.exists(directory_path) and os.path.isdir(directory_path):
            for filename in os.listdir(directory_path):
                if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
                    images.append(filename)

        return images

    def save_annotations_to_file(self, annotations, output_directory):
        # Créer le répertoire s'il n'existe pas
        if not os.path.exists(output_directory):
            os.makedirs(output_directory)

        # Enregistrer le fichier JSON dans le répertoire
        output_path = os.path.join(output_directory, 'annotations.json')
        with open(output_path, 'w') as json_file:
            json_file.write(annotations)


labelling_app = PredictorLabeller()



def get_token(username, password):
    response = requests.post(
        f'{SERVER_URL}/auth', json={'username': username, 'password': password})
    if response.status_code == 200:
        token = response.json().get('access_token')
        return token
    else:
        print(f"Failed to obtain token. Status code: {response.status_code}")
        return None


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
        print(f"Failed to check if the database is empty. Status code: {response.status_code}")
        return False  # Assume the database is not empty to prevent registration in case of an error

# ... (existing code)

@app.route('/register', methods=['GET', 'POST'])
@check_authentication
def register():
    if request.method == 'POST':
        # Check if the database is empty before allowing registration
        if not check_db_empty():
            flash("User registration is not allowed. Users already exist.", 'error')
            return render_template('register.html')

        # Rest of your registration code remains unchanged
        admin_token = session.get('token')
        if admin_token:
            # Créez un nouvel utilisateur avec les données minimales
            username = request.form['username']
            password = request.form['password']
            role = 'utilisateur'

            headers = {'Authorization': f'JWT {admin_token}'}
            data = {
                'username': username,
                'password': password,
                'role': role
            }

            try:
                response = requests.post(f'{SERVER_URL}/create_user', headers=headers, json=data)
                response.raise_for_status()

                if response.status_code == 201:
                    flash('User created successfully', 'success')
                    return redirect(url_for('dashboard'))
                else:
                    error_message = response.json().get('message')
                    flash(f"User creation failed. Status code: {response.status_code}, Message: {error_message}", 'error')

            except requests.exceptions.RequestException as e:
                flash(f"Error during user creation: {e}", 'error')

        else:
            flash("Admin authentication failed", 'error')
            return render_template('login.html')

    return render_template('register.html')

    

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
    labeled_images = []
    return render_template('labelling.html', labeled_images=labeled_images)


@app.route('/predict', methods=['POST'])
@check_authentication
def predict_route():
    uploaded_files = request.files.getlist('myfile')

    if uploaded_files:
        # Save the uploaded files with secure filenames
        filenames = []
        for idx, uploaded_file in enumerate(uploaded_files):
            filename = secure_filename(uploaded_file.filename)
            source = os.path.join(labelling_app.image_directory, filename)
            uploaded_file.save(source)
            filenames.append(source)

        # Predict and get the annotations for all images
        annotations = labelling_app.predict_multiple_images(filenames)

        # Convert list of dictionaries to a single dictionary
        result_dict = {}
        for idx, annotation in enumerate(annotations):
            result_dict.update(annotation)

        # Convert dictionary to JSON format
        annotations_json = json.dumps(result_dict)

        # Save the JSON file to the "labels" directory
        output_directory = './labels'  # Change this to the desired output directory
        labelling_app.save_annotations_to_file(
            annotations_json, output_directory)

        return annotations_json
    else:
        return "No files uploaded."

@app.route('/annotated-by-ai', methods=['GET', 'POST'])
@check_authentication
def annotated_by_ai():
    """Annotate images using AI"""
    # Retrieve the annotations from the VIA interface
    annotations = via.getAnnotations()

    # Send the annotations to the Flask app for prediction
    response = requests.post('http://localhost/predict', json=annotations)  # À Modifier l'URL

    # Handle the response from the Flask app
    if response.status_code == 200:
        # Process the predictions from VIA
        predictions = response.json()

        # Update the annotations with the predictions
        for image_id, annotation in annotations.items():
            annotation['regions'].extend(predictions[image_id]['regions'])

        # Convert the updated annotations to JSON format
        annotations_json = json.dumps(annotations)

        # Save the updated annotations to the "labels" directory
        labelling_app.save_annotations_to_file(
            annotations_json, './labels')
        return 'Annotations annotated by AI'
    else:
        return 'Failed to annotate by AI. Error: ' + response.text
    

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


@app.route('/admin/user_management')
@check_authentication
def user_management():
    try:
        # Replace the URL with the actual URL of your API to retrieve users
        response = requests.get(f'{SERVER_URL}/all_user')
        response.raise_for_status()  # Handle HTTP errors
        users = response.json()  # Convert JSON response to Python dict
        return render_template('user_management.html', users=users)
    except requests.exceptions.RequestException as e:
        print(f"Error fetching users: {e}")
        return []

@app.route('/admin/switch_role/<int:user_id>')
@check_authentication
def switch_role(user_id):
    try:
        # Send a request to your API to switch the user's role
        response = requests.post(f'{SERVER_URL}/change_role/{user_id}')
        response.raise_for_status()
        # Redirect the user to the user management page after role switch
        return redirect('/admin/user_management')
    except requests.exceptions.RequestException as e:
        print(f"Error switching role: {e}")
        print(f"Response content: {response.content}")
        return []


@app.route('/logout')
def logout():
    # Clear the session to log out the user
    session.clear()
    # Redirect to the login page
    return redirect(url_for('login'))


if __name__ == '__main__':
    app.run(debug=True)