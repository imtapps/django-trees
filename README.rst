django_trees
============

.. image:: https://travis-ci.org/imtapps/django-trees.svg?branch=master
    :target: https://travis-ci.org/imtapps/django-trees

Simple way to create, persist and manipulate reliable tree structures using Django models.


Installation
============

``pip install django-trees``


API Usage
=========

Create Model
------------

To create a model extend ``AbstractNode`` and add desired fields.

.. code:: python

    from django.db import models
    from django_trees.models import AbstractNode
    
    class Folder(AbstractNode):
        name = models.CharField(max_length=10)


Create Tree Nodes
-----------------

To create a tree node, there is nothing different than creating a normal Django model other than you may specify a parent node.

.. code:: python

    root = Folder.objects.create(name="Root")
    documents = Folder.objects.create(name="Documents", parent=root)
    downloads = Folder.objects.create(name="Downloads", parent=root)
    projects = Folder.objects.create(name="Projects", parent=documents)


Get Node Descendants
--------------------

To retrieve all of the descendants of a node (including children, grandchildren, great grandchildren, etc) use the ``get_descendants`` method. This method will return a flat list of node objects.

.. code:: python

   root.get_descendants() 


Get Node Ancestors
------------------

To retrieve all of the ancestors of a node (including parents, grandparents, great grandparents, etc) use the ``get_ancestors`` method. This method will return a flat list of node objects.

.. code:: python

   projects.get_ancestors() 


Get Node Children
-----------------

To retrieve all immediate children of the current node use the ``get_children`` method. This method will return a flat list of node objects.

.. code:: python

   projects.get_children() 


Move Node
---------

To move a node to a different position in the tree use the ``move`` method passing the new parent node as an argument.

.. code:: python

   projects.move(root)


Bifurcate Node
--------------

To create a separate tree from a branch of an existing tree use the ``bifurcate`` method. The node object will be removed from the previous tree and it along with it's descendants will now be in a new tree.

.. code:: python

   projects.bifurcate()


Get ASCII Tree
--------------

To get an ascii representation of the tree structure use the ``get_ascii_tree`` method.

.. code:: python

   projects.get_ascii_tree()


Demo
----

.. image:: https://cloud.githubusercontent.com/assets/847632/4188298/1d00fe0a-3771-11e4-8900-ccda9fbb72a1.gif
