from django.apps import AppConfig
import os
import json
from dotenv import load_dotenv

load_dotenv()

class AccountsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'accounts'

    def ready(self):
        import accounts.signals
        import firebase_admin
        from firebase_admin import credentials

        if not firebase_admin._apps:
            firebase_creds = os.getenv('FIREBASE_CREDENTIALS')

            # If it looks like JSON → parse it (Render)
            if firebase_creds.strip().startswith('{'):
                cred = credentials.Certificate(json.loads(firebase_creds))
            else:
                # Otherwise treat it as a file path (local)
                cred = credentials.Certificate(firebase_creds)

            firebase_admin.initialize_app(cred)