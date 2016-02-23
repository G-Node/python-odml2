Terminology API
===============

Besides storing metadata odML also provides means to define the terms used in doML documents
in a terminology. Further the terminologies can even serve as schema like restrictions new
documents have to adhere to.

In odML terminologies consist of two building blocks: type definitions (:class:`~.TypeDef`) and
property definitions (:class:`~.PropertyDef`).

Type definition
---------------

A type definitions describes the type of a thing an odML section can represent. For example: an
experiment, recording session or subject.

The most important part of a type definition is a good type name. It is recommended to use
camel-case names that start with a capital letter e.g. 'Experiment', 'RecordingSession'
or 'Subject'.

In addition a type can have a textual description of the thing it represents.

Finally a type definition can have a set of property names that defined common attributes
of the type. The property names used in type definitions should have a corresponding
property definition (:class:`~.PropertyDef`).

.. autoclass:: odml2.TypeDef
    :members:
    :undoc-members:


Property definition
-------------------

A property definition describes a certain attribute of an odML type definition. The most
essential part of a property definition is the properties name. It is recommended to use
snake-case names that start with a lower letter: 'recording_time', 'age' or 'date_of_birth'.

In addition a property can have a textual description of the attribute it represents.

Further a property definition can have a set of type names associated with it. The type name
must either be the name defined by another type definition or the type of a predefined data type
for odML values: 'string', 'bool', 'int', 'float', 'time', 'date' or 'datetime'.

.. autoclass:: odml2.PropertyDef
    :members:
    :undoc-members:

