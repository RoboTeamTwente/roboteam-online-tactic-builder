import json

from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.views import View
from social_django.models import UserSocialAuth

from .forms import TreeForm
from .models import add_new_tree, Account, Tree


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


class TreeView(View):
    http_method_names = ['get', 'post']


    """
    Select a tree with the given name from the database
    """
    def get(self, request: HttpRequest):
        data = request.GET.get("name", None)
        if data is None:
            return HttpResponse(400)
        else:
            return HttpResponse(Account.objects.get(
                user=UserSocialAuth.objects.get(
                    user=request.user)).tree_set.get(name=data).tree,
                                content_type="application/json")


    """
    Saves a new tree for the user in the database
    Checks whether the user is valid and whether the tree is valid
    If a tree user combination already exists it overwrites the previous one
    """
    def post(self, request: HttpRequest):
        data = json.loads(request.body.decode("utf-8"))
        form = TreeForm(data)
        if form.is_valid() and UserSocialAuth.objects.filter( \
                user=request.user).exists():
            tree = Tree.objects.filter(account=Account.objects.get(
                user=UserSocialAuth.objects.get(user=request.user)),
                name=form.cleaned_data["name"])
            if tree.exists():
                tree = Tree.objects.get(account=Account.objects.get(
                user=UserSocialAuth.objects.get(user=request.user)),
                name=form.cleaned_data["name"])
                tree.tree = form.cleaned_data["tree"]
                tree.save()
            else:
                add_new_tree(form.cleaned_data["name"],
                             form.cleaned_data["tree"],
                             Account.objects.get(
                                 user=UserSocialAuth.objects.get(
                                     user=request.user)))
            return HttpResponse(200)
        else:
            return HttpResponse(400)
