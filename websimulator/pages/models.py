from django.db import models

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