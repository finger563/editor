"""
View Attributes

These classes specify the attributes
that a view object can have when editing views

* author: William Emfinger
* website: github.com/finger563/editor 
* last edited: August 2015
"""

from classes import *

class Object(Attribute):
    tooltip = 'What kind of object is being viewed.'
    options = ['test 1','test 2','service','message']
    def __init__(self, value):
        super(Object, self).__init__("list",value)

class Icon(Attribute):
    tooltip = 'Icon displayed as background of the object.'
    def __init__(self, value):
        super(Icon, self).__init__("file",value)

class Draw_Style(Attribute):
    tooltip = 'How the object is drawn.'
    options = ['icon', 'ellipse', 'rect', 'round rect']
    def __init__(self, value):
        super(Draw_Style, self).__init__("list",value)

class Anchor(Attribute):
    tooltip = 'Which point on the object acts as its root point'
    options = ['top left', 'top right',
               'bottom left', 'bottom right',
               'center left', 'center right',
               'top center', 'bottom center']
    def __init__(self, value):
        super(Anchor, self).__init__("list",value)

class Layout_Style(Attribute):
    tooltip = 'How are the children arranged in this object.'
    options = ['horizontal','vertical','grid','anchor']
    def __init__(self, value):
        super(Layout_Style, self).__init__("list",value)

class Color(Attribute):
    tooltip = 'What color will the object be drawn with.'
    def __init__(self, value):
        super(Color, self).__init__("string",value)

class Width(Attribute):
    tooltip = 'Width of the object.'
    def __init__(self, value):
        super(Width, self).__init__("float",value)

class Height(Attribute):
    tooltip = 'Height of the object.'
    def __init__(self, value):
        super(Height, self).__init__("float",value)

