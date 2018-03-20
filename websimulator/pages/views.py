from django.http import HttpRequest
from django.shortcuts import render
from django.views import View


# Create your views here.


class IndexView(View):
    http_method_names = ['get']

    def get(self, request: HttpRequest):
        return render(request, "pages/interface.html", {})


class EditorView(View):
    http_method_names = ['get']

    def get(self, request: HttpRequest):
        return render(request, "b3js/editor.html", {})
