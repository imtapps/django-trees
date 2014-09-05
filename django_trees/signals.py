

def pre_delete_node(sender, *args, **kwargs):
    instance = sender.objects.get(pk=kwargs.get('instance').pk)
    if not instance._deleting:
        instance.get_descendants().update(_deleting=True)
        sender.objects._renumber_source_tree_for_subtree_deletion(instance)


def pre_save_node(sender, *args, **kwargs):
    instance = kwargs.get('instance')
    if not instance.pk and instance.parent:
        parent = sender.objects.get(pk=instance.parent.pk)
        instance._depth = parent._depth + 1
        instance._left = parent._right
        instance._right = instance._left + 1
        sender.objects._renumber_source_tree_for_node_insertion(instance)
