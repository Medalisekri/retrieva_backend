from firebase_admin import auth
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from django.contrib.auth.models import User

class FirebaseAuthentication(BaseAuthentication):
 def authenticate(self, request):
    auth_header = request.headers.get('Authorization', '')       
    if not auth_header.startswith('Bearer '):
            return None 
            
    token = auth_header[7:] # Extract everything after "Bearer "
        
    if not token:
        return None
    try:
        decoded_token = auth.verify_id_token(token)
       
    except Exception as e:
       
        raise AuthenticationFailed('Invalid Firebase token')

    uid = decoded_token['uid']
    email = decoded_token.get('email', '')

    user, created = User.objects.get_or_create(
            username=uid,
            defaults={'email': email}
        )

    if created:
            user.set_unusable_password()
            user.save()
    else:
            if user.email != email:
                user.email = email
                user.save(update_fields=['email'])

    return user, None

def authenticate_header(self, request):
    return 'Bearer'