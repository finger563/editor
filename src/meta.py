#!/usr/bin/env python

"""This file defines Meta-Meta-Model."""

__author__ = "William Emfinger"
__copyright__ = "Copyright 2015, ROSMOD"
__credits__ = ["Pranav Srinivas Kumar", "William Emfinger"]
__license__ = "GPL"
__version__ = "0.4"
__maintainer__ = "William Emfinger"
__email__ = "emfinger@isis.vanderbilt.edu"
__status__ = "Production"

import os
from collections import OrderedDict, MutableSequence

def get_children(model, kind):
    if model.kind() == kind:
        return [model]
    else:
        kids = []
        for c in model.children:
            kids.extend(get_children(c, kind))
        return kids

class Attribute(object):
    """Generic Attributes class

    Each Attribute has the following:
    kind -- The datatype of the attribute e.g. string, pointer, float, bool etc.
    value -- The value of the attributes e.g. "my_component", 1.642 etc.
    """
    tooltip = ''
    display = ''
    options = []
    editable = True
    def __init__(self, kind, value):
        super(Attribute, self).__init__()
        self.kind = kind
        self.value = value

    def fromQVariant(self, variant):
        if self.kind in ['string','code','list_entry']:
            self.value = variant.toString()
        elif self.kind in ['int','integer']:
            self.value,tmp = variant.toInt()
        elif self.kind in ['float']:
            self.value,tmp = variant.toFloat()
        elif self.kind in ['double']:
            self.value,tmp = variant.toDouble()

class Pointer(object):
    """
    """
    def __init__(self, src, dst, src_type, dst_type):
        super(Pointer, self).__init__()
        self.kind = kind
        self.src = src
        self.dst = dst
        self.src_type = src_type
        self.dst_type = dst_type

class Model(object):
    """Generic Model/Container class

    Every Model has the following:
    parent -- A parent Model Object.
    children -- A list of children (Model) objects.
    attributes -- A dictionary of attributes.
    """
    def __init__(self, parent = None):
        super(Model, self).__init__()
        self.parent = parent

        self.children = Children(allowed=[Model], 
                                 cardinality = {Model\
                                                : '0..*'})

        self.attributes = OrderedDict()
        self.add_attribute('Name', 'string', 'Root')
        self.kwargs = {}

    def __getitem__(self, key):
        return self.attributes[key].value

    def __setitem__(self, key, value):
        self.attributes[key].value = value

    def get_attribute(self, key):
        return self.attributes[key]

    def set_attribute(self, key, attr):
        self.attributes[key] = attr

    def child_count(self):
        return len(self.children)

    def kind(self):
        return self.__class__.__name__

    def child(self, position):
        if position < self.child_count():
            return self.children[position]
        else:
            return None

    def row(self):
        if self.parent:
            return self.parent.children.index(self)

    def remove_child(self, position):
        if position < 0 or position > self.child_count():
            return False
        child = self.children.pop(position)
        child.parent = None
        del child
        return True

    def insert_child(self, position, child_model):
        if position < 0 or position > self.child_count():
            return False
        child_model.parent = self
        self.children.insert(position, child_model)
        return True

    def add_child(self, child_model):
        child_model.parent = self
        self.children.append(child_model)

    def add_attribute(self, name, kind, value):
        self.set_attribute(name, Attribute(kind, value))

class Children(MutableSequence):
    """Children List
    
    _inner -- Contents of the list
    _allowed -- The list will accept only object types contained in _allowed
    _cardinality -- Cardinality of each accepted type
    """
    def __init__(self, it=(), allowed=(), cardinality=()):
        self._inner = list(it)
        self._allowed = allowed
        self._cardinality = cardinality

    def __len__(self):
        return len(self._inner)
    def __iter__(self):
        return iter(self._inner)
    def __contains__(self, item):
        return item in self._inner
    def __getitem__(self, index):
        return self._inner[index]
    def __setitem__(self, index, value):
        self._inner[index] = value
    def __delitem__(self, index):
        del self._inner[index]
    def __repr__(self):
        return 'Children({})'.format(self._inner)
    def insert(self, index, item):
        if type(item) in self._allowed:
            if item not in self._inner:
                item_cardinality = self._cardinality[type(item)]
                children_types = [str(type(val)) for val in self._inner]
                if item_cardinality == '1':
                    if str(type(item)) not in children_types:
                        return self._inner.insert(index, item)
                    else:
                        print "ERROR::Cardinality Error!"
                else:
                    return self._inner.insert(index, item)
        else:
            print "ERROR::Cannot add child: " + str(item)
            return self._inner
