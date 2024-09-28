from django.db import models

from django.contrib.auth.models import User
from config.settings import CREDENTIALS_ENCRYPTION_KEY
from cryptography.fernet import Fernet

class IntegrationCredential(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    provider = models.CharField(max_length=50)  # e.g., 'google', 'twitter'
    credentials = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @staticmethod
    def encrypt_credentials(credentials_json):
        f = Fernet(CREDENTIALS_ENCRYPTION_KEY)
        return f.encrypt(credentials_json.encode()).decode()

    @staticmethod
    def decrypt_credentials(encrypted_credentials):
        f = Fernet(CREDENTIALS_ENCRYPTION_KEY)
        return f.decrypt(encrypted_credentials.encode()).decode()

    def save(self, *args, **kwargs):
        if not self.pk:  # Only encrypt if it's a new object
            self.credentials = self.encrypt_credentials(self.credentials)
        super().save(*args, **kwargs)

    def get_credentials(self):
        return self.decrypt_credentials(self.credentials)
