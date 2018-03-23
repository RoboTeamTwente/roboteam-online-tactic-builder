import json

from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.views import View
from social_django.models import UserSocialAuth
from rest_framework import viewsets
from .serializers import CustomNodeSerializer

from .forms import TreeForm
from .models import add_new_tree, Account, Tree, custom_node


# Create your views here.


class IndexView(View):
    http_method_names = ['get']

    def get(self, request: HttpRequest):
        context = {"trees": []}

        if request.user.is_authenticated and UserSocialAuth.objects.filter( \
                user=request.user).exists():
            context["trees"] = Account.objects.get(
                user=UserSocialAuth.objects.get(
                    user=request.user)).tree_set.all()
        return render(request, "pages/interface.html", context)


class EditorView(View):
    http_method_names = ['get']

    def get(self, request: HttpRequest):
        return render(request, "b3js/editor.html", {})


class CustomNodeViewSet(viewsets.ModelViewSet):
    queryset = custom_node.objects.all()
    serializer_class = CustomNodeSerializer