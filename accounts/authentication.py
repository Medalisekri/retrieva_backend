from firebase_admin import auth
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from django.contrib.auth.models import User

class FirebaseAuthentication(BaseAuthentication):
    def authenticate(self, request):
        token = request.headers.get('Authorization')
        if not token:
            return None
        
        try:
            decoded_token = auth.verify_id_token(token)
            uid = decoded_token['uid']
            email = decoded_token.get('email', '')
            
            user = User.objects.get_or_create(
                username=uid,
                defaults={'email': email}
            )
            return (user, None)
        except Exception:
            raise AuthenticationFailed('Invalid Firebase token')