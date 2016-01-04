
from meta import Model, Attribute, Children

TestModel = Model()
TestModel['Name'].value = 'Test Model'

root = Model()
root['Name'].value = 'Root'
TestModel.add_child( root )

c1 = Model()
c1['Name'].value = 'Software'
c2 = Model()
c2['Name'].value = 'Hardware'
c3 = Model()
c3['Name'].value = 'Deployment'

root.add_child( c1 )
root.add_child( c2 )
root.add_child( c3 )

c4 = Model()
c4['Name'].value = 'Package'
c5 = Model()

c1.add_child(c4)

c5['Name'].value = 'Message'
c6 = Model()
c6['Name'].value = 'Service'
c7 = Model()
c7['Name'].value = 'Component'
c8 = Model()

c4.add_child(c5)
c4.add_child(c6)
c4.add_child(c7)

c8['Name'].value = 'Timer'
c9 = Model()
c9['Name'].value = 'Publisher'
c10 = Model()
c10['Name'].value = 'Subscriber'
c11 = Model()
c11['Name'].value = 'Client'
c12 = Model()
c12['Name'].value = 'Server'

c7.add_child(c8)
c7.add_child(c9)
c7.add_child(c10)
c7.add_child(c11)
c7.add_child(c12)

c13 = Model()
c13['Name'].value = 'Host'
c14 = Model()
c14['Name'].value = 'Route'

c2.add_child(c13)
c2.add_child(c14)

c15 = Model()
c15['Name'].value = 'Interface'

c13.add_child(c15)

c16 = Model()
c16['Name'].value = 'Link'

c14.add_child(c16)

c17 = Model()
c17['Name'].value = 'Node'

c3.add_child(c17)

c18 = Model()
c18['Name'].value = 'Component Instance'

c17.add_child(c18)
