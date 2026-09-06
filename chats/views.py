from django.shortcuts import render

from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from .models import Conversation
from .models import Message
from .serializer import MessageSerializer
from .serializer import ConversationSerializer
from django.db.models import Q
@api_view(['GET' , 'POST'])
@permission_classes([IsAuthenticated])
def chat_conv(request):
    conversation = Conversation.objects.filter(Q(participant1 = request.user) | Q(participant2 = request.user))
    if request.user not in(Conversation.participant1 , Conversation.participant2):
        return Response(status=403)
    if request.method == 'GET': 
       
        serializer = ConversationSerializer(conversation , many = True  )
        return Response(serializer.data)
    elif request.method =='POST':
        serializer = ConversationSerializer(data = request.data)
        if serializer.is_valid():
            serializer.save(participant1 = request.user ) 
            return Response(serializer.data ) 
        return Response(serializer.errors , status=400)

    
def _check_partc(conversation , user):
    return user in (conversation.participant1 , conversation.particiapnt2)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def chat_conv_detail(request, pk):
    try:
        conversation = Conversation.objects.get(pk=pk)
    except Conversation.DoesNotExist:
        return Response(status=404)

    if request.user not in (conversation.participant1, conversation.participant2):
        return Response(status=403)

    serializer = ConversationSerializer(
        conversation,
        context={'request': request}  
    )
    return Response(serializer.data)


@api_view(['GET' , 'POST' , 'DELETE'])
@permission_classes([IsAuthenticated])
def chat_msg(request , pk):
    try:
        conversation = Conversation.objects.get(pk=pk)
    except Message.DoesNotExist:
        return Response(status = 404)
    if not _check_partc(conversation , request.user):
        return Response(status = 403)
    if conversation.blocked_by.exists():
        return Response('Conversation is blocked')
    if request.method == 'GET':
        messages = Message.objects.get()
        serializer = MessageSerializer(messages , context = {'request':request} )
        return Response(serializer.data)
    elif request.method =='POST':
        serializer = MessageSerializer(messages , data = request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data ) 
        return Response(serializer.errors , status=400)

    
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_msg(request , pk):
    try:
        message = Message.objects.get(pk=pk)
    except Message.DoesNotExist:
        return Response(status = 404)
    message.delete()
    return Response('Message deleted')


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def block_unblock(request , pk):
    if request.user not in(Conversation.participant1 , Conversation.participant2):
        return Response(status=403)
    try:
        conversation = Conversation.objects.get(pk=pk)
    except Message.DoesNotExist:
        return Response(status = 404)
    conversation.blocked_by = request.user
    conversation.save()
    return Response('Conversation is blocked')
  


# Create your views here.
