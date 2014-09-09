from django.test import TestCase
from django_trees.tests.test_app.models import Node
from django_trees.tests.helper import NodeTestHelper
from django_trees.exceptions import InvalidNodeMove, UnsupportedAction


class BranchedTreeTests(TestCase, NodeTestHelper):

    def setUp(self):
        self.nA = self.create_node('A')
        self.nB = self.create_node('B', self.nA)
        self.nC = self.create_node('C', self.nA)
        self.nD = self.create_node('D', self.nC)

    def test_children_returns_immediate_descendants(self):
        self.assertEqual(list(self.nA.get_children()), [self.nB, self.nC])
        self.assertEqual(list(self.nB.get_children()), [])
        self.assertEqual(list(self.nC.get_children()), [self.nD])
        self.assertEqual(list(self.nD.get_children()), [])

    def test_add_child_to_recently_moved_parent(self):
        self.nD.move(self.nA)
        self.nE = Node.objects.create(name='E', parent=self.nD)
        self.refresh_node_instances()
        self.assertEqual((1, 10), self.nA.edges)
        self.assertEqual((6, 7), self.nB.edges)
        self.assertEqual((8, 9), self.nC.edges)
        self.assertEqual((2, 5), self.nD.edges)
        self.assertEqual((3, 4), self.nE.edges)

    def test_move_child_to_parent_with_new_depth(self):
        self.nB.move(self.nC)
        self.nD.move(self.nB)
        self.refresh_node_instances()
        self.assertEqual(0, self.nA._depth)
        self.assertEqual(1, self.nC._depth)
        self.assertEqual(2, self.nB._depth)
        self.assertEqual(3, self.nD._depth)
        self.assertEqual((1, 8), self.nA.edges)
        self.assertEqual((2, 7), self.nC.edges)
        self.assertEqual((3, 6), self.nB.edges)
        self.assertEqual((4, 5), self.nD.edges)

    def test_assign_new_parent_to_existing_node_after_parent_moved(self):
        self.nB.move(self.nC)
        self.nE = Node.objects.create(name='E')
        with self.assertRaises(UnsupportedAction) as c:
            self.nE.parent = self.nB

        self.assertEqual("You must use `move` to assign a new parent to an existing node.", str(c.exception))

    def test_move_node_multiple_times(self):
        self.nD.move(self.nB)
        self.nD.move(self.nA)
        self.refresh_node_instances()
        self.assertEqual((1, 8), self.nA.edges)
        self.assertEqual((4, 5), self.nB.edges)
        self.assertEqual((6, 7), self.nC.edges)
        self.assertEqual((2, 3), self.nD.edges)

    def test_cannot_move_node_to_child_after_initial_move(self):
        self.nC.move(self.nB)
        with self.assertRaises(InvalidNodeMove):
            self.nC.move(self.nD)

    def test_get_ancestors_does_not_return_node_siblings(self):
        self.assertEqual(list(self.nA.get_ancestors()), [])
        self.assertEqual(list(self.nB.get_ancestors()), [self.nA])
        self.assertEqual(list(self.nC.get_ancestors()), [self.nA])
        self.assertEqual(list(self.nD.get_ancestors()), [self.nC, self.nA])

    def test_get_descendants_does_not_return_node_siblings(self):
        self.assertEqual(list(self.nA.get_descendants()), [self.nB, self.nC, self.nD])
        self.assertEqual(list(self.nB.get_descendants()), [])
        self.assertEqual(list(self.nC.get_descendants()), [self.nD])
        self.assertEqual(list(self.nD.get_descendants()), [])

    def test_max_tree_depth_returns_deepest_level_of_tree_on_arbitary_nodes(self):
        self.assertEqual(self.nA.max_tree_depth, 2)
        self.assertEqual(self.nB.max_tree_depth, 2)
        self.assertEqual(self.nC.max_tree_depth, 2)
        self.assertEqual(self.nD.max_tree_depth, 2)

    def test_move_node_parent_to_current_parent(self):
        self.nC.move(self.nA)
        self.assertEqual(list(self.nA.get_ancestors()), [])
        self.assertEqual(list(self.nB.get_ancestors()), [self.nA])
        self.assertEqual(list(self.nC.get_ancestors()), [self.nA])
        self.assertEqual(list(self.nD.get_ancestors()), [self.nC, self.nA])
        self.assertEqual(list(self.nA.get_descendants()), [self.nC, self.nD, self.nB])
        self.assertEqual(list(self.nB.get_descendants()), [])
        self.assertEqual(list(self.nC.get_descendants()), [self.nD])
        self.assertEqual(list(self.nD.get_descendants()), [])
        self.assertEqual(self.nA.max_tree_depth, 2)
        self.assertEqual(self.nB.max_tree_depth, 2)
        self.assertEqual(self.nC.max_tree_depth, 2)
        self.assertEqual(self.nD.max_tree_depth, 2)
        self.refresh_node_instances()
        self.assertEqual((1, 8), self.nA.edges)
        self.assertEqual((2, 5), self.nC.edges)
        self.assertEqual((3, 4), self.nD.edges)
        self.assertEqual((6, 7), self.nB.edges)


class SiblingNodeTests(TestCase, NodeTestHelper):

    def setUp(self):
        self.nA = self.create_node('A')
        self.nB = self.create_node('B', self.nA)
        self.nC = self.create_node('C', self.nA)

    def test_adding_a_single_sibling_creates_nodes_with_correct_attributes(self):
        self.assertEqual((1, 6), self.nA.edges)
        self.assertEqual((2, 3), self.nB.edges)
        self.assertEqual((4, 5), self.nC.edges)

    def test_adding_mutiple_siblings_creates_nodes_with_correct_attributes(self):
        self.nD = self.create_node("D", self.nA)
        self.assertEqual((1, 8), self.nA.edges)
        self.assertEqual((2, 3), self.nB.edges)
        self.assertEqual((4, 5), self.nC.edges)
        self.assertEqual((6, 7), self.nD.edges)

    def test_moving_node(self):
        self.nC.move(self.nB)
        self.refresh_node_instances()
        self.assertEqual((1, 6), self.nA.edges)
        self.assertEqual((2, 5), self.nB.edges)
        self.assertEqual((3, 4), self.nC.edges)


class ComplexTests(TestCase, NodeTestHelper):
    """
     #A# = Left - Node - Right
               1A30
              /    \
           2B7      8C29
          /   \       | \
        3D4   5E6  9F26  27G28
                  /    \
               10H23   24I25
              /  |  \
         11J12 13K20 21L22
              /  |  \
         14M15 16N17 18O19
    """

    def setUp(self):
        self.nA = self.create_node('A')
        self.nB = self.create_node('B', self.nA)
        self.nC = self.create_node('C', self.nA)
        self.nD = self.create_node('D', self.nB)
        self.nE = self.create_node('E', self.nB)
        self.nF = self.create_node('F', self.nC)
        self.nG = self.create_node('G', self.nC)
        self.nH = self.create_node('H', self.nF)
        self.nI = self.create_node('I', self.nF)
        self.nJ = self.create_node('J', self.nH)
        self.nK = self.create_node('K', self.nH)
        self.nL = self.create_node('L', self.nH)
        self.nM = self.create_node('M', self.nK)
        self.nN = self.create_node('N', self.nK)
        self.nO = self.create_node('O', self.nK)

    def test_deeply_branched_tree(self):
        self.assertEqual(list(self.nA.get_ancestors()), [])
        self.assertEqual(list(self.nB.get_ancestors()), [self.nA])
        self.assertEqual(list(self.nC.get_ancestors()), [self.nA])
        self.assertEqual(list(self.nD.get_ancestors()), [self.nB, self.nA])
        self.assertEqual(list(self.nE.get_ancestors()), [self.nB, self.nA])
        self.assertEqual(list(self.nF.get_ancestors()), [self.nC, self.nA])
        self.assertEqual(list(self.nG.get_ancestors()), [self.nC, self.nA])
        self.assertEqual(list(self.nH.get_ancestors()), [self.nF, self.nC, self.nA])
        self.assertEqual(list(self.nI.get_ancestors()), [self.nF, self.nC, self.nA])
        self.assertEqual(list(self.nJ.get_ancestors()), [self.nH, self.nF, self.nC, self.nA])
        self.assertEqual(list(self.nK.get_ancestors()), [self.nH, self.nF, self.nC, self.nA])
        self.assertEqual(list(self.nL.get_ancestors()), [self.nH, self.nF, self.nC, self.nA])
        self.assertEqual(list(self.nM.get_ancestors()), [self.nK, self.nH, self.nF, self.nC, self.nA])
        self.assertEqual(list(self.nN.get_ancestors()), [self.nK, self.nH, self.nF, self.nC, self.nA])
        self.assertEqual(list(self.nO.get_ancestors()), [self.nK, self.nH, self.nF, self.nC, self.nA])
        self.assertEqual(list(self.nA.get_descendants()), [
            self.nB, self.nD, self.nE, self.nC, self.nF, self.nH, self.nJ,
            self.nK, self.nM, self.nN, self.nO, self.nL, self.nI, self.nG])
        self.assertEqual(list(self.nB.get_descendants()), [self.nD, self.nE])
        self.assertEqual(list(self.nC.get_descendants()), [
            self.nF, self.nH, self.nJ, self.nK, self.nM, self.nN, self.nO, self.nL, self.nI, self.nG])
        self.assertEqual(list(self.nD.get_descendants()), [])
        self.assertEqual(list(self.nE.get_descendants()), [])
        self.assertEqual(list(self.nF.get_descendants()), [
            self.nH, self.nJ, self.nK, self.nM, self.nN, self.nO, self.nL, self.nI])
        self.assertEqual(list(self.nG.get_descendants()), [])
        self.assertEqual(list(self.nH.get_descendants()), [self.nJ, self.nK, self.nM, self.nN, self.nO, self.nL])
        self.assertEqual(list(self.nI.get_descendants()), [])
        self.assertEqual(list(self.nJ.get_descendants()), [])
        self.assertEqual(list(self.nK.get_descendants()), [self.nM, self.nN, self.nO])
        self.assertEqual(list(self.nL.get_descendants()), [])
        self.assertEqual(list(self.nM.get_descendants()), [])
        self.assertEqual(list(self.nN.get_descendants()), [])
        self.assertEqual(list(self.nO.get_descendants()), [])

    def test_delete_subtree_on_left_side(self):
        self.nB.delete()
        self.refresh_node_instances()
        self.assertEqual((1, 24), self.nA.edges)
        self.assertEqual((2, 23), self.nC.edges)
        self.assertEqual((3, 20), self.nF.edges)
        self.assertEqual((21, 22), self.nG.edges)
        self.assertEqual((4, 17), self.nH.edges)
        self.assertEqual((18, 19), self.nI.edges)
        self.assertEqual((5, 6), self.nJ.edges)
        self.assertEqual((7, 14), self.nK.edges)
        self.assertEqual((15, 16), self.nL.edges)
        self.assertEqual((8, 9), self.nM.edges)
        self.assertEqual((10, 11), self.nN.edges)
        self.assertEqual((12, 13), self.nO.edges)

    def test_delete_subtree_on_right_side(self):
        self.nH.delete()
        self.refresh_node_instances()
        self.assertEqual((1, 16), self.nA.edges)
        self.assertEqual((2, 7), self.nB.edges)
        self.assertEqual((3, 4), self.nD.edges)
        self.assertEqual((5, 6), self.nE.edges)
        self.assertEqual((8, 15), self.nC.edges)
        self.assertEqual((9, 12), self.nF.edges)
        self.assertEqual((13, 14), self.nG.edges)
        self.assertEqual((10, 11), self.nI.edges)

    def test_move_subtree_left(self):
        """
        Expected Result
         #A# = Left - Node - Right
                           1A30
                          /    \
                       2B15     16C29
                      /   \       |  \
                   3D12  13E14  17F26 27G28
                   /           /    \
               4K11          18H23 24I25
              / |  \        /    \
           5M6 7N8 9O10  19J20  21L22
        """
        self.nK.move(self.nD)
        self.assertEqual(list(self.nD.get_descendants()), [self.nK, self.nM, self.nN, self.nO])
        self.assertEqual(list(self.nH.get_descendants()), [self.nJ, self.nL])
        self.assertEqual(list(self.nK.get_ancestors()), [self.nD, self.nB, self.nA])
        self.assertEqual(list(self.nM.get_ancestors()), [self.nK, self.nD, self.nB, self.nA])
        self.assertEqual(list(self.nN.get_ancestors()), [self.nK, self.nD, self.nB, self.nA])
        self.assertEqual(list(self.nO.get_ancestors()), [self.nK, self.nD, self.nB, self.nA])
        self.refresh_node_instances()
        self.assertEqual((1, 30), self.nA.edges)
        self.assertEqual((2, 15), self.nB.edges)
        self.assertEqual((3, 12), self.nD.edges)
        self.assertEqual((13, 14), self.nE.edges)
        self.assertEqual((16, 29), self.nC.edges)
        self.assertEqual((17, 26), self.nF.edges)
        self.assertEqual((27, 28), self.nG.edges)
        self.assertEqual((24, 25), self.nI.edges)
        self.assertEqual((18, 23), self.nH.edges)
        self.assertEqual((4, 11), self.nK.edges)
        self.assertEqual((5, 6), self.nM.edges)
        self.assertEqual((7, 8), self.nN.edges)
        self.assertEqual((9, 10), self.nO.edges)
        self.assertEqual((19, 20), self.nJ.edges)
        self.assertEqual((21, 22), self.nL.edges)
        self.assertEqual(15, Node.objects.filter(_tree_id=self.nA._tree_id).count())
        self.assertEqual(3, self.nK._depth)
        self.assertEqual(4, self.nM._depth)
        self.assertEqual(4, self.nN._depth)
        self.assertEqual(4, self.nO._depth)

    def test_move_subtree_from_deep_to_shallow(self):
        """
         #A# = Left - Node - Right
                              1A30
                         ____/ |  \
                        /    20B25 26C29
                       /     /   \     \
                      /   21D22 23E24   27G28
                     |
                    2F19
                   /    \
               3H16      17I18
              /  |  \
           4J5  6K13 14L15
              /  |  \
           7M8 9N10 11O12
        """
        self.nF.move(self.nA)
        self.refresh_node_instances()
        self.assertEqual((1, 30), self.nA.edges)
        self.assertEqual((2, 19), self.nF.edges)
        self.assertEqual((3, 16), self.nH.edges)
        self.assertEqual((4, 5), self.nJ.edges)
        self.assertEqual((7, 8), self.nM.edges)
        self.assertEqual((9, 10), self.nN.edges)
        self.assertEqual((11, 12), self.nO.edges)
        self.assertEqual((6, 13), self.nK.edges)
        self.assertEqual((14, 15), self.nL.edges)
        self.assertEqual((17, 18), self.nI.edges)
        self.assertEqual((20, 25), self.nB.edges)
        self.assertEqual((26, 29), self.nC.edges)
        self.assertEqual((21, 22), self.nD.edges)
        self.assertEqual((27, 28), self.nG.edges)
        self.assertEqual((23, 24), self.nE.edges)
        self.assertEqual(1, self.nF._depth)
        self.assertEqual(2, self.nH._depth)
        self.assertEqual(2, self.nI._depth)
        self.assertEqual(3, self.nJ._depth)
        self.assertEqual(3, self.nK._depth)
        self.assertEqual(3, self.nL._depth)
        self.assertEqual(4, self.nM._depth)
        self.assertEqual(4, self.nN._depth)
        self.assertEqual(4, self.nO._depth)
        self.assertEqual(15, Node.objects.filter(_tree_id=self.nA._tree_id).count())

    def test_move_subtree_right(self):
        """
         #A# = Left - Node - Right
                   1A30
                  /    \
               2B7      8C29
              /   \     /   \
            3D4   5E6 9F18   19G28
                      /   \       \
                 10H15   16I17   20K27
                /     \         /  |  \
             11J12  13L14  21M22 23N24 25O26
        """
        self.nK.move(self.nG)
        self.assertEqual(list(self.nO.get_ancestors()), [self.nK, self.nG, self.nC, self.nA])
        self.assertEqual(list(self.nA.get_descendants()), [
            self.nB, self.nD, self.nE, self.nC, self.nF, self.nH, self.nJ,
            self.nL, self.nI, self.nG, self.nK, self.nM, self.nN, self.nO])
        self.refresh_node_instances()
        self.assertEqual((1, 30), self.nA.edges)
        self.assertEqual((2, 7), self.nB.edges)
        self.assertEqual((3, 4), self.nD.edges)
        self.assertEqual((5, 6), self.nE.edges)
        self.assertEqual((8, 29), self.nC.edges)
        self.assertEqual((9, 18), self.nF.edges)
        self.assertEqual((19, 28), self.nG.edges)
        self.assertEqual((16, 17), self.nI.edges)
        self.assertEqual((10, 15), self.nH.edges)
        self.assertEqual((20, 27), self.nK.edges)
        self.assertEqual((21, 22), self.nM.edges)
        self.assertEqual((23, 24), self.nN.edges)
        self.assertEqual((25, 26), self.nO.edges)
        self.assertEqual((11, 12), self.nJ.edges)
        self.assertEqual((13, 14), self.nL.edges)

    def test_move_subtree_from_shallow_to_deep(self):
        """
         #A# = Left - Node - Right
                   1A30
                       \
                        2C29
                          | \
                       3F26  27G28
                      /    \
                    4H23   24I25
                  /  |  \
               5J6  7K20 21L22
                  /  |  \
               8M9 10N11 12O19
                             \
                             13B18
                            /   \
                          14D15  16E17
        """
        self.nB.move(self.nO)
        self.assertEqual(list(self.nE.get_ancestors()), [self.nB, self.nO, self.nK, self.nH, self.nF, self.nC, self.nA])
        self.assertEqual(list(self.nM.get_ancestors()), [self.nK, self.nH, self.nF, self.nC, self.nA])
        self.assertEqual(list(self.nI.get_ancestors()), [self.nF, self.nC, self.nA])
        self.assertEqual(list(self.nA.get_descendants()), [
            self.nC, self.nF, self.nH, self.nJ, self.nK, self.nM, self.nN,
            self.nO, self.nB, self.nD, self.nE, self.nL, self.nI, self.nG])
        self.assertEqual(list(self.nO.get_descendants()), [self.nB, self.nD, self.nE])
        self.assertEqual(list(self.nB.get_descendants()), [self.nD, self.nE])
        self.assertEqual(15, Node.objects.filter(_tree_id=self.nA._tree_id).count())
        self.refresh_node_instances()
        self.assertEqual((1, 30), self.nA.edges)
        self.assertEqual((13, 18), self.nB.edges)
        self.assertEqual((14, 15), self.nD.edges)
        self.assertEqual((16, 17), self.nE.edges)
        self.assertEqual((2, 29), self.nC.edges)
        self.assertEqual((3, 26), self.nF.edges)
        self.assertEqual((27, 28), self.nG.edges)
        self.assertEqual((24, 25), self.nI.edges)
        self.assertEqual((4, 23), self.nH.edges)
        self.assertEqual((7, 20), self.nK.edges)
        self.assertEqual((8, 9), self.nM.edges)
        self.assertEqual((10, 11), self.nN.edges)
        self.assertEqual((12, 19), self.nO.edges)
        self.assertEqual((5, 6), self.nJ.edges)
        self.assertEqual((21, 22), self.nL.edges)
        self.assertEqual(0, self.nA._depth)
        self.assertEqual(1, self.nC._depth)
        self.assertTrue(2 == self.nF._depth == self.nG._depth)
        self.assertTrue(3 == self.nH._depth == self.nI._depth)
        self.assertTrue(4 == self.nJ._depth == self.nK._depth == self.nL._depth)
        self.assertTrue(5 == self.nM._depth == self.nN._depth == self.nO._depth)
        self.assertTrue(6 == self.nB._depth)
        self.assertTrue(7 == self.nD._depth == self.nE._depth)

    def test_moving_subtree_to_deep_node_with_existing_child_nodes(self):
        """
         #A# = Left - Node - Right
                  01A30
                       \
                       02C29
                          | \
                      03F26  27G28
                      /    \
                   04H23   24I25
                __/  |  \__
               /     |     \
          05J06    --07K20  21L22
             _____/ /  |  \
            /      /   |   \
           /   14M15 16N17 18O19
         08B13
         /   \
      09D10 11E12
        """
        self.nB.move(self.nK)
        self.assertEqual(list(self.nA.get_descendants()), [
            self.nC, self.nF, self.nH, self.nJ, self.nK, self.nB, self.nD,
            self.nE, self.nM, self.nN, self.nO, self.nL, self.nI, self.nG])
        self.assertEqual(list(self.nK.get_descendants()), [self.nB, self.nD, self.nE, self.nM, self.nN, self.nO])
        self.assertEqual(list(self.nB.get_descendants()), [self.nD, self.nE])
        self.assertEqual(list(self.nD.get_ancestors()), [self.nB, self.nK, self.nH, self.nF, self.nC, self.nA])
        self.assertEqual(15, Node.objects.filter(_tree_id=self.nA._tree_id).count())
        self.refresh_node_instances()
        self.assertEqual((1, 30), self.nA.edges)
        self.assertEqual((2, 29), self.nC.edges)
        self.assertEqual((3, 26), self.nF.edges)
        self.assertEqual((4, 23), self.nH.edges)
        self.assertEqual((5, 6), self.nJ.edges)
        self.assertEqual((7, 20), self.nK.edges)
        self.assertEqual((8, 13), self.nB.edges)
        self.assertEqual((9, 10), self.nD.edges)
        self.assertEqual((11, 12), self.nE.edges)
        self.assertEqual((14, 15), self.nM.edges)
        self.assertEqual((16, 17), self.nN.edges)
        self.assertEqual((18, 19), self.nO.edges)
        self.assertEqual((21, 22), self.nL.edges)
        self.assertEqual((24, 25), self.nI.edges)
        self.assertEqual((27, 28), self.nG.edges)
        self.assertEqual(0, self.nA._depth)
        self.assertEqual(1, self.nC._depth)
        self.assertTrue(2 == self.nF._depth == self.nG._depth)
        self.assertTrue(3 == self.nH._depth == self.nI._depth)
        self.assertTrue(4 == self.nJ._depth == self.nK._depth == self.nL._depth)
        self.assertTrue(5 == self.nB._depth == self.nM._depth == self.nN._depth == self.nO._depth)
        self.assertTrue(6 == self.nD._depth == self.nE._depth)

    def test_move_node_to_an_independent_tree(self):
        """
        #A# = Left - Node - Right
             01A24                     1B6
                  \                   /   \
                  02C23             2D3   4E5
                     | \
                 03F20  21G22
                 /    \
              04H17   18I19
             /  |  \
        05J06 07K14 15L16
             /  |  \
        08M09 10N11 12O13
        """
        self.nB.bifurcate()
        self.assertTrue(list(self.nA.get_descendants()), [
            self.nC, self.nF, self.nG, self.nH, self.nI, self.nJ, self.nK, self.nL, self.nM, self.nN, self.nO])
        self.assertTrue(list(self.nB.get_descendants()), [self.nD, self.nE])
        self.assertTrue(list(self.nE.get_ancestors()), [self.nA])
        self.assertTrue(list(self.nN.get_ancestors()), [self.nK, self.nH, self.nF, self.nC, self.nA])
        self.refresh_node_instances()
        self.assertEqual(12, Node.objects.filter(_tree_id=self.nA._tree_id).count())
        self.assertEqual(3, Node.objects.filter(_tree_id=self.nB._tree_id).count())
        self.assertEqual((1, 24), self.nA.edges)
        self.assertEqual((2, 23), self.nC.edges)
        self.assertEqual((3, 20), self.nF.edges)
        self.assertEqual((21, 22), self.nG.edges)
        self.assertEqual((4, 17), self.nH.edges)
        self.assertEqual((18, 19), self.nI.edges)
        self.assertEqual((5, 6), self.nJ.edges)
        self.assertEqual((7, 14), self.nK.edges)
        self.assertEqual((15, 16), self.nL.edges)
        self.assertEqual((8, 9), self.nM.edges)
        self.assertEqual((10, 11), self.nN.edges)
        self.assertEqual((12, 13), self.nO.edges)
        self.assertEqual((1, 6), self.nB.edges)
        self.assertEqual((2, 3), self.nD.edges)
        self.assertEqual((4, 5), self.nE.edges)
        self.assertEqual(0, self.nB._depth)
        self.assertTrue(1 == self.nD._depth == self.nE._depth)
        self.assertEqual(0, self.nA._depth)
        self.assertEqual(1, self.nC._depth)
        self.assertTrue(2 == self.nF._depth == self.nG._depth)
        self.assertTrue(3 == self.nH._depth == self.nI._depth)
        self.assertTrue(4 == self.nJ._depth == self.nK._depth == self.nL._depth)
        self.assertTrue(5 == self.nM._depth == self.nN._depth == self.nO._depth)
        self.assertEqual(None, self.nB.parent)
