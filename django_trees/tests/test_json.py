from collections import defaultdict
from django import test
from django_trees.tests.test_app.models import Node


class Directory(object):

    def __init__(self, documents, folders):
        self.documents = defaultdict(list)
        for doc in documents:
            self.documents[doc.get('folder')].append(doc)
        self.folders = {x: {
            'documents': [], 'folders': [], 'name': y, 'parent': z
        } for x, y, z in folders.values_list('id', 'name', '_parent')}

    def folder_documents(self, folder):
        return self.documents.get(folder, [])

    def doit(self):
        folders = []

        for key, node in self.folders.items():
            if node['parent']:
                self.folders[node['parent']]['folders'].append(node)
            else:
                folders.append(node)
            node['documents'] = self.folder_documents(key)

        return {
            'folders': folders,
            'documents': self.folder_documents(None)
        }


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
        directory = Directory(self.documents, Node.objects.all())
        self.assertStructureCreated(directory.doit())

    def assertStructureCreated(self, result):
        expected = {
            'documents': [{
                'id': 1, 'name': 'doc1'
            }],
            'folders': [{
                'name': u'a',
                'parent': None,
                'documents': [
                    {'folder': 1, 'id': 2, 'name': 'doc2'},
                    {'folder': 1, 'id': 3, 'name': 'doc3'}
                ],
                'folders': [{
                    'name': u'b',
                    'parent': 1,
                    'documents': [{
                        'folder': 2, 'id': 4, 'name': 'doc4'
                    }],
                    'folders': [{
                        'name': u'e',
                        'parent': 2,
                        'documents': [],
                        'folders': []
                    }],
                }, {
                    'name': u'c',
                    'parent': 1,
                    'documents': [{
                        'folder': 3, 'id': 5, 'name': 'doc5'
                    }, {
                        'folder': 3, 'id': 6, 'name': 'doc6'
                    }],
                    'folders': [{
                        'name': u'd',
                        'parent': 3,
                        'documents': [],
                        'folders': [],
                    }],
                }],
            }]
        }
        self.assertEqual(expected, result)
