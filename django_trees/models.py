from django.db import models
from django_trees.managers import NodeManager
from django_trees.exceptions import UnsupportedAction


class AbstractNode(models.Model):
    _parent = models.ForeignKey('self', null=True, blank=True)
    _left = models.IntegerField(default=1, db_index=True)
    _right = models.IntegerField(default=2, db_index=True)
    _depth = models.IntegerField(default=0, db_index=True)
    _deleting = models.BooleanField(default=False)
    objects = NodeManager()

    class Meta(object):
        abstract = True

    def get_ascii_tree(self):
        return '\n'.join(self._tree_lines())

    def _tree_lines(self):
        yield str(self)
        children = list(self.get_children())
        last = children[-1] if children else None
        for child in children:
            prefix = ' +-- '
            for line in child._tree_lines():
                yield prefix + line
                prefix = '     ' if child is last else ' |   '

    def move(self, new_parent):
        type(self).objects._move_node(self, new_parent)

    def bifurcate(self):
        type(self).objects._bifurcate(self)

    def get_children(self):
        return type(self).objects.filter(_parent=self)

    def get_ancestors(self):
        current_node = type(self).objects.get(pk=self.pk)
        return type(self).objects.filter(
            _left__lt=current_node._left, _right__gt=current_node._right,
            _tree_id=current_node._tree_id).order_by('_right')

    def get_descendants(self):
        current_node = type(self).objects.get(pk=self.pk)
        return type(self).objects.filter(
            _left__gt=current_node._left, _right__lt=current_node._right,
            _tree_id=current_node._tree_id).order_by('_left')

    @property
    def parent(self):
        return self._parent

    @parent.setter
    def parent(self, parent):
        if self.pk:
            raise UnsupportedAction("You must use `move` to assign a new parent to an existing node.")
        self._parent = parent
        self._depth = parent._depth + 1
        self._tree_id = parent._tree_id
