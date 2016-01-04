#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Test (meta)-model for the editor.
"""

__author__ = "William Emfinger"
__copyright__ = "Copyright 2016, ROSMOD"
__credits__ = ["William Emfinger", "Pranav Srinivas Kumar"]
__license__ = "GPL"
__version__ = "0.4"
__maintainer__ = "William Emfinger"
__email__ = "emfinger@isis.vanderbilt.edu"
__status__ = "Production"

from meta import Model, Pointer, Attribute, Children

TestModel = Model()
TestModel['Name'] = 'Test Model'

root = Model()
root['Name'] = 'Project'
TestModel.add_child( root )

c1 = Model()
c1['Name'] = 'Software'
c2 = Model()
c2['Name'] = 'Hardware'
c3 = Model()
c3['Name'] = 'Deployment'

root.add_child( c1 )
root.add_child( c2 )
root.add_child( c3 )

# Software
c4 = Model()
c4['Name'] = 'Package'

c1.add_child(c4)

# Package
c5 = Model()
c5['Name'] = 'Message'
c6 = Model()
c6['Name'] = 'Service'
c7 = Model()
c7['Name'] = 'Component'

c4.add_child(c5)
c4.add_child(c6)
c4.add_child(c7)

# Component
c8 = Model()
c8['Name'] = 'Timer'
c9 = Model()
c9['Name'] = 'Publisher'
c10 = Model()
c10['Name'] = 'Subscriber'
c11 = Model()
c11['Name'] = 'Client'
c12 = Model()
c12['Name'] = 'Server'

c7.add_child(c8)
c7.add_child(c9)
c7.add_child(c10)
c7.add_child(c11)
c7.add_child(c12)

msg_ref1 = Pointer()
msg_ref1['Name'] = 'Ref'
msg_ref2 = Pointer()
msg_ref2['Name'] = 'Ref'

c9.add_child(msg_ref1)
c10.add_child(msg_ref2)

srv_ref1 = Pointer()
srv_ref1['Name'] = 'Ref'
srv_ref2 = Pointer()
srv_ref2['Name'] = 'Ref'

c11.add_child(srv_ref1)
c12.add_child(srv_ref2)

# Hardware
c13 = Model()
c13['Name'] = 'Host'
c14 = Model()
c14['Name'] = 'Route'

c2.add_child(c13)
c2.add_child(c14)

c15 = Model()
c15['Name'] = 'Interface'

c13.add_child(c15)

c16 = Model()
c16['Name'] = 'Link'

c14.add_child(c16)

# Deployment 
hw_ref = Pointer()
hw_ref['Name'] = 'Hardware Ref'

c3.add_child(hw_ref)

c17 = Model()
c17['Name'] = 'Node'

c3.add_child(c17)

c18 = Model()
c18['Name'] = 'Component Instance'

c17.add_child(c18)
