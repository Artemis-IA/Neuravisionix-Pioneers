import os
import json
from PIL import Image
from ultralytics import YOLO


image_directory = "./images"
output_directory = './labels'


class PredictorLabeler:
    def __init__(self, model_path='yolov8n.pt'):
        self.model = YOLO(model_path)

    def predict_single_image(self, image_path):
        results = self.model(image_path, save=False)
        class_names = self.model.names
        annotations = {}

        for idx, result in enumerate(results):
            filename = os.path.basename(image_path)
            file_size = os.path.getsize(image_path)
            unique_key = f"{filename}{file_size}"

            with Image.open(image_path) as img:
                width, height = img.size

            size = width * height
            regions = []

            for i, box in enumerate(result.boxes.xyxy.tolist()):
                class_index = int(result.boxes.cls[i])
                label = class_names[class_index]

                x_abs, y_abs, width_abs, height_abs = map(int, box)

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

    def predict_multiple_images(self, image_paths):
        all_annotations = []

        for image_path in image_paths:
            annotations = self.predict_single_image(image_path)
            all_annotations.append(annotations)

        return all_annotations

    def list_images_in_directory(self, directory_path):
        images = []

        if os.path.exists(directory_path) and os.path.isdir(directory_path):
            for filename in os.listdir(directory_path):
                if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
                    images.append(os.path.join(directory_path, filename))

        return images

    def save_annotations_to_file(self, annotations, output_directory):
        if not os.path.exists(output_directory):
            try:
                os.makedirs(output_directory)
                print(f"Directory '{output_directory}' created.")
            except OSError as e:
                print(f"Error: {output_directory} - {e}")
                return

        output_path = os.path.join(output_directory, 'annotations.json')
        with open(output_path, 'w') as json_file:
            json.dump(annotations, json_file)

        print(f"Annotations saved to {output_path}")


# Example usage:
predictor_labeler = PredictorLabeler()

# Get a list of all image paths in the directory
image_paths = predictor_labeler.list_images_in_directory(image_directory)

# Predict annotations for all images in the directory
annotations = predictor_labeler.predict_multiple_images(image_paths)

# Save annotations to file
saved_annotations = predictor_labeler.save_annotations_to_file(annotations, output_directory)