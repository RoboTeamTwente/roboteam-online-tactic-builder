from django.db import models
from social_django.models import UserSocialAuth


class Account(models.Model):
    user = models.OneToOneField(UserSocialAuth,on_delete=models.CASCADE)


class Tree(models.Model):
    # name = models.CharField(max_length=50)
    tree = models.TextField()
    account = models.ForeignKey(Account,on_delete=models.CASCADE)


def add_user_model(social, is_new, *args, **kwargs):
    if is_new:
        Account.objects.create(user=social)


def add_new_tree(tree, account):
    Tree.objects.create(tree=tree, account=account)