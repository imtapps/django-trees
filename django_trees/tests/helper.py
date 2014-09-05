from django_trees.tests.test_app.models import Node


class NodeTestHelper(object):

    def refresh_node_instances(self):
        for node in Node.objects.all():
            setattr(self, 'n{}'.format(node.name), node)

    def create_node(self, name, parent=None):
        node = Node.objects.create(name=name, parent=parent)
        self.refresh_node_instances()
        return node
