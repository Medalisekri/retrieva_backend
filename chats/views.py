from django.shortcuts import render

from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from .models import Conversation
from .models import Message
from .serializer import MessageSerializer
from .serializer import ConversationSerializer
from django.db.models import Q
from items.notifications import send_push
@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def chat_conv(request):
    if request.method == 'GET':
        conversations = Conversation.objects.filter(
            Q(participant1=request.user) | Q(participant2=request.user)
        )
        serializer = ConversationSerializer(conversations, many=True,
                                            context={'request': request})
        return Response(serializer.data)

    elif request.method == 'POST':
        item_id = request.data.get('item')
        other_user_id = request.data.get('participant2')

       
        existing = Conversation.objects.filter(
            Q(item_id=item_id) &
            (
                (Q(participant1=request.user) & Q(participant2_id=other_user_id)) |
                (Q(participant1_id=other_user_id) & Q(participant2=request.user))
            )
        ).first()

        if existing:
            serializer = ConversationSerializer(existing, context={'request': request})
            return Response(serializer.data, status=200)

      
        serializer = ConversationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(participant1=request.user)
            return Response(serializer.data, status=201)
       
        return Response(serializer.errors, status=400)
    
def _check_partc(conversation , user):
    return user in (conversation.participant1 , conversation.participant2)

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


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def chat_msg(request, pk):
    try:
        conversation = Conversation.objects.get(pk=pk)  # ← Conversation, not Message
    except Conversation.DoesNotExist:
        return Response(status=404)

    if not _check_partc(conversation, request.user):
        return Response(status=403)

    # Only block if THIS user is blocked, not just anyone
    if conversation.blocked_by.filter(id=request.user.id).exists():
        return Response({'detail': 'You blocked this conversation.'}, status=403)

    if request.method == 'GET':
        messages = Message.objects.filter(conversation=conversation).order_by('created_at')
        serializer = MessageSerializer(messages, many=True,
                                       context={'request': request})
        return Response(serializer.data)

    elif request.method == 'POST':
        serializer = MessageSerializer(data=request.data)
        if serializer.is_valid():
             message = serializer.save(conversation=conversation, sender=request.user)

        if conversation.participant1 == request.user:
            recipient = conversation.participant2
        else:
            recipient = conversation.participant1

        if recipient != request.user:
            sender_name = getattr(request.user.profile, 'full_name', '') or 'Someone'
            preview = message.text[:80] if message.text else 'Sent an image'

            send_push(
                external_ids=[recipient.username],
                title=f"New message from {sender_name}",
                body=preview,
                data={
                    "type": "chat_message",
                    "conversation_id": conversation.id,
                    "item_name": conversation.item.name,
                },
            )

        return Response(serializer.data, status=201)


    return Response(serializer.errors, status=400)
    
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
def block_unblock(request, pk):
    try:
        conversation = Conversation.objects.get(pk=pk)  # ← fetch FIRST
    except Conversation.DoesNotExist:
        return Response(status=404)

   
    if request.user not in (conversation.participant1, conversation.participant2):
        return Response(status=403)

   
    if conversation.blocked_by.filter(id=request.user.id).exists():
        conversation.blocked_by.remove(request.user)  # unblock
        return Response({'detail': 'Unblocked'})
    else:
        conversation.blocked_by.add(request.user)     # block
        return Response({'detail': 'Blocked'})
