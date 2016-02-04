#!/usr/bin/env python

'''
This file defines the functions that check Models to their
Meta-Meta-Model.
'''

__author__ = 'William Emfinger'
__copyright__ = 'Copyright 2016, ROSMOD'
__credits__ = ['William Emfinger', 'Pranav Srinivas Kumar']
__license__ = 'GPL'
__version__ = '0.4'
__maintainer__ = 'William Emfinger'
__email__ = 'emfinger@isis.vanderbilt.edu'
__status__ = 'Production'

import meta


def checkModelToMeta(root, meta_dict):
    test = False not in [
        checkObjectToMeta(c, meta_dict)
        for c in root
    ]
    return test


def checkChildrenToMeta(model_dict, meta_dict):
    meta_type = meta_dict[model_dict['Type']]
    meta_name = meta_type['Attributes']['Name']['Value']
    allowed_kids = [
        c['Attributes']['Name']['Value']
        for c in meta_type['Children']
        if 'Cardinality' in c['Attributes']
    ]
    cardinality = {
        c['Attributes']['Name']['Value']:
        c['Attributes']['Cardinality']['Value']
        for c in meta_type['Children']
        if 'Cardinality' in c['Attributes']
    }
    for c in model_dict['Children']:
        # make sure the child type exists in the meta-model
        if not checkObjectToMeta(c, meta_dict):
            print 'ERROR: Child type \'{}\' of {} not in meta-model!'.format(
                c['Type'],
                meta_name
            )
            return False
        child_meta_type = meta_dict[c['Type']]
        child_meta_name = child_meta_type['Attributes']['Name']['Value']
        # make sure the child type is allowed
        if child_meta_name not in allowed_kids:
            print 'ERROR: Child \'{}\' not allowed in {}!'.format(
                child_meta_name,
                meta_name
            )
            print '\tAllowed Children:\n\t\t{}'.format(allowed_kids)
            return False
    # make sure the parent is allowed to have this many kids of this type
    child_types = [
        meta_dict[c['Type']]['Attributes']['Name']['Value']
        for c in model_dict['Children']
    ]
    for kid_type in allowed_kids:
        min_num, max_num = meta.getMinMaxCardinality(
            cardinality[kid_type]
        )
        actual = child_types.count(kid_type)
        if actual < min_num:
            print 'ERROR: must have {} children of type \'{}\' in {}'.format(
                min_num,
                kid_type,
                meta_name
            )
            return False
        if max_num > 0 and actual > max_num:
            print 'ERROR: can only have {} children of type \'{}\' in {}'.format(
                max_num,
                kid_type,
                meta_name
            )
            return False
    return True


def checkPointersToMeta(model_dict, meta_dict):
    meta_type = meta_dict[model_dict['Type']]
    meta_name = meta_type['Attributes']['Name']['Value']
    allowed_ptrs = [
        p['Attributes']['Name']['Value']
        for p in meta_type['Children']
        if p['Type'] == 'MetaPointer'
    ]
    for p in model_dict['Pointers']:
        # make sure the child type exists in the meta-model
        if not checkObjectToMeta(p, meta_dict):
            print 'ERROR: Pointer \'{}\' of {} not in meta-model!'.format(
                p['Type'],
                meta_name
            )
            return False
        ptr_meta_type = meta_dict[p['Type']]
        ptr_meta_name = ptr_meta_type['Attributes']['Name']['Value']
        # make sure the child type is allowed
        if ptr_meta_name not in allowed_ptrs:
            print 'ERROR: Pointer type \'{}\' not allowed in {}!'.format(
                ptr_meta_name,
                meta_name
            )
            print '\tAllowed Pointers:\n\t\t{}'.format(allowed_ptrs)
            return False
    return True


def checkAttributesToMeta(model_dict, meta_dict):
    meta_type = meta_dict[model_dict['Type']]
    meta_name = meta_type['Attributes']['Name']['Value']

    allowed_attr = [
        a['Attributes']['Name']['Value']
        for a in meta_type['Children']
        if a['Type'] == 'MetaAttribute'
    ]

    for a in model_dict['Attributes']:
        if not checkObjectToMeta(a, meta_dict):
            print 'ERROR: Attribute \'{}\' of {} not in meta-model!'.format(
                a['Type'],
                meta_name
            )
            return False
        attr_meta_type = meta_dict[a['Type']]
        attr_meta_name = attr_meta_type['Attribute']['Name']['Value']
        if attr_meta_name not in allowed_attr:
            print 'ERROR: Attribute type \'{}\' not allowed in {}!'.format(
                attr_meta_name,
                meta_name
            )
            print '\tAllowed Attributes:\n\t\t{}'.format(allowed_attr)
            return False

    return True


def checkObjectToMeta(model_dict, meta_dict):
    '''
    This function does a first-level depth check of the validity of a
    model against its meta-model, contained within model_dict and
    meta_dict respectively.
    '''
    # check that it is a valid type
    if model_dict['Type'] not in meta_dict:
        print 'ERROR: object type \'{}\' not in metamodel!'.format(
            model_dict['Type']
        )
        return False

    # check that it has valid children types and numbers (cardinality)
    if 'Children' in model_dict:
        test = checkChildrenToMeta(model_dict, meta_dict)
        if not test:
            return test

    # check that is has valid pointer objects
    if 'Pointers' in model_dict:
        test = checkPointersToMeta(model_dict, meta_dict)
        if not test:
            return test

    # check that is has valid attribute objects
    if 'Attriburtes' in model_dict:
        test = checkAttributesToMeta(model_dict, meta_dict)
        if not test:
            return test
    return True

