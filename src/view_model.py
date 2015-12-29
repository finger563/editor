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
                 kind = 'Container',
                 root = 'top left',
                 anchor = 'top left',
                 text_loc = 'top',
                 text_ha = 'left',
                 text_va = 'top',
                 scope = 'parent',
                 draw_style = 'round rect',
                 icon_file = '',
                 src = '',
                 dst = '',
                 color = 'light blue',
                 width = 50.0,
                 height = 50.0,
                 layout = 'horizontal'):
        self.attributes = OrderedDict()
        
        # describe the model
        self['kind'] = view_attr.Object(kind)
        self['scope'] = view_attr.Scope(scope)

        # describe the drawing of the object
        self['layout style'] = view_attr.Layout_Style(layout)
        self['width'] = view_attr.Width(width)
        self['height'] = view_attr.Height(height)
        self['draw style'] = view_attr.Draw_Style(draw_style)
        self['icon'] = view_attr.Icon(icon_file)
        self['color'] = view_attr.Color(color)
        self['text location'] = view_attr.Text_Location(text_loc)
        self['text horizontal alignment'] = view_attr.Text_Horizontal_Alignment(text_ha)
        self['text vertical alignment'] = view_attr.Text_Vertical_Alignment(text_va)

        # these are relevant for objects which are children of layouts
        self['layout config'] = view_attr.Layout_Config({})
        self['root'] = view_attr.Root(root)
        #self['anchor'] = view_attr.Anchor(anchor)

        # these are relevant for associations
        self['source'] = view_attr.Source(src)
        self['destination'] = view_attr.Source(dst)

        self.children = []

    def __getitem__(self, key):
        return self.attributes[key]

    def __setitem__(self, key, value):
        self.attributes[key] = value

    def add_child(self, child):
        if child not in self.children:
            self.children.append(child)

    def remove_child(self, child):
        self.children = [x for x in self.children if x != child]

    def toStr(self, printKids = True, prefix = ''):
        retstr = ''
        retstr += '{}Kind: {}\n'.format(prefix,self['kind'].value)
        if printKids:
            for c in self.children:
                retstr += "{}{}\n".format(prefix,c)
                retstr += c.toStr(printKids, prefix + '\t')
        return retstr
