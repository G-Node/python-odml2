Document API
============

Representation of an odML document.
Depending on the used back-end an odML document can either be attached to a certain
data source (e.g. a data base) or it can be detached.
Attached documents persist changes immediately to the respective data source while detached
documents write data only when :meth:`~.Document.save` is called.


.. autoclass:: odml2.Document
    :members:
    :undoc-members:


TerminologyStrategy
-------------------

The terminology strategy defines how section types and property names are handled
with respect to a given terminology.

.. class:: odml.TerminologyStrategy

    .. attribute:: Ignore

        Terminology violations such as undefined type or property names are always ignored.
        This is the default strategy.

    .. attribute:: Create

        Property and type definitions without prefix are created and updated on the fly.
        This strategy can be used in order to define your custom terminology.

    .. attribute:: Strict

        Each property and type must be defined and used correctly.
        This strategy can be used to ensure that a document adheres to a terminology.


NameSpaceMap
------------

Provides a dictionary like access to all name spaces of a document.

.. autoclass:: odml2.NameSpaceMap
    :members: set, __len__, __iter__, __getitem__, __setitem__, __delitem__, __str__
    :undoc-members:

    .. method:: keys()

       List or generator of all keys

    .. method:: items()

       List or generator over all items

    .. method:: values()

       List or generator over all name space objects


TypeDefMap
----------

Provides a dictionary like access to all type definitions which are part of the terminology
of a document.

.. autoclass:: odml2.TypeDefMap
    :members: __len__, __iter__, __getitem__, __setitem__, __delitem__, __str__
    :undoc-members:

    .. method:: keys()

       List or generator of all keys

    .. method:: items()

       List or generator over all items

    .. method:: values()

       List or generator over all type definition objects

PropertyDefMap
--------------

Provides a dictionary like access to all property definitions which are part of the terminology
of a document.

.. autoclass:: odml2.PropertyDefMap
    :members: __len__, __iter__, __getitem__, __setitem__, __delitem__, __str__
    :undoc-members:

    .. method:: keys()

        List or generator of all keys

    .. method:: items()

        List or generator over all items

    .. method:: values()

        List or generator over all property definition objects
