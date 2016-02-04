#!/usr/bin/env python

'''
This file defines the functions that allow loading and converting
metamodels.
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


def buildMeta(meta_dict, model_dict, uuid_dict):
    '''This function builds a dict of uuid: meta_dict[key] pairs.'''
    if model_dict['UUID'] not in meta_dict:
        meta_dict[model_dict['UUID']] = model_dict

    # TODO: PUT CLASS CODE HERE FOR INSTANTIATING OBJECTS
    uuid = model_dict['UUID']
    class_type = meta_dict[uuid]['Type']
    if uuid == 'MetaModel':
        meta_dict[uuid]['__CLASS__'] = meta.MetaModel
    elif uuid == 'MetaAttribute':
        meta_dict[uuid]['__CLASS__'] = meta.MetaAttribute
    elif uuid == 'MetaPointer':
        meta_dict[uuid]['__CLASS__'] = meta.MetaPointer
    elif class_type == 'MetaModel':
        meta_dict[uuid]['__CLASS__'] = meta.MetaModel.fromMeta(
            model_dict, uuid_dict
        )
    elif class_type == 'MetaAttribute':
        meta_dict[uuid]['__CLASS__'] = meta.MetaAttribute.fromMeta(
            model_dict, uuid_dict
        )
    elif class_type == 'MetaPointer':
        meta_dict[uuid]['__CLASS__'] = meta.MetaPointer.fromMeta(
            model_dict, uuid_dict
        )

    for c in model_dict['Children']:
        buildMeta(meta_dict, c, uuid_dict)
    for p in model_dict['Pointers']:
        buildMeta(meta_dict, p, uuid_dict)


def convertDictToModel(root_dict, meta_dict):
    # TODO: Make this recursive function which uses meta_dict[obj
    #       type]['__CLASS__'] to instantiate object

    # TODO: Since classes are stored in the meta-dict, figure out how
    #       meta-models will load and instantiate versus how models
    #       will load and instantiate.  Probably will have to have
    #       MetaMetaModel Dict have the class types for MetaModel,
    #       MetaAttribute, and MetaPointer (What about
    #       NameAttribute?), while when building the metadict for
    #       MetaModels to be used with models we will need to use the
    #       fromDict method (or a new equivalent)

    # TODO: Figure out how to properly pass the data in to the newly
    #       created objects
    roots = []
    uuid_dict = {}
    unresolved_keys = {}
    for root in root_dict:
        roots.append(meta.MetaModel.fromDict(root, uuid_dict, unresolved_keys))
    for uuid_key, attr_list in unresolved_keys.iteritems():
        for attr in attr_list:
            if uuid_key in uuid_dict:
                attr.dst_type = uuid_dict[uuid_key].kind()
                attr.setValue(uuid_dict[uuid_key])
            else:
                ur = meta.UnknownReference()
                ur['Reference'] = attr.getValue()
                attr.setValue(ur)
    return roots


