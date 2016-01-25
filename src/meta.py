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

from PyQt4 import QtCore

from collections import OrderedDict, MutableSequence

import uuid

# TODO: Need a nice way of getting root item in the model; this would
#       make getting other objects (for instance in get_root) much
#       easier if they're not close by in the tree

# TODO: Need a nice way of getting pointers; esp. for getting root in
#       meta-pointers.  accessor functions would be especially handy.
#       perhaps meta-class so that there are automatically added
#       functions e.g. Deployment.Hardware_Reference()

# TODO: Need default value attribute for metaAttributes and
#       metaPointers

# TODO: Need to write fromDict functions for Model, Attribute, and
#       Pointer

# TODO: Need to integrate Model/Attribute/Pointer fromDict functions
#       into the fromDict functions for Meta* so that the base
#       attributes (Name, Cardinality, etc.) don't change uuid when
#       opening and then saving the model.  This will prevent the
#       model from changing data when simply opening and saving.

# TODO: Update the fromMeta functions to build meta-dictionary of
#       name:type pairs for quickly instantiating objects as needed.
#       Then we can use this meta-model dictionary for creating models
#       (and possibly checking them as well?)

# TODO: Refactor Attribute fromQVariant() method so that it is no
#       longer needed; should be handled by delegate probably.

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


# Why is this not a function of Model?
def get_children(model, kind):
    if model.kind() == kind:
        return [model]
    else:
        kids = []
        for c in model.children:
            kids.extend(get_children(c, kind))
        return kids


class Model(QtCore.QObject):
    '''Generic Model/Container class

    Every Model has the following:

    * uuid -- A unique identifier for this object.
    * parent -- A parent :class:`Model` object.
    * children -- A list of child :class:`Model` objects.
    * attributes -- A dictionary mapping names to :class:`Attribute` objects.
    * pointers -- A list of :class:`Pointer` objects
    '''
    def __init__(self, parent=None):
        QtCore.QObject.__init__(self)
        self.uuid = str(uuid.uuid4())
        self.parent = parent

        self.attributes = OrderedDict()
        self.pointers = Children()
        self.children = Children(cardinality={Model:
                                              '0..*',
                                              MetaPointer:
                                              '0..*',
                                              MetaAttribute:
                                              '0..*'})

        self.kwargs = {}

    def row_count(self):
        return len(self.children)

    def column_count(self):
        columns = [
            self.children,
            self.attributes,
            self.pointers
        ]
        return len(columns)

    def child_count(self):
        return len(self.children)

    def __getitem__(self, key):
        return self.attributes[key].getValue()

    def __setitem__(self, key, value):
        valid, errMsg = self.attributes[key].setValue(value)
        if not valid:
            print 'ERROR: setting \'{}\' to \'{}\': {}'.format(
                key,
                value,
                errMsg
            )

    def get_attribute(self, key):
        return self.attributes[key]

    def set_attribute(self, key, attr):
        self.attributes[key] = attr
        attr.parent = self

    def kind(self):
        return self.__class__.__name__

    def child(self, row, column):
        item = None
        if column == 0:
            if row < len(self.children) and row >= 0:
                item = self.children[row]
        elif column == 1:
            if row < len(self.attributes) and row >= 0:
                item = self.attributes.values()[row]
        elif column == 2:
            if row < len(self.pointers) and row >= 0:
                item = self.pointers[row]
        return item

    def column(self):
        return 0

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
        return self.insert_child(len(self.children), child_model)

    def add_attribute(self, name, kind, value):
        attr = Attribute(kind, value, self)
        self.set_attribute(name, attr)

    def add_pointer(self, ptr):
        self.pointers.append(ptr)
        ptr.parent = self

    @staticmethod
    def fromDict(model_dict, uuid_dict, unresolved_keys, meta_dict):
        # instantiate a new object
        newobj = meta_dict[model_dict['Type']]()

        model_dict = OrderedDict()
        model_dict['Type'] = model.kind()
        model_dict['UUID'] = model.uuid
        model_dict['Attributes'] = {
            key: value.__class__.toDict(value)
            for key, value in model.attributes.iteritems()
        }
        model_dict['Children'] = Children.toDict(model.children)
        model_dict['Pointers'] = Children.toDict(model.pointers)
        return model_dict

    @staticmethod
    def toDict(model):
        model_dict = OrderedDict()
        model_dict['Type'] = model.kind()
        model_dict['UUID'] = model.uuid
        model_dict['Attributes'] = {
            key: value.__class__.toDict(value)
            for key, value in model.attributes.iteritems()
        }
        model_dict['Children'] = Children.toDict(model.children)
        model_dict['Pointers'] = Children.toDict(model.pointers)
        return model_dict


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
    # Note that 'python' and 'reference' are not allowed types
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
        Model.__init__(self, parent)
        self._kind = kind
        self._value = value

        # Maps value to list of dependent children
        self.dependents = OrderedDict()

    def row(self):
        if self.parent:
            return self.parent.attributes.values().index(self)

    def column(self):
        return 1

    def set_attribute(self, key, attr, dependent_value):
        self.attributes[key] = attr
        self.dependents.setdefault(
            dependent_value, []
        ).append(key)
        attr.editable = (self.getValue() == dependent_value)
        attr.parent = self

    def add_attribute(self, name, kind, value, dependent_value):
        attr = Attribute(kind, value, self)
        self.set_attribute(name, attr)

    def validator(self, newValue):
        valid = True
        errMsg = ''
        return valid, errMsg

    def getKind(self):
        return self._kind

    def setKind(self, kind):
        self._kind = kind

    def getValue(self):
        return self._value

    def setValue(self, value):
        valid, errMsg = self.validator(value)
        if valid:
            self.update_dependents(self._value, value)
            self._value = value
        return valid, errMsg

    def update_dependents(self, oldValue, newValue):
        if oldValue in self.dependents.keys():
            old_deps = self.dependents[oldValue]
            for dep in old_deps:
                self.attributes[dep].editable = False
        if newValue in self.dependents.keys():
            deps = self.dependents[newValue]
            for dep in deps:
                self.attributes[dep].editable = True

    def get_options(self):
        return self.options

    def fromQVariant(self, variant):
        newVal = None
        tmp = None
        if self.getKind() in ['string', 'list']:
            newVal = str(variant.toString())
            tmp = type(newVal) == str
        elif self.getKind() in ['code', 'python']:
            newVal = str(variant)
            tmp = type(newVal) == str
        elif self.getKind() in ['int', 'integer']:
            newVal, tmp = variant.toInt()
        elif self.getKind() in ['float']:
            newVal, tmp = variant.toFloat()
        elif self.getKind() in ['double']:
            newVal, tmp = variant.toDouble()
        elif self.getKind() in ['bool']:
            newVal = variant.toBool()
            tmp = type(newVal) == bool
        elif self.getKind() in ['reference']:
            newVal = variant  # .toPyObject()
        elif 'file' in self.getKind():
            newVal = str(variant)
        if newVal or tmp:
            return self.setValue(newVal)
        return False, 'Attribute has an illegal kind!'

    @staticmethod
    def toDict(model):
        model_dict = Model.toDict(model)
        model_dict.pop('UUID', None)
        model_dict.pop('Pointers', None)
        model_dict.pop('Children', None)
        model_dict['Kind'] = model.getKind()
        model_dict['Value'] = model.getValue()
        model_dict['Dependents'] = model.dependents
        return model_dict


class NameAttribute(Attribute):
    '''
    '''
    def __init__(self, name):
        Attribute.__init__(self, 'string', name)

    def validator(self, newName):
        if not self.parent.parent or not self.parent.parent.children:
            return True, ''
        sibling_names = [c['Name'] for c in self.parent.parent.children
                         if c != self.parent]
        valid = newName not in sibling_names
        errMsg = ''
        if not valid:
            errMsg = 'Name \'{}\' already exists in parent scope!'.format(
                newName
            )
        return valid, errMsg

    def scoped(self):
        name = self.getValue()
        parent = self.parent.parent['Name']
        return parent + '/' + name

    @staticmethod
    def toDict(model):
        model_dict = Attribute.toDict(model)
        model_dict.pop('Dependents', None)
        return model_dict


class Pointer(Model):
    '''
    '''
    def __init__(self,
                 parent=None,
                 dst=None,
                 dst_type='Model'):
        Model.__init__(self, parent)
        self.children = Children(cardinality={})
        self.attributes = OrderedDict()
        self.set_attribute('Name', NameAttribute('Pointer'))
        self.get_attribute('Name').editable = False
        self.dst_type = dst_type
        self.add_attribute('Destination', 'reference', '')

    def row(self):
        if self.parent:
            return self.parent.pointers.index(self)

    def column(self):
        return 2

    @staticmethod
    def toDict(model):
        model_dict = Model.toDict(model)
        model_dict.pop('UUID', None)
        model_dict.pop('Pointers', None)
        model_dict.pop('Children', None)
        # model_dict['Attributes']['Destination Type'] = model.dst_type
        model_dict['Attributes'][
            'Destination'
        ] = model['Destination'].uuid
        return model_dict


class MetaModel(Model):
    '''
    '''

    def __init__(self):
        Model.__init__(self)

        self.children = Children(cardinality={MetaModel:
                                              '0..*',
                                              MetaPointer:
                                              '0..*',
                                              MetaAttribute:
                                              '0..*'})

        self.set_attribute('Name', NameAttribute('Root'))
        self.add_attribute('Cardinality',
                           'string',
                           '0..*')

        def validatorWrapper():
            def genericValidator(newValue):
                valid = True
                errMsg = ''
                try:
                    vals = newValue.split('..', 1)
                    lower = int(vals[0])
                    if lower < 0:
                        valid = False
                        errMsg = 'Lower must be >= 0'
                    if valid and len(vals) > 1:
                        if vals[1] != '*':
                            upper = int(vals[1])
                            if upper <= lower:
                                valid = False
                                errMsg = 'Upper must be > Lower'
                except:
                    valid = False
                    errMsg = 'Format of Cardinality must be '
                    errMsg += '<INT>(..(<INT>|*))'
                return valid, errMsg
            return genericValidator

        cardAttr = self.get_attribute('Cardinality')
        cardAttr.validator = validatorWrapper()

    @staticmethod
    def toDict(model):
        model_dict = Model.toDict(model)
        return model_dict

    @staticmethod
    def toMeta(model):
        allowed_kids = OrderedDict()
        attr_dict = OrderedDict()
        ptrs = OrderedDict()
        for obj in model.children:
            if type(obj) == MetaModel:
                allowed_kids[ MetaModel.toMeta(obj) ] = obj['Cardinality']
            elif type(obj) == MetaPointer:
                ptrs[obj['Name']] = MetaPointer.toMeta(obj)
            elif type(obj) == MetaAttribute:
                attr_dict[obj['Name']] = MetaAttribute.toMeta(obj)

        # Define the init function inline here for the new class, make
        # sure all attributes, pointers, children, etc. are set up
        # properly
        def modelInit(self, parent=None):
            Model.__init__(self, parent)
            self.attributes = OrderedDict()
            self.set_attribute('Name', NameAttribute(self.kind()))
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

        new_model = type(
            model['Name'],
            (Model, ),
            {
                '__init__': modelInit
            }
        )
        return new_model

    @staticmethod
    def fromDict(model_dict, uuid_dict, unresolved_keys):
        newobj = MetaModel()
        newobj.uuid = model_dict['UUID']
        uuid_dict[model_dict['UUID']] = newobj
        # Handle Name/Cardinality attributes
        for key, value in model_dict['Attributes'].iteritems():
            newobj[key] = value['Value']
        # Handle Children
        # TODO: Rework cardinality and how children can be inserted
        for obj_dict in model_dict['Children']:
            child = None
            if obj_dict['Type'] == 'MetaModel':
                child = MetaModel.fromDict(obj_dict, uuid_dict, unresolved_keys)
            elif obj_dict['Type'] == 'MetaAttribute':
                child = MetaAttribute.fromDict(obj_dict, uuid_dict, unresolved_keys)
            elif obj_dict['Type'] == 'MetaPointer':
                child = MetaPointer.fromDict(obj_dict, uuid_dict, unresolved_keys)
            if child:
                newobj.add_child(child)
        return newobj

    @staticmethod
    def fromMeta(model, uuid_dict):
        allowed_kids = OrderedDict()
        attr_dict = OrderedDict()
        ptrs = OrderedDict()

        uuid_dict[model['UUID']] = model['Attributes']['Name']['Value']

        for obj in model['Children']:
            if obj['Type'] == 'MetaModel':
                allowed_kids[ MetaModel.fromMeta(
                    obj,
                    uuid_dict) ] = obj['Attributes']['Cardinality']['Value']
            elif obj['Type'] == 'MetaPointer':
                ptrs[obj['Attributes']['Name']['Value']] = MetaPointer.fromMeta(
                    obj,
                    uuid_dict)
            elif obj['Type'] == 'MetaAttribute':
                attr_dict[obj['Attributes']['Name']['Value']] = MetaAttribute.fromMeta(
                    obj,
                    uuid_dict
                )

        # Define the init function inline here for the new class, make
        # sure all attributes, pointers, children, etc. are set up
        # properly
        def modelInit(self, parent=None):
            Model.__init__(self, parent)
            self.attributes = OrderedDict()
            self.set_attribute('Name', NameAttribute(self.kind()))
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
                self.pointers.set_cardinality_of(t, '1')
            for name, ptr in ptrs.iteritems():
                self.add_pointer(ptr)

            # Handle attributes
            for name, attr in attr_dict.iteritems():
                self.set_attribute(name, attr)

        new_model = type(
            str(model['Attributes']['Name']['Value']),
            (Model, ),
            {
                '__init__': modelInit
            }
        )
        return new_model
    

class MetaAttribute(Model):
    '''
    '''
    def __init__(self,
                 parent=None,
                 name='Attribute',
                 kind=Attribute.allowed_types[0],
                 validator='''def validator(self, newValue):
    valid = True
    errMsg = ''
    return valid, errMsg
                 ''',
                 tooltip='',
                 display='',
                 editable=True):
        Model.__init__(self, parent)
        self.children = Children(cardinality={MetaAttribute:
                                              '0..*'})
        self.attributes = OrderedDict()
        self.set_attribute('Name', NameAttribute(name))
        self.set_attribute('Kind', Attribute('list', kind))
        kindAttr = self.get_attribute('Kind')
        kindAttr.options = Attribute.allowed_types
        listOptionsAttr = Attribute(
            'python',
            '''def get_options(self):
    return []'''
        )
        listOptionsAttr.tooltip = 'Returns a list of options to choose from.'
        kindAttr.set_attribute(
            'List Options',
            listOptionsAttr,
            'list'
        )
        self.set_attribute('Tooltip', Attribute('string', tooltip))
        self.set_attribute('Display', Attribute('string', display))
        self.set_attribute('Editable', Attribute('bool', editable))
        self.set_attribute('Validator', Attribute('python', validator))
        pkattr = Attribute('string', '')
        pkattr.editable = False
        self.set_attribute('Parent Key', pkattr)

    def insert_child(self, position, child_model):
        '''
        Reimplemented from :class:`Model` to add a new attribute to the child.
        '''
        success = Model.insert_child(self, position, child_model)
        if success:
            child_model.get_attribute('Parent Key').editable = True
        return success

    @staticmethod
    def toDict(model):
        model_dict = Model.toDict(model)
        return model_dict

    @staticmethod
    def toMeta(model):
        exec model['Validator'] in globals()

        def attrInit(self):
            Attribute.__init__(
                self,
                model['Kind'],
                Attribute.default_vals[model['Kind']]
            )

        new_attr = type(
            model['Name'],
            (Attribute, ),
            {
                '__init__': attrInit,
                'tooltip': model['Tooltip'],
                'display': model['Display'],
                'editable': model['Editable'],
                'validator': validator,
            }
        )
        return new_attr()

    @staticmethod
    def fromDict(model_dict, uuid_dict, unresolved_keys):
        newobj = MetaAttribute()
        newobj.uuid = model_dict['UUID']
        uuid_dict[model_dict['UUID']] = newobj
        for key, value in model_dict['Attributes'].iteritems():
            newobj[key] = value['Value']
        newobj.get_attribute('Kind').get_attribute('List Options').setValue(
            model_dict['Attributes']['Kind']['Attributes']['List Options']['Value']
        )
        # Handle Children
        # TODO: Rework cardinality and how children can be inserted
        for obj_dict in model_dict['Children']:
            child = None
            if obj_dict['Type'] == 'MetaModel':
                child = MetaModel.fromDict(obj_dict, uuid_dict, unresolved_keys)
            elif obj_dict['Type'] == 'MetaAttribute':
                child = MetaAttribute.fromDict(obj_dict, uuid_dict, unresolved_keys)
            elif obj_dict['Type'] == 'MetaPointer':
                child = MetaPointer.fromDict(obj_dict, uuid_dict, unresolved_keys)
            if child:
                newobj.add_child(child)
        return newobj

    @staticmethod
    def fromMeta(model, uuid_dict):
        attr_dict = OrderedDict()

        # provides validator
        exec model['Attributes']['Validator']['Value'] in locals()
        # provides get_options
        exec model['Attributes']['Kind']['Attributes']['List Options']['Value'] in locals()

        for obj in model['Children']:
            if obj['Type'] == 'MetaAttribute':
                attr_dict[obj['Attributes']['Name']['Value']] = [
                    MetaAttribute.fromMeta(
                        obj,
                        uuid_dict
                    ),
                    obj['Attributes']['Parent Key']['Value']
                ]

        def attrInit(self):
            Attribute.__init__(
                self,
                model['Attributes']['Kind']['Value'],
                Attribute.default_vals[model['Attributes']['Kind']['Value']]
            )
            # Handle attributes
            for name, attrStruct in attr_dict.iteritems():
                attr = attrStruct[0]
                key = attrStruct[1]
                self.set_attribute(name, attr, key)

        new_attr = type(
            str(model['Attributes']['Name']['Value']),
            (Attribute, ),
            {
                '__init__': attrInit,
                'tooltip': model['Attributes']['Tooltip']['Value'],
                'display': model['Attributes']['Display']['Value'],
                'editable': model['Attributes']['Editable']['Value'],
                'get_options': get_options,
                'validator': validator,
            }
        )

        return new_attr()
    

class MetaPointer(Model):
    '''
    '''

    def __init__(self,
                 parent=None,
                 name='Pointer',
                 dst_type='MetaModel',
                 root_object_str='''def get_root(self):
    return self.parent''',
                 filter_function_str='''def filter_function(self, obj):
    objIsAllowed = True
    return objIsAllowed''',
                 tooltip='',
                 display=''):
        Model.__init__(self, parent)
        self.children = Children(cardinality={})
        self.attributes = OrderedDict()
        self.set_attribute('Name', NameAttribute(name))

        self.add_attribute('Destination Type', 'reference', '')
        destAttr = self.get_attribute('Destination Type')
        destAttr.dst_type = dst_type
        def get_root(s):
            r = s.parent
            while r.parent is not None:
                r = r.parent
            return r.children[0]
        def filter_function(s, o):
            return True
        destAttr.get_root = get_root
        destAttr.filter_function = filter_function

        self.set_attribute(
            'Root Object',
            Attribute(
                'python',
                root_object_str
            )
        )
        self.set_attribute(
            'Filter Function',
            Attribute(
                'python',
                filter_function_str
            )
        )
        self.set_attribute('Tooltip', Attribute('string', tooltip))
        self.set_attribute('Display', Attribute('string', display))
        
    @staticmethod
    def toDict(model):
        model_dict = Model.toDict(model)
        model_dict['Attributes'][
            'Destination Type'
        ] = model.get_attribute('Destination Type').getValue().uuid
        return model_dict

    @staticmethod
    def toMeta(model):

        # should fill out get_root(self)
        exec model['Root Object'] in globals()
        # should fill out filter_function(self, obj)
        exec model['Filter Function'] in globals()

        def ref_wrapper(s1, s2):
            return s1.get_references()

        def ptrInit(self):
            Pointer.__init__(
                self,
                dst_type=model['Destination Type']
            )
            self['Name'] = model['Name']
            destAttr = self.get_attribute('Destination')
            destAttr.dst_type = model['Destination Type']
            destAttr.tooltip = model['Tooltip']
            destAttr.display = model['Display']
            
        new_ptr = type(
            model['Name'],
            (Pointer, ),
            {
                '__init__': ptrInit,
                # from model['Valid Objects'] as exec'd text
                'get_root': get_root,
                'filter_function': filter_function,
            }
        )
        return new_ptr()

    @staticmethod
    def fromDict(model_dict, uuid_dict, unresolved_keys):
        newobj = MetaPointer()
        newobj.uuid = model_dict['UUID']
        uuid_dict[model_dict['UUID']] = newobj
        for key, value in model_dict['Attributes'].iteritems():
            if type(value) is not dict:
                continue
            newobj[key] = value['Value']
        key = model_dict['Attributes']['Destination Type']
        attr = newobj.get_attribute('Destination Type')
        if key not in uuid_dict:
            unresolved_keys.set_default(key, []).append(attr)
        else:
            attr.dst_type = uuid_dict[key].kind()
            attr.setValue(uuid_dict[key])
        return newobj

    @staticmethod
    def fromMeta(model, uuid_dict):

        # should fill out get_root(self)
        exec model['Attributes']['Root Object']['Value'] in globals()
        # should fill out filter_function(self, obj)
        exec model['Attributes']['Filter Function']['Value'] in globals()

        def ptrInit(self):
            Pointer.__init__(
                self,
                dst_type=model['Attributes']['Destination Type']
            )
            self['Name'] = model['Attributes']['Name']['Value']
            destAttr = self.get_attribute('Destination')
            destAttr.dst_type = uuid_dict[model['Attributes']['Destination Type']]
            destAttr.tooltip = model['Attributes']['Tooltip']['Value']
            destAttr.display = model['Attributes']['Display']['Value']
            destAttr.get_root = get_root
            destAttr.filter_function = filter_function
            
        new_ptr = type(
            str(model['Attributes']['Name']['Value']),
            (Pointer, ),
            {
                '__init__': ptrInit,
                # from model['Valid Objects'] as exec'd text
                'get_root': get_root,
                'filter_function': filter_function,
            }
        )
        return new_ptr()
    

class Children(MutableSequence):
    '''Children list which extends :class:`MutableSequence` and enforces
    item type and cardinality rules.

    **_inner** -- Contents of the list
    **_cardinality** -- A dictionary providing the types of allowed
    objects, and their cardinality

    '''

    def __init__(self, it=(), cardinality=OrderedDict()):
        '''
        :param in cardinality: :class:`Dictionary` of key:value pairs
            mapping object type to its cardinality string, e.g.
            Model: '0..*'

        '''
        self._inner = list(it)
        self._cardinality = cardinality

    @staticmethod
    def toDict(children):
        model_dict = OrderedDict()
        model_dict = [x.__class__.toDict(x) for x in children]
        return model_dict

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

    def number_of(self, item):
        children_types = [type(item) for val in self._inner]
        return children_types.count(type(item))

    def min_number_of(self, item):
        item_cardinality = self._cardinality[type(item)]
        vals = item_cardinality.split('..', 1)
        return int(vals[0])
        
    def max_number_of(self, item):
        item_cardinality = self._cardinality[type(item)]
        vals = item_cardinality.split('..', 1)
        if len(vals) > 1:
            if vals[1] != '*':
                return int(vals[1])
            else:
                return -1
        return self.min_number_of(item)

    def can_insert(self, item):
        # item is allowed as a child
        if type(item) in self.allowed():
            if item not in self._inner:
                num_allowed = self.max_number_of(item)
                num_existing = self.number_of(item)
                if num_allowed > 0 and num_existing >= num_allowed:
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
