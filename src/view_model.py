'''
These classes contain all the relevant
infomation required to configure or draw
a view for a model
'''

__author__ = 'William Emfinger'
__copyright__ = 'Copyright 2016, ROSMOD'
__credits__ = ['William Emfinger', 'Pranav Srinivas Kumar']
__license__ = 'GPL'
__version__ = '0.4'
__maintainer__ = 'William Emfinger'
__email__ = 'emfinger@isis.vanderbilt.edu'
__status__ = 'Production'

from meta import Model, Children

import view_attributes as view_attr

# TODO: Figure out the structure of the view model and how
#       to access the classes and attributes of the view-model


class ViewModel(Model):
    '''
    Subclass of :class:`Model` which contains attributes that specify
    view controls for objects, such as anchor points, relative text
    location, draw style, etc.
    '''
    def __init__(self,
                 kind='Container',
                 root='top left',
                 anchor='top left',
                 text_loc='top',
                 text_ha='left',
                 text_va='top',
                 scope='parent',
                 draw_style='round rect',
                 icon_file='',
                 src='',
                 dst='',
                 color='light blue',
                 width=50.0,
                 height=50.0,
                 layout='horizontal'):
        super(ViewModel, self).__init__()
        self.children = Children(allowed=[ViewModel],
                                 cardinality={ViewModel: '0..*'})

        # describe the model
        self.set_attribute('Kind', view_attr.Object(kind))
        self.set_attribute('Scope', view_attr.Scope(scope))

        # describe the drawing of the object
        self.set_attribute('layout style', view_attr.Layout_Style(layout))
        self.set_attribute('width', view_attr.Width(width))
        self.set_attribute('height', view_attr.Height(height))
        self.set_attribute('draw style', view_attr.Draw_Style(draw_style))
        self.set_attribute('icon', view_attr.Icon(icon_file))
        self.set_attribute('color', view_attr.Color(color))
        self.set_attribute('text location', view_attr.Text_Location(text_loc))
        self.set_attribute('text horizontal alignment',
                           view_attr.Text_Horizontal_Alignment(text_ha))
        self.set_attribute('text vertical alignment',
                           view_attr.Text_Vertical_Alignment(text_va))

        # these are relevant for objects which are children of layouts
        self.set_attribute('layout config', view_attr.Layout_Config({}))
        self.set_attribute('root', view_attr.Root(root))
        # self.set_attribute('anchor', view_attr.Anchor(anchor))

        # these are relevant for Lines
        self.set_attribute('source', view_attr.Source(src))
        self.set_attribute('destination', view_attr.Source(dst))

    def toStr(self, printKids=True, prefix=''):
        retstr = ''
        retstr += '{}Kind: {}\n'.format(prefix, self['Kind'])
        if printKids:
            for c in self.children:
                retstr += '{}{}\n'.format(prefix, c)
                retstr += c.toStr(printKids, prefix + '\t')
        return retstr
