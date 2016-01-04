
from meta import Model, Attribute, Children

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

c4 = Model()
c4['Name'] = 'Package'
c5 = Model()

c1.add_child(c4)

c5['Name'] = 'Message'
c6 = Model()
c6['Name'] = 'Service'
c7 = Model()
c7['Name'] = 'Component'
c8 = Model()

c4.add_child(c5)
c4.add_child(c6)
c4.add_child(c7)

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

c17 = Model()
c17['Name'] = 'Node'

c3.add_child(c17)

c18 = Model()
c18['Name'] = 'Component Instance'

c17.add_child(c18)
