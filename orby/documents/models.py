from django.db import models
from django.conf import settings
import os

class Category(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name_plural = "Categories"

class Document(models.Model):
    title = models.CharField(max_length=255)
    file = models.FileField(upload_to='documents/')
    description = models.TextField(blank=True, null=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='documents')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='documents')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    expiry_date = models.DateField(blank=True, null=True)
    file_type = models.CharField(max_length=50, blank=True)
    file_size = models.IntegerField(default=0)  # Size in KB
    
    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        if self.file:
            _, extension = os.path.splitext(self.file.name)
            self.file_type = extension[1:].upper()
            if self.file.size:
                self.file_size = self.file.size // 1024  # Convert to KB
        super().save(*args, **kwargs)
