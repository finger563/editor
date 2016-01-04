
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
