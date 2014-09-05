from django import test
from textwrap import dedent
from django_trees.tests.test_app.models import Node


class GetASCIITreeTests(test.TestCase):

    def test_simple_get_ascii_tree(self):
        a = Node.objects.create(name='A')
        self.assertEqual("A", a.get_ascii_tree())

    def test_child(self):
        a = Node.objects.create(name='A')
        Node.objects.create(name='B', parent=a)
        self.assertTree("""
        A
         +-- B
        """, a)

    def test_two_children(self):
        a = Node.objects.create(name='A')
        Node.objects.create(name='B', parent=a)
        Node.objects.create(name='C', parent=a)
        self.assertTree("""
        A
         +-- B
         +-- C
        """, a)

    def test_two_children_with_first_one_having_children(self):
        a = Node.objects.create(name='A')
        b = Node.objects.create(name='B', parent=a)
        Node.objects.create(name='C', parent=a)
        Node.objects.create(name='D', parent=b)
        self.assertTree("""
        A
         +-- B
         |    +-- D
         +-- C
        """, a)

    def test_no_pipes_on_last_siblings(self):
        a = Node.objects.create(name='A')
        b = Node.objects.create(name='B', parent=a)
        c = Node.objects.create(name='C', parent=a)
        Node.objects.create(name='D', parent=b)
        Node.objects.create(name='E', parent=c)
        self.assertTree("""
        A
         +-- B
         |    +-- D
         +-- C
              +-- E
        """, a)

    def test_complex_tree(self):
        a = Node.objects.create(name='A')
        b = Node.objects.create(name='B', parent=a)
        c = Node.objects.create(name='C', parent=a)
        Node.objects.create(name='D', parent=b)
        Node.objects.create(name='E', parent=b)
        f = Node.objects.create(name='F', parent=c)
        Node.objects.create(name='G', parent=c)
        h = Node.objects.create(name='H', parent=f)
        Node.objects.create(name='I', parent=f)
        Node.objects.create(name='J', parent=h)
        k = Node.objects.create(name='K', parent=h)
        Node.objects.create(name='L', parent=h)
        Node.objects.create(name='M', parent=k)
        Node.objects.create(name='N', parent=k)
        Node.objects.create(name='O', parent=k)
        self.assertTree("""
        A
         +-- B
         |    +-- D
         |    +-- E
         +-- C
              +-- F
              |    +-- H
              |    |    +-- J
              |    |    +-- K
              |    |    |    +-- M
              |    |    |    +-- N
              |    |    |    +-- O
              |    |    +-- L
              |    +-- I
              +-- G
        """, a)

    def assertTree(self, tree, node):
        self.assertEqual(dedent(tree).strip(), node.get_ascii_tree())
