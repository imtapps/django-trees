from django_trees.models import AbstractNode
from django.db import models


class Node(AbstractNode):
    name = models.CharField(max_length=100)

    def __unicode__(self):
        return self.name

    @property
    def edges(self):
        return self._left, self._right

    @property
    def max_tree_depth(self):
        return Node.objects.filter(_tree_id=self._tree_id).order_by('-_depth')[0]._depth
