from django.db.models.signals import pre_save, pre_delete
from django_trees.exceptions import InvalidNodeMove
from django.db.models import Max
from django_trees import signals
from django.db import models


class NodeManager(models.Manager):

    def get_next_tree_id(self):
        return (self.all().aggregate(Max('_tree_id')).get('_tree_id__max', 0) or 0) + 1

    def _move_node(self, node, new_parent):
        original_tree_id = node._tree_id
        node = self.get(pk=node.pk)
        if new_parent in list(node.get_descendants()) + [node]:
            raise InvalidNodeMove()
        self._detach_subtree(node)
        node = self.get(pk=node.pk)
        self._renumber_source_tree_edges(original_tree_id, node)
        self._renumber_detached_tree_edges(new_parent, node)
        if new_parent:
            self._renumber_source_tree_for_subtree_insertion(new_parent, node)
            self._attach_subtree(new_parent, node)

    def _bifurcate(self, node_to_sever):
        self._move_node(node_to_sever, None)
        node = self.get(pk=node_to_sever.pk)
        self.filter(_tree_id=node._tree_id).update(_depth=models.F('_depth') - node_to_sever._depth)

    def _renumber_source_tree_for_node_insertion(self, node):
        self.filter(_left__gt=node._left, _tree_id=node._tree_id).update(_left=models.F('_left') + 2)
        self.filter(_right__gte=node._left, _tree_id=node._tree_id).update(_right=models.F('_right') + 2)

    def _renumber_source_tree_edges(self, tree_id, node):
        delta = (len(self.get(pk=node.pk).get_descendants()) + 1) * -2
        self._update_edges(
            delta,
            self.filter(_tree_id=tree_id, _left__gt=node._left),
            self.filter(_tree_id=tree_id, _right__gt=node._left))

    def _renumber_detached_tree_edges(self, parent, node):
        left = self.get(pk=parent.pk)._left if parent else 0
        delta = (left + 1) - node._left
        self._update_edges(
            delta,
            self.filter(_tree_id=node._tree_id, _left__gte=node._left),
            self.filter(_tree_id=node._tree_id, _right__gt=node._left))

    def _renumber_source_tree_for_subtree_insertion(self, parent, node):
        delta = (len(self.get(pk=node.pk).get_descendants()) + 1) * 2
        parent = self.get(pk=parent.pk)
        self._update_edges(
            delta,
            self.filter(_tree_id=parent._tree_id, _left__gt=parent._left),
            self.filter(_tree_id=parent._tree_id, _right__gte=parent._left))

    def _renumber_source_tree_for_subtree_deletion(self, node):
        delta = (len(node.get_descendants()) + 1) * -2
        self._update_edges(
            delta,
            self.filter(_tree_id=node._tree_id, _left__gte=node._right),
            self.filter(_tree_id=node._tree_id, _right__gte=node._right))

    def _attach_subtree(self, parent, node):
        parent = self.get(pk=parent.pk)
        delta = parent._depth + 1 - node._depth
        self.filter(_tree_id=node._tree_id).update(_tree_id=parent._tree_id, _depth=models.F('_depth') + delta)
        f = self.get(pk=node.pk)
        f._parent = parent
        f._depth = parent._depth + 1
        f._tree_id = parent._tree_id
        f.save()

    def _detach_subtree(self, node):
        return self.filter(
            _tree_id=node._tree_id,
            _left__gte=node._left,
            _right__lte=node._right
        ).update(_tree_id=self.get_next_tree_id())

    def _update_edges(self, delta, left, right):
        left.update(_left=models.F("_left") + delta)
        right.update(_right=models.F("_right") + delta)

    def contribute_to_class(self, model, name):
        super(NodeManager, self).contribute_to_class(model, name)
        if not model._meta.abstract:
            tree_id_field = models.IntegerField(default=self.get_next_tree_id)
            tree_id_field.contribute_to_class(model, "_tree_id")

        pre_save.connect(signals.pre_save_node, model)
        pre_delete.connect(signals.pre_delete_node, model)
