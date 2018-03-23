from django.contrib import admin
from .models import Account, Tree

# Register your models here.
from .models import custom_node

admin.site.register(custom_node)
admin.site.register(Account)
admin.site.register(Tree)