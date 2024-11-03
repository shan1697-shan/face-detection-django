# models.py
from django.db import models

class User(models.Model):
    student_id = models.CharField(max_length=100, unique=True)
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Attendance(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField(auto_now_add=True)
    time = models.TimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.name} - {self.date} - {self.time}"
