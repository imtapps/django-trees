from collections import defaultdict
from pprint import pprint
from django import test
from django_trees.tests.test_app.models import Node


class JsonTests(test.TestCase):

    def setUp(self):
        self.a = Node.objects.create(name='a')
        self.b = Node.objects.create(name='b', parent=self.a)
        self.c = Node.objects.create(name='c', parent=self.a)
        Node.objects.create(name='d', parent=self.c)
        Node.objects.create(name='e', parent=self.b)

        self.documents = [
            {'name': 'doc1', 'id': 1},
            {'name': 'doc2', 'id': 2, 'folder': self.a.pk},
            {'name': 'doc3', 'id': 3, 'folder': self.a.pk},
            {'name': 'doc4', 'id': 4, 'folder': self.b.pk},
            {'name': 'doc5', 'id': 5, 'folder': self.c.pk},
            {'name': 'doc6', 'id': 6, 'folder': self.c.pk},
        ]

    def test_create_nested_json(self):
        docs = defaultdict(list)
        for doc in self.documents:
            docs[doc.get('folder')].append(doc)

        folders = []
        data = {x: {
            'folders': [], 'name': y, 'parent': z
        } for x, y, z in Node.objects.all().values_list('id', 'name', '_parent')}

        for key, node in data.items():
            if node['parent']:
                data[node['parent']]['folders'].append(node)
            else:
                folders.append(node)
            node['documents'] = docs.get(key, [])

        self.assertStructureCreated({
            'folders': folders,
            'documents': docs.get(None, [])
        })

    def assertStructureCreated(self, result):
        expected = {
            'documents': [{'id': 1, 'name': 'doc1'}],
            'folders': [{
                'documents': [
                    {'folder': 1, 'id': 2, 'name': 'doc2'},
                    {'folder': 1, 'id': 3, 'name': 'doc3'}
                ],
                'folders': [{
                    'documents': [{
                        'folder': 2, 'id': 4, 'name': 'doc4'
                    }],
                    'folders': [{
                        'documents': [], 'folders': [], 'name': u'e', 'parent': 2
                    }],
                    'name': u'b', 'parent': 1
                }, {
                    'documents': [{
                        'folder': 3, 'id': 5, 'name': 'doc5'
                    }, {
                        'folder': 3, 'id': 6, 'name': 'doc6'
                    }],
                    'folders': [{
                        'documents': [], 'folders': [], 'name': u'd', 'parent': 3
                    }],
                    'name': u'c', 'parent': 1
                }],
                'name': u'a', 'parent': None}]}
        self.assertEqual(expected, result)
