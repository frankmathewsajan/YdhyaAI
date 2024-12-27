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
project = rf.workspace().project("ham10000")
model = project.version(1).model


def process_image(request):
    print(0)
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
            print(detections_data)
            for pred in detections_data:
                x = pred["x"] - pred["width"] / 2
                y = pred["y"] - pred["height"] / 2
                w = pred["width"]
                h = pred["height"]
                print(pred)
                xyxy.append([x, y, x + w, y + h])
                confidences.append(pred["confidence"])
                labels.append(pred["class"])
                print(x, y, w, h)
                print(pred["confidence"], pred["class"])

            xyxy = np.array(xyxy, dtype=np.float32)
            confidences = np.array(confidences, dtype=np.float32)
            class_ids = np.array([labels.index(label) for label in labels])
            print(xyxy, confidences, class_ids)
            detections = sv.Detections(xyxy=xyxy, confidence=confidences, class_id=class_ids)

            # Annotate image
            image = cv2.imread(full_image_path)
            box_annotator = sv.BoxAnnotator()
            label_annotator = sv.LabelAnnotator()

            annotated_image = box_annotator.annotate(scene=image, detections=detections)
            annotated_image = label_annotator.annotate(
                scene=annotated_image, detections=detections, labels=labels
            )

            # Save the annotated image
            output_path = os.path.join(settings.MEDIA_ROOT, "annotated_" + uploaded_file.name)
            cv2.imwrite(output_path, annotated_image)

            # Return annotated image path to template
            annotated_image_url = os.path.join(settings.MEDIA_URL, "annotated_" + uploaded_file.name)
            return render(request, 'arogya_ai/features/detection.html', {'annotated_image_url': annotated_image_url})

    form = ImageUploadForm()
    print(form)
    return render(request, 'arogya_ai/features/detection.html', {'form': form})
