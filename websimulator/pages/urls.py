from django.urls import path

from .views import *

app_name = 'pages'
urlpatterns = [
    path('', IndexView.as_view(), name='index'),
    path('editor/', EditorView.as_view(), name='editor'),
    path('simulator/', SimulatorView.as_view(), name='simulator')
]
