from django.shortcuts import render
from rest_framework.decorators import api_view  , permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from .serializer import RegisterSerializer


@api_view(['POST'])
@permission_classes([AllowAny])
def create_user(request):
       serializer = RegisterSerializer(data = request.data)
       if serializer.is_valid():
            serializer.save()
            return Response({"message" : "User Created"} , status=204)
       return Response(serializer.errors , status=400)

# Create your views here.
