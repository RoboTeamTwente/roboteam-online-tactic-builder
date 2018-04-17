from django.urls import path
from django.conf.urls import url, include
from rest_framework import routers

from .views import *

app_name = 'pages'


urlpatterns = [
    path('custom_nodes/', CustomNodeViewSet.as_view({'get': 'list'}), name='custom_nodes'),
    path('', IndexView.as_view(), name='index'),
    path('editor/', EditorView.as_view(), name='editor'),
    path('simulator/', SimulatorView.as_view(), name='simulator'),
    path('tree/', TreeView.as_view(), name='tree'),
    path('guide/', GuideView.as_view(), name='guide'),
    path('available_trees/', AvailableTrees.as_view(), name='available_trees'),
]
