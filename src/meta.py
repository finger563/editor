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

# TODO: Refactor Attribute fromQVariant() method so that it is no
#       longer needed; should be handled by delegate probably.

# TODO: Add constraints as python functions stored as text and exec'd

# TODO: Add get_options for list attributes as stored python text

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
#
#       How to handle even more complex dependencies such as between
#       host_ref selection and the parent's hardware_ref?

# TODO: Add scoping to some dependent attributes (e.g. for pointers
#       etc.)

# TODO: Figure out how to handle options for attributes, i.e. they
#       could be a simple list of strings or they may be references to
#       other types of objects e.g. pointer src_kind options is
#       dynamic based on the FCO names

# TODO: Might need to extend the cardinality code in children to
#       handle more types of cardinality, e.g. '5'

# TODO: Allow for messages/services which are purely references to
#       libarary/standard messages/services.  Perhaps just allow
#       publishers/subscribers/clients/servers to point to
#       messages/services which are not in the model and are specified
#       as a string just as they would be in the code?
#
#       This could require objects which may allow multiple types, how
#       would that integrate into our current editing paradigm?
#
#       Note: if they have the same definitions and name (and thus MD5
#       hash) they will work out of the box

# TODO: Add pointer conversion operations to 'convertModelToMeta()'

# TODO: Make names only unique within scopes; enforce that no two children
#       of the same parent share the same name.

# TODO: Models can have same names depending on scope; make sure we
#       use uniqueness here! (Editor.openEditorTabs)

# TODO: Editing of attributes needs to be worked out some more,
#       w.r.t. the editable tag and what can/should be editable from
#       where.

# TODO: Refactor convertModelToMeta so that each meta-type performs
#       its own conversion


def convertModelToMeta(model, meta_dict):
    '''This function is used to create classes based on the editor's
    current model.  It works on Model instances, which can have
    pointers, models, and model_attributes as children.  By converting
    the models in to named classes subclassing Model and adding named
    attributes subclassing Attribute it forms a new class structure
    which describes the meta model and which can be used to
    instantiate models.

    Returns the class of the root type of the meta model

    '''

    allowed_kids = OrderedDict()
    attr_dict = OrderedDict()
    ptrs = OrderedDict()
    for obj in model.children:
        # These will be the available children_types of the class
        if type(obj) == MetaModel:
            allowed_kids[convertModelToMeta(obj, meta_dict)] = obj['Cardinality']
        # These will be pointers to other classes
        elif type(obj) == MetaPointer:
            import types
            # should fill out get_references
            exec obj['Valid Objects'] in globals()
            
            def ref_wrapper(s1, s2):
                return s1.get_references()

            def ptrInit(self):
                Pointer.__init__(self,
                                 dst_type=obj['Destination Type'])
                self['Name'] = obj['Name']
                self.get_attribute('Name').editable = False
                self.add_attribute('Destination', 'reference', '')
                destAttr = self.get_attribute('Destination')
                destAttr.dst_type = obj['Destination Type']
                '''
                destAttr.tooltip = obj['Tooltip']
                destAttr.display = obj['Display']
                destAttr.get_options = types.MethodType(
                    lambda s: ref_wrapper(self, s),
                    destAttr,
                    Attribute
                )
                '''
            new_ptr = type(
                obj['Name'],
                (Pointer, object, ),
                {
                    '__init__': ptrInit,
                    # from obj['Valid Objects'] as exec'd text
                    'get_references': get_references,
                }
            )
            ptrs[obj['Name']] = new_ptr()
        # These will be the attributes of the new class
        elif type(obj) == MetaAttribute:
            def attrInit(self):
                Attribute.__init__(self, obj['Kind'],
                                   Attribute.default_vals[obj['Kind']])
            new_attr = type(
                obj['Name'],
                (Attribute, object, ),
                {
                    '__init__': attrInit,
                    'tooltip': obj['Tooltip'],
                    'display': obj['Display'],
                    'editable': obj['Editable'],
                }
            )
            attr_dict[obj['Name']] = new_attr()

    # Define the init function inline here for the new class, make
    # sure all attributes, pointers, children, etc. are set up
    # properly
    def modelInit(self, parent=None):
        super(self.__class__, self).__init__(parent)
        self.attributes = OrderedDict()
        self.add_attribute('Name',
                           'string',
                           '{}'.format(self.__class__.__name__))
        # Handle children
        self.children = Children(cardinality=allowed_kids)
        for t, c in self.children.get_cardinality().iteritems():
            min_number = int(c.split('..')[0])
            for i in range(0, min_number):
                new_child = t()
                new_child['Name'] = '{}_{}'.format(t.__name__, i)
                self.add_child(new_child)
        # Handle pointers
        ptr_types = [type(t) for t in ptrs.values()]
        for t in ptr_types:
            self.children.set_cardinality_of(t, '1')
        for name, ptr in ptrs.iteritems():
            self.add_child(ptr)
        # Handle attributes
        for name, attr in attr_dict.iteritems():
            self.set_attribute(name, attr)

    new_type = type(
        model['Name'],
        (Model, object, ),
        {
            '__init__': modelInit
        }
    )
    meta_dict[model['Name']] = new_type
    return new_type


def get_children(model, kind):
    if model.kind() == kind:
        return [model]
    else:
        kids = []
        for c in model.children:
            kids.extend(get_children(c, kind))
        return kids


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

        self.children = Children(cardinality={Model:
                                              '0..*',
                                              MetaPointer:
                                              '0..*',
                                              MetaAttribute:
                                              '0..*'})

        self.attributes = OrderedDict()
        # self.add_attribute('Name', 'string', 'Root')
        # self.add_attribute('Cardinality',
        #                   'list', 
        #                   Children.valid_cardinalities[0])
        # self.get_attribute(
        #    'Cardinality').options = Children.valid_cardinalities
        self.kwargs = {}

    def __getitem__(self, key):
        return self.attributes[key].value

    def __setitem__(self, key, value):
        self.attributes[key].setValue(value)

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
        success = self.children.insert(position, child_model)
        if success:
            child_model.parent = self
        return success

    def add_child(self, child_model):
        child_model.parent = self
        self.children.append(child_model)

    def add_attribute(self, name, kind, value):
        self.set_attribute(name, Attribute(kind, value))


class Attribute(Model):
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

    def __init__(self, kind, value, parent=None):
        super(Attribute, self).__init__()
        self.kind = kind
        self.value = value
        self.parent = parent

        # Maps value to list of dependent children
        # Perhaps have this editable instead of using Children?
        self.dependents = OrderedDict()

        self.children = Children(cardinality={Attribute:
                                              '0..*'})

    def setValue(self, value):
        self.update_dependents(self.value, value)
        self.value = value

    def update_dependents(self, oldValue, newValue):
        if oldValue in self.dependents.keys():
            old_deps = self.dependents[oldValue]
            for dep in old_deps:
                dep.editable = False
        if newValue in self.dependents.keys():
            deps = self.dependents[newValue]
            for dep in deps:
                dep.editable = True

    def get_options(self):
        return self.options

    def fromQVariant(self, variant):
        if self.kind in ['string', 'list']:
            self.value = str(variant.toString())
        elif self.kind in ['code', 'python']:
            self.value = str(variant)
        elif self.kind in ['int', 'integer']:
            self.value, tmp = variant.toInt()
        elif self.kind in ['float']:
            self.value, tmp = variant.toFloat()
        elif self.kind in ['double']:
            self.value, tmp = variant.toDouble()
        elif self.kind in ['bool']:
            self.value = variant.toBool()
        elif self.kind in ['reference']:
            self.value = variant.toPyObject()
        elif 'file' in self.kind:
            self.value = str(variant)


class Pointer(Model):
    '''
    '''
    def __init__(self,
                 parent=None,
                 dst=None,
                 dst_type='Model'):
        super(Pointer, self).__init__(parent)
        self.children = Children(cardinality={})
        self.attributes = OrderedDict()
        self.add_attribute('Name', 'string', 'Pointer')
        self.dst_type = dst_type


class MetaModel(Model):
    '''
    '''
    
    def __init__(self):
        super(MetaModel, self).__init__()

        self.children = Children(cardinality={MetaModel:
                                              '0..*',
                                              MetaPointer:
                                              '0..*',
                                              MetaAttribute:
                                              '0..*'})

        self.add_attribute('Name', 'string', 'Root')
        self.add_attribute('Cardinality',
                           'list', 
                           Children.valid_cardinalities[0])
        self.get_attribute(
            'Cardinality').options = Children.valid_cardinalities        


class MetaAttribute(Model):
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
        super(MetaAttribute, self).__init__(parent)
        self.children = Children(cardinality={MetaAttribute:
                                              '0..*'})
        self.attributes = OrderedDict()
        self.add_attribute('Name', 'string', name)
        self.set_attribute('Kind', Attribute('list', kind))
        self.get_attribute('Kind').options = Attribute.allowed_types
        self.set_attribute('Tooltip', Attribute('string', tooltip))
        self.set_attribute('Display', Attribute('string', display))
        self.set_attribute('Editable', Attribute('bool', editable))


class MetaPointer(Model):
    '''
    '''

    valid_scopes = ['Root', 'Parent']

    def __init__(self,
                 parent=None,
                 name='Pointer',
                 dst_type='Model',
                 tooltip='',
                 display=''):
        super(MetaPointer, self).__init__(parent)
        self.children = Children(cardinality={})
        self.attributes = OrderedDict()
        self.add_attribute('Name', 'string', name)

        def get_options(base):
            def genericFunc(s):
                def get_names(m):
                    retlist = []
                    if m.kind() == 'MetaModel':
                        retlist.append(m['Name'])
                    for c in m.children:
                        retlist.extend(get_names(c))
                    return retlist
                r = base
                while r.parent is not None:
                    r = r.parent
                r = r.children[0]
                return get_names(r)
            return genericFunc

        import types
        self.add_attribute('Destination Type', 'list', 'Model')
        destAttr = self.get_attribute('Destination Type')
        destAttr.get_options = types.MethodType(
            get_options(self),
            destAttr,
            Attribute
        )

        self.set_attribute(
            'Valid Objects',
            Attribute(
                'python',
                '''def get_references(self):
    _type = self.dst_type
    retTypes = [x['Name'] for x in get_children(self.parent, _type)]
    return retTypes'''
            )
        )
        self.set_attribute('Tooltip', Attribute('string', tooltip))
        self.set_attribute('Display', Attribute('string', display))


class Children(MutableSequence):
    '''Children list which extends :class:`MutableSequence` and enforces
    item type and cardinality rules.

    **_inner** -- Contents of the list
    **_cardinality** -- A dictionary providing the types of allowed
    objects, and their cardinality

    '''

    valid_cardinalities = ['0..*', '1..*', '1']

    def __init__(self, it=(), cardinality=()):
        '''
        :param in cardinality: :class:`Dictionary` of key:value pairs
            mapping object type to its cardinality string, e.g.
            Model: '0..*'

        '''
        self._inner = list(it)
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

    def get_cardinality(self):
        return self._cardinality

    def set_cardinality(self, new_cardinality):
        self._cardinality = new_cardinality

    def get_cardinality_of(self, key):
        return self._cardinality[key]

    def set_cardinality_of(self, key, value):
        self._cardinality[key] = value

    def allowed(self):
        return self._cardinality.keys()

    def can_insert(self, item):
        # item is allowed as a child
        if type(item) in self.allowed():
            if item not in self._inner:
                item_cardinality = self._cardinality[type(item)]
                children_types = [type(val) for val in self._inner]
                if item_cardinality == '1':
                    if type(item) not in children_types:
                        return True, ''
                    else:
                        return [
                            False,
                            'Only allowed to have one {}'.format(
                                type(item)
                            )
                        ]
                # Need to handle cardinalities of the form 'X..Y'
                else:
                    num_allowed = item_cardinality.split('..')[1]
                    if num_allowed and num_allowed != '*':
                        num_existing = children_types.count(type(item))
                        if num_existing >= int(num_allowed):
                            return [
                                False,
                                'Max number of {} is {}'.format(
                                    type(item),
                                    num_allowed
                                )
                            ]
                    return True, ''
        # item is not allowed as a child
        else:
            return False, '{} is not allowed!'.format(type(item))

    def insert(self, index, item):
        test, err = self.can_insert(item)
        if test:
            self._inner.insert(index, item)
        else:
            print 'ERROR::Cannot add child: {}'.format(err)
        return test
