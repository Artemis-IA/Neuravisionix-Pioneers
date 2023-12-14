from flask import session
from flask import flash
from functools import wraps
from flask import Flask, jsonify, redirect, render_template, request, session, url_for
from flask import send_file
import requests
import os
from PIL import Image
import json

from flask import Flask, render_template, request, jsonify
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = '0ec5205f107e18f72f9fd8d363c04c98'
SERVER_URL = "http://equipe2.lumys.tech:5005"


class PredictorLabeller:
    def __init__(self):
        self.image_directory = "./images"
        self.device = "cpu"


    def predict_single_image(self, image_path):
        results = self.model(image_path, save=True)
        class_names = self.model.names
        annotations = {}

        for idx, result in enumerate(results):
            filename = image_path.split("/")[-1]
            file_size = os.path.getsize(image_path)
            unique_key = f"{filename}{file_size}"
            image =[]
            height, width, channels = image.shape

            size = width * height
            regions = []

            for i, box in enumerate(result.boxes.xyxy.tolist()):
                class_index = int(result.boxes.cls[i])
                label = class_names[class_index]

                # Convert normalized coordinates to absolute pixel values
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
def labelling():
    id_image=  '65772409edfb11a6c6d8fac9' #image en dur 
    info_image= requests.get(f'{SERVER_URL}/affiche_image/{id_image}')
    data_image = info_image.json()
    filepath = data_image['result']['path']
    print('prems : ',filepath)
    filepath = {"filepath": filepath}
    response_annotation = requests.post(f'http://equipe2.lumys.tech:5005/load_images', json=filepath)
    data = response_annotation.json()
    filename = [image_info['filename'] for image_info in data['images'].values()]
    filename = filename[0]
    print(f"Image:{filename}")
    
    response_image = requests.post(f'{SERVER_URL}/image_from_server', json=filepath)

    with open(f"./image/{filename}", 'wb') as f:
        f.write(response_image.content)
    image=filename
    return render_template('labelling.html',image=image ,filename=filename ,data=data,id_image=id_image)

@app.route('/get_image/<filename>')
def get_image(filename):
    image_path = f'./image/{filename}'
    with Image.open(image_path) as img:
        # Récupérer le format de l'image (par exemple, 'JPEG', 'PNG', etc.)
        image_format = img.format.lower()
        print('image sans app pls',image_path)
        # Envoyer le fichier avec le bon type MIME
        return send_file(image_path, mimetype=f'image/{image_format}')

    
    #return send_file(image_path, mimetype='image/png')


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

@app.route('/resultat', methods=['POST'])
def resultat():
    print("resultat")

    # Récupérer le fichier du formulaire multipart
    uploaded_file = request.files['file']
    file_content = uploaded_file.read().decode('utf-8')
    id_value = request.form['id']
    # response = requests.post(f'{SERVER_URL}/post_resultat/{id_value}')
    file_content=json.loads(file_content)
    # print(list(file_content.keys())[0])
    data = {'id':id_value ,'regions': file_content[list(file_content.keys())[0]]["regions"]}
    print('uplod',data)
    response = requests.post(f'{SERVER_URL}/post_resultat', json=data)
    response_json = response.json()
    return jsonify({'status': 'success', 'message': 'File uploaded successfully'})



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
        # Remplacez l'URL par l'URL réelle de votre API pour récupérer les utilisateurs
        response = requests.get(f'{SERVER_URL}/all_user')
        response.raise_for_status()  # Gère les erreurs HTTP
        users = response.json()  # Convertit la réponse JSON en Python dict
        print(users)
        return render_template('user_management.html', users=users)
    except requests.exceptions.RequestException as e:
        print(f"Error fetching users: {e}")
        return []


@app.route('/admin/switch_role/<int:user_id>')
@check_authentication
def switch_role(user_id):
    try:
        # Envoyez une requête à votre API pour basculer le rôle de l'utilisateur
        response = requests.post(f'{SERVER_URL}/change_role/{user_id}')
        response.raise_for_status()
        # Redirigez l'utilisateur vers la page de gestion des utilisateurs après le basculement du rôle
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
