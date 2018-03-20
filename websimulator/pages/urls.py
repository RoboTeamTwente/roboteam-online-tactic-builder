from django.urls import path, include

from .views import *

app_name = 'pages'
urlpatterns = [
    path('', IndexView.as_view(), name='index'),
    path('editor/', EditorView.as_view(), name='editor'),
    path('tree/', TreeView.as_view(), name='tree')
]
