"""
View Attributes

These classes specify the attributes
that a view object can have when editing views

* author: William Emfinger
* website: github.com/finger563/editor 
* last edited: August 2015
"""

import inspect
import classes

test = inspect.getmembers(classes, inspect.isclass)
objects = ['Container', 'Association']
for key,val in test:
    if issubclass(val,classes.Model):
        objects.append(key)

# model related
class Object(classes.Attribute):
    tooltip = 'What kind of object is being viewed.'
    options = objects
    def __init__(self, value):
        super(Object, self).__init__("list",value)

class Scope(classes.Attribute):
    tooltip = 'From what scope will objects of this kind be drawn in this view?'
    options = ['project','view','parent']
    def __init__(self, value):
        super(Scope, self).__init__("list",value)

# drawing related
class Layout_Style(classes.Attribute):
    tooltip = 'How are the children arranged in this object.'
    options = ['horizontal','vertical','grid','anchor']
    def __init__(self, value):
        super(Layout_Style, self).__init__("list",value)

class Width(classes.Attribute):
    tooltip = 'Width of the object.'
    def __init__(self, value):
        super(Width, self).__init__("float",value)

class Height(classes.Attribute):
    tooltip = 'Height of the object.'
    def __init__(self, value):
        super(Height, self).__init__("float",value)

class Draw_Style(classes.Attribute):
    tooltip = 'How the object is drawn.'
    options = ['icon', 'ellipse', 'rect', 'round rect']
    def __init__(self, value):
        super(Draw_Style, self).__init__("list",value)

class Icon(classes.Attribute):
    tooltip = 'Icon displayed as background of the object.'
    def __init__(self, value):
        super(Icon, self).__init__("file_png",value)

class Color(classes.Attribute):
    tooltip = 'What color will the object be drawn with.'
    def __init__(self, value):
        super(Color, self).__init__("string",value)

class Text_Location(classes.Attribute):
    tooltip = 'Where will text be located?'
    options = ['top','bottom','left','right','center']
    def __init__(self, value):
        super(Text_Location, self).__init__("list",value)

class Text_Horizontal_Alignment(classes.Attribute):
    tooltip = 'Horizontal Alignment of text'
    options = ['left','right','horizontal center','justify']
    def __init__(self, value):
        super(Text_Horizontal_Alignment, self).__init__("list",value)

class Text_Vertical_Alignment(classes.Attribute):
    tooltip = 'Vertical Alignment of text'
    options = ['top','bottom','vertical center']
    def __init__(self, value):
        super(Text_Vertical_Alignment, self).__init__("list",value)

# Layout configuration related
class Layout_Config(classes.Attribute):
    options = ['horizontal','vertical','grid','anchor']
    editable = False
    def __init__(self, value):
        super(Layout_Config, self).__init__("dictionary_list", value)

class Root(classes.Attribute):
    tooltip = 'What acts as the local anchor for this object?'
    options = ['top left', 'top right',
               'bottom left', 'bottom right',
               'center left', 'center right',
               'top center', 'bottom center']
    def __init__(self, value):
        super(Root, self).__init__("list",value)

class Anchor(classes.Attribute):
    tooltip = 'What other object:point acts as the anchor for this object?'
    options = ['top left', 'top right',
               'bottom left', 'bottom right',
               'center left', 'center right',
               'top center', 'bottom center']
    editable = False
    def __init__(self, value):
        super(Anchor, self).__init__("dictionary_reference",value)

# Association
class Source(classes.Attribute):
    tooltip = 'What is the external oobject source reference for this object'
    def __init__(self, value):
        super(Source, self).__init__("string",value)

class Destination(classes.Attribute):
    tooltip = 'What is the external object destination reference for this object'
    def __init__(self, value):
        super(Destination, self).__init__("string",value)

