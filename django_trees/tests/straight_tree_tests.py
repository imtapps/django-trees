from django.test import TestCase
from django_trees.tests.test_app.models import Node
from django_trees.exceptions import InvalidNodeMove
from django_trees.tests.helper import NodeTestHelper


class StraightTreeTests(TestCase, NodeTestHelper):

    def setUp(self):
        self.nA = self.create_node("A")
        self.nB = self.create_node("B", self.nA)
        self.nC = self.create_node("C", self.nB)
        self.nD = self.create_node("D", self.nC)
        self.nE = self.create_node("E", self.nD)

    def test_can_get_node_ancestors(self):
        self.assertEqual(list(self.nA.get_ancestors()), [])
        self.assertEqual(list(self.nB.get_ancestors()), [self.nA])
        self.assertEqual(list(self.nC.get_ancestors()), [self.nB, self.nA])
        self.assertEqual(list(self.nD.get_ancestors()), [self.nC, self.nB, self.nA])
        self.assertEqual(list(self.nE.get_ancestors()), [self.nD, self.nC, self.nB, self.nA])

    def test_can_get_node_descendants(self):
        self.assertEqual(list(self.nA.get_descendants()), [self.nB, self.nC, self.nD, self.nE])
        self.assertEqual(list(self.nB.get_descendants()), [self.nC, self.nD, self.nE])
        self.assertEqual(list(self.nC.get_descendants()), [self.nD, self.nE])
        self.assertEqual(list(self.nD.get_descendants()), [self.nE])
        self.assertEqual(list(self.nE.get_descendants()), [])

    def test_newly_added_nodes_receive_correct_attributes(self):
        self.assertEqual((1, 10), self.nA.edges)
        self.assertEqual((2, 9), self.nB.edges)
        self.assertEqual((3, 8), self.nC.edges)
        self.assertEqual((4, 7), self.nD.edges)
        self.assertEqual((5, 6), self.nE.edges)
        self.assertEqual(self.nA._depth, 0)
        self.assertEqual(self.nB._depth, 1)
        self.assertEqual(self.nC._depth, 2)
        self.assertEqual(self.nD._depth, 3)
        self.assertEqual(self.nE._depth, 4)

    def test_removing_node_will_reset_tree_attributes(self):
        Node.objects.get(pk=self.nD.pk).delete()
        self.refresh_node_instances()
        self.assertEqual((1, 6), self.nA.edges)
        self.assertEqual((2, 5), self.nB.edges)
        self.assertEqual((3, 4), self.nC.edges)
        self.assertEqual(0, Node.objects.filter(pk=self.nE.pk).count())

    def test_cannot_move_parent_to_one_of_its_children(self):
        with self.assertRaises(InvalidNodeMove):
            self.nB.move(self.nD)

    def test_cannot_move_parent_to_itself(self):
        with self.assertRaises(InvalidNodeMove):
            self.nB.move(self.nB)
