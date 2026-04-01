from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/lists/(?P<list_id>\d+)/$', consumers.ListConsumer.as_asgi()),
]