'''
These classes specify the attributes
that a view object can have when editing views
'''

__author__ = 'William Emfinger'
__copyright__ = 'Copyright 2016, ROSMOD'
__credits__ = ['William Emfinger', 'Pranav Srinivas Kumar']
__license__ = 'GPL'
__version__ = '0.4'
__maintainer__ = 'William Emfinger'
__email__ = 'emfinger@isis.vanderbilt.edu'
__status__ = 'Production'

from meta import Attribute

objects = ['Container', 'Association']


# model related
class Object(Attribute):
    tooltip = 'What kind of object is being viewed.'
    options = objects

    def __init__(self, value):
        super(Object, self).__init__('list', value)


# drawing related
class Layout_Style(Attribute):
    tooltip = 'How are the children arranged in this object.'
    options = ['horizontal', 'vertical', 'grid', 'anchor']

    def __init__(self, value):
        super(Layout_Style, self).__init__('list', value)


class Width(Attribute):
    tooltip = 'Width of the object.'

    def __init__(self, value):
        super(Width, self).__init__('float', value)


class Height(Attribute):
    tooltip = 'Height of the object.'

    def __init__(self, value):
        super(Height, self).__init__('float', value)


class Draw_Style(Attribute):
    tooltip = 'How the object is drawn.'
    options = ['icon', 'ellipse', 'rect', 'round rect', 'hidden']

    def __init__(self, value):
        super(Draw_Style, self).__init__('list', value)


class Icon(Attribute):
    tooltip = 'Icon displayed as background of the object.'

    def __init__(self, value):
        super(Icon, self).__init__('file_png', value)


class Color(Attribute):
    tooltip = 'What color will the object be drawn with.'

    def __init__(self, value):
        super(Color, self).__init__('string', value)


class Text_Location(Attribute):
    tooltip = 'Where will text be located?'
    options = ['top', 'bottom', 'left', 'right', 'center']

    def __init__(self, value):
        super(Text_Location, self).__init__('list', value)


class Text_Horizontal_Alignment(Attribute):
    tooltip = 'Horizontal Alignment of text'
    options = ['left', 'right', 'horizontal center', 'justify']

    def __init__(self, value):
        super(Text_Horizontal_Alignment, self).__init__('list', value)


class Text_Vertical_Alignment(Attribute):
    tooltip = 'Vertical Alignment of text'
    options = ['top', 'bottom', 'vertical center']

    def __init__(self, value):
        super(Text_Vertical_Alignment, self).__init__('list', value)


# Layout configuration related
class Layout_Config(Attribute):
    options = ['horizontal', 'vertical', 'grid', 'anchor']
    editable = False

    def __init__(self, value):
        super(Layout_Config, self).__init__('dictionary_list', value)


class Root(Attribute):
    tooltip = 'What acts as the local anchor for this object?'
    options = ['top left', 'top right',
               'bottom left', 'bottom right',
               'center left', 'center right',
               'top center', 'bottom center']

    def __init__(self, value):
        super(Root, self).__init__('list', value)


class Anchor(Attribute):
    tooltip = 'What other object:point acts as the anchor for this object?'
    options = ['top left', 'top right',
               'bottom left', 'bottom right',
               'center left', 'center right',
               'top center', 'bottom center']
    editable = False

    def __init__(self, value):
        super(Anchor, self).__init__('dictionary_reference', value)


# Association
class Source(Attribute):
    tooltip = 'What is the external oobject source reference for this object'

    def __init__(self, value):
        super(Source, self).__init__('string', value)


class Destination(Attribute):
    tooltip = 'What is the object destination reference for this object'

    def __init__(self, value):
        super(Destination, self).__init__('string', value)

