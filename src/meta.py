#!/usr/bin/env python

'''This file defines Meta-Meta-Model.'''

__author__ = 'William Emfinger'
__copyright__ = 'Copyright 2016, ROSMOD'
__credits__ = ['William Emfinger', 'Pranav Srinivas Kumar']
__license__ = 'GPL'
__version__ = '0.4'
__maintainer__ = 'William Emfinger'
__email__ = 'emfinger@isis.vanderbilt.edu'
__status__ = 'Production'

from collections import OrderedDict, MutableSequence

# TODO: Figure out how exactly to create pointers in meta-models

# TODO: Figure out how to convert pointer meta-models into pointers in
#       real-models, need to determine what objects they correspond
#       to, what their interaction paradigm is, and how they will be
#       edited (and viewed)
#
#       Perhaps Pointers get serialized into attributes whose options
#       are objects of that type?  Need support for getting all
#       objects of a type within a scope of a model at run-time

# TODO: Figure out how to properly handle dependencies between objects
#       (esp. attributes)

# TODO: Refactor children implementation to provide methods for
#       checking cardinality, allowed, etc.  Also don't really need
#       both allowed and cardinality

# TODO: Add scoping to some dependent attributes (e.g. for pointers etc.)

# TODO: Figure out how to handle options for attributes, i.e. they
#       could be a simple list of strings or they may be references to
#       other types of objects e.g. pointer src_kind options is
#       dynamic based on the FCO names


def get_children(model, kind):
    if model.kind() == kind:
        return [model]
    else:
        kids = []
        for c in model.children:
            kids.extend(get_children(c, kind))
        return kids


class Attribute(object):
    '''Generic Attributes class

    Each Attribute has the following:

    * kind -- The datatype of the attribute e.g. pointer, float, bool etc.
    * value -- The value of the attributes e.g. 'my_component', 1.642 etc.
    '''
    allowed_types = [
        'string',
        'code',
        'list',
        'int',
        'float',
        'double',
        'bool'
    ]
    default_vals = {
        'string': '',
        'code': '',
        'list': [],
        'int': 0,
        'float': 0.0,
        'double': 0.0,
        'bool': True
    }
    tooltip = ''
    display = ''
    options = []
    editable = True

    def __init__(self, kind, value):
        super(Attribute, self).__init__()
        self.kind = kind
        self.value = value

    def get_options(self):
        return self.options

    def fromQVariant(self, variant):
        if self.kind in ['string', 'code', 'list']:
            self.value = str(variant.toString())
        elif self.kind in ['int', 'integer']:
            self.value, tmp = variant.toInt()
        elif self.kind in ['float']:
            self.value, tmp = variant.toFloat()
        elif self.kind in ['double']:
            self.value, tmp = variant.toDouble()
        elif self.kind in ['bool']:
            self.value = variant.toBool()


class Model(object):
    '''Generic Model/Container class

    Every Model has the following:

    * parent -- A parent Model Object.
    * children -- A list of children (Model) objects.
    * attributes -- A dictionary of attributes.
    '''
    def __init__(self, parent=None):
        super(Model, self).__init__()
        self.parent = parent

        self.children = Children(allowed=[Model,
                                          Model_Pointer,
                                          Model_Attribute],
                                 cardinality={Model:
                                              '0..*',
                                              Model_Pointer:
                                              '0..*',
                                              Model_Attribute:
                                              '0..*'})

        self.attributes = OrderedDict()
        self.add_attribute('Name', 'string', 'Root')
        self.add_attribute('Cardinality',
                           'list', 
                           Children.valid_cardinalities[0])
        self.get_attribute(
            'Cardinality').options = Children.valid_cardinalities
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
        try:
            self.children.insert(position, child_model)
            child_model.parent = self
            return True
        except:
            return False

    def add_child(self, child_model):
        child_model.parent = self
        self.children.append(child_model)

    def add_attribute(self, name, kind, value):
        self.set_attribute(name, Attribute(kind, value))


class Pointer_Attribute(Attribute):
    '''
    '''
    def __init__(self, base=None):
        super(Pointer_Attribute, self).__init__('list', '')
        self.base = base

    def getNames(self, m):
        retlist = []
        if type(m) == Model:
            retlist.append(m['Name'])
        for c in m.children:
            retlist.extend(self.getNames(c))
        return retlist

    def get_options(self):
        r = self.base
        while r.parent is not None:
            r = r.parent
        r = r.children[0]
        return self.getNames(r)


class Model_Pointer(Model):
    '''
    '''
    def __init__(self,
                 parent=None,
                 name='Pointer',
                 dst_type='Model',
                 tooltip='',
                 display=''):
        super(Model_Pointer, self).__init__(parent)
        self.children = Children(allowed=[], cardinality={})
        self.attributes = OrderedDict()
        self.add_attribute('Name', 'string', name)
        self.set_attribute('Destination Type', Pointer_Attribute(self))
        self.set_attribute('Tooltip', Attribute('string', tooltip))
        self.set_attribute('Display', Attribute('string', display))


class Pointer(Model):
    '''
    '''
    def __init__(self,
                 parent=None,
                 src=None,
                 dst=None,
                 src_type='Model',
                 dst_type='Model'):
        super(Pointer, self).__init__(parent)
        self.src = src
        self.dst = dst
        self.src_type = src_type
        self.dst_type = dst_type
        self.children = Children(allowed=[], cardinality={})
        self.attributes = OrderedDict()
        self.add_attribute('Name', 'string', 'Pointer')


class Model_Attribute(Model):
    '''
    '''
    def __init__(self,
                 parent=None,
                 name='Attribute',
                 kind=Attribute.allowed_types[0],
                 tooltip='',
                 display='',
                 options=[],
                 editable=True):
        super(Model_Attribute, self).__init__(parent)
        self.children = Children(allowed=[], cardinality={})
        self.attributes = OrderedDict()
        self.add_attribute('Name', 'string', name)
        self.set_attribute('Kind', Attribute('list', kind))
        self.get_attribute('Kind').options = Attribute.allowed_types
        self.set_attribute('Tooltip', Attribute('string', tooltip))
        self.set_attribute('Display', Attribute('string', display))
        self.set_attribute('Editable', Attribute('bool', editable))


class Children(MutableSequence):
    '''Children list which extends :class:`MutableSequence` and enforces
    item type and cardinality rules.

    _inner -- Contents of the list
    _allowed -- The list will accept only object types contained in _allowed
    _cardinality -- Cardinality of each accepted type

    '''

    valid_cardinalities = ['0..*', '1..*', '1']

    def __init__(self, it=(), allowed=(), cardinality=()):
        '''
        :param in allowed: :class:`List` containing the allowed types of
            children
        :param in cardinality: :class:`Dictionary` of key:value pairs
            mapping object type to its cardinality string, e.g.
            Model: '0..*'

        '''
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
                children_types = [type(val) for val in self._inner]
                if item_cardinality == '1':
                    if type(item) not in children_types:
                        return self._inner.insert(index, item)
                    else:
                        print 'ERROR: Cardinality Insert Error:\n\t{}'.format(
                            'An object of type \'{}\' already exists!'.format(
                                item.__class__.__name__
                            )
                        )
                        raise 'Cardinality Error'
                else:
                    return self._inner.insert(index, item)
        else:
            print 'ERROR::Cannot add child: ' + str(item)
            return self._inner
