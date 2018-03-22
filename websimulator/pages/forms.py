from django.forms import ModelForm
from .models import Tree


class TreeForm(ModelForm):
    class Meta:
        model = Tree
        fields = ['name', 'tree']
