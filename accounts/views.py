from django.shortcuts import render
from rest_framework.decorators import api_view  , permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from .serializer import RegisterSerializer
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.core.mail import send_mail
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_str
from django.contrib.auth.models import User
@api_view(['POST'])
@permission_classes([AllowAny])
def create_user(request):
       serializer = RegisterSerializer(data = request.data)
       if serializer.is_valid():
            user =  serializer.save()
            send_verification_email(user = user)
            return Response({"message" : "User Created"} , status=204)
       return Response(serializer.errors , status=400)

import sib_api_v3_sdk
from sib_api_v3_sdk.rest import ApiException
from django.conf import settings

def send_verification_email(user):
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = default_token_generator.make_token(user)
    link = f'http://127.0.0.1:8000/auth/verify/?uid={uid}&token={token}'
    
    configuration = sib_api_v3_sdk.Configuration()
    configuration.api_key['api-key'] = settings.BREVO_API_KEY
    
    api_instance = sib_api_v3_sdk.TransactionalEmailsApi(sib_api_v3_sdk.ApiClient(configuration))
    
    email = sib_api_v3_sdk.SendSmtpEmail(
        to=[{'email': user.email}],
        subject='Verify your Retrieva account',
        text_content=f'Click the link to verify your account: {link}',
        sender={'email': settings.DEFAULT_FROM_EMAIL, 'name': 'Retrieva'}
    )
    
    api_instance.send_transac_email(email)

@api_view(['GET'])
@permission_classes([AllowAny])
def verify_email(request):
     try:
          uid = request.GET.get('uid')
          token = request.GET.get('token')
          user_id = force_str(urlsafe_base64_decode(uid))
          user = User.objects.get(pk = user_id)
          if default_token_generator.check_token(token , user):
               user.profile.is_verified= True
               user.profile.save()
               return Response({'message' : 'email verified successfully'})
          return Response({'error':'Invalid or expired token'} , status=400)
     except User.DoesNotExist:
          return Response(status=404)
# Create your views here.
