
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from .models import Item
from .serializer import ItemListSerializer
from django.utils import timezone
from .serializer import ItemDetailSerializer
from .matching import find_matches 
from .notifications import send_match_notifications
from rest_framework.pagination import PageNumberPagination
from datetime import timedelta
from django.db.models import Q
class ItemPagination(PageNumberPagination):
    page_size = 20                         
    page_size_query_param = 'page_size'     
    max_page_size = 50                     
@api_view(['GET' , 'POST'])
def item_list(request):
    if request.method == 'GET':
        today = timezone.now().date()
        items = Item.objects.filter(status='active')
        items = items.filter(
            Q(expires_at__gte=today) | Q(expires_at__isnull=True)
        )

        type = request.GET.get('type')
        category = request.GET.get('category')
        status = request.GET.get('status')
        if type:
            items = items.filter(type = type)
        if category: 
            items = items.filter(category = category)
        if status:
            items = items.filter(status = status)
        paginator = ItemPagination()
        page = paginator.paginate_queryset(items, request)
        serializer = ItemListSerializer(page, many=True , context = {'request':request})
        return paginator.get_paginated_response(serializer.data)
    
    elif request.method =='POST':
        if not request.user.is_authenticated:
            return Response(status=401)
        since = timezone.now() - timedelta(hours=24)
        recent_count = Item.objects.filter(
            user=request.user,
            created_at__gte=since,
        ).count()

        if recent_count >= 5:
            return Response(
                {'error': 'Limit reached. You can post up to 5 items per day.'},
                status=429,  
            )
        serializer = ItemListSerializer(data = request.data)
        if serializer.is_valid():
            item = serializer.save(user=request.user)  

            matches = find_matches(item)  
    
        if matches:
            send_match_notifications(item, matches)

        return Response(ItemListSerializer(item).data, status=201)
            
         

@api_view(['GET' , 'PATCH' , 'DELETE'])
def item_detail(request , pk):
    try:
        item = Item.objects.get(pk=pk)
    except Item.DoesNotExist:
        return Response(status = 404)
    if request.method == 'GET':

        if item.expires_at and item.expires_at < timezone.now().date():
            return Response(status=404)
        serializer = ItemDetailSerializer(item , context={'request': request},)
        return Response(serializer.data)
    if item.user != request.user:
        return Response(status=403)
    elif request.method =='PATCH':
        serializer = ItemDetailSerializer(item , data = request.data , partial = True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data ) 
        return Response(serializer.errors , status=400)
    elif request.method == 'DELETE':
        item.delete()
        return Response(status = 201)
@api_view(['PATCH'])
def report_item(request , pk):
    try:
        item = Item.objects.get(pk=pk)
    except Item.DoesNotExist:
        return Response(status = 404)
    item.is_reported = True
    item.save()
    return Response({"message" : "Item reported"}) 
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def my_items(request):
    items = Item.objects.filter(user=request.user).order_by('-created_at')
    active = request.GET.get('status')
    resolved = request.GET.get('status')
 
    if active:
           items = items.filter(status = 'active')
    if resolved: 
           items = items.filter(status = 'resolved')
    serializer = ItemListSerializer(items, many=True )
    return Response(serializer.data)
  

