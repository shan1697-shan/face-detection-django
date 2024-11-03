import cv2
import os
import pickle
import pandas as pd
from django.shortcuts import render, redirect
from .models import User, Attendance
from django.http import JsonResponse
from .face_detection import (
    check_camera_access, collect_data, train_model, recognize_faces
)
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
import base64

DATA_DIR = "face_data"

@csrf_exempt
def receive_frame(request):
    if request.method == "POST":
        student_id = request.POST.get("student_id")
        name = request.POST.get("name")
        image_data = request.POST.get("image_data")

        # Decode the base64 image
        _, image_data = image_data.split(',')
        image_bytes = base64.b64decode(image_data)

        # Ensure the data directory exists
        if not os.path.exists(DATA_DIR):
            os.makedirs(DATA_DIR)

        # Save image with a timestamp
        timestamp = timezone.now().strftime("%Y%m%d%H%M%S%f")
        filename = f"{student_id}_{timestamp}.jpg"
        file_path = os.path.join(DATA_DIR, filename)

        # Write the image to file
        with open(file_path, "wb") as f:
            f.write(image_bytes)

        return JsonResponse({"status": "success", "filename": filename})
    return JsonResponse({"status": "failure", "error": "Invalid request"})

@csrf_exempt
def start_recognition(request):
    """API endpoint to start face recognition and mark attendance."""
    if request.method == "POST":
        result = recognize_faces()
        return JsonResponse(result)
    return JsonResponse({"error": "Invalid request method."}, status=405)

def collect_data_view(request):
    if request.method == "POST":
        student_id = request.POST.get("student_id")
        name = request.POST.get("name")

        # Create or retrieve user
        user, created = User.objects.get_or_create(student_id=student_id, defaults={'name': name})
        if not created:
            user.name = name  # Update name if different
            user.save()
        print(f"User saved: {user}")

        # Collect face data
        collect_data(student_id=student_id, name=name)
        return JsonResponse({"message": f"Data collection completed for {name} (ID: {student_id})"})

    return render(request, "attendance/collect_data.html")

def train_model_view(request):
    if request.method == "POST":
        train_model()
        return JsonResponse({"status": "success", "message": "Model training completed."})
    return render(request, "attendance/train_model.html")

def recognize_faces_view(request):
    if request.method == "POST":
        recognize_faces()
        return JsonResponse({"message": "Face recognition started."})
    return render(request, "attendance/recognize_faces.html")

def home_view(request):
    attendance_data = Attendance.objects.select_related('user').all()
    print(attendance_data)
    return render(request, "attendance/home.html", {"attendance_data": attendance_data})