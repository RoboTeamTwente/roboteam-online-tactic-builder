from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.views import View
import json

from .models import Tree, add_new_tree, Account
from social_django.models import UserSocialAuth

# Create your views here.


class IndexView(View):
    http_method_names = ['get']

    def get(self, request: HttpRequest):
        return render(request, "pages/interface.html", {})


class EditorView(View):
    http_method_names = ['get']

    def get(self, request: HttpRequest):
        return render(request, "b3js/editor.html", {})


class TreeView(View):
    http_method_names = ['get','post']

    def post(self, request: HttpRequest):
        data = json.loads(request.body.decode("utf-8"))
        if UserSocialAuth.objects.filter(user=request.user).exists():
            add_new_tree(data["name"], data["tree"], Account.objects.get(
                user=UserSocialAuth.objects.get(
                user=request.user)))

        return HttpResponse(200)

