"""
View Model

These classes contain all the relevant
infomation required to configure or draw
a view for a model

* author: William Emfinger
* website: github.com/finger563/editor
* last edited: August 2015
"""

from collections import OrderedDict

import view_attributes as view_attr

class ViewModel(object):
    def __init__(self,
                 parent = None,
                 kind = '',
                 root = 'center',
                 anchor = 'top left',
                 text_loc = 'top',
                 text_ha = 'center',
                 text_va = 'center',
                 scope = 'view',
                 draw_style = 'icon',
                 icon_file = "",
                 color = 'blue',
                 width = 100,
                 height = 100,
                 layout = 'horizontal'):
        self.attributes = OrderedDict()
        self['kind'] = view_attr.Object(kind)
        self['text location'] = view_attr.Text_Location(text_loc)
        self['text horizontal alignment'] = view_attr.Text_Horizontal_Alignment(text_ha)
        self['text vertical alignment'] = view_attr.Text_Vertical_Alignment(text_va)
        self['root'] = view_attr.Root(root)
        self['anchor'] = view_attr.Anchor(anchor)
        self['scope'] = view_attr.Scope(scope)
        self['icon'] = view_attr.Icon(icon_file)
        self['draw style'] = view_attr.Draw_Style(draw_style)
        self['color'] = view_attr.Color(color)
        self['layout style'] = view_attr.Layout_Style(layout)
        self['width'] = view_attr.Width(width)
        self['height'] = view_attr.Height(height)

        self.children = []

    def __getitem__(self, key):
        return self.attributes[key]

    def __setitem__(self, key, value):
        self.attributes[key] = value

    def addChild(self, child):
        if child not in self.children:
            self.children.append(child)

    def removeChild(self, child):
        self.children = [x for x in self.children if x != child]

