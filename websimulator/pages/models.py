from django.db import models
from social_django.models import UserSocialAuth

NODE_TYPE_CHOICES = (
    ('0', 'Composite'),
    ('1', 'Decorator'),
    ('2', 'Condition'),
    ('3', 'Action'),
)

class custom_node(models.Model):
    name = models.CharField(max_length=30)
    type = models.CharField(max_length=1, choices=NODE_TYPE_CHOICES)

    def __str__(self):
        return self.get_type_display() + " " + self.name
        
        
class Account(models.Model):
    user = models.OneToOneField(UserSocialAuth,on_delete=models.CASCADE)


class Tree(models.Model):
    name = models.CharField(max_length=50, default="", blank=True)
    tree = models.TextField()
    account = models.ForeignKey(Account,on_delete=models.CASCADE)

    def __str__(self):
        return self.name


def add_user_model(social, is_new, *args, **kwargs):
    if is_new:
        Account.objects.create(user=social)


def add_new_tree(name, tree, account):
    Tree.objects.create(name=name, tree=tree, account=account)