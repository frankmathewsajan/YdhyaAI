import os

import cv2
import numpy as np
import supervision as sv
from django.conf import settings
from django.core.files.storage import default_storage
from django.shortcuts import render
from roboflow import Roboflow

from .forms import ImageUploadForm

# Initialize Roboflow
rf = Roboflow(api_key=os.environ.get("ROBOFLOW_API_KEY"))
project = rf.workspace("fyp-mlsby").project("skin-cancer-uq13v")
model = project.version(2).model

# Define skin cancer classes with full descriptions
classes = {
    'akiec': 'Actinic keratoses and intraepithelial carcinomae',
    'bcc': 'Basal cell carcinoma',
    'bkl': 'Benign keratosis-like lesions',
    'df': 'Dermatofibroma',
    'nv': 'Melanocytic nevi',
    'vasc': 'Pyogenic granulomas and hemorrhage',
    'mel': 'Melanoma',
}


def process_image(request):
    if request.method == 'POST':
        form = ImageUploadForm(request.POST, request.FILES)
        if form.is_valid():
            # Save uploaded image temporarily
            uploaded_file = request.FILES['image']
            image_path = default_storage.save(uploaded_file.name, uploaded_file)
            full_image_path = os.path.join(settings.MEDIA_ROOT, image_path)

            # Process image with Roboflow
            result = model.predict(full_image_path, confidence=40, overlap=30).json()

            # Convert predictions to supervision format
            detections_data = result["predictions"]
            xyxy = []
            confidences = []
            labels = []
            full_labels = []

            for pred in detections_data:
                x = pred["x"] - pred["width"] / 2
                y = pred["y"] - pred["height"] / 2
                w = pred["width"]
                h = pred["height"]

                class_name = pred["class"]
                full_class_name = classes.get(class_name.lower(), class_name)

                xyxy.append([x, y, x + w, y + h])
                confidences.append(pred["confidence"])
                labels.append(class_name)
                print(full_class_name)
                full_labels.append(f"{full_class_name} ({pred['confidence']:.2f})")

            xyxy = np.array(xyxy, dtype=np.float32)
            confidences = np.array(confidences, dtype=np.float32)
            class_ids = np.array([list(classes.keys()).index(label) if label in classes else 0 for label in labels])

            detections = sv.Detections(xyxy=xyxy, confidence=confidences, class_id=class_ids)

            # Annotate image
            image = cv2.imread(full_image_path)
            box_annotator = sv.BoxAnnotator()
            label_annotator = sv.LabelAnnotator()

            annotated_image = box_annotator.annotate(scene=image, detections=detections)
            annotated_image = label_annotator.annotate(
                scene=annotated_image, detections=detections, labels=full_labels
            )

            # Save the annotated image
            output_path = os.path.join(settings.MEDIA_ROOT, "annotated_" + uploaded_file.name)
            cv2.imwrite(output_path, annotated_image)

            # Return annotated image path and detection results
            annotated_image_url = os.path.join(settings.MEDIA_URL, "annotated_" + uploaded_file.name)
            detection_results = [
                {"class": label, "full_name": classes.get(label, label), "confidence": conf}
                for label, conf in zip(labels, confidences)
            ]

            return render(request, 'arogya_ai/features/detection.html', {
                'annotated_image_url': annotated_image_url,
                'detection_results': detection_results
            })

    form = ImageUploadForm()
    return render(request, 'arogya_ai/features/detection.html', {'form': form})
