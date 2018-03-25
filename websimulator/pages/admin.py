from django.contrib import admin
from .models import Account, Tree

# Register your models here.
from .models import CustomNode

admin.site.register(CustomNode)
admin.site.register(Account)
admin.site.register(Tree)