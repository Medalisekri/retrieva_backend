from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.decorators import api_view
from .models import Item
from .serializer import ItemSerializer
@api_view(['GET' , 'POST'])
def item_list(request):
    if request.method == 'GET':
        items = Item.objects.all()
        serializer = ItemSerializer(items , many = True)
        return Response(serializer.data)
    elif request.method =='POST':
        serializer = ItemSerializer(data = request.data)
        if serializer.is_valid():
            serializer.save(user = request.user)
            return Response(serializer.data ) 
        return Response(serializer.errors , status=400)

@api_view(['GET' , 'PATCH' , 'DELETE'])
def item_detail(request , pk):
    try:
        item = Item.objects.get(pk=pk)
    except Item.DoesNotExist:
        return Response(status = 404)
    if request.method == 'GET':
        serializer = ItemSerializer(item)
        return Response(serializer.data)
    if item.user != request.user:
        return Response(status=403)
    elif request.method =='PATCH':
        serializer = ItemSerializer(item , data = request.data , partial = True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data ) 
        return Response(serializer.errors , status=400)
    elif request.method == 'DELETE':
        item.delete()
        return Response(status = 204)

