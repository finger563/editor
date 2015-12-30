
from meta import Model, Attribute, Children

TestModel = Model()
TestModel['Name'].value = 'Test Model'

root = Model()
root['Name'].value = 'Root'
TestModel.add_child( root )

c1 = Model()
c1['Name'].value = 'Child 1'
c2 = Model()
c2['Name'].value = 'Child 2'

root.add_child( c1 )
root.add_child( c2 )
