import os
import cv2
import json
from ultralytics import YOLO
from flask import Flask, render_template, request, jsonify
from werkzeug.utils import secure_filename

app = Flask(__name__)

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
            image = cv2.imread(image_path)
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

labeling_app = PredictorLabeller()

@app.route('/')
def index():
    labeled_images = []  # You need to populate this list with labeled images data
    return render_template('index.html', labeled_images=labeled_images)

@app.route('/predict', methods=['POST'])
def predict_route():
    uploaded_files = request.files.getlist('myfile')

    if uploaded_files:
        # Save the uploaded files with secure filenames
        filenames = []
        for idx, uploaded_file in enumerate(uploaded_files):
            filename = secure_filename(uploaded_file.filename)
            source = os.path.join(labeling_app.image_directory, filename)
            uploaded_file.save(source)
            filenames.append(source)

        # Predict and get the annotations for all images
        annotations = labeling_app.predict_multiple_images(filenames)

        # Convert list of dictionaries to a single dictionary
        result_dict = {}
        for idx, annotation in enumerate(annotations):
            result_dict.update(annotation)

        # Convert dictionary to JSON format
        annotations_json = json.dumps(result_dict)

        # Save the JSON file to the "labels" directory
        output_directory = './labels'  # Change this to the desired output directory
        labeling_app.save_annotations_to_file(annotations_json, output_directory)

        return annotations_json
    else:
        return "No files uploaded."

@app.route('/load_images', methods=['POST'])
def load_images():
    directory_path = request.json.get('directory_path', '')
    images = labeling_app.list_images_in_directory(directory_path)
    return jsonify({'images': images})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)