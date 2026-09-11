from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from .serializer import ProfileSerializer
import requests
from django.conf import settings
from rest_framework.permissions import IsAuthenticated
@api_view(['GET', 'PATCH'])
def profile(request):
    print("USER:", request.user)
    print("AUTH:", request.auth)
    profile = request.user.profile
    if request.method == 'GET':
        return Response(ProfileSerializer(profile).data)
    elif request.method == 'PATCH':
        serializer = ProfileSerializer(profile, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def contact_us(request):
    name = request.data.get('name', '').strip()
    email = request.data.get('email', '').strip()
    message = request.data.get('message', '').strip()

    # Basic validation
    if not name or not email or not message:
        return Response(
            {'error': 'Name, email, and message are required.'},
            status=400,
        )

    # Verify EmailJS config exists
    if not all([
        settings.EMAILJS_SERVICE_ID,
        settings.EMAILJS_TEMPLATE_ID,
        settings.EMAILJS_PUBLIC_KEY,
    
    ]):
        return Response(
            {'error': 'Email service is not configured.'},
            status=500,
        )

    # Send via EmailJS REST API
    payload = {
        'service_id': settings.EMAILJS_SERVICE_ID,
        'template_id': settings.EMAILJS_TEMPLATE_ID,
        'user_id': settings.EMAILJS_PUBLIC_KEY,
   
        'template_params': {
            'name': name,
            'email': email,
            'message': message,
            'sender_uid': request.user.username,  # Firebase UID, useful for tracing
        },
    }

    try:
        response = requests.post(
            'https://api.emailjs.com/api/v1.0/email/send',
            json=payload,
            timeout=10,
        )
    except requests.RequestException as e:
        print(f"[EMAILJS] Request failed: {e}")
        return Response(
            {'error': 'Failed to connect to email service.'},
            status=502,
        )
    if response.status_code == 200:
        print(f"[EMAILJS] Email sent from {email} ({request.user.username})")
        return Response({'message': 'Email sent successfully.'})

    print(f"[EMAILJS] Failed: {response.status_code} {response.text}")
    return Response(
        {'error': 'Email service rejected the request.'},
        status=502,
    )