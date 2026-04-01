from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from .models import User, List, Item, ListMember
from .serializers import RegisterSerializer, UserSerializer, ListSerializer, ItemSerializer

def get_tokens(user):
    refresh = RefreshToken.for_user(user)
    return str(refresh.access_token)

def broadcast(list_id, payload):
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        f'list_{list_id}',
        {
            'type': 'list_update',
            'payload': payload
        }
    )

# POST /auth/register
@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    serializer = RegisterSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        return Response({'user': UserSerializer(user).data, 'token': get_tokens(user)}, status=201)
    return Response(serializer.errors, status=400)

# POST /auth/login
@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    email = request.data.get('email')
    password = request.data.get('password')
    user = authenticate(request, username=email, password=password)
    if not user:
        return Response({'error': 'Invalid credentials'}, status=401)
    return Response({'user': UserSerializer(user).data, 'token': get_tokens(user)})

# GET, POST /lists
@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def lists(request):
    if request.method == 'GET':
        user_lists = List.objects.filter(members=request.user)
        return Response(ListSerializer(user_lists, many=True).data)

    serializer = ListSerializer(data=request.data)
    if serializer.is_valid():
        lst = serializer.save(owner=request.user)
        ListMember.objects.create(list=lst, user=request.user)
        return Response(ListSerializer(lst).data, status=201)
    return Response(serializer.errors, status=400)

# POST /lists/:id/items
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_item(request, list_id):
    try:
        lst = List.objects.get(id=list_id, members=request.user)
    except List.DoesNotExist:
        return Response({'error': 'List not found'}, status=404)

    serializer = ItemSerializer(data=request.data)
    if serializer.is_valid():
        item = serializer.save(list=lst, added_by=request.user)
        broadcast(list_id, {
            'event': 'item_added',
            'item': ItemSerializer(item).data
        })
        return Response(serializer.data, status=201)
    return Response(serializer.errors, status=400)

# PUT /items/:id/complete
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def complete_item(request, item_id):
    try:
        item = Item.objects.get(id=item_id)
    except Item.DoesNotExist:
        return Response({'error': 'Item not found'}, status=404)
    item.completed = True
    item.completed_by = request.user
    item.save()
    broadcast(item.list_id, {
        'event': 'item_completed',
        'item': ItemSerializer(item).data
    })
    return Response(ItemSerializer(item).data)

# DELETE /items/:id
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def complete_item(request, item_id):
    try:
        item = Item.objects.get(id=item_id)
    except Item.DoesNotExist:
        return Response({'error': 'Item not found'}, status=404)
    item.completed = True
    item.completed_by = request.user
    item.save()
    broadcast(item.list_id, {
        'event': 'item_completed',
        'item': ItemSerializer(item).data
    })
    return Response(ItemSerializer(item).data)

# POST /lists/:id/members
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_member(request, list_id):
    email = request.data.get('email')
    try:
        user = User.objects.get(email=email)
        lst = List.objects.get(id=list_id)
        ListMember.objects.get_or_create(list=lst, user=user)
        return Response({'message': 'Member added'})
    except User.DoesNotExist:
        return Response({'error': 'User not found'}, status=404)
    
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_item(request, item_id):
    try:
        item = Item.objects.get(id=item_id)
    except Item.DoesNotExist:
        return Response({'error': 'Item not found'}, status=404)

    list_id = item.list_id
    item.delete()

    return Response({'message': 'Item deleted'})