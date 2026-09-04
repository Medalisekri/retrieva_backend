import firebase_admin
from firebase_admin import credentials
from django.apps import AppConfig
import os
from dotenv import load_dotenv

load_dotenv()

class AccountsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'accounts'
    def ready(self):
        import accounts.signals

        if not firebase_admin._apps:
            cred = credentials.Certificate(os.getenv('FIREBASE_CREDENTIALS'))
            firebase_admin.initialize_app(cred)