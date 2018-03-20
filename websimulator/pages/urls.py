from django.urls import path
from django.conf.urls import url, include
from rest_framework import routers
from .views import *

app_name = 'pages'

#router = routers.DefaultRouter()
#router.register(r'custom_nodes', CustomNodeViewSet)

urlpatterns = [
    path('custom_nodes/', CustomNodeViewSet.as_view({'get': 'list'}), name='custom_nodes'),
    path('', IndexView.as_view(), name='index'),
    path('editor/', EditorView.as_view(), name='editor')
]
