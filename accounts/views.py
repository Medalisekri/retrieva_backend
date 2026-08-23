from rest_framework.decorators import api_view
from rest_framework.response import Response
from .serializer import ProfileSerializer
@api_view(['GET', 'PATCH'])
def profile(request):
    profile = request.user.profile
    if request.method == 'GET':
        return Response(ProfileSerializer(profile).data)
    elif request.method == 'PATCH':
        serializer = ProfileSerializer(profile, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)