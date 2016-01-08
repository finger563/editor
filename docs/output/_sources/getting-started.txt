.. _getting-started:

Getting Started
===============

.. _using_the_editor:

Using the Editor
----------------

.. note:: This editor is under development.

The editor is designed to allow for graphical modeling of meta-models,
view-models, and models.  Meta-models and view-models are designed
based on a hardcoded meta-meta-model.  Models are designed based on
user-created meta-models which are loaded at run-time.  These
different types of models are all able to be created, loaded, edited,
and saved by the editor.  There is a mode selector in the editor which
allows the user to specify which kind of modeling they will be doing
(meta, view, model).

MetaModling
^^^^^^^^^^^ 

Meta-models define objects and their attributes.  For each meta-model,
there is always a single root, which may have any number of children
objects.  These children can have children of their own, and so on.
Furthermore, each object is specified with at least a **Name**
attribute which governs the name of the class definition that will be
created for that object.  The user can add other attributes which may
have specific types, such as **int**, **bool**, **string**, etc.
Finally, objects may contain pointers to other objects in the
meta-model.  These pointers specify that *model objects* which are
instances of that *meta object type* can have a pointer with the
specified name that points to objects of the *pointer object type*.

View-models are coupled with meta-models and models, and are similar
to meta-models.  They have a single *root view object* which may have
any number of children *view objects*.  Each *view object* contains a
*kind* attribute which specifies the *kind* of *meta object* they
display.  In addition, each *view object* has other attributes
governing its layout, text placement, draw style, etc.  When a *model
object* is loaded into the viewer, the editor automatically loads the
**view model** associated with that object's *meta type*.  If none can
be found, it will default to a predefined view model.

Developing a Module
-------------------

Modules consist of a meta-model file and a set of python files.  These
python files interact with models created using the meta-model and may
perform various functions operating on the model or on artifacts
generated from the model.  The editor provides a set of interfaces
allowing the module to create toolbar, menubar, context menu, and
other callback functions and associated shortcuts and buttons for
letting the user operate on the model.

Installation
^^^^^^^^^^^^

1. Download the analysis tool from the CBSAT repo:

 * `Github <https://github.com/finger563/editor/releases>`_

2. Install the dependencies of the editor:
   ``sudo pip install dill``

Congratulations!  The set-up of the editor is complete!
