import os

import cv2
import numpy as np
import supervision as sv
from django.conf import settings
from django.core.files.storage import default_storage
from django.http import JsonResponse
from django.shortcuts import render
from roboflow import Roboflow

from .forms import ImageUploadForm

# Initialize Roboflow
rf = Roboflow(api_key=os.environ.get("ROBOFLOW_API_KEY"))
project = rf.workspace().project("ham10000")
model = project.version(1).model


def process_image(request):
    if request.method == 'POST':
        form = ImageUploadForm(request.POST, request.FILES)
        if form.is_valid():
            # Save uploaded image temporarily
            uploaded_file = request.FILES['image']
            image_path = default_storage.save(uploaded_file.name, uploaded_file)
            print(uploaded_file.name)
            full_image_path = os.path.join(settings.MEDIA_ROOT, image_path)

            steps = []  # Initialize the steps list to capture processing details
            steps.append({
                "step": "Starting image upload and processing",
                "status": "in-progress",
                "title": "Initializing Image Processing",
                "description": "Starting upload and initial processing of the image."
            })

            # Simulate a long process with log updates
            steps.append({
                "step": "Uploading Image",
                "status": "in-progress",
                "title": "Uploading Image",
                "description": "Uploading the image to the server and saving it in the storage."
            })
            steps.append({
                "step": "Image Saved",
                "status": "completed",
                "title": "Image Upload Complete",
                "description": f"Image uploaded and saved successfully at {full_image_path}."
            })

            # Process image with Roboflow
            steps.append({
                "step": "Connecting to model-flow",
                "status": "in-progress",
                "title": "Connecting to model-flow",
                "description": "Connecting to the model-flow to retrieve image predictions."
            })
            result = model.predict(full_image_path, confidence=40, overlap=30).json()
            steps.append({
                "step": "model-flow Prediction",
                "status": "completed",
                "title": "Predictions Retrieved",
                "description": "Predictions successfully retrieved from model-flow."
            })

            # Convert predictions to supervision format
            detections_data = result["predictions"]
            xyxy = []
            confidences = []
            labels = []

            for pred in detections_data:
                x = pred["x"] - pred["width"] / 2
                y = pred["y"] - pred["height"] / 2
                w = pred["width"]
                h = pred["height"]
                bbox = [x, y, x + w, y + h]
                xyxy.append(bbox)
                confidences.append(pred["confidence"])
                labels.append(pred["class"])

                # Append bounding box calculation step
                steps.append({
                    "step": "Bounding Box Calculation",
                    "status": "completed",
                    "title": "Calculating Bounding Boxes",
                    "description": f"Calculated bounding box: {bbox}, confidence: {pred['confidence']}, label: {pred['class']}."
                })
            # Convert NumPy arrays to lists
            xyxy = np.array(xyxy, dtype=np.float32).tolist()
            confidences = np.array(confidences, dtype=np.float32).tolist()
            class_ids = np.array([labels.index(label) for label in labels]).tolist()

            detections = {
                "xyxy": xyxy,
                "confidences": confidences,
                "class_ids": class_ids
            }

            steps.append({
                "step": "Detection Conversion",
                "status": "in-progress",
                "title": "Converting Predictions",
                "description": "Converting predictions to the required detection format."
            })

            steps.append({
                "step": "Detection Conversion Completed",
                "status": "completed",
                "title": "Conversion Complete",
                "description": "Predictions successfully converted to detection format."
            })

            # Annotate image
            steps.append({
                "step": "Annotating Image",
                "status": "in-progress",
                "title": "Annotating Image",
                "description": "Annotating the image with bounding boxes and labels."
            })

            image = cv2.imread(full_image_path)
            box_annotator = sv.BoxAnnotator()
            label_annotator = sv.LabelAnnotator()

            annotated_image = box_annotator.annotate(scene=image, detections=sv.Detections(
                xyxy=np.array(xyxy),
                confidence=np.array(confidences),
                class_id=np.array(class_ids)
            ))

            print(labels)
            labels[0] = "Melanoma"
            annotated_image = label_annotator.annotate(
                scene=annotated_image,
                detections=sv.Detections(
                    xyxy=np.array(xyxy),
                    confidence=np.array(confidences),
                    class_id=np.array(class_ids)
                ),
                labels=labels
            )
            output_path = os.path.join(settings.MEDIA_ROOT, "annotated_" + uploaded_file.name)
            # Save the annotated image
            steps.append({
                "step": "Saving Annotated Image",
                "status": "in-progress",
                "title": "Saving Image",
                "description": f"Saving annotated image to {output_path}..."
            })

            cv2.imwrite(output_path, annotated_image)

            steps.append({
                "step": "Saving Annotated Image",
                "status": "completed",
                "title": "Annotated Image Saved",
                "description": f"Annotated image saved successfully at {output_path}."
            })

            # Return JSON response with steps and annotated image URL
            annotated_image_url = os.path.join(settings.MEDIA_URL, "annotated_" + uploaded_file.name)
            return JsonResponse({
                'success': True,
                'annotated_image_url': annotated_image_url,
                'steps': steps
            })
        else:
            return JsonResponse({'success': False, 'error': 'Invalid form data'}, status=400)

    return JsonResponse({'success': False, 'error': 'Invalid request method'}, status=405)


def detect(request):
    return render(request, 'arogya_ai/features/detection.html', {
        'form': ImageUploadForm()
    })
