from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_view, name='home'), 
    path('collect_data/', views.collect_data_view, name='collect_data'),
    path('receive_frame/', views.receive_frame, name='receive_frame'), 
    path('train_model/', views.train_model_view, name='train_model'),
    path('recognize_faces/', views.recognize_faces_view, name='recognize_faces'),
    path('start_recognition/', views.start_recognition, name='start_recognition'),
]
